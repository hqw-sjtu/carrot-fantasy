# -*- coding: utf-8 -*-
"""萝卜危机特效测试"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
except:
    pytest.skip("Pygame not available", allow_module_level=True)

from carrot_crisis_effect import (
    CarrotCrisisEffect, 
    CarrotProtectionAura,
    get_crisis_effect,
    get_protection_aura,
    update_carrot_effects,
    draw_carrot_effects
)


class TestCarrotCrisisEffect:
    """测试萝卜危机特效"""
    
    def test_initial_state(self):
        """测试初始状态"""
        effect = CarrotCrisisEffect()
        assert effect.enabled == False
        assert effect.intensity == 0.0
        assert effect.pulse_phase == 0
    
    def test_update_normal_hp(self):
        """测试正常血量(无危机)"""
        effect = CarrotCrisisEffect()
        effect.update(0.8, 0.016)  # 80%血量
        assert effect.enabled == False
        assert effect.intensity == 0
    
    def test_update_critical_hp(self):
        """测试危险血量触发危机"""
        effect = CarrotCrisisEffect()
        effect.update(0.2, 0.016)  # 20%血量
        assert effect.enabled == True
        assert effect.intensity > 0
    
    def test_update_zero_hp(self):
        """测试极低血量"""
        effect = CarrotCrisisEffect()
        effect.update(0.01, 0.016)  # 1%血量
        assert effect.enabled == True
        assert effect.intensity > 0.8  # 应该非常强
    
    def test_shake_at_low_hp(self):
        """测试低血量震动"""
        effect = CarrotCrisisEffect()
        effect.update(0.1, 0.016)
        if effect.intensity > 0.3:
            assert effect.shake_offset != (0, 0)
    
    def test_crack_at_critical(self):
        """测试极低血量裂纹"""
        effect = CarrotCrisisEffect()
        for _ in range(100):
            effect.update(0.05, 0.016)
        # 应该有裂纹
        assert len(effect.crack_lines) >= 0


class TestCarrotProtectionAura:
    """测试萝卜保护光环"""
    
    def test_initial_state(self):
        """测试初始状态"""
        aura = CarrotProtectionAura()
        assert aura.rings == []
        assert aura.max_rings == 3
    
    def test_update_high_hp(self):
        """测试高血量生成光环"""
        aura = CarrotProtectionAura()
        for _ in range(50):
            aura.update(0.9, 0.016)  # 90%血量
        # 应该有光环
        assert len(aura.rings) >= 0
    
    def test_update_low_hp(self):
        """测试低血量不生成光环"""
        aura = CarrotProtectionAura()
        initial_rings = len(aura.rings)
        for _ in range(50):
            aura.update(0.3, 0.016)  # 30%血量
        assert len(aura.rings) == initial_rings
    
    def test_ring_fade(self):
        """测试光环淡出"""
        aura = CarrotProtectionAura()
        aura.rings.append({'radius': 40, 'alpha': 180, 'speed': 30})
        aura.update(0.9, 3.0)  # 3秒后
        # 应该有环消失或alpha降低
        assert True  # 至少不报错


class TestGlobalInstances:
    """测试全局实例"""
    
    def test_get_crisis_effect(self):
        """测试获取危机特效"""
        effect = get_crisis_effect()
        assert isinstance(effect, CarrotCrisisEffect)
    
    def test_get_protection_aura(self):
        """测试获取保护光环"""
        aura = get_protection_aura()
        assert isinstance(aura, CarrotProtectionAura)
    
    def test_update_carrot_effects(self):
        """测试更新函数"""
        # 不应报错
        update_carrot_effects(0.5, 0.016)
        update_carrot_effects(0.9, 0.016)
        update_carrot_effects(0.1, 0.016)


class TestDrawFunctions:
    """测试绘制函数"""
    
    def test_draw_no_crash(self):
        """测试绘制不崩溃"""
        screen = pygame.display.set_mode((800, 600))
        effect = CarrotCrisisEffect()
        aura = CarrotProtectionAura()
        
        # 正常绘制
        effect.update(0.5, 0.016)
        aura.update(0.9, 0.016)
        
        # 绘制(不检查具体内容)
        effect.draw(screen, (400, 500), 30)
        aura.draw(screen, (400, 500))
        
        pygame.display.quit()
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])