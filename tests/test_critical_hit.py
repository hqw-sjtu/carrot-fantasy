"""
保卫萝卜 - 暴击与连击系统测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import pytest

# 初始化pygame（无显示模式）
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))


class TestCriticalHitSystem:
    """暴击系统测试"""
    
    def test_critical_hit_creation(self):
        """测试暴击创建"""
        from critical_hit_system import CriticalHit, add_critical_hit
        hit = CriticalHit(100, 100, 50, is_crit=True)
        assert hit.damage == 50
        assert hit.is_crit == True
        assert hit.life > 0
    
    def test_critical_hit_update(self):
        """测试暴击更新"""
        from critical_hit_system import CriticalHit
        hit = CriticalHit(100, 100, 30, is_crit=False)
        initial_y = hit.y
        hit.update(0.1)
        assert hit.y < initial_y  # 向上飘
        assert hit.life < 1.0
    
    def test_critical_hit_death(self):
        """测试暴击消失"""
        from critical_hit_system import CriticalHit
        hit = CriticalHit(100, 100, 30)
        for _ in range(20):
            alive = hit.update(0.1)
        assert alive == False
    
    def test_crit_vs_normal(self):
        """测试暴击vs普通伤害"""
        from critical_hit_system import CriticalHit
        crit = CriticalHit(100, 100, 100, is_crit=True)
        normal = CriticalHit(100, 100, 100, is_crit=False)
        assert crit.scale > normal.scale
        assert crit.font_size > normal.font_size
        assert len(crit.stars) > 0  # 暴击有星星


class TestComboText:
    """连击文字测试"""
    
    def test_combo_creation(self):
        """测试连击创建"""
        from critical_hit_system import ComboText
        combo = ComboText(100, 100, 5)
        assert combo.combo_count == 5
        assert combo.life > 0
    
    def test_combo_colors(self):
        """测试连击颜色"""
        from critical_hit_system import ComboText
        small = ComboText(100, 100, 2)
        medium = ComboText(100, 100, 5)
        large = ComboText(100, 100, 10)
        assert small.color != large.color  # 不同级别不同颜色
    
    def test_combo_update(self):
        """测试连击更新"""
        from critical_hit_system import ComboText
        combo = ComboText(100, 100, 3)
        initial_scale = combo.scale
        combo.update(0.1)
        assert combo.scale > initial_scale  # 逐渐变大


class TestUpgradeBurst:
    """升级爆发测试"""
    
    def test_burst_creation(self):
        """测试爆发创建"""
        from critical_hit_system import UpgradeBurst
        burst = UpgradeBurst(100, 100, 2)
        assert burst.level == 2
        assert len(burst.rings) == 3
        assert len(burst.particles) == 12
    
    def test_burst_update(self):
        """测试爆发更新"""
        from critical_hit_system import UpgradeBurst
        burst = UpgradeBurst(100, 100, 1)
        initial_radius = burst.rings[0]['radius']
        burst.update(0.1)
        assert burst.rings[0]['radius'] > initial_radius


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_add_critical_hit(self):
        """测试添加暴击"""
        from critical_hit_system import add_critical_hit, critical_hits
        initial_count = len(critical_hits)
        add_critical_hit(100, 100, 50, True)
        assert len(critical_hits) == initial_count + 1
    
    def test_add_combo_text(self):
        """测试添加连击"""
        from critical_hit_system import add_combo_text, combo_texts
        initial_count = len(combo_texts)
        add_combo_text(100, 100, 5)
        assert len(combo_texts) == initial_count + 1
    
    def test_update_effects(self):
        """测试更新所有效果"""
        from critical_hit_system import (
            add_critical_hit, add_combo_text, add_upgrade_burst,
            critical_hits, combo_texts, upgrade_bursts, update_effects
        )
        # 添加一些效果
        add_critical_hit(100, 100, 50)
        add_combo_text(100, 100, 3)
        add_upgrade_burst(100, 100, 1)
        
        # 更新
        update_effects(0.05)
        
        # 效果应该还存在但生命周期减少
        assert True  # 没有崩溃
    
    def test_draw_effects(self):
        """测试绘制效果"""
        from critical_hit_system import (
            add_critical_hit, draw_effects
        )
        add_critical_hit(100, 100, 50)
        # 不报错即通过
        SCREEN = pygame.display.get_surface()
        draw_effects(SCREEN)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])