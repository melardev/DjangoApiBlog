from django.conf.urls import url

from users.views import Register, LoginView

app_name = 'users'
urlpatterns = [
    url(r'^users/login$', LoginView.as_view()),
    url(r'^users/register$', Register.as_view()),
    url(r'^users$', Register.as_view()),

    # url(r'^users/profile', Profile.as_view())
]
