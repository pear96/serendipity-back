from rest_framework import fields, serializers
from .models import Actor, Cast, Movie, Genre, Genre_Score, Review, Review_Comment

class ActorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'

class GenreScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre_Score
        fields = ('genre', 'score', )

class MovieListSerializer(serializers.ModelSerializer):

    genre_set = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ('pk', 'title', 'poster_path', 'genre_set',)

class ActorSerializer(serializers.ModelSerializer):

    # movies = MovieListSerializer(many=True, read_only=True)

    class Meta:
        model = Actor
        fields = '__all__'

class CastSerializer(serializers.ModelSerializer):

    actor = ActorSerializer()

    class Meta:
        model = Cast
        fields = '__all__'

class ReviewListSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField(method_name='get_username')
    def get_username(self, obj):
        return obj.user.username
        
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('movie', )

class MovieSerializer(serializers.ModelSerializer):

    actors = ActorListSerializer(many=True, read_only=True)
    review_set = ReviewListSerializer(many=True, read_only=True)
    genre_set = GenreSerializer(many=True, read_only=True)

    actor_pks = serializers.ListField(write_only=True)

    def create(self, validated_data):
        actor_pks = validated_data.pop('actor_pks')
        movie = Movie.objects.create(**validated_data)

        for actor_pk in actor_pks:
            movie.actors.add(actor_pk)
            
        return movie

    class Meta:
        model = Movie
        fields = '__all__'

class ReviewCommentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review_Comment
        fields = '__all__'

class ReviewCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    liked_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    liked_users_count = serializers.IntegerField(source='liked_users.count', read_only=True)

    class Meta:
        model = Review_Comment
        fields = '__all__'
        read_only_fields = ('review', )

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    review_comment_set = ReviewCommentSerializer(many=True, read_only=True)

    def get_username(self, obj):
        return obj.user.username

    liked_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    liked_users_count = serializers.IntegerField(source='liked_users.count', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('movie', )