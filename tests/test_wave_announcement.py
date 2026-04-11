"""波次公告特效测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None

from extra_effects import WaveAnnouncementEffect


class TestWaveAnnouncementEffect:
    """波次公告特效测试"""
    
    def test_wave_announcement_init(self):
        """测试波次公告初始化"""
        effect = WaveAnnouncementEffect(800, 600, 3)
        assert effect.wave_number == 3
        assert effect.max_life == 2.0
        assert effect.active == True
        assert effect.text_zoom == 0.0
        
    def test_wave_announcement_update(self):
        """测试波次公告更新"""
        effect = WaveAnnouncementEffect(800, 600, 1)
        
        # 初始状态
        assert effect.life == 0
        assert effect.text_zoom == 0.0
        
        # 0.15秒后 - 放大阶段
        effect.update(0.15)
        assert 0 < effect.text_zoom <= 0.5
        assert effect.active == True
        
        # 0.5秒后 - 保持阶段
        effect.update(0.35)
        assert effect.text_zoom == 1.0
        
    def test_wave_announcement_expire(self):
        """测试波次公告过期"""
        effect = WaveAnnouncementEffect(800, 600, 1)
        effect.update(2.5)  # 超过最大生命周期
        assert effect.active == False
        
    def test_wave_announcement_lifecycle(self):
        """测试波次公告完整生命周期"""
        effect = WaveAnnouncementEffect(800, 600, 5)
        
        # 阶段1: 放大
        effect.update(0.2)
        assert effect.text_zoom > 0
        
        # 阶段2: 保持
        effect.update(1.0)
        assert effect.text_zoom == 1.0
        
        # 阶段3: 淡出
        effect.update(0.6)
        assert effect.text_zoom < 1.0
        
        # 阶段4: 结束
        effect.update(0.5)
        assert effect.active == False