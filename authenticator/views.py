from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Authenticator
from .serializers import UserSerializer, AuthenticatorSerializer
from django.utils.timezone import now
from heartbeats.custom_response import CustomResponse
from rest_framework_simplejwt.tokens import RefreshToken

class UserListView(APIView):
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
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        print(username,password)

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            authenticator = Authenticator.objects.get(username = username)

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

                response = CustomResponse(message="Login successful",success=True)
                # Lưu JWT vào HttpOnly Cookies
                response.set_cookie(
                    key='access_token',
                    value=str(refresh.access_token),
                    httponly=True,
                    secure=True,  # Chỉ hoạt động trên HTTPS
                    samesite='Lax'
                )
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite='Lax'
                )
                return response
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Authenticator.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
