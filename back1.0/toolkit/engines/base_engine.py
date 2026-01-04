import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseToolEngine(ABC):
    """工具引擎基类，所有具体工具实现都需要继承此类"""
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具功能
        
        Args:
            params: 工具参数
            
        Returns:
            Dict: 包含执行结果的字典，格式为 {"success": bool, "result": Any, "error": Optional[str]}
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证参数格式
        
        Args:
            params: 需要验证的参数
            
        Returns:
            Dict: 验证结果，格式为 {"valid": bool, "errors": List[str]}
        """
        # 默认实现，子类可以重写
        return {"valid": True, "errors": []}
    
    def format_result(self, result: Any) -> str:
        """
        格式化执行结果为字符串
        
        Args:
            result: 执行结果
            
        Returns:
            str: 格式化后的结果字符串
        """
        if isinstance(result, dict) or isinstance(result, list):
            return json.dumps(result, ensure_ascii=False, indent=2)
        return str(result)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        错误处理
        
        Args:
            error: 发生的异常
            
        Returns:
            Dict: 错误响应
        """
        return {
            "success": False,
            "result": None,
            "error": str(error)
        }
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取工具信息
        
        Returns:
            Dict: 工具信息
        """
        return {
            "name": self.__class__.__name__,
            "description": "基础工具引擎"
        }