from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from articles.views import ArticleList, ArticleCreate, ArticleDetails, ArticleViewSet, ArticlesByTag, ArticlesByCategory

router = DefaultRouter(trailing_slash=False)
router.register(r'', ArticleViewSet)

app_name = 'articles'
urlpatterns = [

    # url(r'^articles2$', include(router.urls)),
    url(r'^articles/', include(router.urls)),
    url(r'^articles2/?$', ArticleList.as_view(), name='article_list'),
    url(r'^articles/new$', ArticleCreate.as_view(), name='article_create'),
    url(r'^articles/(?P<slug>([a-z0-9-])+)$', ArticleDetails.as_view(), name='article_details'),
    url(r'^articles/by_id/(?P<pk>([a-z0-9-])+)$', ArticleDetails.as_view(), name='article_details_by_id'),
    url(r'^articles/by_tag/(?P<tag_name>([a-z0-9-])+)$', ArticlesByTag.as_view(), name='articles_by_tag'),
    url(r'^articles/by_category/(?P<category_name>([a-z0-9-])+)$', ArticlesByCategory.as_view(),
        name='articles_by_category'),

]
