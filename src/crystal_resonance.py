"""
保卫萝卜 - 水晶共鸣系统 (Crystal Resonance)
工艺品级别特性：当多个同类型防御塔相邻时触发共鸣效果

Author: 派蒙 (Hourly Maintenance)
Date: 2026-04-15
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional


class CrystalResonance:
    """水晶共鸣系统 - 塔之间产生共鸣加成"""
    
    # 共鸣阈值：需要相邻的其他同类型塔数量（改为1意味着2个相邻即触发）
    RESONANCE_THRESHOLD = 1
    
    # 共鸣加成系数
    BONUS_DAMAGE = 0.15  # 15% 伤害加成 per resonance
    BONUS_ATTACK_SPEED = 0.10  # 10% 攻速加成 per resonance
    BONUS_RANGE = 0.08  # 8% 射程加成 per resonance
    
    def __init__(self):
        self.resonance_groups: Dict[int, List[int]] = {}  # tower_id -> [neighbor_ids]
        self.resonance_bonuses: Dict[int, Dict[str, float]] = {}  # tower_id -> bonus_dict
        self.active_resonances: set = set()  # 激活共鸣的tower_id集合
        self.resonance_particles: List[Dict] = []  # 共鸣粒子效果
        
        # 共鸣颜色配置
        self.resonance_colors = {
            "箭塔": (255, 200, 50),    # 金色
            "炮塔": (255, 100, 50),    # 橙红
            "魔法塔": (150, 100, 255), # 紫色
            "冰霜塔": (100, 200, 255), # 浅蓝
            "电塔": (255, 255, 100),   # 黄色
            "太阳塔": (255, 220, 50),  # 橙黄
        }
        
    def calculate_resonance(self, towers: Dict, tower_id: int) -> Dict[str, float]:
        """计算单个塔的共鸣加成"""
        if tower_id not in towers:
            return {"damage": 0, "attack_speed": 0, "range": 0}
            
        tower = towers[tower_id]
        tower_type = tower.name
        
        # 查找同类型相邻塔
        neighbors = self._find_neighbors(towers, tower_id, tower_type)
        
        if len(neighbors) < self.RESONANCE_THRESHOLD:
            return {"damage": 0, "attack_speed": 0, "range": 0}
            
        # 计算共鸣等级
        resonance_level = len(neighbors)
        
        bonuses = {
            "damage": resonance_level * self.BONUS_DAMAGE,
            "attack_speed": resonance_level * self.BONUS_ATTACK_SPEED,
            "range": resonance_level * self.BONUS_RANGE,
        }
        
        return bonuses
        
    def _find_neighbors(self, towers: Dict, tower_id: int, tower_type: str) -> List[int]:
        """查找同类型相邻塔"""
        if tower_id not in towers:
            return []
            
        tower = towers[tower_id]
        neighbors = []
        
        for tid, other_tower in towers.items():
            if tid == tower_id:
                continue
            if other_tower.name != tower_type:
                continue
                
            # 计算距离
            dx = tower.x - other_tower.x
            dy = tower.y - other_tower.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 相邻阈值：塔射程的1.5倍或200像素（取较小值）
            tower_range = getattr(tower, 'range', 100) or 100
            threshold = min(tower_range * 1.5, 200)
            
            if distance <= threshold:
                neighbors.append(tid)
                
        return neighbors
        
    def update_all_resonances(self, towers: Dict) -> None:
        """更新所有塔的共鸣状态"""
        self.resonance_bonuses.clear()
        self.active_resonances.clear()
        
        for tower_id in towers:
            bonuses = self.calculate_resonance(towers, tower_id)
            if bonuses["damage"] > 0 or bonuses["attack_speed"] > 0:
                self.resonance_bonuses[tower_id] = bonuses
                self.active_resonances.add(tower_id)
                
    def get_bonus(self, tower_id: int, stat: str) -> float:
        """获取特定属性的共鸣加成"""
        if tower_id not in self.resonance_bonuses:
            return 0.0
        return self.resonance_bonuses[tower_id].get(stat, 0.0)
        
    def apply_bonus(self, tower, stat: str, base_value: float) -> float:
        """应用共鸣加成到实际属性"""
        bonus = self.get_bonus(tower.id if hasattr(tower, 'id') else id(tower), stat)
        return base_value * (1 + bonus)
        
    def update_particles(self, towers: Dict, dt: float) -> None:
        """更新共鸣粒子效果"""
        # 清理过期粒子
        self.resonance_particles = [
            p for p in self.resonance_particles 
            if p.get("life", 0) > 0
        ]
        
        # 为激活共鸣的塔生成粒子
        for tower_id in self.active_resonances:
            if tower_id not in towers:
                continue
                
            tower = towers[tower_id]
            tower_type = tower.name
            color = self.resonance_colors.get(tower_type, (255, 255, 255))
            
            # 随机生成粒子
            if len(self.resonance_particles) < 100:  # 限制粒子数量
                import random
                angle = random.uniform(0, math.pi * 2)
                radius = random.uniform(30, 80)
                
                particle = {
                    "x": tower.x + math.cos(angle) * radius,
                    "y": tower.y + math.sin(angle) * radius,
                    "vx": math.cos(angle + math.pi/2) * 20,
                    "vy": math.sin(angle + math.pi/2) * 20,
                    "life": 1.0,
                    "color": color,
                    "size": random.uniform(2, 5),
                }
                self.resonance_particles.append(particle)
                
        # 更新粒子位置
        for p in self.resonance_particles:
            p["x"] += p.get("vx", 0) * dt
            p["y"] += p.get("vy", 0) * dt
            p["life"] -= dt * 0.5
            
    def draw(self, screen: pygame.Surface, towers: Dict) -> None:
        """绘制共鸣特效"""
        for tower_id in self.active_resonances:
            if tower_id not in towers:
                continue
                
            tower = towers[tower_id]
            tower_type = tower.name
            color = self.resonance_colors.get(tower_type, (255, 255, 255))
            
            # 绘制共鸣光环
            resonance_level = len(self.resonance_bonuses.get(tower_id, {}))
            radius = 50 + resonance_level * 10
            
            # 外圈光环
            pygame.draw.circle(
                screen, 
                (*color, 50),  # 半透明
                (int(tower.x), int(tower.y)),
                int(radius),
                2
            )
            
            # 绘制连线
            for neighbor_id in self.resonance_groups.get(tower_id, []):
                if neighbor_id in towers:
                    neighbor = towers[neighbor_id]
                    pygame.draw.line(
                        screen,
                        (*color, 100),
                        (int(tower.x), int(tower.y)),
                        (int(neighbor.x), int(neighbor.y)),
                        1
                    )
                    
        # 绘制粒子
        for p in self.resonance_particles:
            if p["life"] > 0:
                alpha = int(p["life"] * 255)
                surface = pygame.Surface((int(p["size"]*2), int(p["size"]*2)), pygame.SRCALPHA)
                pygame.draw.circle(
                    surface,
                    (*p["color"], alpha),
                    (int(p["size"]), int(p["size"])),
                    int(p["size"])
                )
                screen.blit(surface, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))
                
    def get_resonance_info(self, tower_id: int) -> Optional[Dict]:
        """获取塔的共鸣信息（用于UI显示）"""
        if tower_id not in self.resonance_bonuses:
            return None
            
        return {
            "active": True,
            "level": len([t for t in self.active_resonances 
                         if t in self.resonance_bonuses]),
            "bonuses": self.resonance_bonuses[tower_id]
        }


# 全局单例
_resonance_system: Optional[CrystalResonance] = None

def get_resonance_system() -> CrystalResonance:
    """获取全局共鸣系统实例"""
    global _resonance_system
    if _resonance_system is None:
        _resonance_system = CrystalResonance()
    return _resonance_system

def reset_resonance_system() -> None:
    """重置共鸣系统"""
    global _resonance_system
    _resonance_system = CrystalResonance()