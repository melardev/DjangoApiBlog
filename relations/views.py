# Create your views here.
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.renderers import ArticleListJsonRenderer
from articles.serializers import ArticleSummarySerializer
from relations.models import UserSubscriptions
from relations.renderers import UserRelationsRenderer
from relations.serializers import UserSubscriptionsSerializer
from shared.models import PageMetaModel2
from users.models import AppUser
from users.serializers import UserUsernameAndIdSerializer


class SubscriptionsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, username=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            following = AppUser.objects.get(username=username)
        except AppUser.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        success = False
        if user.is_not_following(following):
            success = user.follow(following)
        if success:
            full_messages = ['Subscribed Successfully']
        else:
            full_messages = ['You already subscribed to this user']

        if success:
            return Response({'success': success, 'full_messages': full_messages}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': success, 'full_messages': full_messages}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, username=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            following = AppUser.objects.get(username=username)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')
        success = False
        if user.is_following(following):
            success = user.unfollow(following)

        if success:
            return Response({'success': success, 'full_messages': ['You unsubcribed from this user successfully']},
                            status=status.HTTP_200_OK)
        else:
            full_messages = ['You are not subscribed to this user']
            return Response(data={'success': success, 'full_messages': full_messages},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class UserSubscriptionsListView(ListAPIView):
    queryset = AppUser.objects.all()
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserRelationsRenderer,)
    serializer_class = UserSubscriptionsSerializer

    def get_queryset(self):
        qs = super(UserSubscriptionsListView, self).get_queryset()
        return qs

    def get_limit(self, request):
        page_size = 5
        if hasattr(request, 'page_size'):
            page_size = getattr(request, 'page_size')
            if page_size < 0 or page_size > 20:
                page_size = 5
        self.paginator.default_limit = page_size  # monkey paginator patch ...
        return page_size

    def get_offset(self, request):
        page = 1
        if hasattr(request, 'page'):
            if page > 0:
                page = getattr(request, 'page')

        offset = (page - 1) * self.get_limit(request)
        return offset

    def get_serializer_context(self):
        context = super(UserSubscriptionsListView, self).get_serializer_context()
        context['user'] = self.request.user

    def get_renderer_context(self):
        renderer_context = super(UserSubscriptionsListView, self).get_renderer_context()

        if self.paginator is not None and hasattr(self.paginator, 'count'):
            renderer_context['page_meta'] = PageMetaModel2(self.request, self.paginator)

        return renderer_context

    def list(self, request, **kwargs):
        serializer_context = {'request': request}
        subscriptions = UserSubscriptions.objects.filter(
            Q(follower=request.user) | Q(following=request.user)).prefetch_related('follower') \
            .prefetch_related('following')
        page = self.paginate_queryset(subscriptions)
        # page = self.get_queryset()
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        # This returns a Response object, the data field contains the payload and will be passed to the Renderer
        # the .data['results'] will contain the list of articles
        # return self.get_paginated_response(serializer.data)

        following = []
        followers = []

        for subscription in subscriptions:
            if subscription.follower == request.user:
                following.append(subscription.following)
            elif subscription.following == request.user:
                following.append(subscription.follower)

        serializer_context['followers'] = followers
        serializer_context['following'] = following

        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        return self.get_paginated_response(serializer.data)

        for f in request.user.following.all():
            following.append({'id': f.id, 'username': f.username})

        for f in request.user.followers.all():
            followers.append({'id': f.id, 'username': f.username})

        following = UserUsernameAndIdSerializer(request.user.following, many=True)
        return Response({'followers': followers,
                         'following': following.data},
                        status=status.HTTP_200_OK)


class ArticlesLikeView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleListJsonRenderer,)
    serializer_class = ArticleSummarySerializer

    def post(self, request, article_slug=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        if user.is_not_liking(article):
            user.like(article)
        serializer = self.serializer_class(article, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, article_slug=None):
        user = self.request.user
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug was not found.')

        if user.isliking():
            user.unlike(article)

        serializer = self.serializer_class(article, context=serializer_context)

        return Response(serializer.data, status=status.HTTP_200_OK)
