# -*- coding: utf-8 -*-
"""测试新成就系统"""

import sys
sys.path.insert(0, 'src')

from achievement_system import AchievementManager


def test_new_achievements_exist():
    """测试新成就是否存在"""
    manager = AchievementManager()
    achievement_ids = [a.id for a in manager.achievements.values()]
    
    # 新增成就检查
    assert "slayer_1000" in achievement_ids, "缺少 slayer_1000 成就"
    assert "streak_10" in achievement_ids, "缺少 streak_10 成就"
    assert "streak_30" in achievement_ids, "缺少 streak_30 成就"
    assert "crit_10" in achievement_ids, "缺少 crit_10 成就"
    assert "crit_100" in achievement_ids, "缺少 crit_100 成就"
    assert "first_purchase" in achievement_ids, "缺少 first_purchase 成就"
    assert "shop_10" in achievement_ids, "缺少 shop_10 成就"
    
    print("✅ 新成就全部存在")


def test_new_stats():
    """测试新统计字段"""
    manager = AchievementManager()
    
    assert "max_kill_streak" in manager.stats, "缺少 max_kill_streak 统计"
    assert "total_crits" in manager.stats, "缺少 total_crits 统计"
    assert "items_purchased" in manager.stats, "缺少 items_purchased 统计"
    
    print("✅ 新统计字段全部存在")


def test_new_achievements_unlock():
    """测试新成就解锁条件"""
    manager = AchievementManager()
    
    # 测试连杀成就
    manager.update_stat("max_kill_streak", 15)
    unlocked = manager.get_new_unlocks()
    assert any(a.id == "streak_10" for a in manager.achievements.values() if a.unlocked), "streak_10 应该解锁"
    print("✅ 连杀成就可解锁")
    
    # 测试暴击成就 - 新建管理器避免状态干扰
    manager2 = AchievementManager()
    manager2.update_stat("total_crits", 15)
    assert any(a.id == "crit_10" for a in manager2.achievements.values() if a.unlocked), "crit_10 应该解锁"
    print("✅ 暴击成就可解锁")
    
    # 测试商店成就
    manager3 = AchievementManager()
    manager3.update_stat("items_purchased", 5)
    assert any(a.id == "first_purchase" for a in manager3.achievements.values() if a.unlocked), "first_purchase 应该解锁"
    print("✅ 商店成就可解锁")


if __name__ == "__main__":
    test_new_achievements_exist()
    test_new_stats()
    test_new_achievements_unlock()
    print("\n🎉 所有新成就测试通过!")