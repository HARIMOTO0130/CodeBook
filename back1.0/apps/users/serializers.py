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
    role = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'avatar', 'role', 'preferences')
        read_only_fields = ('id', 'role')
    
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
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    role = serializers.ChoiceField(
        choices=[('student', '学生'), ('teacher', '教师'), ('provider', '教材提供者'), ('admin', '管理员')],
        default='student',
        required=False,
        allow_blank=False
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role')
        extra_kwargs = {
            'username': {
                'required': True,
                'min_length': 3,
                'max_length': 150,
                'validators': []
            },
            'email': {
                'required': True
            }
        }
    
    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        # 创建默认偏好设置
        UserPreferences.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)