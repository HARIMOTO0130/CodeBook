"""学习记录URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from .views import (
    LearningRecordViewSet,
    PracticeRecordViewSet,
    WrongQuestionViewSet,
    # RoadmapTemplateViewSet,
    # UserLearningPathViewSet,
    NoteViewSet,
    # JupyterDocumentViewSet,
    # create_jupyter_document,
    # update_jupyter_document,
    # LearningRecommendationViewSet,
    PersonalizedLearningPathAPIView,
    KnowledgeGraphAPIView,
    # LLMAPIView,
    # AIInteractionRecordViewSet,
    # StudentClassViewSet,
    # StudentHomeworkViewSet,
    # StudentResourceViewSet,
    # StudentNoticeViewSet,
    execute_code,
    get_recommended_roadmaps,
)
from .views_ai_assistant import AIAssistantView, CodeCompletionView
# from .views_code_sandbox import get_languages, get_code_template, validate_language

router = DefaultRouter()
router.register(r'records', LearningRecordViewSet, basename='learning-record')
router.register(r'practice-records', PracticeRecordViewSet, basename='practice-record')
router.register(r'wrong-questions', WrongQuestionViewSet, basename='wrong-question')
# router.register(r'roadmaps', RoadmapTemplateViewSet, basename='roadmap')
# router.register(r'user-paths', UserLearningPathViewSet, basename='user-learning-path')
router.register(r'notes', NoteViewSet, basename='note')
# router.register(r'jupyter-documents', JupyterDocumentViewSet, basename='jupyter-document')
# router.register(r'recommendations', LearningRecommendationViewSet, basename='learning-recommendation')
# router.register(r'ai-interactions', AIInteractionRecordViewSet, basename='ai-interaction')
# # 学生端核心功能
# router.register(r'classes', StudentClassViewSet, basename='student-class')
# router.register(r'homeworks', StudentHomeworkViewSet, basename='student-homework')
# router.register(r'resources', StudentResourceViewSet, basename='student-resource')
# router.register(r'notices', StudentNoticeViewSet, basename='student-notice')

urlpatterns = [
    path('', include(router.urls)),
    path('execute/', execute_code, name='execute-code'),
    # 个性化学习路径相关路由
    path('personalized-path/generate/', PersonalizedLearningPathAPIView.generate_path, name='generate-personalized-path'),
    path('personalized-path/update/', PersonalizedLearningPathAPIView.update_path, name='update-personalized-path'),
    path('personalized-path/feedback/', PersonalizedLearningPathAPIView.generate_feedback, name='generate-learning-feedback'),
    path('personalized-path/smart-path/', PersonalizedLearningPathAPIView.generate_smart_path, name='generate-smart-path'),
    # 学习推荐相关路由
    path('recommendations/roadmap/', get_recommended_roadmaps, name='get-recommended-roadmaps'),
    # 知识图谱相关路由
    path('knowledge-graph/nodes/', KnowledgeGraphAPIView.get_nodes, name='get-knowledge-nodes'),
    path('knowledge-graph/relations/', KnowledgeGraphAPIView.get_relations, name='get-knowledge-relations'),
    path('knowledge-graph/nodes/add/', KnowledgeGraphAPIView.add_node, name='add-knowledge-node'),
    # path('knowledge-graph/relations/add/', KnowledgeGraphAPIView.add_relation, name='add-knowledge-relation'),
    # AI助手相关路由
    path('ai-assistant/', AIAssistantView.as_view(), name='ai-assistant'),
    path('ai-assistant/code-completion/', CodeCompletionView.as_view(), name='code-completion'),
]