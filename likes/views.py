# Create your views here.

from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article


class ArticlesLikeView(APIView):
    permission_classes = (IsAuthenticated,)

    # renderer_classes = (LikeRenderer,)

    def post(self, request, article_slug=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        success = False
        if user.is_not_liking(article):
            success = user.like(article)
        if success:
            full_messages = ['Liked Successfully']
        else:
            full_messages = ['You already liked it']

        if success:
            return Response({'success': success, 'full_messages': full_messages}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': success, 'full_messages': full_messages}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, article_slug=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')
        success = False
        if user.is_liking(article):
            success = user.unlike(article)

        if success:
            return Response({'success': success, 'full_messages': ['You unliked the article successfully']},
                            status=status.HTTP_200_OK)
        else:
            full_messages = ['You are not liking this article']
            return Response(data={'success': success, 'full_messages': full_messages},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class ArticlesLikedBy(generics.ListAPIView):

    def get_queryset(self):
        # Review this
        Article.objects.filter(liked_by__username=self.request.get('username'))
