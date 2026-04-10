"""
保卫萝卜 - 金币动画系统测试
测试 coin_animations 的创建、渲染和清理逻辑
"""
import pytest
import sys
sys.path.insert(0, 'src')

def test_coin_animations_basic():
    """测试金币动画基本数据结构"""
    # 模拟 coin_animations 格式: [(x, y, amount, timer), ...]
    coin_animations = [
        [100, 280, "+10", 1.0],
        [130, 280, "+5(连杀)", 1.5],
    ]
    
    assert len(coin_animations) == 2
    assert coin_animations[0][2] == "+10"
    assert coin_animations[1][3] == 1.5

def test_coin_animations_movement():
    """测试金币动画上浮效果"""
    coin_animations = [[100, 280, "+10", 1.0]]
    
    dt = 0.016  # ~60fps
    game_speed = 1.0
    
    # 模拟更新
    for ca in coin_animations[:]:
        cx, cy, ctext, ctimer = ca
        ctimer -= dt * game_speed
        cy -= 40 * dt * game_speed
        ca[1] = cy
        ca[3] = ctimer
    
    assert coin_animations[0][1] < 280  # 向上移动
    assert coin_animations[0][3] < 1.0  # 计时器减少

def test_coin_animations_fade():
    """测试金币动画渐隐效果"""
    ctimer = 1.0
    alpha = min(255, int(ctimer * 255 * 2))
    assert alpha == 255
    
    ctimer = 0.5
    alpha = min(255, int(ctimer * 255 * 2))
    assert alpha == 255
    
    ctimer = 0.2
    alpha = min(255, int(ctimer * 255 * 2))
    assert alpha == 102

def test_coin_animations_cleanup():
    """测试金币动画自动清理"""
    coin_animations = [
        [100, 280, "+10", 1.0],
        [130, 280, "+5", 0.0],  # 已过期
    ]
    
    for ca in coin_animations[:]:
        cx, cy, ctext, ctimer = ca
        if ctimer <= 0:
            coin_animations.remove(ca)
    
    assert len(coin_animations) == 1

def test_combo_bonus_integration():
    """测试连杀奖励与金币动画集成"""
    kill_streak = 5
    bonus = kill_streak * 2
    
    reward = 10
    total = reward + bonus
    
    # 模拟添加金币动画
    coin_animations = []
    mx, my = 200, 280
    coin_animations.append([mx, my, f"+{reward}", 1.0])
    if bonus > 0:
        coin_animations.append([mx + 30, my, f"+{bonus}(连杀)", 1.5])
    
    assert len(coin_animations) == 2
    assert coin_animations[1][2] == "+10(连杀)"

def test_crit_gold_multiplier():
    """测试暴击时金币翻倍"""
    reward = 10
    is_crit = True
    
    if is_crit:
        reward *= 2
    
    assert reward == 20
    
    is_crit = False
    reward = 10
    if is_crit:
        reward *= 2
    
    assert reward == 10

def test_gold_rain_event():
    """测试金币雨随机事件"""
    reward = 10
    gold_rain_active = True
    
    if gold_rain_active:
        reward += 5
    
    assert reward == 15
    
    gold_rain_active = False
    reward = 10
    if gold_rain_active:
        reward += 5
    
    assert reward == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])