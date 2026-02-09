from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q, F, Avg, FloatField
from django.db.models.functions import Greatest
from .models import Product


class ProductSearch:
    """Product search with PostgreSQL full-text search"""
    def __init__(self, query=None, filters=None):
        self.query = query
        self.filters = filters or {}

    def get_base_queryset(self):
        return Product.objects.select_related(
            'category', 'student', 'student__user'
        ).prefetch_related('reviews').filter(is_active=True)

    def apply_search(self, queryset):
        if not self.query:
            return queryset

        vector = SearchVector('title', weight='A') + \
                 SearchVector('description', weight='B') + \
                 SearchVector('category__name', weight='C')
        
        search_query = SearchQuery(self.query)
        rank = SearchRank(vector, search_query)
        
        similarities = [
            TrigramSimilarity('title', self.query),
            TrigramSimilarity('description', self.query),
            TrigramSimilarity('category__name', self.query)
        ]
        
        combined_similarity = Greatest(*similarities)
        
        return queryset.annotate(
            search_rank=rank,
            similarity=combined_similarity,
            search_score=Greatest(F('search_rank'), F('similarity'), output_field=FloatField())
        ).filter(
            Q(search_rank__gte=0.3) | Q(similarity__gte=0.3)
        ).order_by('-search_score')

    def apply_filters(self, queryset):
        if category_id := self.filters.get('category'):
            queryset = queryset.filter(category_id=category_id)
        
        if min_price := self.filters.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.filters.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)
        
        if condition := self.filters.get('condition'):
            queryset = queryset.filter(condition=condition)
        
        if self.filters.get('in_stock'):
            queryset = queryset.filter(stock__gt=F('reserved_stock'))
        
        if student_id := self.filters.get('student'):
            queryset = queryset.filter(student_id=student_id)
        
        return queryset

    def apply_sorting(self, queryset):
        sort_by = self.filters.get('sort_by', 'newest')
        
        if sort_by == 'price_asc':
            return queryset.order_by('price')
        elif sort_by == 'price_desc':
            return queryset.order_by('-price')
        elif sort_by == 'rating':
            return queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        elif sort_by == 'popularity':
            return queryset.order_by('-views_count')
        
        return queryset.order_by('-created_at')

    def search(self):
        queryset = self.get_base_queryset()
        
        if self.query:
            queryset = self.apply_search(queryset)
        
        queryset = self.apply_filters(queryset)
        
        if not self.query:
            queryset = self.apply_sorting(queryset)
        
        return queryset


def search_products(query=None, filters=None):
    searcher = ProductSearch(query, filters)
    return searcher.search()
