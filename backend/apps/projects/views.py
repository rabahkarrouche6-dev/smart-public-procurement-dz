"""Views and Serializers for Projects."""
from rest_framework import serializers, viewsets, permissions
from apps.projects.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'organization', 'code', 'name', 'description', 'program', 'operation', 'estimated_cost', 'created_at']

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return Project.objects.none()
        if user.is_central_admin or user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
