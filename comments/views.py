from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from articles.models import Article
from comments.models import Comment
from comments.renderers import CommentJsonRenderer
from comments.serializers import CommentSerializer
from shared.models import PageMetaModel2
from users.authentication import IsAdminOrOwnerOrReadOnly


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.select_related(
        'user', 'article'  # 'article', 'article__user', not useful
    )

    renderer_classes = (CommentJsonRenderer,)
    serializer_class = CommentSerializer

    def get_limit(self, request):
        page_size = 5
        if hasattr(request, 'page_size'):
            page_size = getattr(request, 'page_size')
            if page_size < 0 or page_size > 20:
                page_size = 5
        return page_size

    def get_offset(self, request):
        page = 1
        if hasattr(request, 'page'):
            if page > 0:
                page = getattr(request, 'page')
        return (page - 1) * self.get_limit(request)

    def filter_queryset(self, queryset):
        # The built-in list function calls `filter_queryset`. Since we only
        # want comments for a specific article, this is a good place to do
        # that filtering.
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}

        filtered_queryset = queryset.filter(**filters)[self.get_offset(self.request):self.get_limit(self.request)]
        return filtered_queryset

    def create(self, request, *args, **kwargs):  # def create(self, request, article_slug=None):
        data = request.data
        context = {'user': request.user}

        try:
            context['article'] = Article.objects.get(slug=kwargs['article_slug'])
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_renderer_context(self):
        renderer_context = super(CommentsListCreateAPIView, self).get_renderer_context()

        if self.paginator is not None and hasattr(self.paginator, 'count'):
            renderer_context['page_meta'] = PageMetaModel2(self.request, self.paginator)

        return renderer_context


class CommentsDestroyAPIView(generics.RetrieveDestroyAPIView):
    lookup_url_kwarg = 'comment_pk'
    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    renderer_classes = (CommentJsonRenderer,)

    def get_object(self):
        obj = Comment.objects.get(pk=self.kwargs['comment_pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, article_slug=None, comment_pk=None):
        try:
            comment = Comment.objects.get(pk=comment_pk)
            self.check_object_permissions(self.request, comment)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')

        comment.delete()

        return Response({'full_messages': ['Comment deleted successfully']}, status=status.HTTP_200_OK)
