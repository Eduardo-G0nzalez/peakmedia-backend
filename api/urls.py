from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserLibraryViewSet, SearchAPI, UserCreate

router = DefaultRouter()
router.register(r'library', UserLibraryViewSet, basename='library')

urlpatterns = [
    path('', include(router.urls)),
    
    path('search/', SearchAPI.as_view(), name='search-api'),
    
    # URLs de Autenticación
    path('register/', UserCreate.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]