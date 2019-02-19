import datetime
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_api.settings')
django.setup()
from django.contrib.contenttypes.models import ContentType

import faker
from django.contrib.auth.models import User, Permission, Group

from articles.models import Article, Like
from categories.models import Category
from comments.models import Comment
from tags.models import Tag
from users.models import AppUser

faker = faker.Faker()


def seed_articles():
    articles_count = Article.objects.count()
    articles_to_seed = 23
    sys.stdout.write('[+] Seeding %d articles\n' % (articles_to_seed - articles_count))
    for i in range(articles_count, articles_to_seed):
        title = faker.sentence()
        description = '\n'.join(faker.sentences(2))
        body = faker.text()
        user = AppUser.objects.order_by('?').first()
        tag = Tag.objects.get_random_tag()
        category = Category.objects.get_random_category()
        start_date = datetime.date(year=2017, month=1, day=1)
        random_date = faker.date_between(start_date=start_date, end_date='+4y')
        publish_on = random_date
        a = Article.objects.create(title=title, body=body, description=description, user=user,
                                   publish_on=publish_on)
        a.tags.add(tag)
        a.categories.add(category)


def seed_admin():
    admin = AppUser.objects.filter(is_superuser=True).first()
    if admin is None:
        AppUser.objects.create_superuser('admin', 'admin@blogapi.com', 'password', first_name='adminFN',
                                         last_name='adminLN')


def seed_authors():
    content_type = ContentType.objects.get(app_label='articles', model='article')
    create_article_permission, created = Permission.objects.get_or_create(codename='can_create_articles',
                                                                 defaults={'name': 'Can create Articles',
                                                                           'content_type': content_type}, )
    update_article_permission, created = Permission.objects.get_or_create(codename='can_update_articles',
                                                                 defaults={'name': 'Can update Articles',
                                                                           'content_type': content_type}, )
    delete_article_permission, created = Permission.objects.get_or_create(codename='can_delete_articles',
                                                                 defaults={'name': 'Can delete Articles',
                                                                           'content_type': content_type}, )

    authors_group, created = Group.objects.get_or_create(name='authors')
    authors_group.permissions.add(create_article_permission)
    authors_group.permissions.add(update_article_permission)
    authors_group.permissions.add(delete_article_permission)

    authors_count = AppUser.objects.filter(groups__name__iexact='authors').count()
    authors_to_seed = 5
    sys.stdout.write('[+] Seeding %d authors\n' % (authors_to_seed - authors_count))
    for i in range(authors_count, authors_to_seed):
        username = faker.profile(fields='username')['username']
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = faker.email()
        password = 'password'
        # create_user instead of create, to hash
        author = AppUser.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                             password=password)
        author.groups.add(authors_group)


def seed_users():
    users_count = AppUser.objects.count()
    users_to_seed = 23
    sys.stdout.write('[+] Seeding %d users\n' % (users_to_seed - users_count))
    for i in range(users_count, users_to_seed):
        username = faker.profile(fields='username')['username']
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = faker.email()
        password = 'password'
        # create_user instead of create, to hash
        AppUser.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                    password=password)


def seed_tags():
    sys.stdout.write('[+] Seeding tags\n')
    Tag.objects.get_or_create(name='spring', defaults={'description': 'spring mvc tutorials'})
    Tag.objects.get_or_create(name='rails', defaults={'description': 'rails tutorials'})
    Tag.objects.get_or_create(name='.net core', defaults={'description': '.net core tutorials'})


def seed_categories():
    sys.stdout.write('[+] Seeding categories\n')
    Category.objects.get_or_create(name='java', defaults={'description': 'java tutorials'})
    Category.objects.get_or_create(name='python', defaults={'description': 'python tutorials'})
    Category.objects.get_or_create(name='ruby', defaults={'description': 'ruby tutorials'})


def seed_comments():
    comments_count = Comment.objects.count()
    comments_to_seed = 31
    sys.stdout.write('[+] Seeding %d comments\n' % (comments_to_seed - comments_count))
    for i in range(comments_count, comments_to_seed):
        if Comment.objects.count() > 1 and faker.boolean():
            Comment.objects.create(article=Article.objects.order_by('?').first(),
                                   user=AppUser.objects.order_by('?').first(),
                                   content=faker.sentence())


def seed_replies():
    replies_count = Comment.objects.exclude(parent_comment__isnull=True).count()
    replies_to_seed = 33
    sys.stdout.write('[+] Seeding %d replies\n' % (replies_to_seed - replies_count))
    for i in range(replies_count, replies_to_seed):
        Comment.objects.create(article=Article.objects.order_by('?').first(),
                               user=AppUser.objects.order_by('?').first(),
                               content=faker.sentence(),
                               parent_comment=Comment.objects.order_by('?').first())


def seed_likes():
    likes_count = Like.objects.count()
    comments_to_seed = 31
    sys.stdout.write('[+] Seeding %d likes' % (comments_to_seed - likes_count))
    for i in range(likes_count, comments_to_seed):
        Like.objects.create(article=Article.objects.order_by('?').first(),
                            user=AppUser.objects.order_by('?').first())


def seed_relations():
    relationships_to_seed = 91
    relationships_count = AppUser.objects.values_list('followers', named=True).filter(followers__isnull=False).count()
    sys.stdout.write('[+] Seeding %d user relations\n' % (relationships_to_seed - relationships_count))
    for i in range(relationships_count, relationships_to_seed):
        follower = AppUser.objects.order_by('?').first()
        to_be_followed = AppUser.objects.exclude(following__in=follower.following.all()).first()
        if to_be_followed is None:
            raise AssertionError(
                'the to_be_followed is None, have you seeded users and make sure there are enough??')
        follower.follow(to_be_followed)

        # or
        # follower.following.add(to_be_followed)


if __name__ == '__main__':
    seed_categories()
    seed_tags()
    seed_admin()
    seed_authors()
    seed_users()
    seed_articles()
    seed_comments()
    seed_replies()
    seed_likes()
    seed_relations()

article = faker.text(max_nb_chars=20)
