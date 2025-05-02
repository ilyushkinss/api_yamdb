from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_slug, validate_username, validate_year

MAX_SCORE = 10
MIN_SCORE = 1


class User(AbstractUser):
    """
    Переопределенная модель пользователей.

    Описывает пользователя и его обязательные поля для регистрации.
    Обязательные поля: почта и ник.
    Необязательные поля:имя, фамилия, биография, роль
    """

    username = models.CharField(
        'Никнейм',
        max_length=150,
        unique=True,
        validators=[validate_username]
    )
    email = models.CharField('Почта', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Роль', max_length=20, default='user')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Category(models.Model):
    """
    Модель категорий.

    Описывает категории(типы) произведений.
    Все поля обязательные.
    """

    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField(
        'Слаг категории',
        max_length=50,
        unique=True,
        validators=[validate_slug],
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Модель жанров.

    Описывает категории жанров.
    Все поля обязательные.
    """

    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField(
        'Слаг жанра',
        max_length=50,
        unique=True,
        validators=[validate_slug],
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Модель произведений.

    Описывает произведение.
    Обязатеьные поля: name, year, category, genre
    Необязательные поля: description
    """

    name = models.CharField('Название произведения', max_length=256)
    year = models.SmallIntegerField(
        'Год выпуска произведения',
        validators=[validate_year]
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='title',
        verbose_name='Категория',
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='title',
        verbose_name='Жанр',
    )
    description = models.TextField(
        'Описание произведения',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель отзывов.

    Описывает отзыв на произведение, в отзыве можно оставить текст и оценку.
    Все поля обязательные.
    """

    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Автор',

    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Произведение',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        auto_now=False,
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)
        ],
        error_messages='Оценка может быть от 1 до 10.',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique_review'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """
    Модель комментариев.

    Описывает комментарии для отзывов, можно оставить только текст.
    Все поля обязательные.
    """

    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Автор',

    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Произведение',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Отзыв',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        auto_now=False,
    )
