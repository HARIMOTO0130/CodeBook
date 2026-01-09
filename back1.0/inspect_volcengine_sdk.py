#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查Volcengine SDK的可用属性
"""

import os
import sys

# 设置环境变量
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 检查volcenginesdkark模块
print("检查volcenginesdkark模块...")
try:
    import volcenginesdkark
    print(f"volcenginesdkark版本: {volcenginesdkark.__version__}")
    print(f"volcenginesdkark可用属性: {dir(volcenginesdkark)}")
    
    # 检查子模块
    print(f"\nvolcenginesdkark的子模块: {[attr for attr in dir(volcenginesdkark) if not attr.startswith('_')]}")
    
except Exception as e:
    print(f"导入volcenginesdkark失败: {e}")

# 检查volcenginesdkcore模块
print("\n" + "=" * 50)
print("检查volcenginesdkcore模块...")
try:
    import volcenginesdkcore
    print(f"volcenginesdkcore版本: {getattr(volcenginesdkcore, '__version__', '未知')}")
    print(f"volcenginesdkcore可用属性: {dir(volcenginesdkcore)}")
except Exception as e:
    print(f"导入volcenginesdkcore失败: {e}")

# 检查是否有其他相关模块
print("\n" + "=" * 50)
print("检查其他相关模块...")
try:
    import pkgutil
    print("Volcengine SDK相关模块:")
    for importer, modname, ispkg in pkgutil.iter_modules():
        if modname.startswith('volcengine'):
            print(f"  - {modname}")
except Exception as e:
    print(f"检查模块失败: {e}")
