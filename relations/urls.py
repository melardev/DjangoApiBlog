from django.conf.urls import url

from relations.views import UserSubscriptionsListView, SubscriptionsView

app_name = 'subscriptions'
urlpatterns = [
    url(r'^users/subscriptions$', UserSubscriptionsListView.as_view(), name='user_subscriptions'),
    url(r'^users/subscriptions/(?P<username>[-\w]+)/followers/?$', SubscriptionsView.as_view(), name='follow_unfollow'),
]
