from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import UserSerializer, DashboardDataSerializer
from ..models import User, DashboardData

class AdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        data = DashboardData.get_dashboard_data()
        serializer = DashboardDataSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def users(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data) 