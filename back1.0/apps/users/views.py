"""用户视图函数"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User, UserPreferences
from apps.learning.models import LearningStyle, KnowledgeMastery, LearningPreference
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, 
    UserPreferencesSerializer, UserProfileSerializer
)


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
        
        if not username or not password:
            return Response({
                'error': '请提供用户名和密码'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用Django的authenticate函数进行认证
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 认证成功，生成token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'role': user.role  # 返回用户角色
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': '用户名或密码错误'
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
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[INFO] GET /me/ called by user: {request.user}, user ID: {request.user.id}")
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user, context={'request': request})
            logger.info(f"[INFO] User data retrieved: username={request.user.username}, nickname={request.user.nickname}")
            logger.info(f"[INFO] Response data: {serializer.data}")
            return Response(serializer.data)
        logger.warning("[WARNING] Unauthenticated user attempted to get profile")
        return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['put', 'post'])
    def update_me(self, request):
        """更新当前用户信息"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[INFO] PUT/POST /me/ called by user: {request.user}, user ID: {request.user.id}")
        logger.info(f"[INFO] Request data: {request.data}")
        
        if not request.user.is_authenticated:
            logger.warning("[WARNING] Unauthenticated user attempted to update profile")
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"[INFO] User updated successfully: {user}, user ID: {user.id}")
            logger.info(f"[INFO] Updated user data: username={user.username}, nickname={user.nickname}, email={user.email}")
            
            # 检查是否是学生用户，并记录学生信息
            if user.role == 'student':
                try:
                    from apps.teacher.models import Student
                    student_profile = Student.objects.get(user=user)
                    logger.info(f"[INFO] Student profile found: {student_profile}, student ID: {student_profile.id}")
                    logger.info(f"[INFO] Student data: student_name={student_profile.student_name}, student_no={student_profile.student_no}, class_name={student_profile.class_name}")
                except Student.DoesNotExist:
                    logger.warning(f"[WARNING] No student profile found for user: {user}")
                except Exception as e:
                    logger.error(f"[ERROR] Error retrieving student profile: {e}")
            
            response_data = UserSerializer(user, context={'request': request}).data
            logger.info(f"[INFO] Response data: {response_data}")
            return Response(response_data)
        
        logger.error(f"[ERROR] Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put'], url_path='preferences')
    def preferences(self, request):
        """获取或更新用户偏好设置"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[INFO] {request.method} /preferences/ called by user: {request.user}, user ID: {request.user.id}")
        
        if request.method == 'PUT':
            logger.info(f"[INFO] Preferences update data: {request.data}")
        
        if not request.user.is_authenticated:
            logger.warning("[WARNING] Unauthenticated user attempted to access preferences")
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if request.method == 'GET':
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            serializer = UserPreferencesSerializer(preferences)
            logger.info(f"[INFO] Preferences retrieved: {preferences}, created: {created}")
            logger.info(f"[INFO] Preferences data: {serializer.data}")
            return Response(serializer.data)
        elif request.method == 'PUT':
            preferences, created = UserPreferences.objects.get_or_create(user=request.user)
            logger.info(f"[INFO] Updating preferences: {preferences}, created: {created}")
            
            serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)
            if serializer.is_valid():
                updated_preferences = serializer.save()
                logger.info(f"[INFO] Preferences updated successfully: {updated_preferences}")
                
                # 使用序列化器返回所有更新后的字段
                response_data = UserPreferencesSerializer(updated_preferences).data
                logger.info(f"[INFO] Updated preferences response: {response_data}")
                return Response(response_data)
            
            logger.error(f"[ERROR] Preferences serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """修改用户密码"""
        if not request.user.is_authenticated:
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # 验证密码
        if not current_password:
            return Response({'error': '当前密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({'error': '新密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': '两次输入的新密码不一致'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证当前密码是否正确
        if not request.user.check_password(current_password):
            return Response({'error': '当前密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新密码
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': '密码修改成功'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='profile')
    def user_profile(self, request):
        """获取用户画像数据，包括多维度特征提取、知识状态评估和专业倾向性分析"""
        if not request.user.is_authenticated:
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 获取当前用户
        user = request.user
        
        # 获取关联数据
        learning_style, _ = LearningStyle.objects.get_or_create(user=user)
        learning_preference, _ = LearningPreference.objects.get_or_create(user=user)
        knowledge_mastery = KnowledgeMastery.objects.filter(user=user).all()
        
        # 获取学习情况数据
        from apps.learning.models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion
        learning_records = LearningRecord.objects.filter(user=user).all()
        practice_records = PracticeRecord.objects.filter(user=user).all()
        heatmap_data = HeatmapData.objects.filter(user=user).all()
        wrong_questions = WrongQuestion.objects.filter(user=user).all()
        
        # 构建用户画像数据
        profile_data = {
            'user': user,
            'learning_style': learning_style,
            'learning_preference': learning_preference,
            'knowledge_mastery': knowledge_mastery,
            'learning_records': learning_records,
            'practice_records': practice_records,
            'heatmap_data': heatmap_data,
            'wrong_questions': wrong_questions
        }
        
        # 序列化并返回
        serializer = UserProfileSerializer(profile_data)
        return Response(serializer.data)