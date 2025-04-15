from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,OrderViewSet,UserProfileViewSet
from django.urls import path, include
router=DefaultRouter()
router.register('products',ProductViewSet)
router.register('orders',OrderViewSet)
router.register('user-profiles',UserProfileViewSet)
urlpatterns = [
    path('',include(router.urls))
]