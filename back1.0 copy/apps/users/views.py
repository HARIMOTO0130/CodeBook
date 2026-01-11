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
        # 打印接收到的数据用于调试
        print(f"[注册] 接收到的数据: {request.data}")
        
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'user': UserSerializer(user).data,
                    'token': token.key,
                    'role': user.role  # 返回用户角色
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"[注册] 保存用户时出错: {str(e)}")
                return Response({
                    'error': f'创建用户失败: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(f"[注册] 验证失败: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """用户登录"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        print(f"[登录API] 收到登录请求 - 用户名: {username}, 路径: {request.path}")
        
        if not username or not password:
            return Response({
                'error': '请提供用户名和密码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户是否存在
        try:
            db_user = User.objects.get(username=username)
            print(f"[登录API] 用户存在: {db_user.username}, is_active: {db_user.is_active}")
        except User.DoesNotExist:
            print(f"[登录API] 用户不存在: {username}")
            return Response({
                'error': '用户名或密码错误',
                'debug': '用户不存在'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 使用Django的authenticate函数进行认证
        user = authenticate(request, username=username, password=password)
        print(f"[登录API] authenticate结果: {user is not None}")
        
        if user is not None:
            # 认证成功，生成token
            token, created = Token.objects.get_or_create(user=user)
            print(f"[登录API] 登录成功 - Token已生成")
            
            # 构建响应数据
            response_data = {
                'user': UserSerializer(user).data,
                'token': token.key,
                'role': user.role
            }
            
            # 如果是教师，添加teacher_id
            if user.role == 'teacher':
                response_data['teacher_id'] = user.id
                print(f"[登录API] 教师登录 - teacher_id: {user.id}")
            
            # 如果是学生，添加student_id
            elif user.role == 'student':
                response_data['student_id'] = user.id
                print(f"[登录API] 学生登录 - student_id: {user.id}")
            
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print(f"[登录API] 认证失败 - 密码错误或用户未激活")
            return Response({
                'error': '用户名或密码错误',
                'debug': '密码验证失败'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
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