from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """
    Generic error response serializer
    """
    error_code = serializers.CharField()
    message = serializers.CharField()
    status = serializers.CharField()