"""测试连击倍数特效"""
import pytest
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

import sys
sys.path.insert(0, 'src')
from combo_system import ComboMultiplierEffect


class TestComboMultiplierEffect:
    """连击倍数特效测试"""
    
    def test_combo_multiplier_init(self):
        effect = ComboMultiplierEffect(400, 300, 15)
        assert effect.combo_count == 15
        assert effect.life > 0
        assert effect.scale >= 1.0
    
    def test_combo_multiplier_update(self):
        effect = ComboMultiplierEffect(400, 300, 25)
        initial_y = effect.y
        result = effect.update(0.016)
        assert result is True
        assert effect.y < initial_y
    
    def test_combo_multiplier_expire(self):
        effect = ComboMultiplierEffect(400, 300, 10)
        for _ in range(100):
            if not effect.update(0.016):
                break
        assert effect.life <= 0
    
    def test_combo_multiplier_render_no_crash(self):
        effect = ComboMultiplierEffect(400, 300, 35)
        font = pygame.font.Font(None, 36)
        surface = pygame.Surface((800, 600))
        effect.render(surface, font)
        assert True
    
    def test_combo_multiplier_high_combo_colors(self):
        """高连击应有不同颜色"""
        effect_30 = ComboMultiplierEffect(400, 300, 30)
        effect_20 = ComboMultiplierEffect(400, 300, 20)
        effect_10 = ComboMultiplierEffect(400, 300, 10)
        
        assert effect_30.color == (255, 0, 100)
        assert effect_20.color == (255, 165, 0)
        assert effect_10.color == (255, 215, 0)