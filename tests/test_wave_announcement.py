"""
测试波次公告系统
"""
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_wave_announcement_init():
    """测试波次公告初始化"""
    from wave_announcement import WaveAnnouncement
    
    monsters_info = ["小怪物", "中怪物", "大怪物"]
    announcement = WaveAnnouncement(1, 10, monsters_info)
    
    assert announcement.wave_num == 1
    assert announcement.total_waves == 10
    assert announcement.monsters_info == monsters_info
    assert announcement.active == True
    assert announcement.lifetime == 2.5
    assert announcement.alpha == 255
    
    print("✅ test_wave_announcement_init PASSED")


def test_wave_announcement_update():
    """测试波次公告更新"""
    from wave_announcement import WaveAnnouncement
    
    announcement = WaveAnnouncement(1, 10, ["小怪物"])
    
    # 正常更新
    announcement.update(0.1)
    assert announcement.timer == 0.1
    assert announcement.active == True
    
    # 更新到结束
    announcement.timer = 3.0
    announcement.update(0.1)
    assert announcement.active == False
    
    print("✅ test_wave_announcement_update PASSED")


def test_announcement_manager():
    """测试公告管理器"""
    from wave_announcement import WaveAnnouncementManager
    
    manager = WaveAnnouncementManager()
    
    # 添加公告
    manager.add_announcement(1, 10, ["小怪物", "中怪物"])
    assert len(manager.announcements) == 1
    
    # 更新
    manager.update(0.1)
    assert len(manager.announcements) == 1
    
    # 清理已结束的公告
    manager.announcements[0].timer = 3.0
    manager.update(0.1)
    assert len(manager.announcements) == 0
    
    # 检查has_active
    assert manager.has_active() == False
    
    manager.add_announcement(1, 10, ["Boss"])
    assert manager.has_active() == True
    
    print("✅ test_announcement_manager PASSED")


def test_scale_animation():
    """测试缩放动画"""
    from wave_announcement import WaveAnnouncement
    
    announcement = WaveAnnouncement(1, 10, ["小怪物"])
    
    # 初始缩放为0
    assert announcement.scale == 0.0
    
    # 更新后缩放增加
    announcement.update(0.1)
    assert announcement.scale > 0.0
    
    # 缩放不能超过目标值
    announcement.scale = 1.0
    announcement.update(1.0)
    assert announcement.scale <= announcement.target_scale
    
    print("✅ test_scale_animation PASSED")


def test_fade_effect():
    """测试淡出效果"""
    from wave_announcement import WaveAnnouncement
    
    announcement = WaveAnnouncement(1, 10, ["小怪物"])
    
    # 初始透明度255
    assert announcement.alpha == 255
    
    # 未到淡出时间前不变
    announcement.timer = 1.0
    announcement.update(0.1)
    assert announcement.alpha == 255
    
    # 到达淡出时间后渐变
    announcement.timer = 2.0
    announcement.update(0.1)
    assert announcement.alpha < 255
    
    print("✅ test_fade_effect PASSED")


if __name__ == "__main__":
    print("Running Wave Announcement Tests...")
    print("=" * 50)
    
    test_wave_announcement_init()
    test_wave_announcement_update()
    test_announcement_manager()
    test_scale_animation()
    test_fade_effect()
    
    print("=" * 50)
    print("🎉 All Wave Announcement Tests Passed!")