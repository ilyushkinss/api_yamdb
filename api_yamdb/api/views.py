from django.shortcuts import render
from rest_framework import viewsets, mixins, permissions, filters
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import User, Review, Title, Comment, Genre, Category
from .serializers import (ReviewSerializer, TitleSerializer, UserSerializer,
                          CommentSerializer, GenreSerializer,
                          CategorySerializer)
from .permissions import IsAuthorOrReadOnly, IsSuperUserOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by("name")
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


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsSuperUserOrAdmin,)
