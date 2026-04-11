# -*- coding: utf-8 -*-
"""成就系统测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from achievement_system import Achievement, AchievementManager


class TestAchievement:
    """单个成就测试"""
    
    def test_achievement_init(self):
        """测试成就初始化"""
        ach = Achievement("test", "测试成就", "描述", "🏆", 100, lambda s: True)
        assert ach.id == "test"
        assert ach.name == "测试成就"
        assert not ach.unlocked
    
    def test_achievement_unlock(self):
        """测试成就解锁"""
        ach = Achievement("test", "测试", "描述", "🏆", 100, lambda s: True)
        assert ach.unlock()  # 第一次解锁成功
        assert not ach.unlock()  # 重复解锁失败


class TestAchievementManager:
    """成就管理器测试"""
    
    def test_manager_init(self):
        """测试管理器初始化"""
        mgr = AchievementManager(save_path="test_achievements.json")
        assert mgr.get_total_count() > 0
        # 清理
        if os.path.exists("test_achievements.json"):
            os.remove("test_achievements.json")
    
    def test_stat_update(self):
        """测试统计更新"""
        mgr = AchievementManager(save_path="test_achievements.json")
        mgr.increment_stat("monsters_killed")
        assert mgr.stats["monsters_killed"] == 1
        # 清理
        if os.path.exists("test_achievements.json"):
            os.remove("test_achievements.json")
    
    def test_achievement_unlock(self):
        """测试成就解锁"""
        mgr = AchievementManager(save_path="test_achievements.json")
        mgr.stats["monsters_killed"] = 10
        mgr._check_achievements()
        
        unlocked = [a.id for a in mgr.achievements.values() if a.unlocked]
        assert "first_blood" in unlocked
        assert "slayer_10" in unlocked
        # 清理
        if os.path.exists("test_achievements.json"):
            os.remove("test_achievements.json")
    
    def test_get_unlocked_count(self):
        """测试获取已解锁数量"""
        mgr = AchievementManager(save_path="test_achievements.json")
        count = mgr.get_unlocked_count()
        assert count >= 0
        assert count <= mgr.get_total_count()
        # 清理
        if os.path.exists("test_achievements.json"):
            os.remove("test_achievements.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])