from rest_framework import serializers

from users.serializers import UserUsernameAndIdSerializer


class UserSubscriptionsSerializer(serializers.Serializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    def get_followers(self, instance):
        return UserUsernameAndIdSerializer(self.context['followers'], many=True).data

    def get_following(self, instance):
        return UserUsernameAndIdSerializer(self.context['following'], many=True).data
