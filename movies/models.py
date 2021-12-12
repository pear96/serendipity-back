from django.db import models
from django.conf import settings
from django.db.models.deletion import CASCADE

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Movie(models.Model):
    adult = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    release_date = models.DateField(null=True)
    popularity = models.FloatField()
    overview = models.TextField(null=True, blank=True)
    backdrop_path = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200)
    liked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_movies")
    wished_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="wishlisted_movies")
    genres = models.ManyToManyField(Genre, related_name='movie_by_genre')

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.CharField(max_length=100)
    profile_path = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Cast(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=CASCADE)
    cast_id = models.IntegerField()
    character = models.CharField(max_length=100)

    def __str__(self):
        return self.character

class Genre_Score(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="genre_score")
    score = models.IntegerField(default=0)


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    liked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_reviews")

    def __str__(self):
        return self.content
    

class Review_Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    liked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_review_comments")

    def __str__(self):
        return self.content