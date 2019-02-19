from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.renderers import JsonLoginRenderer
from users.serializers import RegistrationSerializer, LoginSerializer2


class Register2(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class Register(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        # user = request.data.values()
        user = request.data
        # user = user.intersect('email', 'username', 'password', 'password_confirmation')
        serialized = self.serializer_class(data=user)
        serialized.is_valid(raise_exception=True)
        serialized.save()

        return Response(data=serialized.data
                        , status=status.HTTP_201_CREATED)


# Note there are many ways to send the token
'''
1. The obvious way is to hook into renderer's render method and add it
2. This one and other approaches are given https://stackoverflow.com/questions/26648680/django-rest-framework-add-fields-to-json
'''


class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer2
    renderer_classes = (JsonLoginRenderer,)  # append the token

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        # Make Model validations
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data)


'''
class UserRetrieveUpdate(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserProfileRenderer,)
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = request.data.values().intersect(self.serializer.fields())
        data2 = {
            'username': data.get('username', request.user.username),
            'password': data.get('email', request.user.email),
            'image_url': data.get('image_url', request.user.image_url)
        }

        serialized = self.serializer_class(request.user, data=data2, partial=True)
        serialized.save()
        return Response(serialized.data)
    
'''
