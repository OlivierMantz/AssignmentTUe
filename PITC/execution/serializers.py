from rest_framework import serializers
from .models import User, ServiceProvider, AccountManager, Customer, Job, Order, ServiceProviderAccountManager

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type']

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'description']

class ServiceProviderAccountManagerSerializer(serializers.ModelSerializer):
    service_provider = ServiceProviderSerializer(read_only=True)

    class Meta:
        model = ServiceProviderAccountManager
        fields = ['id', 'service_provider', 'assigned_date', 'is_active']

class AccountManagerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    managed_providers = serializers.PrimaryKeyRelatedField(queryset=ServiceProvider.objects.all(), many=True)

    class Meta:
        model = AccountManager
        fields = ['user', 'managed_providers']

    def update(self, instance, validated_data):
        managed_providers = validated_data.pop('managed_providers', None)
        instance = super().update(instance, validated_data)
        
        if managed_providers is not None:
            current_providers = set(instance.managed_providers.all())
            new_providers = set(managed_providers)
            
            for provider in current_providers - new_providers:
                ServiceProviderAccountManager.objects.filter(
                    account_manager=instance,
                    service_provider=provider
                ).update(is_active=False)
            
            for provider in new_providers - current_providers:
                ServiceProviderAccountManager.objects.update_or_create(
                    account_manager=instance,
                    service_provider=provider,
                    defaults={'is_active': True}
                )
        
        return instance
    def get_managed_providers(self, obj):
        managed_providers = ServiceProviderAccountManager.objects.filter(
            account_manager=obj,
            is_active=True
        )
        return ServiceProviderAccountManagerSerializer(managed_providers, many=True).data

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assigned_account_manager = serializers.PrimaryKeyRelatedField(queryset=AccountManager.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Customer
        fields = ['user', 'assigned_account_manager']
        
    def create(self, validated_data):
        user_data = self.context['request'].data.get('user')
        if not user_data:
            raise serializers.ValidationError("User data is required")
        
        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            user_type='CUSTOMER'
        )
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'account_manager', 'job', 'quantity', 'created_at']

    def validate(self, data):
        customer = data['customer']
        job = data['job']
        account_manager = data['account_manager']

        if account_manager != customer.assigned_account_manager:
            raise serializers.ValidationError("The account manager must be the customer's assigned manager.")

        if job.service_provider not in account_manager.managed_providers.all():
            raise serializers.ValidationError("The job's service provider must be managed by the account manager.")

        return data

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['job_id', 'job_name', 'state', 'job_type', 'starting_date', 'end_date', 'completion_time', 'service_provider', 'price']
        read_only_fields = ['job_id']  