"""
保卫萝卜 - 波次系统
"""
import time
from monsters import MonsterFactory

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
        self.wave_in_progress = False  # 兼容测试
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
        self.wave_in_progress = True  # 兼容测试
        self.wave_complete = False
        self.wave_start_time = time.time()
        return True
        
    def update(self, dt, state, difficulty=1.0):
        """更新波次系统"""
        self.wave_in_progress = self.is_waving and not self.wave_complete
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
                
                # 怪物出现时显示传送门特效
                import main
                if hasattr(main, 'effect_manager'):
                    # 根据怪物类型选择传送门颜色
                    if getattr(monster, 'is_boss', False):
                        main.effect_manager.add_portal(monster.x, monster.y, (255, 100, 100), 60)
                    elif getattr(monster, 'is_elite', False):
                        main.effect_manager.add_portal(monster.x, monster.y, (255, 200, 50), 50)
                    else:
                        main.effect_manager.add_portal(monster.x, monster.y, (100, 200, 255), 40)
                
                # Boss出现时触发屏幕震动和警告特效
                if getattr(monster, 'is_boss', False):
                    main.trigger_screen_shake(15, 0.5)
                    # 添加Boss警告特效
                    if hasattr(main, 'boss_warning_effects'):
                        from base_effects import BossWarningEffect
                        main.boss_warning_effects.append(
                            BossWarningEffect(500, 350, main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
                        )
                
        # 检查波次是否完成
        if not self.monster_queue and not state.monsters:
            self.is_waving = False
            self.wave_in_progress = False
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


class ChallengeMode:
    """挑战模式 - 无限波次，难度递增"""
    
    # 挑战难度配置
    DIFFICULTY_LEVELS = [
        {"name": "简单", "hp_mult": 1.0, "speed_mult": 1.0, "reward_mult": 1.0},
        {"name": "普通", "hp_mult": 1.5, "speed_mult": 1.1, "reward_mult": 1.2},
        {"name": "困难", "hp_mult": 2.0, "speed_mult": 1.2, "reward_mult": 1.5},
        {"name": "噩梦", "hp_mult": 3.0, "speed_mult": 1.3, "reward_mult": 2.0},
        {"name": "地狱", "hp_mult": 5.0, "speed_mult": 1.5, "reward_mult": 3.0},
    ]
    
    # 无限波次怪物池（从简单到困难）
    CHALLENGE_MONSTER_POOL = [
        ["小怪物", "中怪物"],
        ["小怪物", "中怪物", "大怪物", "快速怪"],
        ["中怪物", "大怪物", "快速怪", "装甲怪", "Boss"],
        ["大怪物", "Boss", "装甲怪", "快速怪"],
        ["Boss", "超级Boss", "装甲怪", "快速怪"],
    ]
    
    def __init__(self, difficulty=1):
        self.difficulty = min(difficulty, len(self.DIFFICULTY_LEVELS) - 1)
        self.current_wave = 0
        self.is_active = False
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        self.monster_queue = []
        self.total_kills = 0
        self.total_coins = 0
        self.time_elapsed = 0
        
    def get_difficulty_config(self):
        """获取当前难度配置"""
        return self.DIFFICULTY_LEVELS[self.difficulty]
    
    def start(self):
        """启动挑战模式"""
        self.is_active = True
        self.current_wave = 1
        self._generate_wave()
        
    def _generate_wave(self):
        """生成当前波次怪物"""
        difficulty_config = self.get_difficulty_config()
        monster_pool = self.CHALLENGE_MONSTER_POOL[self.difficulty]
        
        # 怪物数量 = 波次数 * (1 + 难度加成)
        base_count = 3 + self.current_wave // 2
        count = int(base_count * difficulty_config["hp_mult"] / 1.5)
        count = max(3, min(count, 20))  # 限制3-20只
        
        import random
        for _ in range(count):
            monster_type = random.choice(monster_pool)
            # 后面波次增加Boss概率
            if self.current_wave >= 5 and random.random() < 0.1 + self.current_wave * 0.02:
                monster_type = "Boss" if random.random() < 0.8 else "超级Boss"
            self.monster_queue.append(monster_type)
        
        # 间隔时间随波次递减
        self.spawn_interval = max(0.3, 1.0 - self.current_wave * 0.02)
        
    def update(self, dt, state):
        """更新挑战模式"""
        if not self.is_active:
            return
            
        self.time_elapsed += dt
        self.spawn_timer += dt
        
        # 生成怪物
        if self.spawn_timer >= self.spawn_interval and self.monster_queue:
            from monsters import MonsterFactory
            monster_type = self.monster_queue.pop(0)
            monster = MonsterFactory.create(monster_type)
            
            if monster:
                difficulty_config = self.get_difficulty_config()
                # 应用难度倍率
                monster.health = int(monster.health * difficulty_config["hp_mult"])
                monster.max_health = int(monster.max_health * difficulty_config["hp_mult"])
                monster.speed = monster.speed * difficulty_config["speed_mult"]
                # 波次递增额外加成
                wave_bonus = 1 + (self.current_wave - 1) * 0.1
                monster.health = int(monster.health * wave_bonus)
                monster.max_health = int(monster.max_health * wave_bonus)
                
                state.monsters.append(monster)
                self.spawn_timer = 0
        
        # 检查波次完成
        if not self.monster_queue and not state.monsters:
            self.current_wave += 1
            self._generate_wave()
            
    def get_info(self):
        """获取挑战模式信息"""
        return {
            "wave": self.current_wave,
            "difficulty": self.DIFFICULTY_LEVELS[self.difficulty]["name"],
            "kills": self.total_kills,
            "coins": self.total_coins,
            "time": int(self.time_elapsed),
        }