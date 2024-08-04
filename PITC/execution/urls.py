from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ServiceProviderViewSet,
    AccountManagerViewSet,
    CustomerViewSet,
    JobViewSet,
    OrderViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'service-providers', ServiceProviderViewSet)
router.register(r'account-managers', AccountManagerViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]