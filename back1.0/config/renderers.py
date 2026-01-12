# -*- coding: utf-8 -*-
"""自定义渲染器，确保 JSON 响应正确处理中文"""
from rest_framework.renderers import JSONRenderer
import json


class UTF8JSONRenderer(JSONRenderer):
    """UTF-8 JSON 渲染器，确保中文正确显示"""
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        渲染数据为 JSON，确保 ensure_ascii=False 以正确显示中文
        """
        if data is None:
            return b''
        
        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)
        
        if indent is None:
            separators = (',', ':')
        else:
            separators = (',', ': ')
        
        ret = json.dumps(
            data,
            cls=self.encoder_class,
            indent=indent,
            ensure_ascii=False,  # 关键：设置为 False 以正确显示中文
            allow_nan=not self.strict,
            separators=separators
        )
        
        # 在 Windows 上，确保返回字节
        if isinstance(ret, str):
            ret = ret.encode('utf-8')
        
        return ret

