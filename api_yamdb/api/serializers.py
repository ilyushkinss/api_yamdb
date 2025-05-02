from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Review, Comment, User, Category, Title, Genre


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
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(
        many=False,

    )
    genre = GenreSerializer(
        many=False,
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z',
        max_length=32,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)
        model = User
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username', },
        }
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]

    # def validate_username(self, value):
    #     if value.lower() == 'me':
    #         raise serializers.ValidationError(
    #             'Запрещено использовать юзернейм "me"!'
    #         )
    #     return value
