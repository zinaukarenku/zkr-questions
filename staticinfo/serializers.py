from rest_framework import serializers

from .models import Page

class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        exclude = ('content', 'hidden', 'id')


class PageSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source="as_html")

    class Meta:
        model = Page
        exclude = ('hidden', 'id')
