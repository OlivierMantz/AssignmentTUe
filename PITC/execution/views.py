from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import User, ServiceProvider, AccountManager, Customer, Job, Order, ServiceProviderAccountManager
from .serializers import (
    UserSerializer, 
    ServiceProviderSerializer, 
    AccountManagerSerializer,
    CustomerSerializer,
    JobSerializer,
    OrderSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer


class AccountManagerViewSet(viewsets.ModelViewSet):
    queryset = AccountManager.objects.all()
    serializer_class = AccountManagerSerializer

    @action(detail=True, methods=['post'])
    def add_provider(self, request, pk=None):
        account_manager = self.get_object()
        provider_id = request.data.get('provider_id')
        
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(id=provider_id)
                ServiceProviderAccountManager.objects.get_or_create(
                    account_manager=account_manager,
                    service_provider=provider,
                    defaults={'is_active': True}
                )
                return Response({'status': 'provider added'}, status=status.HTTP_200_OK)
            except ServiceProvider.DoesNotExist:
                return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'provider_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_provider(self, request, pk=None):
        account_manager = self.get_object()
        provider_id = request.data.get('provider_id')
        
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(id=provider_id)
                ServiceProviderAccountManager.objects.filter(
                    account_manager=account_manager,
                    service_provider=provider
                ).update(is_active=False)
                return Response({'status': 'provider removed'}, status=status.HTTP_200_OK)
            except ServiceProvider.DoesNotExist:
                return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'provider_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def assign_account_manager(self, request, pk=None):
        customer = self.get_object()
        account_manager_id = request.data.get('account_manager_id')
        if account_manager_id:
            try:
                account_manager = AccountManager.objects.get(id=account_manager_id)
                customer.assigned_account_manager = account_manager
                customer.save()
                return Response({'status': 'account manager assigned'})
            except AccountManager.DoesNotExist:
                return Response({'error': 'Account manager not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'account_manager_id is required'}, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        account_manager_id = self.request.query_params.get('account_manager_id')
        customer_id = self.request.query_params.get('customer_id')
        
        queryset = Order.objects.all()
        
        if account_manager_id:
            queryset = queryset.filter(account_manager_id=account_manager_id)
        elif customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        return queryset

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer