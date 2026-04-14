import pygame
import random
from config_loader import get_config
from sound_manager import SoundManager
from base_effects import get_base_effect_manager

""" 
保卫萝卜 - 防御塔系统
""" 

# 全局音效播放器（可在 main.py 中设置）
sound_player = None

# 全局音效管理器
_sound_manager = None

def set_sound_manager(sm):
    """设置全局音效管理器"""
    global _sound_manager
    _sound_manager = sm

def set_sound_player(player):
    """设置全局音效播放器(兼容旧代码)"""
    global sound_player
    sound_player = player

class Tower:
    """防御塔基类"""
    max_level = 3
    
    # 新增：Combo Strike系统 - 多塔集火加成
    _combo_targets = {}  # 记录哪些塔正在攻击同一目标
    
    # 塔主动技能定义
    ACTIVE_SKILLS = {
        "箭塔": {"name": "专注射击", "cooldown": 15, "duration": 5, "effect": "attack_speed_boost"},
        "炮塔": {"name": "轰炸", "cooldown": 20, "duration": 3, "effect": "aoe_damage"},
        "魔法塔": {"name": "能量汲取", "cooldown": 18, "duration": 8, "effect": "life_steal"},
        "冰霜塔": {"name": "冰封大地", "cooldown": 25, "duration": 6, "effect": "freeze_wave"},
    }
    
    def __init__(self, name, damage, range, cost, attack_speed, x=0, y=0, slow_factor=1.0, freeze_duration=0, poison_damage=0, poison_duration=0):
        self.name = name
        self.damage = damage
        self.range = range
        self.cost = cost
        self.attack_speed = attack_speed
        self.slow_factor = slow_factor  # 减速因子
        self.freeze_duration = freeze_duration  # 冰冻时长（帧数）
        self.poison_damage = poison_damage  # 中毒伤害/秒
        self.poison_duration = poison_duration  # 中毒持续时间
        self.level = 1
        self.target = None
        self.x = x
        self.y = y
        self.cooldown = 0
        self.projectiles = []
        self.kill_count = 0  # 击杀统计
        # 攻击优先级: "first"=最前, "last"=最后, "strong"=最强, "weak"=最弱
        self.priority = "first"
        
        # 主动技能系统
        self.skill_active = False
        self.skill_timer = 0
        self.skill_cooldown = 0
        skill_info = self.ACTIVE_SKILLS.get(name, {})
        self.skill_name = skill_info.get("name", "")
        self.skill_cooldown_max = skill_info.get("cooldown", 0)
        self.skill_duration = skill_info.get("duration", 0)
        self.skill_effect = skill_info.get("effect", "")
        
        # 塔品质系统：普通/优秀/史诗
        self.quality = "normal"  # 默认普通
        # 随机品质（10%几率史诗，30%优秀）
        roll = random.random()
        if roll < 0.1:
            self.quality = "epic"
            self.damage = int(self.damage * 1.5)
            self.range = self.range * 1.2
        elif roll < 0.4:
            self.quality = "rare"
            self.damage = int(self.damage * 1.25)
            self.range = self.range * 1.1
        
        # 专精系统：满级后可选专精方向
        self.specialization = None  # "damage", "range", "speed", "aoe"
        self.specialized = False  # 是否已专精
        
        # 升级动画效果
        self.upgrade_animation = 0  # 升级动画计时器
        self.glow_intensity = 0  # 发光强度
        
        # 瞄准线预览系统
        self.targeting_line_alpha = 0  # 瞄准线透明度（淡入效果）
        self.last_target = None  # 上一个目标（用于平滑过渡）
    
    def get_upgrade_cost(self):
        """获取升级费用"""
        config = get_config()
        tower_config = config.get('towers', {}).get(self.name, {})
        return tower_config.get('upgrade_cost', self.cost // 2)
    
    def get_sell_price(self):
        """获取出售价格（升级花费的50%）"""
        return int(self.get_upgrade_cost() * 0.5)
    
    def can_upgrade(self):
        """检查是否可以升级"""
        return self.level < self.max_level
    
    def upgrade(self):
        """升级防御塔"""
        if not self.can_upgrade():
            return None
        self.level += 1
        self.damage *= 1.3
        self.range *= 1.1
        self.attack_speed *= 1.1
        # 触发升级动画
        self.upgrade_animation = 30  # 30帧动画
        self.glow_intensity = 1.0
        # 触发升级光柱特效
        base_effects = get_base_effect_manager()
        base_effects.trigger_upgrade_effect(self)
        return self.level
    
    def can_specialize(self):
        """检查是否可以专精（满级且未专精）"""
        return self.level >= self.max_level and not self.specialized
    
    def get_specialization_options(self):
        """获取可用的专精选项"""
        if not self.can_specialize():
            return []
        return TOWER_SPECIALIZATIONS.get(self.name, {})
    
    def specialize(self, spec_type):
        """应用专精"""
        if not self.can_specialize():
            return False
        options = self.get_specialization_options()
        if spec_type not in options:
            return False
        self.specialization = spec_type
        self.specialized = True
        spec = options[spec_type]
        # 应用专精效果
        self.damage *= spec.get("damage_mult", 1.0)
        self.range *= spec.get("range_mult", 1.0)
        self.attack_speed *= spec.get("speed_mult", 1.0)
        return True
    
    def get_effective_damage(self):
        """获取实际伤害（考虑专精）"""
        if not self.specialized or not self.specialization:
            return self.damage
        spec = TOWER_SPECIALIZATIONS.get(self.name, {}).get(self.specialization, {})
        return self.damage  # 基础伤害已在specialize中乘过了
    
    def get_effective_range(self):
        """获取实际范围（考虑专精）"""
        if not self.specialized or not self.specialization:
            return self.range
        spec = TOWER_SPECIALIZATIONS.get(self.name, {}).get(self.specialization, {})
        return self.range  # 已在specialize中应用
    
    def get_effective_speed(self):
        """获取实际攻速（考虑专精）"""
        if not self.specialized or not self.specialization:
            return self.attack_speed
        spec = TOWER_SPECIALIZATIONS.get(self.name, {}).get(self.specialization, {})
        return self.attack_speed  # 已在specialize中应用
    
    def get_specialization_bonus(self, attr):
        """获取专精加成属性"""
        if not self.specialized or not self.specialization:
            return None
        spec = TOWER_SPECIALIZATIONS.get(self.name, {}).get(self.specialization, {})
        return spec.get(attr)
    
    def find_target(self, monsters):
        """根据优先级寻找目标"""
        # 过滤活着的怪物
        alive_monsters = [m for m in monsters if hasattr(m, 'alive') and m.alive]
        if not alive_monsters:
            return None
        
        # 根据优先级排序
        if self.priority == "first":
            # 最前（position最大，最接近终点）
            sorted_monsters = sorted(alive_monsters, key=lambda m: m.position, reverse=True)
        elif self.priority == "last":
            # 最后（position最小，最远离起点）
            sorted_monsters = sorted(alive_monsters, key=lambda m: m.position)
        elif self.priority == "strong":
            # 最强（血量最多）
            sorted_monsters = sorted(alive_monsters, key=lambda m: m.health, reverse=True)
        elif self.priority == "weak":
            # 最弱（血量最少）
            sorted_monsters = sorted(alive_monsters, key=lambda m: m.health)
        else:
            sorted_monsters = alive_monsters
        
        # 在排序后的怪物中找范围内最近的
        for m in sorted_monsters:
            m_x = int(100 + m.position * 600)
            m_y = 300
            dx = m_x - self.x
            dy = m_y - self.y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist <= self.range * 50:  # range单位转换
                return m
        
        return None
    
    def attack(self, monsters, projectiles, all_towers=None):
        """攻击冷却更新和发射子弹"""
        self.cooldown -= 1/60  # 每帧减少冷却
        if self.cooldown <= 0:
            target = self.find_target(monsters)
            if target:
                # 更新Combo Strike计数
                target_id = id(target)
                Tower._combo_targets[target_id] = Tower._combo_targets.get(target_id, 0) + 1
                
                # 计算组合加成
                if all_towers is None:
                    synergy = 1.0
                else:
                    synergy = self.check_synergy(all_towers, target)
                
                actual_damage = int(self.damage * synergy)
                
                # 创建子弹（带冰冻效果）
                from projectiles import Projectile
                p = Projectile(self.x, self.y, target, actual_damage, slow_factor=self.slow_factor, source_tower=self, tower_type=self.name, freeze_duration=self.freeze_duration, poison_damage=self.poison_damage, poison_duration=self.poison_duration)
                # 记录组合加成用于UI显示
                p.synergy = synergy
                p.is_combo = Tower._combo_targets.get(target_id, 1) > 1  # 标记集火
                projectiles.append(p)
                # 播放音效
                if _sound_manager:
                    _sound_manager.play('shoot')
                elif sound_player:
                    sound_player()
                self.cooldown = 1 / self.attack_speed
                
                # 更新瞄准线：攻击后透明度を重置
                self.targeting_line_alpha = 0
                self.last_target = target
    
    def update_skill(self, dt, monsters, projectiles):
        """更新主动技能状态"""
        if not self.skill_name:
            return
        
        # 更新技能冷却
        if self.skill_cooldown > 0:
            self.skill_cooldown -= dt
        
        # 更新技能持续时间
        if self.skill_active:
            self.skill_timer -= dt
            if self.skill_timer <= 0:
                self.skill_active = False
            # 技能效果应用
            self._apply_skill_effect(monsters, projectiles)
    
    def activate_skill(self):
        """激活主动技能"""
        if not self.skill_name or self.skill_cooldown > 0 or self.skill_active:
            return False
        self.skill_active = True
        self.skill_timer = self.skill_duration
        self.skill_cooldown = self.skill_cooldown_max
        return True
    
    def _apply_skill_effect(self, monsters, projectiles):
        """应用技能效果"""
        if self.skill_effect == "attack_speed_boost" and self.target:
            # 专注射击：攻速翻倍
            self.cooldown = max(0, self.cooldown - 0.02)
        elif self.skill_effect == "aoe_damage" and self.target:
            # 轰炸：对目标周围造成范围伤害
            for m in monsters:
                if hasattr(m, 'alive') and m.alive:
                    m_x = int(100 + m.position * 600)
                    m_y = 300
                    dist = ((m_x - self.target.x)**2 + (m_y - self.target.y)**2) ** 0.5
                    if dist < 80:
                        m.take_damage(self.damage // 2)
        elif self.skill_effect == "life_steal" and self.target:
            # 能量汲取：50%伤害转化为金币
            pass  # 后续可在main.py中处理
    
    def get_skill_status(self):
        """获取技能状态"""
        if not self.skill_name:
            return None
        return {
            "name": self.skill_name,
            "active": self.skill_active,
            "cooldown": self.skill_cooldown,
            "cooldown_max": self.skill_cooldown_max,
            "ready": self.skill_cooldown <= 0 and not self.skill_active
        }
    
    def update_projectiles(self, dt):
        """更新所有子弹"""
        for p in self.projectiles[:]:
            p.update(dt)
            if not p.active:
                self.projectiles.remove(p)
    
    def check_synergy(self, all_towers, target=None):
        """检测与相邻塔的组合效果 + 集火加成"""
        synergy_bonus = 1.0
        
        for other in all_towers:
            if other is self:
                continue
            # 计算距离（像素）
            dist = ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5
            if dist < 100:  # 相距100像素内
                # 同类型加成
                if self.name == other.name:
                    synergy_bonus += 0.1  # 10%伤害加成
        
        # Combo Strike：集火同一目标的塔获得额外+5%伤害/塔
        if target and id(target) in Tower._combo_targets:
            combo_count = Tower._combo_targets[id(target)]
            synergy_bonus += combo_count * 0.05
        
        return min(synergy_bonus, 1.5)  # 最多+50%
    
    def __str__(self):
        return f"{self.name} Lv.{self.level} (伤害:{self.damage}, 射程:{self.range})"


# 防御塔专精配置
TOWER_SPECIALIZATIONS = {
    "箭塔": {
        "damage": {"name": "穿透射击", "effect": "穿透+100%伤害", "damage_mult": 2.0, "range_mult": 1.0, "speed_mult": 1.0, "aoe": False},
        "range": {"name": "狙击大师", "effect": "+50%范围", "damage_mult": 1.0, "range_mult": 1.5, "speed_mult": 1.0, "aoe": False},
        "speed": {"name": "急速射击", "effect": "+100%攻速", "damage_mult": 1.0, "range_mult": 1.0, "speed_mult": 2.0, "aoe": False},
    },
    "炮塔": {
        "damage": {"name": "毁灭轰炸", "effect": "+100%伤害", "damage_mult": 2.0, "range_mult": 1.0, "speed_mult": 1.0, "aoe": True},
        "range": {"name": "远程轰炸", "effect": "+50%范围+AOE", "damage_mult": 1.0, "range_mult": 1.5, "speed_mult": 1.0, "aoe": True},
        "speed": {"name": "速射炮", "effect": "+80%攻速", "damage_mult": 1.0, "range_mult": 1.0, "speed_mult": 1.8, "aoe": True},
    },
    "魔法塔": {
        "damage": {"name": "奥术爆发", "effect": "+100%伤害+吸血", "damage_mult": 2.0, "range_mult": 1.0, "speed_mult": 1.0, "aoe": False, "lifesteal": 0.1},
        "range": {"name": "精神控制", "effect": "+50%范围+减速强化", "damage_mult": 1.0, "range_mult": 1.5, "speed_mult": 1.0, "aoe": False, "slow_boost": 2.0},
        "speed": {"name": "能量倾泻", "effect": "+100%攻速", "damage_mult": 1.0, "range_mult": 1.0, "speed_mult": 2.0, "aoe": False},
    },
    "冰霜塔": {
        "damage": {"name": "冰封千里", "effect": "+100%伤害+范围冰冻", "damage_mult": 2.0, "range_mult": 1.0, "speed_mult": 1.0, "freeze_aoe": True},
        "range": {"name": "绝对零度", "effect": "+50%范围+强化减速", "damage_mult": 1.0, "range_mult": 1.5, "speed_mult": 1.0, "slow_factor": 0.25},
        "speed": {"name": "寒冰风暴", "effect": "+100%攻速", "damage_mult": 1.0, "range_mult": 1.0, "speed_mult": 2.0, "freeze_wave": True},
    },
}


class TowerFactory:
    """防御塔工厂"""
    
    TOWERS = {
        "箭塔": {"damage": 10, "range": 3, "cost": 50, "speed": 2},
        "炮塔": {"damage": 30, "range": 2, "cost": 100, "speed": 0.5},
        "魔法塔": {"damage": 20, "range": 4, "cost": 80, "speed": 1},
        "冰霜塔": {"damage": 15, "range": 1.8, "cost": 120, "speed": 0.8, "slow": 0.5},
    }
    
    @classmethod
    def create(cls, name):
        """创建防御塔"""
        if name not in cls.TOWERS:
            return None
        stats = cls.TOWERS[name]
        slow_factor = stats.get("slow", 1.0)  # 获取减速因子
        # 冰霜塔特殊属性
        freeze_duration = 30 if "冰霜" in name else 0  # 冰霜塔子弹冰冻30帧
        return Tower(name, stats["damage"], stats["range"], stats["cost"], stats["speed"], slow_factor=slow_factor, freeze_duration=freeze_duration)
    
    @classmethod
    def list_towers(cls):
        """列出所有防御塔"""
        return list(cls.TOWERS.keys())
    
    @classmethod
    def get_info(cls, name):
        """获取防御塔信息"""
        if name not in cls.TOWERS:
            return None
        return cls.TOWERS[name]