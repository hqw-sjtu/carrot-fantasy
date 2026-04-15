# -*- coding: utf-8 -*-
"""灵魂锁链特效系统 - Soul Chain Effect System

Boss战入场时的灵魂锁链特效，从地图边缘伸向Boss，视觉震撼。
工艺品级别实现：链节动画、灵魂粒子、能量脉冲、淡入淡出
"""

import pygame
import math
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class ChainLink:
    """单个链节"""
    x: float
    y: float
    angle: float
    length: float
    width: float
    alpha: int
    glow_intensity: float = 0.0


@dataclass
class SoulParticle:
    """灵魂粒子"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    alpha: int
    hue: int  # 色相用于渐变


class SoulChainEffect:
    """灵魂锁链特效"""
    
    # 链子状态
    STATE_IDLE = "idle"
    STATE_EXTENDING = "extending"
    STATE_CONNECTED = "connected"
    STATE_RETRACTING = "retracting"
    
    def __init__(self):
        self.state = self.STATE_IDLE
        self.chain_links: List[ChainLink] = []
        self.soul_particles: List[SoulParticle] = []
        self.boss_pos: Tuple[float, float] = (0, 0)
        self.source_pos: Tuple[float, float] = (0, 0)
        self.extension_progress: float = 0.0  # 0-1 延伸进度
        self.anim_time: float = 0.0
        self.screen_width: int = 800
        self.screen_height: int = 600
        self.link_count: int = 15  # 链节数量
        self.particle_pool: List[SoulParticle] = []
        self.max_particles: int = 50
        
        # 链子样式配置
        self.chain_color = (100, 50, 180)  # 紫色
        self.glow_colors = [
            (138, 43, 226),   # 紫罗兰
            (148, 0, 211),    # 深紫
            (186, 85, 211),   # 中紫色
            (255, 0, 255),    # 洋红
        ]
        
    def initialize(self, width: int, height: int):
        """初始化"""
        self.screen_width = width
        self.screen_height = height
        
    def start_extension(self, boss_pos: Tuple[float, float], side: str = "auto"):
        """开始锁链延伸
        
        Args:
            boss_pos: Boss位置
            side: 来源边 ('top', 'bottom', 'left', 'right', 'auto')
        """
        self.boss_pos = boss_pos
        self.anim_time = 0
        
        # 根据Boss位置选择锁链来源
        if side == "auto":
            # 从Boss上方进入
            side = "top"
            
        # 设置来源位置
        if side == "top":
            self.source_pos = (boss_pos[0], -50)
        elif side == "bottom":
            self.source_pos = (boss_pos[0], self.screen_height + 50)
        elif side == "left":
            self.source_pos = (-50, boss_pos[1])
        elif side == "right":
            self.source_pos = (self.screen_width + 50, boss_pos[1])
        else:
            self.source_pos = (boss_pos[0], -50)
            
        # 初始化链节
        self._init_chain_links()
        self.state = self.STATE_EXTENDING
        self.extension_progress = 0.0
        
    def _init_chain_links(self):
        """初始化链节"""
        self.chain_links = []
        dx = (self.boss_pos[0] - self.source_pos[0]) / self.link_count
        dy = (self.boss_pos[1] - self.source_pos[1]) / self.link_count
        
        for i in range(self.link_count):
            link = ChainLink(
                x=self.source_pos[0] + dx * i,
                y=self.source_pos[1] + dy * i,
                angle=math.atan2(dy, dx),
                length=25,
                width=max(3, 10 - i * 0.3),
                alpha=0,
                glow_intensity=0.0
            )
            self.chain_links.append(link)
            
    def spawn_soul_particle(self, x: float, y: float) -> Optional[SoulParticle]:
        """生成灵魂粒子"""
        if len(self.soul_particles) >= self.max_particles:
            return None
            
        if self.particle_pool:
            p = self.particle_pool.pop()
            p.x = x
            p.y = y
            p.vx = random.uniform(-15, 15)
            p.vy = random.uniform(-15, 15)
            p.size = random.uniform(2, 6)
            p.alpha = random.randint(150, 255)
            p.hue = random.randint(260, 320)
        else:
            p = SoulParticle(
                x=x, y=y,
                vx=random.uniform(-15, 15),
                vy=random.uniform(-15, 15),
                size=random.uniform(2, 6),
                alpha=random.randint(150, 255),
                hue=random.randint(260, 320)
            )
            
        self.soul_particles.append(p)
        return p
        
    def update(self, dt: float):
        """更新特效"""
        self.anim_time += dt
        
        if self.state == self.STATE_EXTENDING:
            # 锁链延伸动画
            self.extension_progress += dt * 0.8  # 1.25秒延伸完成
            
            if self.extension_progress >= 1.0:
                self.extension_progress = 1.0
                self.state = self.STATE_CONNECTED
                
            # 更新链节
            active_links = int(self.extension_progress * self.link_count)
            for i, link in enumerate(self.chain_links):
                if i < active_links:
                    # 淡入效果
                    link.alpha = min(255, link.alpha + int(dt * 500))
                    # 摆动效果
                    link.angle += math.sin(self.anim_time * 3 + i * 0.5) * dt * 0.5
                    # 发光效果
                    link.glow_intensity = min(1.0, link.glow_intensity + dt * 2)
                else:
                    link.alpha = 0
                    
            # 延伸时产生粒子
            if random.random() < 0.3:
                active_link = self.chain_links[min(active_links - 1, len(self.chain_links) - 1)]
                if active_link and active_link.alpha > 100:
                    self.spawn_soul_particle(active_link.x, active_link.y)
                    
        elif self.state == self.STATE_CONNECTED:
            # 连接状态，持续产生粒子
            for link in self.chain_links:
                if random.random() < 0.1 and link.alpha > 50:
                    self.spawn_soul_particle(link.x, link.y)
                    
            # 周期性脉冲
            pulse = (math.sin(self.anim_time * 2) + 1) / 2
            for link in self.chain_links:
                link.glow_intensity = 0.5 + pulse * 0.5
                
        elif self.state == self.STATE_RETRACTING:
            # 锁链收回
            self.extension_progress -= dt * 0.8
            
            if self.extension_progress <= 0:
                self.extension_progress = 0
                self.state = self.STATE_IDLE
                
            # 链节淡出
            for link in self.chain_links:
                link.alpha = max(0, int(link.alpha - dt * 300))
                link.glow_intensity = max(0, link.glow_intensity - dt * 2)
                
        # 更新粒子
        to_remove = []
        for p in self.soul_particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.alpha -= int(dt * 80)
            p.size -= dt * 2
            
            if p.alpha <= 0 or p.size <= 0:
                to_remove.append(p)
                
        for p in to_remove:
            self.soul_particles.remove(p)
            self.particle_pool.append(p)
            
    def draw(self, screen: pygame.Surface):
        """绘制特效"""
        if self.state == self.STATE_IDLE or not self.chain_links:
            return
            
        # 绘制链节
        for i, link in enumerate(self.chain_links):
            if link.alpha <= 0:
                continue
                
            # 计算链节两端位置
            half_len = link.length / 2
            start_x = link.x - math.cos(link.angle) * half_len
            start_y = link.y - math.sin(link.angle) * half_len
            end_x = link.x + math.cos(link.angle) * half_len
            end_y = link.y + math.sin(link.angle) * half_len
            
            # 发光效果
            if link.glow_intensity > 0:
                glow_alpha = int(link.alpha * link.glow_intensity * 0.3)
                glow_width = int(link.width + link.glow_intensity * 10)
                glow_color = (180, 100, 255, glow_alpha)
                
                # 绘制多层发光
                for g in range(3, 0, -1):
                    g_width = glow_width * g // 2
                    g_alpha = glow_alpha * (4 - g) // 4
                    if g_alpha > 5:
                        pygame.draw.line(
                            screen, 
                            (150, 80, 220, g_alpha),
                            (start_x, start_y),
                            (end_x, end_y),
                            g_width
                        )
                        
            # 主体链节
            color = (
                min(255, self.chain_color[0] + int(link.glow_intensity * 50)),
                min(255, self.chain_color[1] + int(link.glow_intensity * 30)),
                min(255, self.chain_color[2] + int(link.glow_intensity * 50)),
                link.alpha
            )
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), int(link.width))
            
            # 链节节点
            node_size = max(2, link.width * 0.8)
            pygame.draw.circle(screen, color[:3] + (link.alpha,), (int(link.x), int(link.y)), int(node_size))
            
        # 绘制灵魂粒子
        for p in self.soul_particles:
            if p.alpha <= 0:
                continue
                
            # 颜色渐变 (紫色到洋红)
            r = int(150 + (p.hue - 260) * 0.5)
            g = 50
            b = int(200 + (320 - p.hue) * 0.3)
            color = (min(255, r), g, min(255, b), p.alpha)
            
            # 粒子发光
            if p.size > 3:
                pygame.draw.circle(
                    screen, 
                    (180, 100, 255, int(p.alpha * 0.3)),
                    (int(p.x), int(p.y)),
                    int(p.size * 1.5)
                )
                
            pygame.draw.circle(screen, color, (int(p.x), int(p.y)), max(1, int(p.size)))
            
    def connect_to_boss(self):
        """连接到Boss（外部调用）"""
        if self.state == self.STATE_EXTENDING:
            self.extension_progress = 1.0
            self.state = self.STATE_CONNECTED
            
    def start_retraction(self):
        """开始收回锁链"""
        if self.state == self.STATE_CONNECTED:
            self.state = self.STATE_RETRACTING
            
    def reset(self):
        """重置"""
        self.state = self.STATE_IDLE
        self.chain_links.clear()
        self.soul_particles.clear()
        self.extension_progress = 0.0
        self.anim_time = 0.0
        
    def is_active(self) -> bool:
        """是否激活"""
        return self.state != self.STATE_IDLE
        
    def get_state(self) -> str:
        """获取当前状态"""
        return self.state


# 全局单例
_soul_chain_instance: Optional[SoulChainEffect] = None


def get_soul_chain_effect() -> SoulChainEffect:
    """获取灵魂锁链特效单例"""
    global _soul_chain_instance
    if _soul_chain_instance is None:
        _soul_chain_instance = SoulChainEffect()
    return _soul_chain_instance


def init_soul_chain(width: int = 800, height: int = 600):
    """便捷初始化"""
    effect = get_soul_chain_effect()
    effect.initialize(width, height)
    return effect