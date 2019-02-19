from django.conf.urls import url

from categories.views import CategoryList

urlpatterns = [
    url(r'^categories/$', CategoryList.as_view())
]
