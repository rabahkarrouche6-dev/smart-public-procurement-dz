"""Views and Serializers for Subscriptions and Entitlements."""
from rest_framework import serializers, viewsets, permissions, views
from rest_framework.response import Response
from apps.subscriptions.models import Plan, Subscription

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'code', 'name', 'description', 'is_active']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_code = serializers.CharField(source='plan.code', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    class Meta:
        model = Subscription
        fields = ['id', 'organization', 'plan', 'plan_code', 'plan_name', 'status', 'starts_at', 'expires_at']

class CurrentSubscriptionView(views.APIView):
    """Returns current active subscription tier for user's organization."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        org = getattr(user, 'organization', None)
        if not org:
            return Response({'plan': 'NO_ORGANIZATION', 'ai_enabled': False})

        sub = getattr(org, 'subscription', None)
        if sub:
            return Response(SubscriptionSerializer(sub).data)

        # Default fallback: MVP_FREE tier
        return Response({
            'plan_code': 'MVP_FREE',
            'plan_name': 'النسخة التجريبية المجانية الشاملة',
            'status': 'ACTIVE',
            'ai_enabled': True
        })
