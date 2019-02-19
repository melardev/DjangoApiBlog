import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from categories.models import Category
from shared.models import TimestampedModel
from tags.models import Tag


class ArticleManager():

    def get_all(self):
        return self.queryset.filter(
            Q(publish_on__lte=timezone.now()) | Q(publish_on__isnull=True))


class Article(TimestampedModel):
    title = models.CharField(db_index=True, max_length=255)
    slug = models.SlugField(db_index=True, max_length=255, unique=True,
                            help_text='What is used to lookup the table basically')
    description = models.TextField(null=True, blank=True)
    body = models.TextField()
    # liked_by = models.ManyToManyField(AppUser, through='Like', related_name='articles_liked')

    # Every article must have an author. This will answer questions like "Who
    # gets credit for writing this article?" and "Who can edit this article?".
    # Unlike the `User` <-> `Profile` relationship, this is a simple foreign
    # key (or one-to-many) relationship. In this case, one `Profile` can have
    # many `Article`s.
    user = models.ForeignKey(
        'users.AppUser', on_delete=models.CASCADE, related_name='articles'
    )

    tags = models.ManyToManyField(
        Tag, related_name='articles'
    )

    categories = models.ManyToManyField(
        Category, related_name='articles'
    )

    # likes = models.ManyTo('Like')
    publish_on = models.DateTimeField(blank=True, null=True)

    # views = models.IntegerField(default=0)

    def save(self, slug="", *args, **kwargs):
        if not self.publish_on:
            self.publish_on = datetime.datetime.now()
            # self.slug = unique_slug(self.title)

        self.slug = slugify(self.title)
        return super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return ('article_details', None, {'slug': self.slug})

    class Meta:
        ordering = ('-publish_on',)


class Like(TimestampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('users.AppUser', on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return '%s %s liked %s' % (self.user.first_name, self.user.last_name, self.article.slug)
