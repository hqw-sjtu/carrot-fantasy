"""
保卫萝卜 - 波次系统
"""
import time
from src.monsters import MonsterFactory

# 波次配置
WAVES = [
    {"monsters": [("小怪物", 5)], "interval": 1.0},  # 第1波：5个小怪，间隔1秒
    {"monsters": [("小怪物", 8), ("中怪物", 2)], "interval": 0.8},
    {"monsters": [("中怪物", 5), ("大怪物", 1)], "interval": 0.6},
    {"monsters": [("大怪物", 3), ("Boss", 1)], "interval": 0.5},
    {"monsters": [("快速怪", 10)], "interval": 0.5},  # 新增快速怪
    {"monsters": [("装甲怪", 3), ("中怪物", 5)], "interval": 1.0},  # 新增装甲怪
    {"monsters": [("快速怪", 5), ("装甲怪", 2), ("Boss", 1)], "interval": 0.8},  # 混合波次
    {"monsters": [("超级Boss", 1), ("装甲怪", 5)], "interval": 1.0},  # 最终波
]

class WaveManager:
    """波次管理器"""
    
    def __init__(self):
        self.current_wave = 0
        self.waves = WAVES
        self.is_waving = False
        self.spawn_timer = 0
        self.spawn_interval = 0
        self.monster_queue = []
        self.wave_complete = True
        self.wave_start_time = 0
        
    def start_wave(self, wave_index):
        """开始指定波次"""
        if wave_index >= len(self.waves):
            return False
            
        self.current_wave = wave_index
        wave_data = self.waves[wave_index]
        
        # 设置波次参数
        self.spawn_interval = wave_data["interval"]
        self.spawn_timer = 0
        self.monster_queue = []
        
        # 构建怪物队列
        for monster_type, count in wave_data["monsters"]:
            for _ in range(count):
                self.monster_queue.append(monster_type)
                
        self.is_waving = True
        self.wave_complete = False
        self.wave_start_time = time.time()
        return True
        
    def update(self, dt, state, difficulty=1.0):
        """更新波次系统"""
        if not self.is_waving or self.wave_complete:
            return
            
        # 检查是否应该生成新的怪物
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.spawn_interval and self.monster_queue:
            # 生成一个怪物
            monster_type = self.monster_queue.pop(0)
            monster = MonsterFactory.create(monster_type)
            
            if monster:
                # 应用难度倍率
                monster.health = int(monster.health * difficulty)
                monster.max_health = int(monster.max_health * difficulty)
                state.monsters.append(monster)
                self.spawn_timer = 0
                
        # 检查波次是否完成
        if not self.monster_queue and not state.monsters:
            self.is_waving = False
            self.wave_complete = True
            
    def is_wave_complete(self):
        """检查波次是否完成"""
        return self.wave_complete
        
    def get_current_wave_info(self):
        """获取当前波次信息"""
        if self.current_wave < len(self.waves):
            return self.waves[self.current_wave]
        return None
        
    def get_next_wave_index(self):
        """获取下一波索引"""
        return self.current_wave + 1
        
    def has_more_waves(self):
        """检查是否有更多波次"""
        return self.current_wave < len(self.waves) - 1