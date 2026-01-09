#!/usr/bin/env python3
from apps.toolkit.models import Tool

# 获取工具ID为4的工具信息
tool = Tool.objects.get(id=4)
print(f'Tool ID: {tool.id}')
print(f'Name: {tool.name}')
print(f'Implementation Class: {tool.implementation_class}')
print(f'Parameters: {list(tool.parameters.all().values_list("name", flat=True))}')
