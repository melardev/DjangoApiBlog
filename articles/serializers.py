from django.utils.text import slugify
from rest_framework import serializers

from articles.models import Article, Like
from categories.models import Category
from comments.serializers import CommentSerializer
from shared.serializers import PageMetaSerializer
from tags.models import Tag
from users.serializers import UserUsernameAndIdSerializer


class TagRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Tag.objects.all()

    def to_internal_value(self, tg):
        # TODO: for some reason name__iexact does not work
        t, has_beed_created = Tag.objects.get_or_create(
            slug=slugify(tg['name']),
            # name__iexact=tg['name'],
            defaults={'name': tg['name'], 'description': tg.get('description', '')})

        return t

    def to_representation(self, tag_obj):
        return tag_obj.name


class CategoryRelatedField(serializers.RelatedField):
    def get_queryset(self):
        return Category.objects.all()

    def to_internal_value(self, category):
        # TODO: for some reason name__iexact does not work
        category, has_beed_created = Category.objects.get_or_create(slug=slugify(category['name']),
                                                                    # name__iexact=category['name'],
                                                                    defaults=
                                                                    {
                                                                        'name': category['name'],
                                                                        'description': category.get('description', '')
                                                                    })

        return category

    def to_representation(self, category_obj):
        return category_obj.name


class ArticleSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    user = UserUsernameAndIdSerializer(read_only=True)
    description = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)
    liked = serializers.SerializerMethodField()
    likesCount = serializers.SerializerMethodField(
        method_name='get_likes_count'
    )

    # tagList = TagRelatedField(many=True, required=False, source='tags')
    tags = TagRelatedField(many=True, required=False)
    categories = CategoryRelatedField(many=True, required=False)
    # Django REST Framework makes it possible to create a read-only field that
    # gets it's value by calling a function. In this case, the client expects
    # `created_at` to be called `createdAt` and `updated_at` to be `updatedAt`.
    # `serializers.SerializerMethodField` is a good way to avoid having the
    # requirements of the client leak into our API.
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'slug',
            'description',
            'comment_count',
            'user',
            'liked',
            'likesCount',
            'tags',
            'categories',
            'createdAt',
            'updatedAt',
        )

    def create(self, validated_data):
        user = self.context.get('user', None)

        tags = validated_data.pop('tags', [])
        categories = validated_data.pop('categories', [])

        article = Article.objects.create(user=user, **validated_data)

        for tag in tags:
            article.tags.add(tag)

        for category in categories:
            article.categories.add(category)

        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        categories = validated_data.pop('categories', [])

        instance.title = validated_data.get('title')
        instance.description = validated_data.get('description')
        instance.body = validated_data.get('body')
        instance.tags.clear()
        instance.categories.clear()
        for tag in tags:
            instance.tags.add(tag)

        for category in categories:
            instance.categories.add(category)

        return instance

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_comment_count(self, instance):
        return getattr(instance, 'comments__count', None)

    def get_liked(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated:
            return False

        return request.user.is_liking(instance)

    def get_likes_count(self, instance):
        return instance.likes.count()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()


class ArticleSummarySerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    user = UserUsernameAndIdSerializer(read_only=True)

    def get_user(self, article):
        return article.user.username

    def get_likes_count(self, article):
        return Like.objects.filter(article=article).count()

    def save(self, **kwargs):
        return super(ArticleSummarySerializer, self).save(**kwargs)

    class Meta:
        model = Article
        fields = ['title', 'description', 'slug', 'likes_count', 'user']


# Not working as expected I am just playing with it, this is mapped to /articles2, use /articles instead, that one works
class ArticleListSummarySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    page_meta = PageMetaSerializer(read_only=True)
    articles = serializers.SerializerMethodField(method_name='serialize_articles')

    def serialize_articles(self, instance):
        return ArticleSummarySerializer(instance).data


class ArticleDetailsSerializer(serializers.ModelSerializer):
    user = UserUsernameAndIdSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    slug = serializers.SlugField(required=False)
    tags = serializers.SlugRelatedField(many=True, required=False, read_only=True, slug_field='name')
    categories = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    def update(self, instance, validated_data):
        article = self.save_or_update(instance, validated_data)
        article.save()
        return article

    def create(self, validated_data):
        user = self.context.get('user', None)
        article = Article.objects.create(user=user, **validated_data)
        # article = Article(user=user, **validated_data)
        self.save_or_update(article, validated_data)

    def save_or_update(self, article, validated_data):

        article.title = validated_data['title']
        article.description = validated_data['description']
        article.body = validated_data['body']

        tags = self.context['request'].data['tags']
        categories = self.context['request'].data['categories']

        input_tags = []
        for tag in tags:
            t, has_beed_created = Tag.objects.get_or_create(
                slug=slugify(tag['name']),
                # name__iexact=tag['name'],
                defaults={'name': tag['name'], 'description': tag.get('description', '')})
            input_tags.append(t)
        article.tags.set(input_tags)
        article.categories.clear()
        for category in categories:
            c, has_beed_created = Category.objects.get_or_create(
                slug=slugify(category['name']),
                defaults={
                    'name': category['name'],
                    'description': getattr(category, 'description', '')
                })
            article.categories.add(c)

        return article

    class Meta:
        model = Article
        fields = ['id', 'title', 'description', 'slug', 'body', 'user', 'comments', 'tags', 'categories']
