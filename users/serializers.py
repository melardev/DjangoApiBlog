from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import AppUser


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=AppUser.objects.all())])
    email = serializers.CharField(validators=[UniqueValidator(queryset=AppUser.objects.all())])
    password = serializers.CharField(write_only=True)  # do not return password in response
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = AppUser.objects.create_user(**validated_data)
        return user

    class Meta:
        model = AppUser
        fields = ['username', 'email', 'password', 'created_at']


class LoginSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField() -> defaults to get_token
    token = serializers.SerializerMethodField()  # 'get_token')

    class Meta:
        model = AppUser
        fields = ['username', 'email', 'token']

    # yet another way of doing the same, extra jwt field
    @classmethod
    def get_jwt(self, user):
        return user.generate_jwt_token()

    def get_token(self, obj):
        return obj.generate_jwt_token()

    # TODO: Remove this to make it more unique, perform validation on Controller
    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None or password is None:
            raise serializers.ValidationError('You are required to pass email and password to log in')

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'No user with these credentials'
            )
        return {
            'email': user.email,
            'username': user.username,
            'token': user.generate_jwt_token()
        }


class StringListField(serializers.ListField):
    elem = serializers.CharField


class LoginSerializer2(serializers.Serializer):
    #    email = serializers.CharField(max_length=255)
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True, allow_null=False,
                                     allow_blank=True)  # blank, null for testing only
    email = serializers.CharField(max_length=255,
                                  read_only=True)  # we send the email in the response, but user has to use username to login
    # this is why read_only=True meaning the user does not have to send the email
    token = serializers.CharField(max_length=255, read_only=True)
    roles = StringListField(read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        username = data.get('username', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if username is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=username, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        roles = []
        if user.is_staff:
            roles.append('ROLE_ADMIN')

        if user.groups.filter(name='authors').count() > 0:
            roles.append('ROLE_AUTHOR')
        if len(roles) == 0:
            roles.append('ROLE_USER')

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'token': user.generate_jwt_token(),
            'roles': roles
        }


class UserProfileSerializer(serializers.ModelSerializer):
    # articles_liked = serializers.SerializerMethodField()
    # following = serializers.SerializerMethodField()
    # followers = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ['username', 'email', 'image_url', 'likes', ]  # 'following', 'followers']
        read_only_fields = ('username',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_image_url(self, obj):
        if obj.image:
            return obj.image
        return 'default.png'

    def get_following(self, obj):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated():
            return False

        follower = request.user.profile
        followee = obj

        return follower.is_following(followee)

    def get_followers(self, obj):
        return 'not implemented'


class UserUsernameAndIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'username']
