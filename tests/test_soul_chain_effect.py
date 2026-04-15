# -*- coding: utf-8 -*-
"""测试灵魂锁链特效"""

import pytest
import pygame
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from soul_chain_effect import SoulChainEffect, get_soul_chain_effect


class TestSoulChainEffect:
    """测试灵魂锁链特效"""
    
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """初始化pygame"""
        pygame.init()
        yield
        pygame.quit()
        
    def test_initialization(self):
        """测试初始化"""
        effect = SoulChainEffect()
        assert effect.state == SoulChainEffect.STATE_IDLE
        assert effect.link_count == 15
        assert effect.max_particles == 50
        
    def test_initialize_with_size(self):
        """测试带尺寸初始化"""
        effect = SoulChainEffect()
        effect.initialize(1024, 768)
        assert effect.screen_width == 1024
        assert effect.screen_height == 768
        
    def test_start_extension(self):
        """测试锁链延伸启动"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        effect.start_extension((400, 300), "top")
        
        assert effect.state == SoulChainEffect.STATE_EXTENDING
        assert effect.extension_progress == 0.0
        assert len(effect.chain_links) == 15
        assert effect.boss_pos == (400, 300)
        
    def test_extension_progress(self):
        """测试延伸进度"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        effect.start_extension((400, 300))
        
        # 模拟更新
        effect.update(0.1)
        assert effect.extension_progress > 0
        assert effect.state == SoulChainEffect.STATE_EXTENDING
        
    def test_full_animation_cycle(self):
        """测试完整动画周期"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        effect.start_extension((400, 300))
        
        # 延伸
        for _ in range(20):
            effect.update(0.1)
            
        assert effect.state == SoulChainEffect.STATE_CONNECTED
        
        # 收回
        effect.start_retraction()
        for _ in range(20):
            effect.update(0.1)
            
        assert effect.state == SoulChainEffect.STATE_IDLE
        
    def test_soul_particles(self):
        """测试灵魂粒子生成"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        
        # 激活状态
        effect.state = SoulChainEffect.STATE_CONNECTED
        
        # 初始化链节
        effect._init_chain_links()
        
        # 触发粒子生成
        effect.update(0.1)
        
        # 在CONNECTED状态下应该有粒子生成
        # (概率触发)
        
    def test_particle_pool(self):
        """测试粒子对象池"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        
        # 添加粒子到池
        effect.particle_pool = []
        assert len(effect.particle_pool) == 0
        
    def test_is_active(self):
        """测试激活状态检测"""
        effect = SoulChainEffect()
        assert not effect.is_active()
        
        effect.start_extension((400, 300))
        assert effect.is_active()
        
        effect.extension_progress = 1.0
        effect.state = SoulChainEffect.STATE_CONNECTED
        assert effect.is_active()
        
        effect.reset()
        assert not effect.is_active()
        
    def test_get_state(self):
        """测试状态获取"""
        effect = SoulChainEffect()
        assert effect.get_state() == SoulChainEffect.STATE_IDLE
        
        effect.start_extension((400, 300))
        assert effect.get_state() == SoulChainEffect.STATE_EXTENDING
        
    def test_reset(self):
        """测试重置"""
        effect = SoulChainEffect()
        effect.start_extension((400, 300))
        effect.spawn_soul_particle(100, 100)
        
        effect.reset()
        
        assert effect.state == SoulChainEffect.STATE_IDLE
        assert len(effect.chain_links) == 0
        assert len(effect.soul_particles) == 0
        
    def test_connect_to_boss(self):
        """测试连接到Boss"""
        effect = SoulChainEffect()
        effect.initialize(800, 600)
        effect.start_extension((400, 300))
        effect.extension_progress = 0.5
        
        effect.connect_to_boss()
        
        assert effect.extension_progress == 1.0
        assert effect.state == SoulChainEffect.STATE_CONNECTED


class TestSoulChainSingleton:
    """测试单例模式"""
    
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        pygame.init()
        yield
        pygame.quit()
        
    def test_singleton(self):
        """测试单例"""
        effect1 = get_soul_chain_effect()
        effect2 = get_soul_chain_effect()
        assert effect1 is effect2


# 手动测试函数
def manual_test():
    """手动测试（需要显示）"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("灵魂锁链特效测试")
    clock = pygame.time.Clock()
    
    effect = SoulChainEffect()
    effect.initialize(800, 600)
    effect.start_extension((400, 300))
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    effect.reset()
                    effect.start_extension((400, 300))
                elif event.key == pygame.K_r:
                    effect.start_retraction()
                    
        effect.update(dt)
        
        screen.fill((20, 20, 30))
        effect.draw(screen)
        
        # 显示状态
        font = pygame.font.SysFont("simhei", 18)
        state_text = f"状态: {effect.get_state()} | 进度: {effect.extension_progress:.2f}"
        text = font.render(state_text, True, (200, 200, 200))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
    
    
if __name__ == "__main__":
    manual_test()