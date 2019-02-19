# Create your views here.
import datetime

from django.contrib.syndication.views import Feed
from django.db.models import Count
from faker.utils.text import slugify
from markdown import Markdown
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from articles.models import Article
from articles.renderers import ArticleListJsonRenderer, ArticleJSONRenderer
from articles.serializers import ArticleSummarySerializer, ArticleDetailsSerializer, ArticleSerializer, \
    ArticleListSummarySerializer
from categories.models import Category
from shared.models import PageMetaModel2
from tags.models import Tag
from users.authentication import IsAuthorOrAdminOrReadOnly
from users.models import AppUser


def get_all(request):
    Article.objects.all().order_by('-created_at')


class ArticleList(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleListSummarySerializer

    def get_queryset(self):
        qs = super(ArticleList, self).get_queryset()

        # Filter by tag
        tag = self.kwargs.get('tag')
        if tag:
            tag = Tag.objects.get(slug=tag)
            return qs.filter(tags=tag)

        # Filter by category
        category = self.kwargs.get('category')
        if category:
            category = Category.objects.get(slug=category)
            return qs.filter(category=category)

        return qs


class ArticlesByAuthor(ListAPIView):
    serializer_class = ArticleSummarySerializer

    def get_queryset(self):
        if self.request.path == 'by_author':
            Article.objects.filter(user__username=self.req.username)
        elif self.request.path == 'by_author_id':
            Article.objects.filter(user__id=self.req.id)


class ArticlesByTag(ListAPIView):
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('user')

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.annotate(Count('comments'))
        return queryset.filter(tags__slug=self.kwargs['tag_name'])

    def list(self, request, **kwargs):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())
        # page = self.get_queryset()
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        # This returns a Response object, the data field contains the payload and will be passed to the Renderer
        # the .data['results'] will contain the list of articles
        serializer_context['page'] = 2
        return self.get_paginated_response(serializer.data)

    def get_renderer_context(self):
        renderer_context = super(ArticlesByTag, self).get_renderer_context()

        if self.paginator is not None and hasattr(self.paginator, 'count'):
            renderer_context['page_meta'] = PageMetaModel2(self.request, self.paginator)

        return renderer_context


class ArticlesByCategory(ListAPIView):
    serializer_class = ArticleSerializer
    renderer_classes = (ArticleJSONRenderer,)
    queryset = Article.objects.select_related('user')

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.annotate(Count('comments'))
        return queryset.filter(categories__slug=self.kwargs['category_name'])

    def list(self, request, **kwargs):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())
        # page = self.get_queryset()
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        # This returns a Response object, the data field contains the payload and will be passed to the Renderer
        # the .data['results'] will contain the list of articles
        serializer_context['page'] = 2
        return self.get_paginated_response(serializer.data)

    def get_renderer_context(self):
        renderer_context = super(ArticlesByCategory, self).get_renderer_context()

        if self.paginator is not None and hasattr(self.paginator, 'count'):
            renderer_context['page_meta'] = PageMetaModel2(self.request, self.paginator)

        return renderer_context


class ArticleViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = Article.objects.select_related('user')
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.annotate(Count('comments'))
        return queryset

    def filter_queryset(self, queryset):
        return super(ArticleViewSet, self).filter_queryset(queryset)

    def get_limit(self, request):
        page_size = 5
        if hasattr(request, 'page_size'):
            page_size = getattr(request, 'page_size')
            if page_size < 0 or page_size > 20:
                page_size = 5
        self.paginator.default_limit = page_size
        return page_size

    def get_offset(self, request):
        page = 1
        if hasattr(request, 'page'):
            if page > 0:
                page = getattr(request, 'page')

        offset = (page - 1) * self.get_limit(request)
        return offset

    def create(self, request, **kwargs):
        serializer_context = {
            'user': request.user,
            'request': request
        }

        serializer_data = request.data

        serializer = self.serializer_class(
            data=serializer_data, context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_renderer_context(self):
        renderer_context = super(ArticleViewSet, self).get_renderer_context()

        if self.paginator is not None and hasattr(self.paginator, 'count'):
            renderer_context['page_meta'] = PageMetaModel2(self.request, self.paginator)

        return renderer_context

    def list(self, request, **kwargs):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())
        # page = self.get_queryset()
        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        # This returns a Response object, the data field contains the payload and will be passed to the Renderer
        # the .data['results'] will contain the list of articles
        serializer_context['page'] = 2
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, **kwargs):
        serializer_context = {'request': request}

        try:
            article = self.queryset.get(slug=kwargs['slug'])
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(
            article,
            context=serializer_context
        )
        serializer = ArticleDetailsSerializer(article, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        serializer_context = {'request': request}

        try:
            article = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer_data = request.data
        '''
        serializer = self.serializer_class(
            article,
            context=serializer_context,
            data=serializer_data,
            partial=True
        )
        '''
        serializer = ArticleDetailsSerializer(article, context=serializer_context, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes((IsAuthenticated,))
class ArticleCreate(CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailsSerializer

    def perform_create(self, serializer):
        serializer.context['user'] = self.request.user
        article = serializer.save()
        article.user = self.request.user
        if not self.request.user.is_authenticated:
            article.user = AppUser.objects.first()

        categories = self.request.get('categories', [])
        tags = self.request.get('tags', [])

        for category in categories:
            if hasattr(category, 'name'):
                article.categories.add(Category.objects.get_or_create(  # name=category.name,
                    slug=slugify(category.name),
                    defaults={'description',
                              getattr(category,
                                      'description',
                                      '')}))
        for tag in tags:
            if hasattr(tag, 'name'):
                article.tags.add(
                    Tag.objects.get_or_create(  # name=tag.name,
                        slug=slugify(tag.name),
                        defaults={'name': tag.name, 'description': getattr(tag, 'description', '')}))

        article.save()


class ArticleDetails3(generics.RetrieveAPIView):
    serializer_class = ArticleDetailsSerializer
    lookup_field = 'slug'
    queryset = Article.objects.all()
    # kwargs['slug']


class ArticleDetailsWrite(generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)  # Allow read
    lookup_field = 'slug'

    def get_queryset(self):
        if self.kwargs.get('pk', None) is not None:
            return Article.objects.filter(pk=self.kwargs['pk'])
        else:
            return Article.objects.filter(slug=self.kwargs['slug'])

    def get_object(self):
        if self.kwargs.get('pk', None) is not None:
            return Article.objects.get(pk=self.kwargs['pk'])
        else:
            return Article.objects.get(slug=self.kwargs['slug'])

    def perform_update(self, serializer):
        instance = serializer.save()
        tags = self.request.data.pop('tags', [])
        categories = self.request.data.pop('categories', [])

        instance.title = self.request.data.get('title')
        instance.description = self.request.data.get('description')
        instance.body = self.request.data.get('body')
        instance.tags.clear()
        instance.categories.clear()
        for tag in tags:
            instance.tags.add(tag)

        for category in categories:
            instance.categories.add(category)

        instance.save()
        return instance

    def destroy(self, request, *args, **kwargs):
        return super(ArticleDetailsWrite, self).destroy(request, *args, **kwargs)


# TODO: Set permissions
class ArticleDetails(generics.RetrieveAPIView):
    '''
    Either use get_object alone (by slug and id), or
    lookup_field + get_queryset returning queryset super() -> will only retrieve article if slug in kwargs but not if id
    or
    get_queryset as implemented below without lookup_field (by slug and id)
    '''
    queryset = Article.objects.all()
    serializer_class = ArticleDetailsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)  # Allow read
    lookup_field = 'slug'

    def get_queryset(self):
        if self.kwargs.get('pk', None) is not None:
            return Article.objects.filter(pk=self.kwargs['pk'])
        else:
            return Article.objects.filter(slug=self.kwargs['slug'])

    def get_object(self):
        if self.kwargs.get('pk', None) is not None:
            return Article.objects.get(pk=self.kwargs['pk'])
        else:
            return Article.objects.get(slug=self.kwargs['slug'])
