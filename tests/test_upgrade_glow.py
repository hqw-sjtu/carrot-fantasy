"""升级光辉特效测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import pygame


class TestTowerUpgradeGlow(unittest.TestCase):
    
    def setUp(self):
        """每个测试前重新初始化pygame"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def tearDown(self):
        """每个测试后清理"""
        pygame.quit()
    
    def test_glow_creation(self):
        from tower_upgrade_glow import TowerUpgradeGlow
        glow = TowerUpgradeGlow(400, 300, 3)
        self.assertEqual(glow.x, 400)
        self.assertEqual(glow.y, 300)
        self.assertEqual(glow.level, 3)
        self.assertIsNotNone(glow.particles)
        self.assertGreater(len(glow.particles), 0)
    
    def test_glow_update(self):
        from tower_upgrade_glow import TowerUpgradeGlow
        glow = TowerUpgradeGlow(400, 300, 2)
        initial_count = len(glow.particles)
        
        # 模拟更新
        for _ in range(10):
            glow.update(0.016)
        
        # 粒子应该有减少
        self.assertLessEqual(len(glow.particles), initial_count)
    
    def test_glow_manager(self):
        from tower_upgrade_glow import UpgradeGlowManager
        manager = UpgradeGlowManager()
        
        manager.spawn(100, 100, 1)
        manager.spawn(200, 200, 2)
        
        self.assertEqual(len(manager.effects), 2)
        
        # 更新并绘制（不报错）
        manager.update(0.016)
        manager.draw(self.screen)
        
        manager.clear()
        self.assertEqual(len(manager.effects), 0)


if __name__ == '__main__':
    unittest.main()