from rest_framework import serializers
from .models import User, Organization, Cluster, Deployment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'organization', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = '__all__'


class DeploymentSerializer(serializers.ModelSerializer):

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Deployment
        fields = '__all__'
