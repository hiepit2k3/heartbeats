import random
from faker import Faker
from authenticator.models import User, Authenticator
from django.utils.timezone import now, make_aware

fake = Faker()

def create_users(num_users=10):
    """Tạo dữ liệu test cho bảng User"""
    for _ in range(num_users):
        user = User.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            is_active=random.choice([True, False]),
            is_premium=random.choice([True, False]),
            bio=fake.sentence(nb_words=10),
            country=fake.country(),
            favorite_genre=random.choice(["Pop", "Rock", "Jazz", "Classical", "Hip-Hop", "EDM"]),
        )
        print(f"Created User: {user}")

def create_authenticators(num_authenticators=10):
    """Tạo dữ liệu test cho bảng Authenticator"""
    all_users = list(User.objects.all())
    for _ in range(num_authenticators):
        if not all_users:
            print("No users available to link with Authenticator. Create users first.")
            break
        user = random.choice(all_users)

        # Tạo datetime với thông tin múi giờ
        naive_datetime = fake.date_time_this_year()  # datetime không có thông tin múi giờ
        aware_datetime = make_aware(naive_datetime)  # Chuyển sang datetime có múi giờ

        authenticator = Authenticator.objects.create(
            username=fake.unique.user_name(),
            password=fake.password(length=12),
            user_id=user.id,
            last_login=aware_datetime,  # Sử dụng datetime có múi giờ
            login_attempts=random.randint(0, 5),
            is_locked=random.choice([True, False]),
            reset_token=fake.uuid4() if random.choice([True, False]) else None,
        )
        print(f"Created Authenticator: {authenticator}")

# Chạy tạo dữ liệu
def run():
    create_users(num_users=10)          # Tạo 10 User
    create_authenticators(num_authenticators=10)  # Tạo 10 Authenticator
