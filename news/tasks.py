from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category
import datetime

@shared_task
def send_email_task(pk):
    post = Post.objects.get(pk=pk)
    categories = post.post_category.all()
    title = post.post_title
    subscribes_emails = []
    for categoty in categories:
        subscribes_users = categoty.subscribers.all()
        for sub_user in subscribes_users:
            subscribes_emails.append(sub_user.email)
    html_content = render_to_string('post_created_email.html',
                                    {
                                        'text': f'{post.post_title}',
                                        'link': f'{settings.SITE_URL}/news/{pk}',
                                            }
                                    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribes_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

@shared_task
def weelky_send_email_task():
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(creation_date__gte=last_week)
    categories = set(posts.values_list('category__categoryName', flat=True))
    subscribers = set(Category.objects.filter(categoryName__in=categories).values_list('subscribers__email', flat=True))
    html_content = render_to_string(
        'daily_post.html',
        {
            'link': settings.SITE_URL,
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject='Статьи за неделю',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers,
    )