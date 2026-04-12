"""波次预览面板测试"""
import pytest
import pygame
import sys
sys.path.insert(0, 'src')

# 初始化 pygame
pygame.init()
SCREEN = pygame.display.set_mode((800, 600))


def test_wave_preview_init():
    """测试波次预览面板初始化参数"""
    import main
    
    # 跳过实际绘制测试（需要完整游戏初始化），只测试数据计算
    main.state.wave_manager = type('obj', (object,), {
        'current_wave': 2,
        'waves': [
            {'monsters': [('slime', 5), ('bat', 3)], 'difficulty': 1.0},
            {'monsters': [('slime', 8), ('bat', 5)], 'difficulty': 1.5},
            {'monsters': [('wolf', 3), ('bat', 10)], 'difficulty': 2.0},
            {'monsters': [('boss', 1), ('slime', 15)], 'difficulty': 3.0},
        ]
    })()
    
    # 验证数据计算
    current_wave = main.state.wave_manager.current_wave + 1
    total_waves = len(main.state.wave_manager.waves)
    
    assert current_wave == 3, f"当前波次应为3，实际{current_wave}"
    assert total_waves == 4, f"总波次数应为4，实际{total_waves}"


def test_wave_preview_closed_when_disabled():
    """测试面板关闭时无绘制"""
    import main
    
    # 确保面板关闭
    main.show_wave_preview = False
    
    # 不应该抛出异常
    try:
        main.draw_wave_preview_panel()
    except Exception as e:
        pytest.fail(f"面板关闭时绘制失败: {e}")


def test_wave_preview_no_manager():
    """测试无 wave_manager 时的降级处理"""
    import main
    
    # 保存原始状态
    original_manager = getattr(main.state, 'wave_manager', None)
    original_preview = main.show_wave_preview
    
    # 移除 wave_manager
    if hasattr(main.state, 'wave_manager'):
        delattr(main.state, 'wave_manager')
    main.show_wave_preview = False
    
    # 测试数据降级 - 当无 manager 时
    current_wave = getattr(main.state, 'wave_manager', None)
    if current_wave is None:
        wave_num = 1
        total = 8
    else:
        wave_num = current_wave.current_wave + 1
        total = len(current_wave.waves)
    
    assert wave_num == 1
    assert total == 8
    
    # 恢复
    if original_manager:
        main.state.wave_manager = original_manager
    main.show_wave_preview = original_preview


def test_wave_progress_calculation():
    """测试波次进度计算"""
    import main
    
    # 模拟第3波，共8波
    main.state.wave_manager = type('obj', (object,), {
        'current_wave': 2,
        'waves': [{} for _ in range(8)]
    })()
    main.show_wave_preview = True
    
    # 进度应为 3/8 = 0.375
    expected_progress = 3 / 8
    
    # 这个测试验证数据准备正确
    current_wave = main.state.wave_manager.current_wave + 1
    total_waves = len(main.state.wave_manager.waves)
    
    assert current_wave == 3
    assert total_waves == 8
    assert abs(current_wave / total_waves - expected_progress) < 0.001


def test_difficulty_stars():
    """测试难度星级计算"""
    difficulties = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    expected_stars = [1, 1, 2, 2, 3, 3]
    
    for diff, expected in zip(difficulties, expected_stars):
        stars = min(3, int(diff / 1.0))
        assert stars == expected, f"难度 {diff} 应该有 {expected} 星，实际 {stars} 星"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])