# -*- coding: utf-8 -*-
"""自定义中间件，确保响应使用 UTF-8 编码"""
from django.utils.deprecation import MiddlewareMixin


class UTF8ResponseMiddleware(MiddlewareMixin):
    """确保所有 HTTP 响应使用 UTF-8 编码"""
    
    def process_response(self, request, response):
        """处理响应，设置正确的字符集"""
        if hasattr(response, 'charset') and response.charset != 'utf-8':
            response.charset = 'utf-8'
        elif not hasattr(response, 'charset'):
            response.charset = 'utf-8'
        
        # 确保 Content-Type 包含 charset
        content_type = response.get('Content-Type', '')
        if 'charset' not in content_type.lower():
            if 'text/html' in content_type or 'application/json' in content_type:
                if 'application/json' in content_type:
                    response['Content-Type'] = 'application/json; charset=utf-8'
                elif 'text/html' in content_type:
                    response['Content-Type'] = 'text/html; charset=utf-8'
        
        return response


