"""用户视图函数"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, UserPreferences
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserPreferencesSerializer


class TestAPIView(APIView):
    """测试API视图，用于诊断问题"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """测试GET请求"""
        return Response({
            'message': '测试成功',
            'method': 'GET',
            'request_data': request.GET.dict()
        })
    
    def post(self, request):
        """测试POST请求"""
        return Response({
            'message': '测试成功',
            'method': 'POST',
            'request_data': request.data
        })


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # 为特定操作设置不同的权限
    def get_permissions(self):
        # 登录和注册操作允许匿名访问
        if self.action in ['login', 'register']:
            return [permissions.AllowAny()]
        # 其他操作需要身份认证
        return super().get_permissions()
    
    def get_queryset(self):
        # 普通用户只能查看自己的信息
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """用户注册"""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """用户登录"""
        # 直接检查请求数据并返回更详细的信息
        username = request.data.get('username', 'None')
        password = request.data.get('password', 'None')
        
        # 检查用户是否存在
        try:
            user_exists = User.objects.filter(username=username).exists()
            
            if user_exists:
                user = User.objects.get(username=username)
                # 使用Django的认证系统验证密码
                from django.contrib.auth.hashers import check_password
                password_valid = check_password(password, user.password)
                
                if password_valid:
                    # 密码正确，生成token
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'user': UserSerializer(user).data,
                        'token': token.key,
                        'debug_info': '认证成功'
                    })
                else:
                    return Response({
                        'error': '用户名或密码错误',
                        'debug_info': '用户存在但密码错误'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({
                    'error': '用户名或密码错误',
                    'debug_info': '用户不存在',
                    'received_username': username
                }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'error': str(e),
                'debug_info': '登录过程发生异常',
                'received_data': request.data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get', 'put'], url_path='preferences')
    def preferences(self, request):
        """获取或更新用户偏好设置"""
        if not request.user.is_authenticated:
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if request.method == 'GET':
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            serializer = UserPreferencesSerializer(preferences)
            return Response(serializer.data)
        elif request.method == 'PUT':
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            if serializer.is_valid():
                preferences = serializer.save()
                return Response({
                    'default_language': preferences.default_language,
                    'code_theme': preferences.code_theme,
                    'auto_play_video': preferences.auto_play_video,
                    'keyboard_shortcuts': preferences.keyboard_shortcuts
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)