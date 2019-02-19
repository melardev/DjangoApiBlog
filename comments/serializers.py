from rest_framework import serializers

from comments.models import Comment
from users.serializers import UserUsernameAndIdSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserUsernameAndIdSerializer(required=False)
    article_id = serializers.SerializerMethodField()
    is_reply = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'is_reply', 'article_id', 'content', 'created_at', 'updated_at']

    def create(self, validated_data):
        article = self.context['article']
        user = self.context['user']
        return Comment.objects.create(user=user, article=article, **validated_data)

    def get_article_id(self, instance):
        return instance.article.id

    def get_is_reply(self, instance):
        return instance.parent_comment is not None
