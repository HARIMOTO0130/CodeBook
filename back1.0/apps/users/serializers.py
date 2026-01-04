"""用户序列化器"""
from rest_framework import serializers
from .models import User, UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """用户偏好设置序列化器"""
    class Meta:
        model = UserPreferences
        fields = ('default_language', 'code_theme', 'auto_play_video', 'keyboard_shortcuts')


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    preferences = UserPreferencesSerializer(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar', 'preferences')
        read_only_fields = ('id',)
    
    def update(self, instance, validated_data):
        preferences_data = validated_data.pop('preferences', None)
        
        # 更新用户基本信息
        instance = super().update(instance, validated_data)
        
        # 更新用户偏好设置
        if preferences_data:
            preferences, created = UserPreferences.objects.get_or_create(user=instance)
            for key, value in preferences_data.items():
                setattr(preferences, key, value)
            preferences.save()
        
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # 创建默认偏好设置
        UserPreferences.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)