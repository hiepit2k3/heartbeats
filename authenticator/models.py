from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Authenticator(models.Model):
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=500)
    user_id = models.IntegerField()
    # Thêm các trường bổ sung
    last_login = models.DateTimeField(null=True, blank=True)  # Lần đăng nhập cuối cùng
    login_attempts = models.IntegerField(default=0)  # Số lần thử đăng nhập sai
    is_locked = models.BooleanField(default=False)  # Tài khoản có bị khóa không
    refresh_token = models.CharField(max_length=255, null=True, blank=True)
    

    # def set_password(self, raw_password):
    #     """Mã hóa và lưu mật khẩu"""
    #     self.password = make_password(raw_password)
    #     self.save()

    # def check_password(self, raw_password):
    #     """Kiểm tra mật khẩu (so sánh với mật khẩu đã mã hóa)"""
    #     return check_password(raw_password, self.password)
    def check_password(self, raw_password):
        """Kiểm tra mật khẩu (so sánh trực tiếp với mật khẩu đã lưu)"""
        return raw_password == self.password 

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'db_authenticator'

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=50, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)  # Ảnh đại diện
    is_active = models.BooleanField(default=True)  # Trạng thái tài khoản (kích hoạt hay không)
    is_premium = models.BooleanField(default=False)  # Người dùng premium hay không
    last_login = models.DateTimeField(null=True, blank=True)  # Lần đăng nhập cuối cùng
    bio = models.TextField(null=True, blank=True)  # Mô tả ngắn về người dùng
    country = models.CharField(max_length=100, null=True, blank=True)  # Quốc gia của người dùng
    favorite_genre = models.CharField(max_length=50, null=True, blank=True)  # Thể loại nhạc yêu thích

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'db_user'