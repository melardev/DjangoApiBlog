from django.conf.urls import url

from likes.views import ArticlesLikeView

app_name = 'likes'
urlpatterns = [
    url(r'^articles/(?P<article_slug>[-\w]+)/likes/?$',
        ArticlesLikeView.as_view()),
]
