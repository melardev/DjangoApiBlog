
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from tags.models import Tag
from tags.serializers import TagOnlyNameSerializer


class TagListCreate(ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagOnlyNameSerializer


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagOnlyNameSerializer

    def list(self, request, *args, **kwargs):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagOnlyNameSerializer

    def list(self, request, *args, **kwargs):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class TagRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagOnlyNameSerializer
    lookup_field = 'slug'
