# core/views.py

from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .models import User, Organization, Cluster, Deployment
from .serializers import UserSerializer, OrganizationSerializer, ClusterSerializer, DeploymentSerializer
from .tasks import schedule_deployments
from .permissions import IsAdmin, IsDeveloper, IsViewer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, IsDeveloper]


def delete_deployment(deployment):
    cluster = deployment.cluster
    cluster.available_ram += deployment.required_ram
    cluster.available_cpu += deployment.required_cpu
    cluster.available_gpu += deployment.required_gpu
    cluster.save()


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    permission_classes = [IsAuthenticated, IsDeveloper]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        deployment = serializer.instance
        schedule_deployments.delay()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        delete_deployment(instance)
        instance.delete()
        schedule_deployments.delay()


class JoinOrganization(APIView):
    permission_classes = [IsAuthenticated, IsViewer]

    def post(self, *args, **kwargs):
        user = self.request.user
        invite_code = self.request.data.get('invite_code')
        try:
            organization = Organization.objects.get(invite_code=invite_code)
            user.organization = organization
            user.save()
            return Response({'status': 'joined'}, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response({'error': 'Invalid invite code'}, status=status.HTTP_400_BAD_REQUEST)
