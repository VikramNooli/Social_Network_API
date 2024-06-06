# api/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer,FriendRequestSerializer
from rest_framework.pagination import PageNumberPagination
import datetime
from datetime import timedelta
from django.utils import timezone
from .models import FriendRequest

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if request.method == 'POST':
        email = request.data.get('email').lower()
        if User.objects.filter(email=email).exists():
            return Response({'error': 'This email address has already been used'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,'message': 'User with mail address %s created succefully'%user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    if request.method == 'POST':
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'message': 'User with mail address %s logged in successfully' % user.email}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    # Example protected view
    return Response({'message': 'This is a protected view'}, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        request = self.request
        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = authorization_header.split(' ')[1] if 'Token' in authorization_header else None

        if token:
            response.data['next'] = self.append_token_to_url(response.data.get('next'), token)
            response.data['previous'] = self.append_token_to_url(response.data.get('previous'), token)
        
        return response

    def append_token_to_url(self, url, token):
        if url:
            separator = '&' if '?' in url else '?'
            return f'{url}{separator}token={token}'
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.query_params.get('q', '')
    if query:
        if '@' in query:
            try:
                user = User.objects.get(email__iexact=query)
                serializer = UserSerializer(user)
                print("serializer.data",type(serializer.data))
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'No user found with this email'}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.objects.filter(username__icontains=query)
            paginator = StandardResultsSetPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = UserSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
    return Response({'error': 'A search query parameter "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    from_user = request.user
    print("from_user",from_user)
    to_user_id = request.data.get('to_user_id')
    print("to_user_id",to_user_id)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    print("to_user",to_user)

    # Check if the request already exists
    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

    # Rate limiting: only 3 friend requests within the last minute
    one_minute_ago = timezone.now() - datetime.timedelta(minutes=1)
    recent_requests = FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count()
    if recent_requests >= 3:
        return Response({'error': 'You can only send 3 friend requests per minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    friend_request = FriendRequest(from_user=from_user, to_user=to_user)
    friend_request.save()
    return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_friend_request(request):
    current_user = request.user
    request_id = request.data.get('request_id')
    action = request.data.get('action')
    
    if action not in ['accept', 'reject']:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        friend_request = FriendRequest.objects.get(id=request_id, to_user=current_user, status='pending')
    except Exception as exp:
        return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if action == 'accept':
        friend_request.status = 'accepted'
    elif action == 'reject':
        friend_request.status = 'rejected'
    
    friend_request.save()
    return Response({'message': f'Friend request {action}ed'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    current_user = request.user
    friends = User.objects.filter(sent_requests__to_user=current_user, sent_requests__status='accepted') | \
              User.objects.filter(received_requests__from_user=current_user, received_requests__status='accepted')
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(friends, request)
    serializer = UserSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_requests(request):
    current_user = request.user
    pending_requests = FriendRequest.objects.filter(to_user=current_user, status='pending')
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(pending_requests, request)
    # Assuming you have a serializer for FriendRequest
    serializer = FriendRequestSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)