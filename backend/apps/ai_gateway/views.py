"""Views and Serializers for AI Gateway."""
from rest_framework import serializers, views, permissions, status
from rest_framework.response import Response
from apps.ai_gateway.orchestrator import dispatch_ai_request

class AIQuerySerializer(serializers.Serializer):
    agent_type = serializers.CharField(default='PROCUREMENT_COPILOT')
    query = serializers.CharField()
    context_data = serializers.DictField(required=False, default=dict)

class AIQueryView(views.APIView):
    """Secure AI Gateway query endpoint."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AIQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent_type = serializer.validated_data['agent_type']
        query = serializer.validated_data['query']
        context_data = serializer.validated_data.get('context_data', {})

        result = dispatch_ai_request(
            user=request.user,
            agent_type=agent_type,
            query=query,
            context_data=context_data
        )

        return Response(result, status=status.HTTP_200_OK)
