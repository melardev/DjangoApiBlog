from django.db import models
from rest_framework import serializers

from shared.models import PageMetaModel


class PageMetaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMetaModel
        fields = ['next_page_url']


class PageMetaSerializer(serializers.Serializer):
    next_page_url = serializers.SerializerMethodField()
    prev_page_url = serializers.SerializerMethodField()
    has_next_page_number = serializers.SerializerMethodField()
    has_prev_page_number = serializers.SerializerMethodField()

    def get_next_page_url(self, context):
        return self.context.get('next_page_url', '')

    def get_prev_page_url(self, s):
        return self.context.get('prev_page_url', '')

    def get_has_next_page_number(self, c):
        return self.context.get('prev_page_url', False)

    def get_has_prev_page_number(self, c):
        return self.context.get('prev_page_number', '')
