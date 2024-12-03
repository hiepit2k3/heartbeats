from rest_framework.views import APIView
from django.middleware import csrf
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from .models import User, Authenticator
from .serializers import UserSerializer, AuthenticatorSerializer
from django.utils.timezone import now
from heartbeats.custom_response import CustomResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class AuthenticatorListView(APIView):
    def get(self, request):
        authenticators = Authenticator.objects.all()
        serializer = AuthenticatorSerializer(authenticators, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuthenticatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        print(username,password)
        response = Response()

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            authenticator = Authenticator.objects.get(username = username)
            data = get_tokens_for_user(authenticator)

            if authenticator.check_password(password):
                user = User.objects.get(id=authenticator.user_id)
                user.last_login = now()  # Cập nhật thời gian đăng nhập cuối cùng
                user.save()

                # Cập nhật thời gian đăng nhập trong Authenticator
                authenticator.last_login = now()
                authenticator.save()

                # Tạo refresh token và access token
                refresh = RefreshToken.for_user(authenticator)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Lưu refresh token vào database
                authenticator.refresh_token = refresh_token
                # RefreshTokenModel.objects.create(
                #     user=user,
                #     token=refresh_token,
                #     expires_at=now() + timedelta(days=7)  # Đặt thời gian hết hạn cho refresh token
                # )

                response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value = data["access"],
                    expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {"Success" : "Login successfully","data":data}
                return response
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Authenticator.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
