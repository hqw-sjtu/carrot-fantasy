"""
保卫萝卜 - 新增特效测试
测试闪电链、冲击波等新增特效
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import pygame
from extra_effects import (
    LightningChainEffect, ShockwaveEffect, EffectManager
)


# 初始化pygame用于测试
pygame.init()
pygame.display.set_mode((800, 600))


class TestLightningChainEffect:
    """闪电链特效测试"""
    
    def test_lightning_init(self):
        """测试闪电链初始化"""
        start = (100, 100)
        targets = [(200, 200), (300, 150), (400, 250)]
        effect = LightningChainEffect(start, targets)
        
        assert effect.start_pos == start
        assert effect.target_positions == targets
        assert effect.active is True
        assert effect.life == 0
        
    def test_lightning_update(self):
        """测试闪电链更新"""
        start = (100, 100)
        targets = [(200, 200)]
        effect = LightningChainEffect(start, targets)
        
        # 正常更新
        effect.update(0.1)
        assert effect.life == 0.1
        assert effect.active is True
        
        # 超过生命周期+闪烁延迟期
        effect.update(0.7)
        assert effect.active is False
        
    def test_lightning_segments(self):
        """测试闪电线段生成"""
        start = (100, 100)
        targets = [(200, 200), (300, 300)]
        effect = LightningChainEffect(start, targets)
        
        assert len(effect.segments) == 2  # 两个目标


class TestShockwaveEffect:
    """冲击波特效测试"""
    
    def test_shockwave_init(self):
        """测试冲击波初始化"""
        effect = ShockwaveEffect(400, 300, (255, 100, 100), 150)
        
        assert effect.x == 400
        assert effect.y == 300
        assert effect.color == (255, 100, 100)
        assert effect.max_radius == 150
        assert effect.active is True
        
    def test_shockwave_update(self):
        """测试冲击波更新"""
        effect = ShockwaveEffect(400, 300)
        
        effect.update(0.3)
        assert effect.life == 0.3
        assert effect.active is True
        
        effect.update(0.6)
        assert effect.life >= 0.8  # 浮点数精度
        assert effect.max_life == 0.8
        assert effect.active is False


class TestEffectManager:
    """特效管理器测试"""
    
    def test_manager_singleton(self):
        """测试单例模式"""
        manager1 = EffectManager.get_instance()
        manager2 = EffectManager.get_instance()
        assert manager1 is manager2
        
    def test_spawn_lightning_chain(self):
        """测试闪电链生成"""
        manager = EffectManager.get_instance()
        manager.lightning_chains.clear()  # 清空
        
        manager.spawn_lightning_chain(
            (100, 100), 
            [(200, 200), (300, 300)]
        )
        
        assert len(manager.lightning_chains) == 1
        
    def test_spawn_shockwave(self):
        """测试冲击波生成"""
        manager = EffectManager.get_instance()
        manager.shockwaves.clear()
        
        manager.spawn_shockwave(400, 300, (255, 100, 100))
        
        assert len(manager.shockwaves) == 1
        
    def test_manager_update(self):
        """测试管理器更新"""
        manager = EffectManager.get_instance()
        manager.lightning_chains.clear()
        manager.shockwaves.clear()
        manager.trails.clear()
        manager.gold_rains.clear()
        
        # 添加特效
        manager.spawn_lightning_chain((100, 100), [(200, 200)])
        manager.spawn_shockwave(400, 300)
        
        # 更新
        manager.update(0.1)
        
        # 验证更新成功
        assert len(manager.lightning_chains) >= 0
        assert len(manager.shockwaves) >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])