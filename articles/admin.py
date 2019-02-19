from django.contrib import admin

# Register your models here.
from articles.models import Article


class ArticleADmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'body']


admin.site.register(Article, ArticleADmin)
