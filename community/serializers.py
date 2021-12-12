from rest_framework import serializers
from .models import Article, Article_Comment
from django.conf import settings

class ArticleListSerializer(serializers.ModelSerializer):
    
    username = serializers.SerializerMethodField(method_name='get_username')
    def get_username(self, obj):
        return obj.user.username
        
    class Meta:
        model = Article
        fields = '__all__'

class ArticleCommentSerializer(serializers.ModelSerializer):
    def get_username(self, obj):
        return obj.user.username
        
    username = serializers.SerializerMethodField(method_name='get_username')
    liked_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    comment_liked_users_count = serializers.IntegerField(source='liked_users.count', read_only=True)
    
    def create(self, validated_data):
        comment = Article_Comment.objects.create(**validated_data)

        return comment

    class Meta:
        model = Article_Comment
        fields = (
            'id', 'content', 'created_at', 'updated_at', 'user',
            'username', 'liked_users', 'comment_liked_users_count'
        )

class ArticleSerializer(serializers.ModelSerializer):
    article_comment_set = ArticleCommentSerializer(many=True, read_only=True)
    article_comment_count = serializers.IntegerField(source='article_comment_set.count', read_only=True)
        
    # Article 안에는 많은 fields가 있고 create시에는 다르게 작동해야한다.
    def create(self, validated_data):
        article = Article.objects.create(**validated_data)

        return article

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('liked_users',)