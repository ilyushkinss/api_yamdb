import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Review, Comment, User, Category, Title, Genre

LENGTH_CONFIRMATION_CODE = 6


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    pub_date = serializers.DateTimeField(
        read_only=True,
    )
    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
    )

    class Meta:
        model = Review
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    pub_date = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadSerializer(serializers.ModelSerializer):
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
    Регистрация пользователя.
    """

    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=150,
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
        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if ((user_by_email and user_by_username)
                and user_by_email == user_by_username):
            return data

        if user_by_username:
            raise serializers.ValidationError(
                f'Username {username} уже занято'
            )

        if user_by_email:
            raise serializers.ValidationError(
                f'Пользователь с такой почтой уже зарагистрирован.'
            )
        return data


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=LENGTH_CONFIRMATION_CODE,
        required=True,
    )

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return data
