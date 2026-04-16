"""
Item Drop System - 道具掉落系统
击败怪物时随机掉落道具，增强游戏策略性
"""

import pygame
import random
import math


class ItemDrop:
    """掉落的道具"""
    
    # 道具类型定义
    TYPES = {
        "coin": {
            "name": "金币",
            "color": (255, 215, 0),
            "size": 12,
            "value": 10,
            "chance": 0.15,  # 基础掉落率
            "desc": "额外金币"
        },
        "health": {
            "name": "生命之心",
            "color": (255, 80, 80),
            "size": 14,
            "value": 1,
            "chance": 0.05,
            "desc": "恢复萝卜生命"
        },
        "speed": {
            "name": "加速符",
            "color": (100, 200, 255),
            "size": 12,
            "value": 1.5,
            "chance": 0.08,
            "desc": "所有塔攻速+50%"
        },
        "damage": {
            "name": "力量符",
            "color": (255, 100, 100),
            "size": 12,
            "value": 1.5,
            "chance": 0.08,
            "desc": "所有塔伤害+50%"
        },
        "slow": {
            "name": "冰霜符",
            "color": (150, 230, 255),
            "size": 12,
            "value": 2.0,
            "chance": 0.06,
            "desc": "范围内敌人减速"
        },
        "shield": {
            "name": "护盾",
            "color": (180, 180, 255),
            "size": 16,
            "value": 1,
            "chance": 0.03,
            "desc": "抵挡一次伤害"
        },
        "skill": {
            "name": "技能书",
            "color": (200, 100, 255),
            "size": 14,
            "value": 1,
            "chance": 0.02,
            "desc": "随机技能充能"
        }
    }
    
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.data = self.TYPES[item_type]
        
        self.vx = random.uniform(-60, 60)
        self.vy = random.uniform(-100, -50)
        self.gravity = 200
        
        self.lifetime = 10.0  # 10秒后消失
        self.collect_radius = 30
        
        # 动画
        self.bob_phase = random.random() * math.pi * 2
        self.bob_speed = 4
        self.bob_amplitude = 5
        self.rotation = 0
        self.rotation_speed = random.uniform(-30, 30)
        
        # 收集效果
        self.collected = False
        self.collect_anim_progress = 0
        
    def update(self, dt):
        """更新"""
        if self.collected:
            self.collect_anim_progress += dt * 5
            return self.collect_anim_progress < 1.0
        
        # 物理更新
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        
        # 边界反弹
        if self.y > 550:
            self.y = 550
            self.vy *= -0.5
            self.vx *= 0.8
        
        # 动画更新
        self.bob_phase += self.bob_speed * dt
        self.rotation += self.rotation_speed * dt
        self.lifetime -= dt
        
        # 闪烁提示即将消失
        if self.lifetime < 2.0:
            blink = math.sin(self.lifetime * 10) > 0
            return blink
        
        return self.lifetime > 0
    
    def draw(self, screen):
        """绘制"""
        if self.collected:
            # 收集动画：缩小+上浮
            progress = self.collect_anim_progress
            scale = 1 - progress
            size = self.data["size"] * scale
            offset_y = -50 * progress
            
            if size > 0:
                pygame.draw.circle(screen, self.data["color"],
                                 (int(self.x), int(self.y + offset_y)), int(size))
            return
        
        # 浮动效果
        bob_offset = math.sin(self.bob_phase) * self.bob_amplitude
        draw_y = self.y + bob_offset
        
        # 主体
        color = self.data["color"]
        size = self.data["size"]
        
        # 发光效果
        glow_radius = size + 5 + math.sin(self.bob_phase * 2) * 2
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, 80), (glow_radius, glow_radius), glow_radius)
        screen.blit(glow_surface, (self.x - glow_radius, draw_y - glow_radius))
        
        # 主圆
        pygame.draw.circle(screen, color, (int(self.x), int(draw_y)), size)
        
        # 高光
        highlight_pos = (int(self.x - size * 0.3), int(draw_y - size * 0.3))
        pygame.draw.circle(screen, (255, 255, 255), highlight_pos, size // 3)
        
        # 边框
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(draw_y)), size, 2)
        
    def collect(self):
        """收集道具"""
        self.collected = True
        return self.data
    
    @staticmethod
    def try_drop(x, y, monster_value=10, is_boss=False):
        """尝试掉落道具"""
        drops = []
        
        for item_type, data in ItemDrop.TYPES.items():
            # 基础概率
            chance = data["chance"]
            
            # 根据怪物价值调整
            chance *= (monster_value / 20)
            
            # Boss必定掉落
            if is_boss:
                chance = max(chance, 0.5)
            
            if random.random() < chance:
                drops.append(ItemDrop(x, y, item_type))
        
        return drops


class ItemManager:
    """道具管理器"""
    
    def __init__(self):
        self.items = []
        
    def add_drop(self, item):
        """添加掉落"""
        self.items.append(item)
        
    def update(self, dt):
        """更新"""
        self.items = [item for item in self.items if item.update(dt)]
        
    def draw(self, screen):
        """绘制"""
        for item in self.items:
            item.draw(screen)
    
    def check_collect(self, mouse_x, mouse_y):
        """检查鼠标收集"""
        collected = []
        for item in self.items:
            if item.collected:
                continue
            dist = math.hypot(item.x - mouse_x, item.y - mouse_y)
            if dist < item.collect_radius:
                collected.append(item.collect())
                item.collected = True
        return collected
    
    def get_count(self):
        """获取道具数量"""
        return len([i for i in self.items if not i.collected])
