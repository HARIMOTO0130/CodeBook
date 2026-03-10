# 修复views.py文件中的execute方法
import os

# 读取修复后的execute方法
with open('execute_fixed.py', 'r', encoding='utf-8') as f:
    fixed_execute_method = f.read()

# 读取原始views.py文件
views_path = 'apps/learning/views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到需要替换的部分：从@action(detail=False, methods=['post']开始，到return Response({结束
start_pattern = "@action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])"
end_pattern = "    return Response({"

# 找到起始位置
start_idx = content.find(start_pattern)
if start_idx == -1:
    print("未找到execute方法的起始位置")
    exit(1)

# 找到结束位置（需要包含完整的return Response块）
end_idx = content.find(end_pattern, start_idx)
if end_idx == -1:
    print("未找到execute方法的结束位置")
    exit(1)

# 找到return Response块的结束位置（闭合的})）
brace_count = 1
current_idx = end_idx + len(end_pattern)
while brace_count > 0 and current_idx < len(content):
    if content[current_idx] == '{':
        brace_count += 1
    elif content[current_idx] == '}':
        brace_count -= 1
    current_idx += 1

# 构建新的内容
new_content = content[:start_idx] + fixed_execute_method + content[current_idx:]

# 写入修复后的文件
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("文件修复成功！")