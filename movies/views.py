from django.http.response import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import Actor, Cast, Genre_Score, Movie, Genre, Review, Review_Comment
from django.contrib.auth import get_user_model
from .serializers import (
    ActorListSerializer,
    ActorSerializer,
    CastSerializer,
    GenreScoreSerializer,
    MovieListSerializer,
    MovieSerializer,
    GenreSerializer,
    ReviewCommentSerializer,
    ReviewListSerializer,
    ReviewSerializer,
)
import sqlite3
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds


# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def actor_list_by_movie(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        actors = Cast.objects.filter(movie=movie)
        serializer = CastSerializer(actors, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_t20(request):
    if request.method == 'GET':
        movies = get_list_or_404(Movie.objects.order_by('-popularity')[:20])
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def movie_list_r6(request):
    if request.method == 'GET':
        default_list = Movie.objects.order_by('?')[:6]
        serializer = MovieSerializer(default_list, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def genre_list(request):
    if request.method == 'GET':
        genres = get_list_or_404(Genre)
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_by_title(request, query):
    movies = get_list_or_404(Movie.objects.filter(title__icontains=query))
    paginator = Paginator(movies, 10)

    num_pages = paginator.num_pages

    page_number = request.GET.get('page')

    if page_number is None or int(page_number) <= num_pages:
        page_obj = paginator.get_page(page_number)

        serializer = MovieListSerializer(page_obj, many=True)
        return Response(serializer.data)
    else:
        return Response({'message':'end of page'})

@api_view(['GET'])
@permission_classes([AllowAny])
def search_by_genre(request, query):
    genre = get_object_or_404(Genre, name=query)
    movies = genre.movie_by_genre.all()
    paginator = Paginator(movies, 10)

    num_pages = paginator.num_pages

    page_number = request.GET.get('page')

    if page_number is None or int(page_number) <= num_pages:
        page_obj = paginator.get_page(page_number)

        serializer = MovieListSerializer(page_obj, many=True)
        return Response(serializer.data)
    else:
        return Response({'message':'end of page'})

@api_view(['GET'])
def personal_curation(request):
    user_count = get_user_model().objects.count()
    myK = user_count//2
    default_list = Movie.objects.order_by('?')[:20]
    serializer = MovieSerializer(default_list, many=True)
    if myK < 2:
        context = {
            'message': 'failed',
            'default_list': serializer.data,
        }
    else:
        con = sqlite3.connect('db.sqlite3')
        df_ratings = pd.read_sql('SELECT * FROM movies_movie_liked_users', con)
        df_ratings.drop('id', axis=1, inplace=True)
        df_ratings['rating'] = 1
        df_genres = pd.read_sql('SELECT * FROM movies_movie_genres', con)
        df_genres = df_genres.groupby(['movie_id'])['genre_id'].apply(lambda x: ','.join(x.astype(str))).reset_index()
        df_movies = pd.read_sql('SELECT * FROM movies_movie', con)
        df_movies.drop(['release_date', 'popularity', 'overview', 'adult'], axis=1, inplace=True)
        df_movies = df_movies.rename(columns={'id': 'movie_id'})
        df_user_movie_ratings = df_ratings.pivot(index = 'user_id', columns='movie_id', values='rating').fillna(0)
        id2rownum = {}
        rownum = 0
        for row in df_user_movie_ratings.index:
            id2rownum[row] = rownum
            rownum += 1
        matrix = df_user_movie_ratings.to_numpy()
        user_ratings_mean = np.mean(matrix, axis=1)
        matrix_user_mean = matrix - user_ratings_mean.reshape(-1, 1)
        pd.DataFrame(matrix_user_mean, columns = df_user_movie_ratings.columns).head()
        U, sigma, Vt = svds(matrix_user_mean, k = min(myK, min(matrix_user_mean.shape) - 1))
        sigma = np.diag(sigma)
        svd_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
        df_svd_preds = pd.DataFrame(svd_user_predicted_ratings, columns=df_user_movie_ratings.columns)

        def recommend_movies(df_svd_preds, user_id, ori_movies_df, ori_ratings_df, num_recommendations=6):
            user_row_number = id2rownum[user_id]
            sorted_user_predictions = df_svd_preds.iloc[user_row_number].sort_values(ascending=False)
            user_data = ori_ratings_df[ori_ratings_df.user_id == user_id]
            user_history = user_data.merge(ori_movies_df, on='movie_id').sort_values(['rating'], ascending=False)
            recommendations = ori_movies_df[~ori_movies_df['movie_id'].isin(user_history['movie_id'])]
            recommendations = recommendations.merge(pd.DataFrame(sorted_user_predictions).reset_index(), on='movie_id')
            recommendations = recommendations.rename(columns = {user_row_number: 'Predictions'}).sort_values('Predictions', ascending=False)
        
            return recommendations

        if request.user.pk in id2rownum:
            predictions = recommend_movies(df_svd_preds, request.user.pk, df_movies, df_ratings)
            pred_w_g = pd.merge(predictions, df_genres, on='movie_id')
            pred_w_g = pred_w_g.rename(columns={'movie_id': 'pk'})
            pred_w_g = pred_w_g.to_json(orient='records', force_ascii=False)
            context = {
                'message': 'success',
                'user_pk': request.user.pk,
                'predictions': pred_w_g,
                'default_list': serializer.data
            }
        else:
            context = {
                'message': 'nolikes',
                'user_pk': request.user.pk,
                'default_list': serializer.data
            }
    return Response(context)

@api_view(['GET'])
def get_genre_score(request):
    scores = get_list_or_404(Genre_Score, user_id = request.user.pk)
    serializer = GenreScoreSerializer(scores, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = MovieSerializer(movie, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        movie.delete()
        message = {
            '[SYSTEM]' : f'Movie No.{movie_pk} Deleted.'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def movie_like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.liked_users.filter(pk=user.pk).exists():
        movie.liked_users.remove(user)
        liked = False
    else:
        movie.liked_users.add(user)
        liked = True
    context = {
        'liked': liked,
        'likers': movie.liked_users.count(),
    }
    return JsonResponse(context)

@api_view(['POST'])
def genre_score(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.liked_users.filter(pk=user.pk).exists():
        for genre in movie.genres.all():
            gpk = genre.pk
            score_qs = Genre_Score.objects.filter(genre_id=gpk).filter(user_id=user.pk)
            score_before = score_qs.values()[0]['score']
            score_qs.update(score = score_before - 1)
    else:
        for genre in movie.genres.all():
            gpk = genre.pk
            if Genre_Score.objects.filter(genre_id=gpk).filter(user_id=user.pk).exists():
                score_qs = Genre_Score.objects.filter(genre_id=gpk).filter(user_id=user.pk)
                score_before = score_qs.values()[0]['score']
                score_qs.update(score = score_before + 1)
            else:
                Genre_Score.objects.create(genre_id=gpk, user_id=user.pk, score=1)
    message = {
        '[SYSTEM]' : 'Personal Genre Score was updated.'
    }
    return Response(message)

@api_view(['POST'])
def movie_wish(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.wished_users.filter(pk=user.pk).exists():
        movie.wished_users.remove(user)
        wished = False
    else:
        movie.wished_users.add(user)
        wished = True
    context = {
        'wished': wished,
        'wishes': movie.wished_users.count(),
    }
    return JsonResponse(context)

@api_view(['GET'])
def movie_review_all(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        reviews = get_list_or_404(Review, movie=movie)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def movie_review_CR(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'GET':
        reviews = get_list_or_404(Review, movie=movie)
        paginator = Paginator(reviews, 3)

        num_pages = paginator.num_pages

        page_number = request.GET.get('page')

        if page_number is None or int(page_number) <= num_pages:
            page_obj = paginator.get_page(page_number)

            serializer = ReviewSerializer(page_obj, many=True)
            return Response(serializer.data)
        else:
            return Response({'message':'end of page'})
    if request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
def movie_review_UD(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'PUT':
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': '리뷰 수정'})
    if request.method == 'DELETE':
        review.delete()
        return Response({ 'id': review_pk }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def movie_review_like(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    user = request.user
    if review.liked_users.filter(pk=user.pk).exists():
        review.liked_users.remove(user)
        liked = False
    else:
        review.liked_users.add(user)
        liked = True
    context = {
        'liked': liked,
        'likers': review.liked_users.count(),
    }
    return JsonResponse(context)

@api_view(['GET'])
def review_comment_all(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'GET':
        comments = get_list_or_404(Review_Comment, review=review)
        serializer = ReviewCommentSerializer(comments, many=True)
        return Response(serializer.data)

@api_view(['GET', 'POST'])
def review_comment_CR(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'GET':
        comments = get_list_or_404(Review_Comment, review=review)
        paginator = Paginator(comments, 3)

        num_pages = paginator.num_pages

        page_number = request.GET.get('page')

        if page_number is None or int(page_number) <= num_pages:
            page_obj = paginator.get_page(page_number)

            serializer = ReviewCommentSerializer(page_obj, many=True)

            hasNext = page_obj.has_next()
            context = {
                'hasNext' : hasNext,
                'serializer' : serializer.data,
            }
            return Response(context)
        else:
            return Response({'message':'end of page'}, status=status.HTTP_400_BAD_REQUEST)
        # serializer = ReviewCommentSerializer(comments, many=True)
        # return Response(serializer.data)
    if request.method == 'POST':
        serializer = ReviewCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print('serializer valid')
            serializer.save(review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT', 'DELETE'])
def review_comment_UD(request, review_pk, comment_pk):
    comment = get_object_or_404(Review_Comment, pk=comment_pk)
    if request.method == 'PUT':
        serializer = ReviewCommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': '리뷰 댓글 수정'})
    if request.method == 'DELETE':
        comment.delete()
        return Response({ 'id': comment_pk }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def review_comment_like(request, review_pk, comment_pk):
    comment = get_object_or_404(Review_Comment, pk=comment_pk)
    user = request.user
    if comment.liked_users.filter(pk=user.pk).exists():
        comment.liked_users.remove(user)
        liked = False
    else:
        comment.liked_users.add(user)
        liked = True
    context = {
        'liked': liked,
        'likers': comment.liked_users.count(),
    }
    return JsonResponse(context)