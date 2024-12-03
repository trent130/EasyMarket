from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity
)
from django.db.models import Q, F, Value, FloatField, Avg
from django.db.models.functions import Greatest
from django.conf import settings
from .models import Product
from marketplace.models import Review

class ProductSearch:
    """Product search functionality with full-text search and trigram similarity"""
    
    def __init__(self, query=None, filters=None):
        self.query = query
        self.filters = filters or {}
        self.search_fields = ['title', 'description', 'category__name']
        self.vector = None
        self.base_queryset = None

    def get_base_queryset(self):
        """Get base queryset with all necessary joins"""
        if not self.base_queryset:
            self.base_queryset = Product.objects.select_related(
                'category',
                'student',
                'student__user'
            ).prefetch_related(
                'reviews'
            ).filter(
                is_active=True
            )
        return self.base_queryset

    def apply_search(self, queryset):
        """Apply full-text search with ranking"""
        if not self.query:
            return queryset

        # Create search vector
        self.vector = SearchVector('title', weight='A') + \
                     SearchVector('description', weight='B') + \
                     SearchVector('category__name', weight='C')

        # Create search query
        search_query = SearchQuery(self.query)

        # Calculate search rank and trigram similarity
        rank = SearchRank(self.vector, search_query)
        
        # Calculate trigram similarity for each search field
        similarities = []
        for field in self.search_fields:
            similarity = TrigramSimilarity(field, self.query)
            similarities.append(similarity)

        # Combine similarities using Greatest
        combined_similarity = Greatest(*similarities)

        # Annotate queryset with search rank and similarity
        queryset = queryset.annotate(
            search_rank=rank,
            similarity=combined_similarity,
            search_score=Greatest(
                F('search_rank'),
                F('similarity'),
                output_field=FloatField()
            )
        ).filter(
            Q(search_rank__gte=0.3) | Q(similarity__gte=0.3)
        ).order_by('-search_score')

        return queryset

    def apply_filters(self, queryset):
        """Apply filters to queryset"""
        # Category filter
        if category_id := self.filters.get('category'):
            queryset = queryset.filter(category_id=category_id)

        # Price range filter
        if min_price := self.filters.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)
        if max_price := self.filters.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)

        # Condition filter
        if condition := self.filters.get('condition'):
            queryset = queryset.filter(condition=condition)

        # Stock filter
        if self.filters.get('in_stock'):
            queryset = queryset.filter(stock__gt=F('reserved_stock'))

        # Student filter
        if student_id := self.filters.get('student'):
            queryset = queryset.filter(student_id=student_id)

        return queryset

    def apply_sorting(self, queryset):
        """Apply sorting to queryset"""
        sort_by = self.filters.get('sort_by', 'newest')
        
        if sort_by == 'price_asc':
            return queryset.order_by('price')
        elif sort_by == 'price_desc':
            return queryset.order_by('-price')
        elif sort_by == 'rating':
            return queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'popularity':
            return queryset.order_by('-views_count')
        
        # Default to newest
        return queryset.order_by('-created_at')

    def search(self):
        """Execute search and return results"""
        queryset = self.get_base_queryset()
        
        # Apply search if query exists
        if self.query:
            queryset = self.apply_search(queryset)
        
        # Apply filters
        queryset = self.apply_filters(queryset)
        
        # Apply sorting if no search query
        # (search results are already sorted by relevance)
        if not self.query:
            queryset = self.apply_sorting(queryset)

        return queryset

def search_products(query=None, filters=None):
    """Helper function to perform product search"""
    searcher = ProductSearch(query, filters)
    return searcher.search()
