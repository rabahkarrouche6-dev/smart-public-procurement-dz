"""Serializers for accounts and authentication."""
from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import User
from apps.organizations.models import Organization

class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    org_type = serializers.CharField(source='organization.org_type', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone', 'role',
            'organization', 'organization_name', 'org_type',
            'is_active', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    org_name = serializers.CharField(write_only=True, required=False)
    org_type = serializers.ChoiceField(choices=Organization.OrgType.choices, write_only=True, required=False)
    nif = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'phone', 'role', 'org_name', 'org_type', 'nif']

    def create(self, validated_data):
        org_name = validated_data.pop('org_name', None)
        org_type = validated_data.pop('org_type', None)
        nif = validated_data.pop('nif', None)
        password = validated_data.pop('password')

        organization = None
        if org_name and org_type:
            organization = Organization.objects.create(
                name=org_name,
                org_type=org_type,
                nif=nif
            )

        user = User.objects.create_user(
            organization=organization,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
        if not user.is_active:
            raise serializers.ValidationError("هذا الحساب معطل حالياً.")
        data['user'] = user
        return data
