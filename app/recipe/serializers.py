"""
Recipe serializers
"""

from core.models import Recipe
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """recipe model serializer."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'description', 'link'
            ]
        read_only_fields = ['id']
