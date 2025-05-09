from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api import consts
from reviews.models import Category, Comment, Genre, Review, Title, User
from .utils import generate_and_save_confirmation_codes


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    score = serializers.IntegerField(
        min_value=consts.MIN_SCORE,
        max_value=consts.MAX_SCORE,
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        author = self.context['request'].user
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=author, title_id=title_id).exists():
            raise serializers.ValidationError(
                'Ваш отзыв уже был добавлен. '
                'На одно произведние, можно добавить только один отзыв.'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категорий.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор жанров
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор комментариев.
    """
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи произведений.
    """
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True,
        allow_empty=False,
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения произведений.
    """
    category = CategorySerializer(
        read_only=True,
    )
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class MeSerializer(UserSerializer):
    """
    Сериализтор для обновления данных пользователя.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class SignUpSerializers(serializers.Serializer):
    """
    Сериализатор для регистрации пользователя.
    """

    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=consts.NAME_USER_LENGTH,
        required=True,
    )
    email = serializers.EmailField(max_length=254, required=True,)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"')
        return username

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        try:
            user_by_username = User.objects.get(username=username)
        except User.DoesNotExist:
            user_by_username = None
        try:
            user_by_email = User.objects.get(email=email)
        except User.DoesNotExist:
            user_by_email = None
        if ((user_by_email and user_by_username)
                and user_by_email == user_by_username):
            return data

        if user_by_username:
            raise serializers.ValidationError(
                f'Username {username} уже занято'
            )

        if user_by_email:
            raise serializers.ValidationError(
                f'Пользователь с почтой {email} уже зарагистрирован.'
            )
        return data

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        confirmation_code = generate_and_save_confirmation_codes(user)
        send_mail(
            subject='Ваш код подтверждения',
            message=(
                'Ваш код подтверждения для получения токена:'
                f'{confirmation_code}'
            ),
            from_email='api_yamdb@email.com',
            recipient_list=[user.email],
        )
        return user


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор получения токена для пользователя.
    """
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=consts.NAME_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=consts.LENGTH_CONFIRMATION_CODE,
        required=True,
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        confirmation_code = data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения.')
        return data
