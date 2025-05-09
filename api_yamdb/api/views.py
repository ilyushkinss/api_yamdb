from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, views, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin, ListModelMixin
)
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (
    IsModerOrAdminOrAuthorOrReadOnly,
    IsSuperUserOrAdminOnly,
    IsSuperUserOrAdminOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, MeSerializer,
    SignUpSerializers, TitleSerializer, TitleReadSerializer, TokenSerializer,
    ReviewSerializer, UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdminOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def me_patch(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ('me', 'me_patch'):
            return MeSerializer
        return UserSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели отзывов.
    """
    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsModerOrAdminOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели произведений.
    """
    queryset = (
        Title.objects.annotate(rating=Avg('reviews__score')).order_by('rating')
    )
    permission_classes = (IsSuperUserOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели комментариев.
    """
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsModerOrAdminOrAuthorOrReadOnly,)

    def get_review(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        return review

    def get_queryset(self):
        return self.get_review().comment.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return IsModerOrAdminOrAuthorOrReadOnly(),
        return permissions.IsAuthenticatedOrReadOnly(),


class CategoryGenreBaseViewSet(viewsets.GenericViewSet,
                      ListModelMixin,
                      DestroyModelMixin,
                      CreateModelMixin):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdminOrReadOnly,)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для модели категорий.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBaseViewSet):
    """
    Вьюсет для модели жанров.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination


class SignUpView(views.APIView):
    """
    Вьюсет для регистрация пользователя.
    """
    def post(self, request):
        serializer = SignUpSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """
    Вьюсет для получение токена.
    """
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access_token = {'token': str(AccessToken.for_user(user))}
        return Response(access_token, status=status.HTTP_200_OK)
