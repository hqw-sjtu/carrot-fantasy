"""
保卫萝卜 - 宠物跟随系统
Carrot Fantasy - Pet Companion System
工艺品级别：可爱宠物伴随玩家，提供增益效果
"""

import pygame
import random
import math


class Pet:
    """宠物基类"""
    
    def __init__(self, pet_type, x, y):
        self.pet_type = pet_type
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.state = "idle"  # idle, walking, eating, happy
        self.direction = 1  # 1=right, -1=left
        self.animation_frame = 0
        self.animation_timer = 0
        self.bounce_offset = 0
        self.bounce_timer = 0
        
    def update(self, dt, player_pos):
        """更新宠物状态
        
        Args:
            dt: 时间增量
            player_pos: 玩家/萝卜位置 (x, y)
        """
        # 跟随玩家
        self.target_x = player_pos[0] + 40
        self.target_y = player_pos[1] + 20
        
        # 平滑移动
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 5:
            speed = 150  # 跟随速度
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt
            self.state = "walking"
            self.direction = 1 if dx > 0 else -1
        else:
            self.state = "idle"
        
        # 弹跳动画
        self.bounce_timer += dt * 8
        self.bounce_offset = math.sin(self.bounce_timer) * 3
        
        # 动画帧更新
        self.animation_timer += dt
        if self.animation_timer > 0.15:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
    def draw(self, screen):
        """绘制宠物"""
        draw_x = int(self.x)
        draw_y = int(self.y + self.bounce_offset)
        
        if self.pet_type == "cat":
            self._draw_cat(screen, draw_x, draw_y)
        elif self.pet_type == "dog":
            self._draw_dog(screen, draw_x, draw_y)
        elif self.pet_type == "rabbit":
            self._draw_rabbit(screen, draw_x, draw_y)
    
    def _draw_cat(self, screen, x, y):
        """绘制小猫"""
        # 身体
        body_color = (255, 200, 100)
        pygame.draw.ellipse(screen, body_color, (x - 15, y - 10, 30, 20))
        # 耳朵
        pygame.draw.polygon(screen, body_color, [(x - 12, y - 10), (x - 8, y - 20), (x - 4, y - 10)])
        pygame.draw.polygon(screen, body_color, [(x + 4, y - 10), (x + 8, y - 20), (x + 12, y - 10)])
        # 眼睛
        eye_offset = 4 if self.direction == 1 else -4
        pygame.draw.circle(screen, (0, 0, 0), (x - 6 + eye_offset, y - 5), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + 6 + eye_offset, y - 5), 2)
        # 尾巴
        tail_start = x + (12 if self.direction == 1 else -12)
        tail_end = x + (20 if self.direction == 1 else -20)
        pygame.draw.line(screen, body_color, (tail_start, y), (tail_end, y - 10), 3)
        
    def _draw_dog(self, screen, x, y):
        """绘制小狗"""
        # 身体
        body_color = (180, 120, 60)
        pygame.draw.ellipse(screen, body_color, (x - 15, y - 8, 30, 18))
        # 耳朵
        ear_color = (150, 100, 50)
        pygame.draw.ellipse(screen, ear_color, (x - 18, y - 15, 8, 12))
        pygame.draw.ellipse(screen, ear_color, (x + 10, y - 15, 8, 12))
        # 眼睛和鼻子
        eye_offset = 4 if self.direction == 1 else -4
        pygame.draw.circle(screen, (0, 0, 0), (x - 5 + eye_offset, y - 3), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + 5 + eye_offset, y - 3), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + eye_offset, y + 2), 3)
        
    def _draw_rabbit(self, screen, x, y):
        """绘制小兔"""
        # 身体
        body_color = (240, 240, 250)
        pygame.draw.ellipse(screen, body_color, (x - 12, y - 8, 24, 18))
        # 耳朵
        pygame.draw.ellipse(screen, body_color, (x - 10, y - 25, 6, 18))
        pygame.draw.ellipse(screen, body_color, (x + 4, y - 25, 6, 18))
        # 眼睛
        eye_offset = 3 if self.direction == 1 else -3
        pygame.draw.circle(screen, (0, 0, 0), (x - 4 + eye_offset, y - 2), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + 4 + eye_offset, y - 2), 2)
        # 鼻子
        pygame.draw.circle(screen, (255, 150, 150), (x + eye_offset, y + 3), 2)


class PetSystem:
    """宠物系统管理器"""
    
    # 宠物类型定义
    PET_TYPES = {
        "cat": {
            "name": "🐱 小喵",
            "bonus": "+5% 金币获取",
            "color": (255, 200, 100)
        },
        "dog": {
            "name": "🐶 小旺",
            "bonus": "+3% 经验获取",
            "color": (180, 120, 60)
        },
        "rabbit": {
            "name": "🐰 小白",
            "bonus": "+2% 攻速加成",
            "color": (240, 240, 250)
        }
    }
    
    def __init__(self):
        self.active_pets = []  # 当前激活的宠物
        self.pet_unlocked = {
            "cat": True,  # 默认解锁
            "dog": False,
            "rabbit": False
        }
        self.bonus_multipliers = {
            "gold": 1.0,
            "experience": 1.0,
            "attack_speed": 1.0
        }
        
    def add_pet(self, pet_type, x, y):
        """添加宠物"""
        if len(self.active_pets) >= 3:  # 最多3只宠物
            return False
        
        if pet_type not in self.PET_TYPES:
            return False
            
        pet = Pet(pet_type, x, y)
        self.active_pets.append(pet)
        self._update_bonuses()
        return True
    
    def remove_pet(self, pet_type):
        """移除宠物"""
        for i, pet in enumerate(self.active_pets):
            if pet.pet_type == pet_type:
                self.active_pets.pop(i)
                self._update_bonuses()
                return True
        return False
    
    def unlock_pet(self, pet_type):
        """解锁宠物"""
        if pet_type in self.pet_unlocked:
            self.pet_unlocked[pet_type] = True
    
    def _update_bonuses(self):
        """更新增益倍数"""
        self.bonus_multipliers = {
            "gold": 1.0,
            "experience": 1.0,
            "attack_speed": 1.0
        }
        
        for pet in self.active_pets:
            if pet.pet_type == "cat":
                self.bonus_multipliers["gold"] += 0.05
            elif pet.pet_type == "dog":
                self.bonus_multipliers["experience"] += 0.03
            elif pet.pet_type == "rabbit":
                self.bonus_multipliers["attack_speed"] += 0.02
    
    def update(self, dt, player_pos):
        """更新所有宠物"""
        for pet in self.active_pets:
            pet.update(dt, player_pos)
    
    def draw(self, screen):
        """绘制所有宠物"""
        for pet in self.active_pets:
            pet.draw(screen)
    
    def get_bonus(self, bonus_type):
        """获取指定类型的增益"""
        return self.bonus_multipliers.get(bonus_type, 1.0)
    
    def apply_gold_bonus(self, base_gold):
        """应用金币增益"""
        return int(base_gold * self.bonus_multipliers["gold"])
    
    def apply_exp_bonus(self, base_exp):
        """应用经验增益"""
        return int(base_exp * self.bonus_multipliers["experience"])
    
    def get_pet_info(self):
        """获取宠物信息用于UI显示"""
        info = []
        for pet in self.active_pets:
            pet_data = self.PET_TYPES[pet.pet_type]
            info.append({
                "type": pet.pet_type,
                "name": pet_data["name"],
                "bonus": pet_data["bonus"],
                "state": pet.state
            })
        return info


# 全局实例
_pet_system_instance = None

def get_pet_system():
    """获取宠物系统全局实例"""
    global _pet_system_instance
    if _pet_system_instance is None:
        _pet_system_instance = PetSystem()
    return _pet_system_instance