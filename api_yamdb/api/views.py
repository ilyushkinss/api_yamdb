from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, filters, views, status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)

from reviews.models import User, Review, Title, Comment, Genre, Category
from .serializers import (
    ReviewSerializer, TitleSerializer, UserSerializer, CommentSerializer,
    GenreSerializer, CategorySerializer, SignUpSerializers, TokenSerializer
)
from .utils import generate_and_save_confirmation_codes
from .permissions import IsAuthorOrReadOnly, IsSuperUserOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by("title")
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    # pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

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


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdmin,)


class GenreViewSet(viewsets.GenericViewSet,
                   ListModelMixin,
                   DestroyModelMixin,
                   CreateModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdmin,)
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

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access_token = {'token': AccessToken.for_user(user)}
        return Response(access_token, status=status.HTTP_200_OK)
