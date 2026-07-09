from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 닉네임 필드 (중복 비허용)
    nickname = models.CharField(max_length=20, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}의 프로필 ({self.nickname})"
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """User 모델이 신규 생성될 때 Profile 모델도 자동으로 생성"""
    if created:
        # 가입 초기에는 고유 ID를 활용해 중복되지 않는 기본 닉네임을 부여
        Profile.objects.create(user=instance, nickname=f"유저_{instance.id}")

