from django.conf.urls import url

from comments.views import CommentsListCreateAPIView, CommentsDestroyAPIView

app_name = 'comments'

urlpatterns = [
    url(r'^articles/(?P<article_slug>[-\w]+)/comments/?$',
        CommentsListCreateAPIView.as_view()),

    url(r'^articles/(?P<article_slug>[-\w]+)/comments/(?P<comment_pk>[\d]+)/?$',
        CommentsDestroyAPIView.as_view()),

    url(r'^comments/(?P<comment_pk>[\d]+)/?$',
        CommentsDestroyAPIView.as_view()),

url(r'^comments/(?P<comment_pk>[\d]+)/replies/?$',
        CommentsDestroyAPIView.as_view()),
]
