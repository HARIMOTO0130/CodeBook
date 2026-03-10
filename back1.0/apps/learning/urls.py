"""学习记录URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from .views import (
    LearningRecordViewSet,
    PracticeRecordViewSet,
    WrongQuestionViewSet,
    NoteViewSet,
    PersonalizedLearningPathAPIView,
    KnowledgeGraphAPIView,
    execute_code,
    get_recommended_roadmaps,
)
from .views_ai_assistant import AIAssistantView, CodeCompletionView
from .views_code_review import CodeReviewView, CodeReviewHistoryView, CodeReviewDetailView, CodeReviewStatsView
from .views_exercise_generator import ExerciseGeneratorView, ExerciseSetGeneratorView, ExerciseRecommendationView, ExerciseHistoryView, ExerciseTypesView
from .views_learning_prediction import LearningPredictionView, BatchPredictionView, PredictionHistoryView, InterventionView, PredictionStatsView
from .views_learning_analytics import LearningAnalyticsView, LearningPatternsView, LearningRecommendationsView, LearningEfficiencyView
from .views_adaptive_difficulty import AdaptiveDifficultyView, AbilityEvaluationView, OptimalDifficultyView, DifficultyRecommendationsView
from .views_code_similarity import CodeSimilarityView, BatchSimilarityView, SimilarityAnalysisView
from .views_learning_summary import LearningSummaryView, TopicSummaryView, SummaryHistoryView, SummaryStatsView
from .strategy_kg_views import (
    StrategyKnowledgeNodeViewSet,
    StrategyRelationViewSet,
    StrategyLearningPathViewSet,
    UserStrategyPathViewSet,
    StrategyRecommendationViewSet,
    StrategyUserProfileViewSet,
    StrategyResourceViewSet,
)

router = DefaultRouter()
router.register(r'records', LearningRecordViewSet, basename='learning-record')
router.register(r'practice-records', PracticeRecordViewSet, basename='practice-record')
router.register(r'wrong-questions', WrongQuestionViewSet, basename='wrong-question')
router.register(r'notes', NoteViewSet, basename='note')

router.register(r'strategy/nodes', StrategyKnowledgeNodeViewSet, basename='strategy-node')
router.register(r'strategy/relations', StrategyRelationViewSet, basename='strategy-relation')
router.register(r'strategy/paths', StrategyLearningPathViewSet, basename='strategy-path')
router.register(r'strategy/user-paths', UserStrategyPathViewSet, basename='strategy-user-path')
router.register(r'strategy/recommendations', StrategyRecommendationViewSet, basename='strategy-recommendation')
router.register(r'strategy/profile', StrategyUserProfileViewSet, basename='strategy-profile')
router.register(r'strategy/resources', StrategyResourceViewSet, basename='strategy-resource')

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
    # 代码审查相关路由
    path('code-review/', CodeReviewView.as_view(), name='code-review'),
    path('code-review/history/', CodeReviewHistoryView.as_view(), name='code-review-history'),
    path('code-review/history/<int:record_id>/', CodeReviewDetailView.as_view(), name='code-review-detail'),
    path('code-review/stats/', CodeReviewStatsView.as_view(), name='code-review-stats'),
    # 习题生成相关路由
    path('exercise-generator/', ExerciseGeneratorView.as_view(), name='exercise-generator'),
    path('exercise-generator/set/', ExerciseSetGeneratorView.as_view(), name='exercise-set-generator'),
    path('exercise-generator/recommend/', ExerciseRecommendationView.as_view(), name='exercise-recommendation'),
    path('exercise-generator/history/', ExerciseHistoryView.as_view(), name='exercise-history'),
    path('exercise-generator/types/', ExerciseTypesView.as_view(), name='exercise-types'),
    # 学习效果预测相关路由
    path('learning-prediction/', LearningPredictionView.as_view(), name='learning-prediction'),
    path('learning-prediction/batch/', BatchPredictionView.as_view(), name='batch-prediction'),
    path('learning-prediction/history/', PredictionHistoryView.as_view(), name='prediction-history'),
    path('learning-prediction/intervention/', InterventionView.as_view(), name='intervention'),
    path('learning-prediction/stats/', PredictionStatsView.as_view(), name='prediction-stats'),
    # 学情智能分析相关路由
    path('learning-analytics/', LearningAnalyticsView.as_view(), name='learning-analytics'),
    path('learning-analytics/patterns/', LearningPatternsView.as_view(), name='learning-patterns'),
    path('learning-analytics/recommendations/', LearningRecommendationsView.as_view(), name='learning-recommendations'),
    path('learning-analytics/efficiency/', LearningEfficiencyView.as_view(), name='learning-efficiency'),
    # 自适应难度调整相关路由
    path('adaptive-difficulty/', AdaptiveDifficultyView.as_view(), name='adaptive-difficulty'),
    path('adaptive-difficulty/ability/', AbilityEvaluationView.as_view(), name='ability-evaluation'),
    path('adaptive-difficulty/optimal/', OptimalDifficultyView.as_view(), name='optimal-difficulty'),
    path('adaptive-difficulty/recommendations/', DifficultyRecommendationsView.as_view(), name='difficulty-recommendations'),
    # 代码相似度检测相关路由
    path('code-similarity/', CodeSimilarityView.as_view(), name='code-similarity'),
    path('code-similarity/batch/', BatchSimilarityView.as_view(), name='code-similarity-batch'),
    path('code-similarity/analysis/', SimilarityAnalysisView.as_view(), name='code-similarity-analysis'),
    # 学习摘要生成相关路由
    path('learning-summary/', LearningSummaryView.as_view(), name='learning-summary'),
    path('learning-summary/topic/', TopicSummaryView.as_view(), name='topic-summary'),
    path('learning-summary/history/', SummaryHistoryView.as_view(), name='summary-history'),
    path('learning-summary/stats/', SummaryStatsView.as_view(), name='summary-stats'),
]