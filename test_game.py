#!/usr/bin/env python3
"""
测试保卫萝卜游戏
"""
import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 检查Pygame安装
try:
    import pygame
    print("✓ Pygame已安装")
except ImportError:
    print("✗ 需要安装Pygame: pip install pygame")
    sys.exit(1)

# 检查游戏文件
import importlib.util

def check_module(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False
    return True

# 检查所有模块
modules = ['towers', 'monsters', 'levels']
for module in modules:
    if check_module(f'src.{module}'):
        print(f"✓ {module} 模块存在")
    else:
        print(f"✗ {module} 模块不存在")

# 检查主程序
if os.path.exists('src/main.py'):
    print("✓ main.py 存在")
else:
    print("✗ main.py 不存在")

# 尝试运行游戏
print("\n正在启动游戏...")
try:
    exec(open('src/main.py').read())
    print("✓ 游戏启动成功")
except Exception as e:
    print(f"✗ 游戏启动失败: {e}")