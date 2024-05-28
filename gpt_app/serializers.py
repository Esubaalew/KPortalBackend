from rest_framework import serializers


class GPTRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=2048)


class GPTResponseSerializer(serializers.Serializer):
    response = serializers.CharField()