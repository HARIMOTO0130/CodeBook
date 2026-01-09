#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查volcenginesdkark和volcenginesdkarkruntime模块的具体内容
"""

print("检查volcenginesdkark模块...")
try:
    import volcenginesdkark
    print(f"volcenginesdkark可用属性: {dir(volcenginesdkark)}")
    
    # 检查是否有子模块
    print("\nvolcenginesdkark子模块:")
    for attr in dir(volcenginesdkark):
        if not attr.startswith('_'):
            try:
                attr_value = getattr(volcenginesdkark, attr)
                print(f"  - {attr}: {type(attr_value)}")
                if hasattr(attr_value, '__dir__'):
                    print(f"    可用方法/属性: {[a for a in dir(attr_value) if not a.startswith('_')][:10]}")
            except Exception as e:
                print(f"    无法检查: {e}")
                
except Exception as e:
    print(f"导入volcenginesdkark失败: {e}")

print("\n" + "=" * 60)
print("检查volcenginesdkarkruntime模块...")
try:
    import volcenginesdkarkruntime
    print(f"volcenginesdkarkruntime可用属性: {dir(volcenginesdkarkruntime)}")
    
    # 检查是否有子模块
    print("\nvolcenginesdkarkruntime子模块:")
    for attr in dir(volcenginesdkarkruntime):
        if not attr.startswith('_'):
            try:
                attr_value = getattr(volcenginesdkarkruntime, attr)
                print(f"  - {attr}: {type(attr_value)}")
                if hasattr(attr_value, '__dir__'):
                    print(f"    可用方法/属性: {[a for a in dir(attr_value) if not a.startswith('_')][:10]}")
            except Exception as e:
                print(f"    无法检查: {e}")
                
except Exception as e:
    print(f"导入volcenginesdkarkruntime失败: {e}")

# 检查volcenginesdkark的具体API结构
print("\n" + "=" * 60)
print("检查volcenginesdkark的API结构...")
try:
    import volcenginesdkark
    from volcenginesdkcore import Configuration, ApiClient
    
    # 尝试创建配置和API客户端
    config = Configuration()
    config.ak = "test_ak"
    config.sk = "test_sk"
    config.region = "cn-beijing"
    
    api_client = ApiClient(config)
    print(f"成功创建ApiClient: {api_client}")
    
    # 检查volcenginesdkark的API类
    print("\nvolcenginesdkark中的API类:")
    for attr in dir(volcenginesdkark):
        if attr.endswith('Api'):
            print(f"  - {attr}")
            try:
                api_class = getattr(volcenginesdkark, attr)
                api_instance = api_class(api_client)
                print(f"    成功创建实例: {api_instance}")
                print(f"    可用方法: {[m for m in dir(api_instance) if not m.startswith('_') and callable(getattr(api_instance, m))]}")
            except Exception as e:
                print(f"    创建实例失败: {e}")
                
    # 检查是否有Chat相关的API
    print("\n查找Chat相关API:")
    for attr in dir(volcenginesdkark):
        if 'chat' in attr.lower():
            print(f"  - {attr}")
    
except Exception as e:
    print(f"检查失败: {e}")
    import traceback
    traceback.print_exc()
