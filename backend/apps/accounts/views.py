"""Authentication and user profile views."""
from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from apps.accounts.serializers import UserSerializer, RegisterSerializer, LoginSerializer
from apps.audit.services import record_audit_event

class RegisterView(views.APIView):
    """User registration with progressive profile disclosure."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        record_audit_event(
            action='USER_REGISTER',
            resource_type='User',
            resource_id=str(user.id),
            actor=user,
            organization=user.organization,
            request=request
        )

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(views.APIView):
    """User login returning profile and authentication token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        record_audit_event(
            action='USER_LOGIN',
            resource_type='User',
            resource_id=str(user.id),
            actor=user,
            organization=user.organization,
            request=request
        )

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_200_OK)

class CurrentUserView(views.APIView):
    """Returns profile and workspace metadata of the currently authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
