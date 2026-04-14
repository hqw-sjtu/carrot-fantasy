"""
保卫萝卜 - 技能冷却显示系统
为终极技能提供视觉化冷却指示器
"""
import pygame
import math


class SkillCooldownDisplay:
    """技能冷却显示组件"""
    
    def __init__(self, x, y, size=60):
        self.x = x
        self.y = y
        self.size = size
        self.font = pygame.font.SysFont("microsoftyahei", 14, bold=True)
        self.skill = None
        self.ready_pulse = 0  # 就绪时脉冲动画
        
    def set_skill(self, skill):
        """绑定技能"""
        self.skill = skill
        
    def update(self, dt):
        """更新动画状态"""
        if self.skill and self.skill.is_ready():
            self.ready_pulse = (self.ready_pulse + dt * 3) % (2 * math.pi)
        else:
            self.ready_pulse = 0
    
    def draw(self, screen):
        """绘制冷却指示器"""
        if not self.skill:
            return
            
        cx, cy = self.x + self.size // 2, self.y + self.size // 2
        radius = self.size // 2 - 4
        
        # 背景圆形
        pygame.draw.circle(screen, (40, 40, 50), (cx, cy), radius + 2)
        
        # 冷却进度背景
        bg_color = (30, 30, 40)
        pygame.draw.circle(screen, bg_color, (cx, cy), radius)
        
        # 计算冷却进度
        if self.skill.current_cooldown > 0:
            # 冷却中 - 绘制扇形
            progress = 1 - (self.skill.current_cooldown / self.skill.cooldown)
            if progress > 0:
                start_angle = -math.pi / 2
                end_angle = start_angle + 2 * math.pi * progress
                
                # 冷却进度扇形
                points = [(cx, cy)]
                segments = 30
                for i in range(segments + 1):
                    angle = start_angle + (end_angle - start_angle) * i / segments
                    px = cx + radius * math.cos(angle)
                    py = cy + radius * math.sin(angle)
                    points.append((px, py))
                    
                if len(points) > 2:
                    pygame.draw.polygon(screen, (80, 120, 200), points)
                    
            # 剩余冷却时间文字
            cd_text = f"{self.skill.current_cooldown:.1f}"
            text = self.font.render(cd_text, True, (180, 180, 180))
            text_rect = text.get_rect(center=(cx, cy))
            screen.blit(text, text_rect)
            
        else:
            # 就绪状态 - 脉冲光效
            pulse_alpha = int(100 + 100 * math.sin(self.ready_pulse))
            
            # 外圈脉冲
            pulse_radius = radius + 3 + 2 * math.sin(self.ready_pulse)
            pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surface, (100, 200, 255, pulse_alpha), 
                             (pulse_radius, pulse_radius), pulse_radius - 2)
            screen.blit(pulse_surface, (cx - pulse_radius, cy - pulse_radius))
            
            # 中心就绪指示
            pygame.draw.circle(screen, (80, 200, 120), (cx, cy), radius)
            
            # "READY" 文字
            ready_text = self.font.render("就绪", True, (255, 255, 255))
            text_rect = ready_text.get_rect(center=(cx, cy))
            screen.blit(ready_text, text_rect)
            
        # 技能名称
        name_text = self.font.render(self.skill.name, True, (220, 220, 220))
        name_rect = name_text.get_rect(midtop=(cx, self.y + self.size + 4))
        screen.blit(name_text, name_rect)
        
        # 边框
        border_color = (100, 180, 255) if self.skill.is_ready() else (80, 80, 100)
        pygame.draw.circle(screen, border_color, (cx, cy), radius + 2, 2)


class SkillBar:
    """技能栏 - 管理多个技能冷却显示"""
    
    def __init__(self, x, y, skill_size=50, spacing=10):
        self.x = x
        self.y = y
        self.skill_size = skill_size
        self.spacing = spacing
        self.slots = []
        
    def add_skill(self, skill):
        """添加技能到栏位"""
        slot_x = self.x + len(self.slots) * (self.skill_size + self.spacing)
        display = SkillCooldownDisplay(slot_x, self.y, self.skill_size)
        display.set_skill(skill)
        self.slots.append(display)
        
    def update(self, dt):
        """更新所有技能显示"""
        for slot in self.slots:
            slot.update(dt)
            
    def draw(self, screen):
        """绘制技能栏"""
        # 背景条
        bg_width = len(self.slots) * (self.skill_size + self.spacing) - self.spacing + 20
        bg_height = self.skill_size + 40
        bg_rect = pygame.Rect(self.x - 10, self.y - 5, bg_width, bg_height)
        
        # 半透明背景
        s = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        s.fill((20, 20, 30, 180))
        screen.blit(s, (self.x - 10, self.y - 5))
        
        # 绘制每个技能槽
        for slot in self.slots:
            slot.draw(screen)
            
    def get_skill_by_index(self, index):
        """通过索引获取技能"""
        if 0 <= index < len(self.slots):
            return self.slots[index].skill
        return None