# -*- coding: utf-8 -*-
"""AI审核引擎"""
import json
import time
import logging
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AIReviewEngine:
    """AI审核引擎 - 使用豆包大模型API"""
    
    def __init__(self):
        self.api_key = settings.DOUBAO_API_KEY
        self.api_base_url = settings.DOUBAO_API_BASE_URL
        self.model_id = settings.DOUBAO_MODEL_ID
    
    def _call_api(self, messages, max_tokens=4096):
        """调用豆包大模型API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': self.model_id,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.3,
        }
        
        try:
            response = requests.post(
                f'{self.api_base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'AI API调用失败: {str(e)}')
            raise Exception(f'AI API调用失败: {str(e)}')
    
    def review_book(self, book_data, chapters_data):
        """
        审核教材内容
        
        Args:
            book_data: 教材基本信息 {'title': '', 'author': '', 'description': ''}
            chapters_data: 章节列表 [{'title': '', 'content': '', 'code': ''}]
        
        Returns:
            dict: 审核结果
        """
        start_time = time.time()
        
        try:
            content_text = self._prepare_content(book_data, chapters_data)
            
            prompt = self._build_review_prompt(book_data, content_text)
            
            messages = [
                {'role': 'system', 'content': self._get_system_prompt()},
                {'role': 'user', 'content': prompt}
            ]
            
            response = self._call_api(messages)
            
            if 'choices' not in response or len(response['choices']) == 0:
                raise Exception('AI响应格式错误')
            
            ai_response = response['choices'][0]['message']['content']
            
            result = self._parse_response(ai_response)
            
            processing_time = int((time.time() - start_time) * 1000)
            result['processing_time'] = processing_time
            result['raw_response'] = ai_response
            result['model_version'] = self.model_id
            
            return result
            
        except Exception as e:
            logger.error(f'AI审核失败: {str(e)}')
            return {
                'error': str(e),
                'processing_time': int((time.time() - start_time) * 1000),
            }
    
    def _prepare_content(self, book_data, chapters_data):
        """准备审核内容"""
        content_parts = []
        
        content_parts.append(f"【教材标题】{book_data.get('title', '')}")
        content_parts.append(f"【作者】{book_data.get('author', '')}")
        content_parts.append(f"【描述】{book_data.get('description', '')}")
        content_parts.append("\n" + "="*50 + "\n")
        
        for i, chapter in enumerate(chapters_data[:10], 1):
            content_parts.append(f"\n【章节{i}】{chapter.get('title', '')}")
            
            chapter_content = chapter.get('content', '')
            if chapter_content:
                if len(chapter_content) > 2000:
                    chapter_content = chapter_content[:2000] + '...(内容过长已截断)'
                content_parts.append(chapter_content)
            
            chapter_code = chapter.get('code', '')
            if chapter_code:
                if len(chapter_code) > 1000:
                    chapter_code = chapter_code[:1000] + '...(代码过长已截断)'
                content_parts.append(f"\n【示例代码】\n{chapter_code}")
        
        return '\n'.join(content_parts)
    
    def _get_system_prompt(self):
        """获取系统提示词"""
        return """你是一位专业的教材审核专家，负责审核数字教材内容。请从以下维度进行评估：

1. 内容合规性(30%权重)：检查是否存在政治敏感、违法违规、不当言论等内容
2. 准确性(25%权重)：评估知识点的正确性、代码的可执行性
3. 完整性(20%权重)：检查章节结构是否完整、内容是否连贯
4. 可读性(15%权重)：评估语言表达、逻辑结构
5. 格式规范(10%权重)：检查排版规范、多媒体质量

请严格按照JSON格式返回审核结果，格式如下：
{
    "overall_score": 85,
    "risk_level": "low",
    "scores": {
        "content_compliance": 90,
        "accuracy": 85,
        "completeness": 80,
        "readability": 88,
        "formatting": 82
    },
    "detected_issues": [
        {
            "type": "content",
            "severity": "medium",
            "location": "第3章第2节",
            "description": "问题描述"
        }
    ],
    "risk_items": [
        {
            "level": "medium",
            "category": "准确性",
            "description": "风险描述"
        }
    ],
    "suggestions": [
        "建议1：具体修改建议",
        "建议2：具体修改建议"
    ]
}

风险等级：low(低风险,80-100分)、medium(中等风险,60-80分)、high(高风险,40-60分)、critical(严重风险,0-40分)
严重程度：low(轻微)、medium(中等)、high(严重)、critical(严重)"""
    
    def _build_review_prompt(self, book_data, content_text):
        """构建审核提示词"""
        return f"""请审核以下教材内容：

{content_text}

请按照要求的JSON格式返回审核结果。注意：
1. 评分范围0-100分
2. 客观公正地评估每个维度
3. 详细列出发现的问题和风险
4. 提供具体的修改建议"""
    
    def _parse_response(self, response_text):
        """解析AI响应"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError('未找到JSON内容')
            
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            
            return {
                'overall_score': result.get('overall_score', 0),
                'risk_level': result.get('risk_level', 'medium'),
                'content_compliance_score': result.get('scores', {}).get('content_compliance', 0),
                'accuracy_score': result.get('scores', {}).get('accuracy', 0),
                'completeness_score': result.get('scores', {}).get('completeness', 0),
                'readability_score': result.get('scores', {}).get('readability', 0),
                'detected_issues': result.get('detected_issues', []),
                'risk_items': result.get('risk_items', []),
                'suggestions': result.get('suggestions', []),
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f'解析AI响应失败: {str(e)}')
            return {
                'overall_score': 0,
                'risk_level': 'critical',
                'error': f'解析AI响应失败: {str(e)}',
                'raw_response': response_text,
            }


def run_ai_review(task, book_data, chapters_data):
    """
    执行AI审核任务
    
    Args:
        task: ReviewTask实例
        book_data: 教材数据
        chapters_data: 章节数据
    
    Returns:
        AIReviewRecord实例
    """
    from .models import AIReviewRecord, WorkflowLog
    
    ai_record, created = AIReviewRecord.objects.get_or_create(
        task=task,
        defaults={'status': 'pending'}
    )
    
    if ai_record.status == 'completed':
        return ai_record
    
    ai_record.status = 'processing'
    ai_record.save()
    
    try:
        engine = AIReviewEngine()
        result = engine.review_book(book_data, chapters_data)
        
        if 'error' in result:
            ai_record.status = 'failed'
            ai_record.error_message = result['error']
        else:
            ai_record.status = 'completed'
            ai_record.overall_score = result.get('overall_score')
            ai_record.risk_level = result.get('risk_level')
            ai_record.content_compliance_score = result.get('content_compliance_score')
            ai_record.accuracy_score = result.get('accuracy_score')
            ai_record.completeness_score = result.get('completeness_score')
            ai_record.readability_score = result.get('readability_score')
            ai_record.detected_issues = result.get('detected_issues', [])
            ai_record.risk_items = result.get('risk_items', [])
            ai_record.suggestions = result.get('suggestions', [])
            ai_record.raw_response = result.get('raw_response', '')
            ai_record.model_version = result.get('model_version', '')
            ai_record.processing_time = result.get('processing_time')
        
        ai_record.save()
        
        WorkflowLog.objects.create(
            task=task,
            action='ai_reviewed',
            actor_type='system',
            comment=f'AI审核完成，评分: {ai_record.overall_score}'
        )
        
        return ai_record
        
    except Exception as e:
        ai_record.status = 'failed'
        ai_record.error_message = str(e)
        ai_record.save()
        
        logger.error(f'AI审核任务失败: {str(e)}')
        raise
