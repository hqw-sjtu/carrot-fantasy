"""
配置验证测试 - 确保游戏参数在合理范围内
Config Validation Tests - Ensure game parameters are within reasonable bounds
"""
import sys
sys.path.insert(0, 'src')
import json
import os


def load_config():
    """加载游戏配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_tower_configs():
    """验证防御塔配置"""
    config = load_config()
    towers = config.get('towers', {})
    
    for tower_id, tower_data in towers.items():
        # 检查必要字段
        assert 'name' in tower_data, f"{tower_id}: missing name"
        assert 'cost' in tower_data, f"{tower_id}: missing cost"
        assert 'damage' in tower_data, f"{tower_id}: missing damage"
        
        # 数值合理性检查
        assert tower_data['cost'] > 0, f"{tower_id}: cost must be positive"
        assert tower_data['damage'] > 0, f"{tower_id}: damage must be positive"
        assert tower_data.get('range', 0) > 0, f"{tower_id}: range must be positive"
        
        # 攻速合理性 (0.1 - 5.0 秒/次)
        attack_speed = tower_data.get('attack_speed', 1.0)
        assert 0.1 <= attack_speed <= 5.0, f"{tower_id}: attack_speed out of range"
        
        print(f"  ✅ {tower_id}: {tower_data['name']} (cost={tower_data['cost']})")


def test_monster_configs():
    """验证怪物配置"""
    config = load_config()
    monsters = config.get('monsters', {})
    
    for monster_id, monster_data in monsters.items():
        assert 'name' in monster_data, f"{monster_id}: missing name"
        assert 'health' in monster_data, f"{monster_id}: missing health"
        
        # 血量合理性
        assert monster_data['health'] > 0, f"{monster_id}: health must be positive"
        
        # 速度合理性 (0.5 - 5.0 像素/帧)
        speed = monster_data.get('speed', 1.0)
        assert 0.5 <= speed <= 5.0, f"{monster_id}: speed out of range"
        
        print(f"  ✅ {monster_id}: {monster_data['name']} (hp={monster_data['health']})")


def test_wave_configs():
    """验证波次配置"""
    config = load_config()
    waves = config.get('waves', {})
    
    for wave_id, wave_data in waves.items():
        assert 'monsters' in wave_data, f"{wave_id}: missing monsters"
        assert len(wave_data['monsters']) > 0, f"{wave_id}: empty monster list"
        
        print(f"  ✅ Wave {wave_id}: {len(wave_data['monsters'])} monster types")


def test_ui_configs():
    """验证UI配置"""
    config = load_config()
    ui = config.get('ui', {})
    
    # 窗口大小检查
    screen = config.get('screen', {})
    width = screen.get('width', 800)
    height = screen.get('height', 600)
    assert 400 <= width <= 3840, "width out of reasonable range"
    assert 300 <= height <= 2160, "height out of reasonable range"
    
    print(f"  ✅ Screen: {width}x{height}")
    print(f"  ✅ UI theme: {ui.get('theme', 'default')}")


def test_color_configs():
    """验证颜色配置"""
    config = load_config()
    colors = config.get('colors', {})
    
    for color_name, color_value in colors.items():
        # RGB格式
        if isinstance(color_value, list):
            assert len(color_value) == 3, f"{color_name}: invalid RGB"
            assert all(0 <= c <= 255 for c in color_value), f"{color_name}: color out of range"
    
    print(f"  ✅ {len(colors)} colors validated")


def main():
    print("🧪 Running Config Validation Tests...")
    print()
    
    print("📋 Testing Tower Configs:")
    test_tower_configs()
    print()
    
    print("👾 Testing Monster Configs:")
    test_monster_configs()
    print()
    
    print("🌊 Testing Wave Configs:")
    test_wave_configs()
    print()
    
    print("🖥️ Testing UI Configs:")
    test_ui_configs()
    print()
    
    print("🎨 Testing Color Configs:")
    test_color_configs()
    print()
    
    print("=" * 40)
    print("✅ All config validation tests PASSED!")
    print("=" * 40)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)