"""
保卫萝卜 - Boss技能系统
Boss在战斗中可以使用特殊技能，增加战斗变数和趣味性
"""
import pygame
import random
import math

class BossSkill:
    """Boss技能基类"""
    
    def __init__(self, boss, cooldown=10.0):
        self.boss = boss
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.active = False
        self.duration = 0
        self.name = "Skill"
        
    def update(self, dt, game):
        """更新技能状态"""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
        if self.active:
            self.duration -= dt
            if self.duration <= 0:
                self.end(game)
                self.active = False
                
    def activate(self, game):
        """激活技能"""
        if self.current_cooldown <= 0 and not self.active:
            self.active = True
            self.current_cooldown = self.cooldown
            self.start(game)
            return True
        return False
        
    def start(self, game):
        """技能开始时调用"""
        pass
        
    def update_effect(self, game):
        """技能效果更新"""
        pass
        
    def end(self, game):
        """技能结束时调用"""
        pass


class SummonMinionsSkill(BossSkill):
    """召唤小怪技能"""
    
    def __init__(self, boss):
        super().__init__(boss, cooldown=15.0)
        self.name = "召唤小怪"
        self.spawn_count = 5
        
    def start(self, game):
        """召唤小怪"""
        from src.monsters import Monster
        # 在Boss位置附近生成小怪
        bx, by = self.boss.x, self.boss.y
        for _ in range(self.spawn_count):
            game.monsters.append(Monster(
                x=bx + random.randint(-50, 50),
                y=by + random.randint(-50, 50),
                hp=20,
                speed=1.5,
                reward=5
            ))


class AreaAttackSkill(BossSkill):
    """区域攻击技能"""
    
    def __init__(self, boss):
        super().__init__(boss, cooldown=20.0)
        self.name = "地震攻击"
        self.damage = 30
        self.target_x = 0
        self.target_y = 0
        self.warning_timer = 0
        self.attack_timer = 0
        
    def start(self, game):
        """选择攻击区域"""
        # 选择玩家放置塔最多的区域
        if game.towers:
            target_tower = random.choice(game.towers)
            self.target_x = target_tower.x
            self.target_y = target_tower.y
        else:
            self.target_x = 400
            self.target_y = 300
        self.warning_timer = 1.5  # 1.5秒预警
        self.attack_timer = 0
        
    def update_effect(self, game):
        """区域攻击效果"""
        if self.warning_timer > 0:
            self.warning_timer -= game.dt
            if self.warning_timer <= 0:
                # 执行攻击
                for tower in game.towers[:]:
                    dist = math.hypot(tower.x - self.target_x, tower.y - self.target_y)
                    if dist < 100:
                        tower.hp -= self.damage
                        if tower.hp <= 0:
                            game.towers.remove(tower)
                            
    def draw(self, screen):
        """绘制预警圈"""
        if self.warning_timer > 0:
            # 绘制预警圈
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.target_x), int(self.target_y)), 
                             int(100 * (1.5 - self.warning_timer) / 1.5), 2)


class HealingSkill(BossSkill):
    """Boss回血技能"""
    
    def __init__(self, boss):
        super().__init__(boss, cooldown=25.0)
        self.name = "自我修复"
        self.heal_amount = 50
        
    def start(self, game):
        """Boss回血"""
        self.boss.hp = min(self.boss.max_hp, self.boss.hp + self.heal_amount)


class ShieldSkill(BossSkill):
    """Boss护盾技能"""
    
    def __init__(self, boss):
        super().__init__(boss, cooldown=30.0)
        self.name = "能量护盾"
        self.shield_duration = 5.0
        self.shield_hp = 100
        
    def start(self, game):
        """激活护盾"""
        self.duration = self.shield_duration
        self.boss.shield = self.shield_hp
        
    def update_effect(self, game):
        """护盾效果更新"""
        if self.boss.shield > 0:
            self.boss.shield -= game.dt * 20  # 护盾逐渐消耗
        else:
            self.active = False


class TeleportSkill(BossSkill):
    """Boss传送技能"""
    
    def __init__(self, boss):
        super().__init__(boss, cooldown=12.0)
        self.name = "瞬间移动"
        
    def start(self, game):
        """Boss传送到随机位置"""
        self.boss.x = random.randint(100, 700)
        self.boss.y = random.randint(100, 500)
        # 传送特效
        game.particle_system.add_teleport_effect(self.boss.x, self.boss.y)


class BossSkillManager:
    """Boss技能管理器"""
    
    def __init__(self, boss):
        self.boss = boss
        self.skills = [
            SummonMinionsSkill(boss),
            AreaAttackSkill(boss),
            HealingSkill(boss),
            ShieldSkill(boss),
            TeleportSkill(boss)
        ]
        self.current_skill = None
        
    def update(self, dt, game):
        """更新所有技能"""
        # 更新所有技能的冷却
        for skill in self.skills:
            skill.update(dt, game)
            
        # 如果有当前技能在激活，更新效果
        if self.current_skill and self.current_skill.active:
            self.current_skill.update_effect(game)
            
        # Boss血量低于50%时，尝试使用技能
        if self.boss.hp < self.boss.max_hp * 0.5:
            self._try_use_skill(game)
            
    def _try_use_skill(self, game):
        """尝试使用技能"""
        if self.current_skill and self.current_skill.active:
            return
            
        # 随机选择一个可用的技能
        available_skills = [s for s in self.skills if s.current_cooldown <= 0]
        if available_skills:
            skill = random.choice(available_skills)
            if skill.activate(game):
                self.current_skill = skill
                
    def draw(self, screen):
        """绘制技能效果"""
        if self.current_skill and self.current_skill.active:
            if hasattr(self.current_skill, 'draw'):
                self.current_skill.draw(screen)
                
    def get_skill_info(self):
        """获取技能信息"""
        info = []
        for skill in self.skills:
            cd = max(0, skill.current_cooldown)
            status = "⏳" if cd > 0 else "✅"
            info.append(f"{status} {skill.name}: {cd:.1f}s")
        return info


# 全局单例管理
_boss_skill_managers = {}

def get_boss_skill_manager(boss):
    """获取指定Boss的技能管理器"""
    if id(boss) not in _boss_skill_managers:
        _boss_skill_managers[id(boss)] = BossSkillManager(boss)
    return _boss_skill_managers[id(boss)]


def clear_boss_skill_manager(boss):
    """清除Boss技能管理器"""
    if id(boss) in _boss_skill_managers:
        del _boss_skill_managers[id(boss)]