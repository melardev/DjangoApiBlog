from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from articles.models import Like


class AppUser(AbstractUser):
    # user = req.user user.following user.followers
    # symmetrical False: if I follow you it does not mean You are following me
    # an example of symmetrical True would be friends, if I am your friend, you are mine as well or sisters/brothers
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False)

    # articles_liked = models.ManyToManyField('articles.Article', through='articles.Like', related_name='liked_by')

    def __str__(self):
        return self.username

    def follow(self, user):
        if user not in self.following.all():
            self.following.add(user)
            return True
        return False

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
            return True
        return False

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()
        # return user in self.following

    def is_not_following(self, user):
        return not self.following.filter(pk=user.pk).exists()

    def is_followed_by(self, user):
        return self.followers.filter(pk=user.pk).exists()

    def like(self, article):
        # self.likes.filter(article=article.id).exists()
        # self.likes.filter(article__in=[article]).exists()
        if not self.likes.filter(article=article, user=self).exists():
            self.likes.add(Like.objects.create(article=article, user=self))
            return True
        return False

    def unlike(self, article):
        if self.likes.filter(article=article, user=self).exists():
            self.likes.filter(article=article, user=self).delete()
            return True
        return False

    def is_liking(self, article):
        return self.likes.filter(article__id=article.pk).exists()

    def is_not_liking(self, article):
        return not self.likes.filter(pk=article.pk).exists()

    def generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'username': self.username,
            'roles': [role.name for role in self.roles]
        }, settings.JWT['SECRET'], algorithm='HS512')

        return token.decode('utf-8')
