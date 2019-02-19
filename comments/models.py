from django.db import models
# Create your models here.
from django.db.models import Q

from shared.models import TimestampedModel


class CommentManager(models.Manager):

    def get_all_replies(self):
        return Comment.objects.exclude(Q(parent_comment__isnull=True))


class Comment(TimestampedModel):
    content = models.TextField()

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True)
    # parent_comment = models.ForeignKey('comments.Comment', on_delete=models.CASCADE)

    user = models.ForeignKey(
        'users.AppUser', related_name='comments', on_delete=models.CASCADE
    )

    objects = CommentManager()

    def is_reply(self):
        return self.parent_comment is not None

    def get_root(self):
        if not self.is_reply():
            return self
        ptr = self
        prev = None
        while True:
            prev = ptr
            ptr = ptr.parent_comment
            if ptr is None:
                return prev
