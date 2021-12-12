from rest_framework import serializers
from django.contrib.auth import get_user_model
from movies.serializers import MovieListSerializer, ReviewListSerializer, ReviewCommentListSerializer
from community.serializers import ArticleListSerializer, ArticleCommentSerializer


class UserSerializer(serializers.ModelSerializer):
    # 응답에서 출력을 막아 비번 암호화
    password = serializers.CharField(write_only=True)


    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


class UserDetailSerializer(serializers.ModelSerializer):

    # 좋아하는, 보고싶은 영화
    # liked_movies = MovieListSerializer(many=True, read_only=True)
    # wishlisted_movies = MovieListSerializer(many=True, read_only=True)
    liked_movies_count = serializers.IntegerField(source='liked_movies.count', read_only=True)
    wished_movies_count = serializers.IntegerField(source='wishlisted_movies.count', read_only=True)

    # 작성한 리뷰, 리뷰 댓글
    # review_set = ReviewListSerializer(many=True, read_only=True)
    review_count = serializers.IntegerField(source='review_set.count', read_only=True)
    review_comment_set = ReviewCommentListSerializer(many=True, read_only=True)

    # 좋아하는 리뷰, 리뷰 댓글
    # liked_reviews = ReviewListSerializer(many=True, read_only=True)
    liked_reviews_count = serializers.IntegerField(source='liked_reviews.count', read_only=True)
    # liked_review_comments = ReviewCommentListSerializer(many=True, read_only=True)

    # 작성한 게시글, 게시글 댓글
    article_set = ArticleListSerializer(many=True, read_only=True)
    article_comment_set = ArticleCommentSerializer(many=True, read_only=True)

    # 좋아하는 게시글, 게시글 댓글
    liked_articles = ArticleListSerializer(many=True, read_only=True)
    # liked_article_comments = ArticleCommentSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'date_joined', 'profile_path',
            'followings', 'followers',
            'liked_movies_count', 'wished_movies_count',
            'review_count', 'review_comment_set',
            'liked_reviews_count',
            'article_set', 'article_comment_set',
            'liked_articles'
        )

class UserMovieSerializer(serializers.ModelSerializer):

    # 좋아하는, 보고싶은 영화
    liked_movies = MovieListSerializer(many=True, read_only=True)
    wishlisted_movies = MovieListSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'liked_movies', 'wishlisted_movies',
        )

class UserReviewSerializer(serializers.ModelSerializer):

    # 작성한 리뷰, 좋아하는 리뷰, 작성한 게시글
    review_set = ReviewListSerializer(many=True, read_only=True)
    liked_reviews = ReviewListSerializer(many=True, read_only=True)
    article_set = ArticleListSerializer(many=True, read_only=True)
    liked_articles = ArticleListSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'review_set',
            'liked_reviews',
            'article_set',
            'liked_articles'
        )