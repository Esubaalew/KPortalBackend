from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GPTRequestSerializer, GPTResponseSerializer
from .utils import GPTClient


class GPTView(APIView):
    def post(self, request):
        serializer = GPTRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prompt = serializer.validated_data['prompt']
        gpt_client = GPTClient()
        response = gpt_client.generate(prompt)

        response_serializer = GPTResponseSerializer({'response': response})

        return Response(response_serializer.data)
