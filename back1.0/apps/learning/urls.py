"""学习记录URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from .views import (
    LearningRecordViewSet,
    PracticeRecordViewSet,
    WrongQuestionViewSet,
    RoadmapTemplateViewSet,
    UserLearningPathViewSet,
    NoteViewSet,
    execute_code,
    JupyterDocumentViewSet,
    create_jupyter_document,
    update_jupyter_document,
    LearningRecommendationViewSet,
    PersonalizedLearningPathAPIView,
    KnowledgeGraphAPIView,
    LLMAPIView,
)
from .views_ai_assistant import AIAssistantView, CodeCompletionView
from .views_code_sandbox import get_languages, get_code_template, validate_language

router = DefaultRouter()
router.register(r'records', LearningRecordViewSet, basename='learning-record')
router.register(r'practice-records', PracticeRecordViewSet, basename='practice-record')
router.register(r'wrong-questions', WrongQuestionViewSet, basename='wrong-question')
router.register(r'roadmaps', RoadmapTemplateViewSet, basename='roadmap')
router.register(r'user-paths', UserLearningPathViewSet, basename='user-learning-path')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'jupyter-documents', JupyterDocumentViewSet, basename='jupyter-document')
router.register(r'recommendations', LearningRecommendationViewSet, basename='learning-recommendation')

urlpatterns = [
    path('', include(router.urls)),
    path('save-progress/', LearningRecordViewSet.as_view({'post': 'save_progress'})),
    path('practice-submit/', PracticeRecordViewSet.as_view({'post': 'submit'})),
    path('heatmap/', LearningRecordViewSet.as_view({'get': 'heatmap'})),
    path('execute/', execute_code),
    # 路线图相关的额外路由
    path('roadmaps/recommended/', RoadmapTemplateViewSet.as_view({'get': 'recommended_for_user'})),
    path('user-paths/create/', UserLearningPathViewSet.as_view({'post': 'create_path'})),
    # Jupyter文档相关路由
    path('jupyter-documents/create/', create_jupyter_document, name='create-jupyter-document'),
    path('jupyter-documents/update/<int:pk>/', update_jupyter_document, name='update-jupyter-document'),
    # AI助手路由
    path('ai-assistant/', AIAssistantView.as_view(), name='ai-assistant'),
    # 代码补全API路由
    path('code-completion/', CodeCompletionView.as_view(), name='code-completion'),
    # 代码沙盒相关路由
    path('code-sandbox/languages/', get_languages, name='get-supported-languages'),
    path('code-sandbox/template/<str:language>/', get_code_template, name='get-code-template'),
    path('code-sandbox/validate/', validate_language, name='validate-language'),
    # 为错题本提供显式路由，确保学生端 /api/student/learning/wrong-questions/add_from_exercise/ 可正常访问
    path(
        'wrong-questions/add_from_exercise/',
        WrongQuestionViewSet.as_view({'post': 'add_from_exercise'}),
        name='wrong-question-add-from-exercise',
    ),
    # 个性化学习路径相关路由
    path('personalized-path/generate/', PersonalizedLearningPathAPIView.generate_path, name='generate-personalized-path'),
    path('personalized-path/update/', PersonalizedLearningPathAPIView.update_path, name='update-personalized-path'),
    path('personalized-path/feedback/', PersonalizedLearningPathAPIView.generate_feedback, name='generate-learning-feedback'),
    path('personalized-path/smart-path/', PersonalizedLearningPathAPIView.generate_smart_path, name='generate-smart-path'),
    # 知识图谱相关路由
    path('knowledge-graph/nodes/', KnowledgeGraphAPIView.get_nodes, name='get-knowledge-nodes'),
    path('knowledge-graph/relations/', KnowledgeGraphAPIView.get_relations, name='get-knowledge-relations'),
    path('knowledge-graph/nodes/add/', KnowledgeGraphAPIView.add_node, name='add-knowledge-node'),
    path('knowledge-graph/relations/add/', KnowledgeGraphAPIView.add_relation, name='add-knowledge-relation'),
    # 大模型相关路由
    path('llm/generate/', LLMAPIView.generate_response, name='generate-llm-response'),
    path('llm/extract-knowledge/', LLMAPIView.extract_knowledge, name='extract-knowledge-nodes'),
    
    # 智能推荐路由
    path('recommendations/roadmap/', LearningRecommendationViewSet.as_view({'get': 'recommend_roadmap'}), name='recommend-roadmap'),
    path('recommendations/personalized-suggestions/', LearningRecommendationViewSet.as_view({'post': 'generate_personalized_suggestions'}), name='generate-personalized-suggestions'),
    path('recommendations/next-content/', LearningRecommendationViewSet.as_view({'get': 'next_content'}), name='recommend-next-content'),
    path('recommendations/user-profile/', LearningRecommendationViewSet.as_view({'get': 'build_profile'}), name='build-user-profile'),
]