from django.core.mail import send_mail
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, permissions, filters, views, status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)

from reviews.models import User, Review, Title, Comment, Genre, Category
from .serializers import (
    ReviewSerializer, TitleSerializer, UserSerializer, CommentSerializer,
    GenreSerializer, CategorySerializer, SignUpSerializers, TokenSerializer,
    MeSerializer, TitleReadSerializer
)
from .utils import generate_and_save_confirmation_codes
from .permissions import IsAuthorOrReadOnly, IsSuperUserOrAdmin, IsSuperUserOrAdminOrReadOnly, CategoryPermission
from .filters import TitleFilter


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user.username)
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsSuperUserOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly, IsSuperUserOrAdmin,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(viewsets.GenericViewSet,
                      ListModelMixin,
                      DestroyModelMixin,
                      CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (CategoryPermission,
    lookup_field = 'slug'


class GenreViewSet(viewsets.GenericViewSet,
                   ListModelMixin,
                   DestroyModelMixin,
                   CreateModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'


class SignUpView(views.APIView):
    """
    Регистрация пользователя.
    """
    def post(self, request):
        serializer = SignUpSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        user, created = User.objects.get_or_create(
            username=username, email=email,
        )
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
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """
    Получение токена.
    """
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access_token = {'token': str(AccessToken.for_user(user))}
        return Response(access_token, status=status.HTTP_200_OK)
