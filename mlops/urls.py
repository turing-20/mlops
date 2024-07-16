# mlops/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import RegisterView, OrganizationViewSet, ClusterViewSet, DeploymentViewSet, JoinOrganization

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'clusters', ClusterViewSet)
router.register(r'deployments', DeploymentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/organizations/join/', JoinOrganization.as_view(), name='join-organization'),
    path('api/', include(router.urls)),
]


