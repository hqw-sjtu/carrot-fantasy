"""
保卫萝卜 - 连击系统测试
Carrot Fantasy - Combo System Tests
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
import unittest
from unittest.mock import Mock, patch
import time


class TestComboSystem(unittest.TestCase):
    """连击系统测试"""
    
    @classmethod
    def setUpClass(cls):
        """初始化pygame"""
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 600))
    
    def test_combo_creation(self):
        """测试连击创建"""
        from combo_system import ComboSystem
        system = ComboSystem()
        self.assertEqual(system.combo_count, 0)
        self.assertEqual(len(system.combos), 0)
    
    def test_add_kill(self):
        """测试添加击杀"""
        from combo_system import ComboSystem
        system = ComboSystem()
        
        # 第一次击杀
        system.add_kill(100, 100, False)
        self.assertEqual(system.combo_count, 1)
        
        # 第二次击杀（在连击时间内）
        time.sleep(0.1)
        system.add_kill(200, 200, False)
        self.assertEqual(system.combo_count, 2)
    
    def test_combo_timeout(self):
        """测试连击超时"""
        from combo_system import ComboSystem
        system = ComboSystem()
        
        system.add_kill(100, 100, False)
        self.assertEqual(system.combo_count, 1)
        
        # 等待超时
        time.sleep(system.combo_timeout + 0.1)
        system.update(0.1)
        
        # 连击应该过期
        self.assertEqual(system.combo_count, 0)
    
    def test_combo_bonus(self):
        """测试连击金币奖励"""
        from combo_system import ComboSystem
        system = ComboSystem()
        
        # 2连击无奖励
        system.combo_count = 2
        self.assertEqual(system._calculate_bonus(), 0)
        
        # 3连击有奖励
        system.combo_count = 3
        self.assertEqual(system._calculate_bonus(), 5)
        
        # 5连击
        system.combo_count = 5
        self.assertEqual(system._calculate_bonus(), 10)
        
        # 10连击
        system.combo_count = 10
        self.assertEqual(system._calculate_bonus(), 25)
    
    def test_combo_text_update(self):
        """测试连击文字更新"""
        from combo_system import ComboText
        text = ComboText(100, 100, 5, False)
        
        # 更新几次
        for _ in range(10):
            alive = text.update(0.1)
            if not alive:
                break
        
        self.assertLess(text.y, 100)  # 应该向上移动
    
    def test_get_combo_system_singleton(self):
        """测试单例模式"""
        from combo_system import get_combo_system
        system1 = get_combo_system()
        system2 = get_combo_system()
        self.assertIs(system1, system2)
    
    def test_combo_system_reset(self):
        """测试重置"""
        from combo_system import ComboSystem
        system = ComboSystem()
        
        system.add_kill(100, 100, False)
        system.add_kill(200, 200, False)
        self.assertGreater(system.combo_count, 0)
        
        system.reset()
        self.assertEqual(system.combo_count, 0)
        self.assertEqual(len(system.combos), 0)


class TestComboText(unittest.TestCase):
    """连击文字测试"""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 600))
    
    def test_combo_text_lifecycle(self):
        """测试连击文字生命周期"""
        from combo_system import ComboText
        text = ComboText(400, 300, 5, False)
        
        # 应该初始存活
        self.assertTrue(text.life > 0)
        
        # 更新直到死亡
        for _ in range(20):
            if not text.update(0.1):
                break
        
        # 应该死亡
        self.assertLessEqual(text.life, 0)
    
    def test_critical_combo_colors(self):
        """测试暴击连击颜色"""
        from combo_system import ComboText
        normal = ComboText(100, 100, 3, False)
        critical = ComboText(100, 100, 3, True)
        
        # 暴击应该有不同颜色
        self.assertNotEqual(normal.base_color, critical.base_color)
        self.assertEqual(critical.base_color, (255, 100, 0))  # 橙色


if __name__ == '__main__':
    unittest.main(verbosity=2)