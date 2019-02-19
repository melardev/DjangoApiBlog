import math

from django.db import models


# Create your models here.


class PageMetaModel(models.Model):
    next_page_url = models.CharField(max_length=100)
    hast_page_url = models.CharField(max_length=100)

    class Meta:
        managed = False  # do not create a table for this model


class PageMetaModel2():
    def __init__(self, request, paginator):
        if not hasattr(paginator, 'count'):
            return
        self.data = {}
        self.data['total_items_count'] = paginator.count
        self.data['offset'] = paginator.offset
        self.data['requested_page_size'] = paginator.limit
        self.data['current_page_number'] = int(request.query_params.get('page', 1))

        self.data['prev_page_number'] = 1
        self.data['total_pages_count'] = math.ceil(self.data['total_items_count'] / self.data['requested_page_size'])

        if self.data['current_page_number'] < self.data['total_pages_count']:
            self.data['has_next_page'] = True
            self.data['next_page_number'] = self.data['current_page_number'] + 1
        else:
            self.data['has_next_page'] = False
            self.data['next_page_number'] = 1

        if self.data['current_page_number'] > 1:
            self.data['prev_page_number'] = self.data['current_page_number'] - 1
        else:
            self.data['has_prev_page'] = False
            self.data['prev_page_number'] = 1

        self.data['next_page_url'] = '%s?page=%d&page_size=%d' % (
            request.path, self.data['next_page_number'], self.data['requested_page_size'])
        self.data['prev_page_url'] = '%s?page=%d&page_size=%d' % (
            request.path, self.data['prev_page_number'], self.data['requested_page_size'])

        # self.paginator.default_limit

        # self.paginator.offset_query_param
        # self.paginator.limit_query_param

    def get_data(self):
        return self.data


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ['-created_at', '-updated_at']
