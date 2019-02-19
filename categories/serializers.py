from rest_framework import serializers

from categories.models import Category


class CategoryOnlyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # or just fields = '__all__'
        fields = (
            'id'
            'name',
            'slug',
            'description',
        )
