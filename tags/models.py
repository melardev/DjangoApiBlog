from django.db import models, IntegrityError

# Create your models here.
from django.utils.text import slugify

from shared.models import TimestampedModel


class TagManager(models.Manager):

    def get_random_tag(self):
        return Tag.objects.order_by('?').first()

    def get(self, **kwargs):
        return super(TagManager, self).get(**kwargs)


'''
  def get_or_create(self, **kwargs):
        if 'name' in kwargs:
            name = kwargs.pop('name')
            return super(TagManager, self).get_or_create(name__iextact=name, **kwargs)
        else:
            return super(TagManager, self).get_or_create(**kwargs)
'''


class Tag(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)
    description = models.CharField(max_length=140, null=True)

    objects = TagManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
