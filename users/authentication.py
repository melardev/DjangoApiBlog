import jwt
from django.conf import settings
from rest_framework import authentication, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from users.models import AppUser


class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


# This is my custom Authentication Backend, it is not needed, because
# the above authentication makes the app functional already
# See the implementation of the backend provided by https://github.com/davesque/django-rest-framework-simplejwt
# https://github.com/GetBlimp/django-rest-framework-jwt
class JwtAuthenticationBacked(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_' + 'AUTHORIZATION')
        if auth_header is None:
            # if authentication is not attempted return None
            return None
        parts = auth_header.split(' ')
        if len(parts) != 2:
            return None

        if parts[0].lower() not in ('bearer', 'token'):
            return None
        token = parts[1]
        try:
            payload = jwt.decode(token, settings.JWT['SECRET'])
            user = AppUser.objects.get(pk=payload['id'])
            return (user, token)
        except Exception as e:
            if e is AppUser.DoesNotExists:
                # If authentication is attempted but fails raise a AuthenticationFailed
                raise AuthenticationFailed(detail='The user does not exist')

        return None


class IsAuthorPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user is not None and request.user.groups.filter(name='authors').count() > 0:
            return True
        return False


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS or
                request.user and
                (request.user.is_staff or request.user.groups.filter(name='authors').count() > 0)
        )


class IsAdminOrOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return request.user and (request.user.is_staff or obj.user == request.user)
