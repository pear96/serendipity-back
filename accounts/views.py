from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, UserDetailSerializer, UserMovieSerializer, UserReviewSerializer
from rest_framework.permissions import AllowAny

# POST 요청만 받아들인다 = User DB 수정
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
	# 1-1. Client에서 온 데이터를 받아서
    username = request.data.get('username')
    password = request.data.get('password')
    password_confirmation = request.data.get('passwordConfirmation')

	# 1-2. 오류 처리하기
    if password != password_confirmation:
        return Response({'error': ['비밀번호가 일치하지 않습니다.']}, status=status.HTTP_400_BAD_REQUEST)
    
    if not username or not password or not password_confirmation:
        return Response({'error': ['빈 칸이 있어서는 안됩니다.']}, status=status.HTTP_400_BAD_REQUEST)
		
    
    # 2. UserSerializer를 통해 데이터 직렬화
    serializer = UserSerializer(data=request.data)
    
	# 3. validation 작업 진행 -> password도 같이 직렬화 진행
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        #4. 비밀번호 해싱(암호화) = set_password() 후 
        user.set_password(request.data.get('password'))
        user.save()
        # write_only : password는 직렬화 과정에는 포함 되지만 → 표현(response)할 때는 나타나지 않는다.
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def user_manage(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    if request.method == 'GET':
        serializer = UserDetailSerializer(person)

        person_followers, person_followings = [], []
        # 팔로워 이름 찾기
        for follower in person.followers.all():
            follower_info ={
                'username': follower.username,
                'profile_path': follower.profile_path
            }
            person_followers.append(follower_info)
        # 팔로잉 이름 찾기
        for following in person.followings.all():
            following_info ={
                'username': following.username,
                'profile_path': following.profile_path
            }
            person_followings.append(following_info)

        context = {
            'user': serializer.data,
            'followers_info' : person_followers,
            'followings_info' : person_followings
        }
        return Response(context)
    elif request.method == 'PUT':
        password = request.data.get('password')
        password_confirmation = request.data.get('passwordConfirmation')
		
        # 1-2. 패스워드 일치 여부 체크
        if password != password_confirmation:
            return Response({'error': ['비밀번호가 일치하지 않습니다.']}, status=status.HTTP_400_BAD_REQUEST)
    
        if not password or not password_confirmation:
            return Response({'error': ['빈 칸이 있어서는 안됩니다.']}, status=status.HTTP_400_BAD_REQUEST)
		
        # 2. UserSerializer를 통해 데이터 직렬화
        serializer = UserSerializer(person, data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user.set_password(request.data.get('newPassword'))
            #4. 비밀번호 해싱(암호화) = set_password() 후 
            user.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def follow(request, username):
    me = request.user
    you = get_object_or_404(get_user_model(), username=username)
    if me != you:
        if you.followers.filter(pk=me.pk).exists():
            you.followers.remove(me)
            isFollowed = False
        else:
            you.followers.add(me)
            isFollowed = True
        you_followers, you_followings = [], []
        # 팔로워 이름 찾기
        for follower in you.followers.all():
            follower_info ={
                'username': follower.username,
                'profile_path': follower.profile_path
            }
            you_followers.append(follower_info)
        # 팔로잉 이름 찾기
        for following in you.followings.all():
            following_info ={
                'username': following.username,
                'profile_path': following.profile_path
            }
            you_followings.append(following_info)
        context = {
            'is_followed': isFollowed,
            'followers_count': you.followers.count(),
            'followings_count': you.followings.count(),
            'followers_info' : you_followers,
            'followings_info' : you_followings
        }
        return Response(context)
    return Response({'message': '스스로를 팔로우 할 수 없습니다.'})

@api_view(['PUT'])
def set_profile_img(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    # 프로필 이미지 갱신한거 할당하고 저장
    person.profile_path = request.data.get('newProfileImg')
    person.save()
    return Response({ 'new_profile_path' : person.profile_path })

@api_view(['GET'])
def get_user_movies(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    serializer = UserMovieSerializer(person)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_reviews(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    serializer = UserReviewSerializer(person)
    return Response(serializer.data)