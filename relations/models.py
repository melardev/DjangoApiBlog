from django.db import models

# Create your models here.
from users.models import AppUser


class UserSubscriptions(models.Model):
    following = models.ForeignKey(to=AppUser, on_delete=models.CASCADE, db_column='to_appuser_id',
                                  related_name='following_relations')
    follower = models.ForeignKey(to=AppUser, on_delete=models.CASCADE, db_column='from_appuser_id')

    class Meta:
        db_table = 'users_appuser_following'
        managed = False
