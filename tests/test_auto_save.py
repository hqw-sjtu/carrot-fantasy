"""测试自动存档系统"""
import sys
import os
import time
sys.path.insert(0, 'src')

from auto_save_system import (
    auto_save, load_save, get_save_files, 
    AutoSaveManager, cleanup_old_saves
)

# 模拟游戏状态
class MockState:
    def __init__(self):
        self.money = 1000
        self.lives = 20
        self.wave = 5
        self.level = 2
        self.score = 5000
        self.towers = []

def test_auto_save():
    """测试自动存档"""
    state = MockState()
    
    # 执行自动存档
    save_name = auto_save(state)
    assert save_name.startswith("autosave_")
    print(f"✓ 自动存档成功: {save_name}")
    
    # 检查存档文件存在
    files = get_save_files()
    assert len(files) > 0
    print(f"✓ 存档列表: {len(files)} 个文件")
    
    # 加载存档
    save_path = files[0]['path']
    data = load_save(save_path)
    assert data is not None
    assert data['money'] == 1000
    assert data['wave'] == 5
    print(f"✓ 存档加载成功: wave={data['wave']}, money={data['money']}")
    
    return True

def test_auto_save_manager():
    """测试自动存档管理器"""
    state = MockState()
    manager = AutoSaveManager(state)
    
    # 模拟游戏循环
    manager.update(1.0)  # 1秒后不应触发存档
    assert manager.get_notification() is None
    print("✓ 1秒后无存档触发")
    
    # 强制存档
    result = manager.force_save()
    assert result == True
    print("✓ 强制存档成功")
    
    # 检查提示
    notif = manager.get_notification()
    assert notif is not None
    assert notif['type'] == 'success'
    print(f"✓ 存档提示: {notif['message']}")
    
    return True

def test_cleanup():
    """测试清理旧存档"""
    removed = cleanup_old_saves(keep=3)
    print(f"✓ 清理旧存档: {removed} 个")
    return True

if __name__ == "__main__":
    print("=" * 40)
    print("测试自动存档系统")
    print("=" * 40)
    
    test_auto_save()
    test_auto_save_manager()
    test_cleanup()
    
    print("=" * 40)
    print("🎉 所有测试通过!")
    print("=" * 40)