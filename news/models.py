from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse



class Author(models.Model):
    # связь «один к одному» с встроенной моделью пользователей User.
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    # рейтинг пользователя.
    ratingAuthor = models.IntegerField(default=0)

    # Подсчитываем рейтинг:
    def update_rating(self):
        #  суммарный рейтинг статей автора умножается на 3.
        postRat = self.post_set.all().aggregate(sum=Sum('rating'))['sum']
        #  суммарный рейтинг всех комментариев автора.
        userRat = self.authorUser.comment_set.all().aggregate(sum=Sum('rating'))['sum']
        #  суммарный рейтинг всех комментариев к статьям автора.
        commentRat = Comment.objects.filter(commentPost__author=self).aggregate(sum=Sum('rating'))['sum']
        self.ratingAuthor = postRat * 3 + userRat + commentRat
        self.save()

        def __str__(self):
            return self.authorUser.username

class Category(models.Model):
    categoryName = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, blank=True)


    def __str__(self):
        return self.categoryName


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPE = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость')
    ]

    # связь «один ко многим» с моделью Author.
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    # поле с выбором — «статья» или «новость».
    categoryType = models.CharField(max_length=2, choices=POST_TYPE, default=ARTICLE, verbose_name='Тип')
    # автоматически добавляемая дата и время создания.
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    # связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory).
    postCategory = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категория')
    # заголовок статьи/новости.
    title = models.CharField(max_length=124, verbose_name='Заголовок')
    # текст статьи/новости.
    text = models.TextField(verbose_name='Текст')
    # рейтинг статьи/новости.
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    # Методы like() и dislike().
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    # Метод preview().
    def preview(self):
        return self.text[:124] + '...'

    def __str__(self):
        return f'id-{self.pk}: {self.title}'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    # Методы like() и dislike().
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()




