from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.paginator import Paginator

from django.db.models import Count
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404

from .serializers import (
    ArticleListSerializer, 
    ArticleSerializer, 
    ArticleCommentSerializer)
from .models import Article, Article_Comment


@api_view(['GET'])
def index(request):
    articles = get_list_or_404(Article.objects.annotate(num_likes=Count('liked_users')).order_by('-num_likes'))
    paginator = Paginator(articles, 10)
    num_pages = paginator.num_pages
    page_number = request.GET.get('page')
    if page_number is None or int(page_number) <= num_pages:
        page_obj = paginator.get_page(page_number)
        serializer = ArticleListSerializer(page_obj, many=True)
        return Response(serializer.data)
    else:
        return Response({'message':'end of page'})
    

@api_view(['POST'])
def article_create(request):
    serializer = ArticleSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def article_RUD(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'GET':
        user = article.user
        username = get_user_model().objects.get(pk=user.pk).username
        serializer = ArticleSerializer(article)
        context = {
            'serializer': serializer.data,
            'username': username
        }
        return Response(context)
    elif request.method == 'PUT':
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'meesage': '게시글 수정 완료'})
    elif request.method == 'DELETE':
        article.delete()
        return Response({ 'id': article_pk }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def article_like(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    user = request.user
    if article.liked_users.filter(pk=user.pk).exists():
        article.liked_users.remove(user)
        liked = False
    else:
        article.liked_users.add(user)
        liked = True
    context = {
        'liked': liked,
        'liked_users_count': article.liked_users.count(),
    }
    return JsonResponse(context)

@api_view(['GET', 'POST'])
def comment_CR(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if request.method == 'POST':
        serializer = ArticleCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'GET':
        comments = get_list_or_404(Article_Comment, article=article)
        paginator = Paginator(comments, 5)
        num_pages = paginator.num_pages
        page_number = request.GET.get('page')
        if page_number is None or int(page_number) <= num_pages:
            page_obj = paginator.get_page(page_number)
            serializer = ArticleCommentSerializer(page_obj, many=True)
            return Response(serializer.data)
        else:
            return Response({'message':'end of page'})

@api_view(['PUT', 'DELETE'])
def comment_UD(request, article_pk, comment_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comment = get_object_or_404(Article_Comment, pk=comment_pk)
    if request.method == 'PUT':
        serializer = ArticleSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article=article)
            return Response({'meesage': '댓글 수정 완료'})
    elif request.method == 'DELETE':
        comment.delete()
        return Response({ 'id': comment_pk }, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def comment_ALL(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    comments = get_list_or_404(Article_Comment, article=article)
    serializer = ArticleCommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def comment_like(request, article_pk, comment_pk):
    # article = get_object_or_404(Article, pk=article_pk)
    comment = get_object_or_404(Article_Comment, pk=comment_pk)
    user = request.user
    if comment.liked_users.filter(pk=user.pk).exists():
        comment.liked_users.remove(user)
        liked = False
    else:
        comment.liked_users.add(user)
        liked = True
    context = {
        'likedComment': liked,
        'likedComment_users_count': comment.liked_users.count(),
    }
    return JsonResponse(context)