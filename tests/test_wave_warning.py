"""
保卫萝卜 - 波次预警特效测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from base_effects import WaveWarningEffect


class TestWaveWarningEffect:
    """波次预警特效测试"""
    
    def test_wave_warning_init(self):
        """测试波次预警初始化"""
        path = [(100, 100), (200, 200), (300, 300)]
        effect = WaveWarningEffect(path, 5)
        assert effect.active is True
        assert effect.time_left == 5
        assert effect.max_time == 5
        assert effect.warning_color == (255, 100, 100)
        
    def test_wave_warning_update(self):
        """测试波次预警更新"""
        path = [(100, 100), (200, 200)]
        effect = WaveWarningEffect(path, 3)
        initial_time = effect.time_left
        
        effect.update(60)  # 1秒
        assert effect.time_left < initial_time
        assert effect.life > 0
        
    def test_wave_warning_intensity(self):
        """测试预警强度变化"""
        path = [(100, 100), (200, 200)]
        
        # 最后3秒应该高强度
        effect = WaveWarningEffect(path, 5)
        effect.life = 120  # 2秒后，还剩3秒
        effect.update(0)
        assert effect.warning_intensity == 1.0
        
        # 超过3秒应该低强度
        effect2 = WaveWarningEffect(path, 5)
        effect2.life = 60  # 1秒后，还剩4秒
        effect2.update(0)
        assert effect2.warning_intensity == 0.5
        
    def test_wave_warning_deactivate(self):
        """测试预警结束"""
        path = [(100, 100)]
        effect = WaveWarningEffect(path, 1)
        effect.life = 70  # 超过最大寿命
        effect.update(10)
        assert effect.active is False