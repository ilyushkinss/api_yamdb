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
from .utils import generate_and_save_confirmation_codes


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
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return IsModerOrAdminOrAuthorOrReadOnly(),
        return permissions.IsAuthenticatedOrReadOnly(),


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.annotate(rating=Avg('reviews__score')).order_by('rating')
    )
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
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'))
        return review

    def get_queryset(self):
        review = self.get_review()
        return review.comment.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_permissions(self):
        if self.request.method in ('PATCH', 'DELETE'):
            return IsModerOrAdminOrAuthorOrReadOnly(),
        return permissions.IsAuthenticatedOrReadOnly(),


class CategoryViewSet(viewsets.GenericViewSet,
                      ListModelMixin,
                      DestroyModelMixin,
                      CreateModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdminOrReadOnly,)
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
