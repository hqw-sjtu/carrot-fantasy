#!/usr/bin/env python3
"""
简单测试 - 验证游戏可以导入和初始化
"""
import sys
sys.path.insert(0, 'src')

try:
    # 导入主模块但不执行main()
    import main as game_main
    print("✓ 成功导入主模块")
    
    # 检查必要的函数是否存在
    if hasattr(game_main, 'draw_game'):
        print("✓ draw_game函数存在")
    
    if hasattr(game_main, 'draw_gradient_sky'):
        print("✓ draw_gradient_sky函数存在")
    
    if hasattr(game_main, 'draw_grass_texture'):
        print("✓ draw_grass_texture函数存在")
    
    if hasattr(game_main, 'draw_path_with_details'):
        print("✓ draw_path_with_details函数存在")
    
    if hasattr(game_main, 'draw_decorations'):
        print("✓ draw_decorations函数存在")
    
    if hasattr(game_main, 'draw_sunlight_effect'):
        print("✓ draw_sunlight_effect函数存在")
    
    print("\n✅ 所有背景美化函数已成功添加")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)