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


class RecipeDetailSerializer(RecipeSerializer):
    """recipe detail model serializer."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
