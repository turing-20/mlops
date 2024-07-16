# core/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from .models import Organization, Cluster, Deployment, User


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123')
        self.user = User.objects.create_user('newuser', 'user@test.com', 'password123')

    def test_register_user(self):
        data = {
            'username': 'testuser',
            'role': 'admin',
            'password': 'password123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)  # Adjust count based on existing users

    def test_login_user(self):
        data = {
            'username': 'newuser',
            'password': 'password123',
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'user',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RBACTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123', role='admin')
        self.developer_user = User.objects.create_user('developer', 'dev@test.com', 'password123', role='developer')
        self.viewer_user = User.objects.create_user('viewer', 'viewer@test.com', 'password123', role='viewer')
        self.organization = Organization.objects.create(name='Test Org')
        self.client_admin = APIClient()
        self.client_developer = APIClient()
        self.client_viewer = APIClient()
        self.client_admin.force_authenticate(user=self.admin_user)
        self.client_developer.force_authenticate(user=self.developer_user)
        self.client_viewer.force_authenticate(user=self.viewer_user)

    def test_create_organization(self):
        url = reverse('organization-list')
        data = {'name': 'New Org', "invite_code": "1234"}

        # Admin should be able to create organization
        response_admin = self.client_admin.post(url, data, format='json')
        self.assertEqual(response_admin.status_code, status.HTTP_201_CREATED)

        # Developer should not be able to create organization
        response_developer = self.client_developer.post(url, data, format='json')
        self.assertEqual(response_developer.status_code, status.HTTP_403_FORBIDDEN)

        # Viewer should not be able to create organization
        response_viewer = self.client_viewer.post(url, data, format='json')
        self.assertEqual(response_viewer.status_code, status.HTTP_403_FORBIDDEN)


class CRUDTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'password123', role='admin')
        self.developer_user = User.objects.create_user('developer', 'dev@test.com', 'password123', role='developer')
        self.viewer_user = User.objects.create_user('viewer', 'viewer@test.com', 'password123', role='viewer')
        self.organization = Organization.objects.create(name='Test Org', invite_code='1234')
        self.cluster = Cluster.objects.create(name='Test Cluster', organization=self.organization,
                                              total_ram=1024, total_cpu=4, total_gpu=1,
                                              available_ram=1024, available_cpu=4, available_gpu=1)
        self.deployment = Deployment.objects.create(cluster=self.cluster, docker_image_path='path/to/image',
                                                    required_ram=512, required_cpu=2, required_gpu=1,
                                                    priority=10, status='Queued',user_id=self.admin_user.id)
        self.client_admin = APIClient()
        self.client_developer = APIClient()
        self.client_viewer = APIClient()
        self.client_admin.force_authenticate(user=self.admin_user)
        self.client_developer.force_authenticate(user=self.developer_user)
        self.client_viewer.force_authenticate(user=self.viewer_user)

    def test_create_cluster(self):
        url = reverse('cluster-list')
        data = {
            'name': 'New Cluster',
            'organization': self.organization.id,
            'total_ram': 2048,
            'total_cpu': 8,
            'total_gpu': 2,
            'available_ram': 2048,
            'available_cpu': 8,
            'available_gpu': 2
        }

        # Developer should be able to create cluster
        response_developer = self.client_developer.post(url, data, format='json')
        self.assertEqual(response_developer.status_code, status.HTTP_201_CREATED)

        # Viewer should not be able to create cluster
        response_viewer = self.client_viewer.post(url, data, format='json')
        self.assertEqual(response_viewer.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_deployment(self):
        url = reverse('deployment-list')
        data = {
            'cluster': self.cluster.id,
            'docker_image_path': 'new/path/to/image',
            'required_ram': 512,
            'required_cpu': 2,
            'required_gpu': 1,
            'priority': 5,
        }

        # Developer should be able to create deployment
        response_developer = self.client_developer.post(url, data, format='json')
        self.assertEqual(response_developer.status_code, status.HTTP_201_CREATED)

        # Viewer should not be able to create deployment
        response_viewer = self.client_viewer.post(url, data, format='json')
        self.assertEqual(response_viewer.status_code, status.HTTP_403_FORBIDDEN)


class UserTests(TestCase):
    def test_create_user(self):
        user = get_user_model()
        user = user.objects.create_user(username='testuser', password='password123', role='admin')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))


class OrganizationTests(TestCase):
    def test_create_organization(self):
        organization = Organization.objects.create(name='Test Org', invite_code='1234')
        self.assertEqual(organization.name, 'Test Org')
        self.assertEqual(organization.invite_code, '1234')
