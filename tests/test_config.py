"""配置系统测试 - 确保配置文件完整性"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_loads():
    """测试配置加载"""
    import json
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 验证必需字段
    required = ['levels', 'towers', 'monsters', 'waves', 'visual_effects', 'gameplay']
    for field in required:
        assert field in config, f"Missing required field: {field}"
    
    # 验证视觉效果配置
    ve = config['visual_effects']
    assert 'screen_shake' in ve
    assert 'particle_system' in ve
    assert ve['screen_shake']['enabled'] == True
    
    # 验证游戏玩法配置
    gp = config['gameplay']
    assert gp['auto_save'] == True
    assert gp['combo_multiplier_cap'] >= 1.0
    
    # 验证塔配置
    towers = config['towers']
    for name, tower in towers.items():
        assert 'damage' in tower, f"{name} missing damage"
        assert 'range' in tower, f"{name} missing range"
    
    print("✅ 配置加载测试通过")
    

if __name__ == '__main__':
    test_config_loads()