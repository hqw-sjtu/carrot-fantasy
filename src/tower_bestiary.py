import pygame
import json
import os

""" 
保卫萝卜 - 防御塔图鉴系统 
记录玩家见过/拥有的所有塔类型
"""

class TowerBestiary:
    """防御塔图鉴管理器"""
    _instance = None
    _force_new = False  # 测试模式标志
    
    def __new__(cls, path=None):
        if cls._force_new:
            # 测试模式: 每次创建新实例
            instance = super().__new__(cls)
            instance._initialized = False
            instance._path_set = False  # 标记路径是否已设置
            instance._pending_path = path  # 保存传入的路径
            return instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            cls._instance._path_set = False
        return cls._instance
    
    def __init__(self, path=None):
        if self._initialized:
            return
        self._initialized = True
        self.unlocked_towers = set()  # 已解锁的塔类型
        self.tower_stats = {}  # 塔的详细统计
        # 优先使用__new__传入的路径，其次使用测试设置的路径
        pending_path = getattr(self, '_pending_path', None)
        if pending_path:
            self.bestiary_path = pending_path
        elif path:
            self.bestiary_path = path
        elif getattr(self, '_path_set', False) and hasattr(self, '_custom_path'):
            self.bestiary_path = self._custom_path
        else:
            self.bestiary_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves", "bestiary.json")
        self._load_bestiary()
    
    def set_path(self, path):
        """设置图鉴文件路径(测试用)"""
        self._custom_path = path
        self._path_set = True
        self.bestiary_path = path
    
    @classmethod
    def reset_instance(cls):
        """重置单例(测试用)"""
        cls._instance = None
        cls._force_new = False
    
    @classmethod
    def enable_test_mode(cls):
        """启用测试模式 - 每次创建新实例"""
        cls._force_new = True
        cls._instance = None
    
    def _load_bestiary(self):
        """加载图鉴数据"""
        if os.path.exists(self.bestiary_path):
            try:
                with open(self.bestiary_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unlocked_towers = set(data.get('unlocked', []))
                    self.tower_stats = data.get('stats', {})
            except Exception:
                pass
    
    def save_bestiary(self):
        """保存图鉴数据"""
        os.makedirs(os.path.dirname(self.bestiary_path), exist_ok=True)
        data = {
            'unlocked': list(self.unlocked_towers),
            'stats': self.tower_stats
        }
        with open(self.bestiary_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def unlock_tower(self, tower_name):
        """解锁新塔类型"""
        if tower_name not in self.unlocked_towers:
            self.unlocked_towers.add(tower_name)
            self.save_bestiary()
            return True
        return False
    
    def get_unlocked_count(self):
        """获取已解锁数量"""
        return len(self.unlocked_towers)
    
    def record_kill(self, tower_name):
        """记录塔的击杀数"""
        if tower_name not in self.tower_stats:
            self.tower_stats[tower_name] = {'kills': 0, 'damage': 0}
        self.tower_stats[tower_name]['kills'] += 1
        self.save_bestiary()
    
    def record_damage(self, tower_name, damage):
        """记录塔的伤害"""
        if tower_name not in self.tower_stats:
            self.tower_stats[tower_name] = {'kills': 0, 'damage': 0}
        self.tower_stats[tower_name]['damage'] += damage
        self.save_bestiary()
    
    def get_tower_stats(self, tower_name):
        """获取塔的统计信息"""
        return self.tower_stats.get(tower_name, {'kills': 0, 'damage': 0})
    
    def is_unlocked(self, tower_name):
        """检查塔是否已解锁"""
        return tower_name in self.unlocked_towers
    
    def reset(self):
        """重置图鉴"""
        self.unlocked_towers.clear()
        self.tower_stats.clear()
        self.save_bestiary()


def get_bestiary():
    """获取图鉴单例"""
    return TowerBestiary()