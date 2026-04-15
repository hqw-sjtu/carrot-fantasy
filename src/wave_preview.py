# -*- coding: utf-8 -*-
"""波次预览系统 - Wave Preview System

在每波开始前显示即将到来的怪物信息，让玩家提前做好防御准备。
"""

import pygame
import random


class WavePreview:
    """波次预览显示"""
    
    def __init__(self):
        self.visible = False
        self.current_wave = 0
        self.preview_time = 0
        self.max_preview_time = 5.0  # 预览5秒
        self.monster_counts = {}  # {monster_type: count}
        self.total_enemies = 0
        self.difficulty = 1.0
        self.animation_offset = 0
        self.icons = {
            "小怪物": "🐛",
            "中怪物": "🦂", 
            "大怪物": "👹",
            "Boss": "👺",
            "快速怪": "⚡",
            "装甲怪": "🛡️",
            "超级Boss": "💀",
        }
        
    def show_preview(self, wave_num, waves_config, difficulty=1.0):
        """显示波次预览
        
        Args:
            wave_num: 波次编号
            waves_config: 波次配置列表
            difficulty: 难度系数
        """
        if wave_num >= len(waves_config):
            return False
            
        self.current_wave = wave_num
        self.difficulty = difficulty
        self.monster_counts = {}
        self.total_enemies = 0
        
        wave_data = waves_config[wave_num]
        for monster_type, count in wave_data.get("monsters", []):
            actual_count = int(count * difficulty)
            self.monster_counts[monster_type] = actual_count
            self.total_enemies += actual_count
            
        self.preview_time = 0
        self.visible = True
        return True
    
    def update(self, dt):
        """更新预览状态"""
        if not self.visible:
            return
            
        self.preview_time += dt
        self.animation_offset += dt * 20
        
        if self.preview_time >= self.max_preview_time:
            self.visible = False
            
    def draw(self, screen):
        """绘制波次预览"""
        if not self.visible:
            return
            
        width, height = screen.get_size()
        
        # 计算透明度（淡入淡出）
        fade_duration = 0.5
        if self.preview_time < fade_duration:
            alpha = int(255 * (self.preview_time / fade_duration))
        elif self.preview_time > self.max_preview_time - fade_duration:
            alpha = int(255 * ((self.max_preview_time - self.preview_time) / fade_duration))
        else:
            alpha = 255
            
        # 背景面板
        panel_width = 400
        panel_height = 250
        panel_x = (width - panel_width) // 2
        panel_y = (height - panel_height) // 2
        
        # 绘制背景
        bg_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_color = (20, 20, 40, min(230, alpha))
        pygame.draw.rect(bg_surface, bg_color, (0, 0, panel_width, panel_height), border_radius=20)
        
        # 边框
        border_color = (100, 150, 255, min(255, alpha))
        pygame.draw.rect(bg_surface, border_color, (0, 0, panel_width, panel_height), 3, border_radius=20)
        
        screen.blit(bg_surface, (panel_x, panel_y))
        
        # 标题
        title = f"第 {self.current_wave + 1} 波即将来袭！"
        title_font = pygame.font.SysFont("simhei", 28, bold=True)
        title_surface = title_font.render(title, True, (255, 200, 50, alpha))
        title_rect = title_surface.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        screen.blit(title_surface, title_rect)
        
        # 难度提示
        if self.difficulty > 1.0:
            diff_text = f"⚠️ 难度: {self.difficulty:.1f}x"
            diff_font = pygame.font.SysFont("simhei", 18)
            diff_surface = diff_font.render(diff_text, True, (255, 100, 100, alpha))
            screen.blit(diff_surface, (panel_x + 20, panel_y + 70))
        
        # 怪物列表
        y_offset = panel_y + 100
        font = pygame.font.SysFont("simhei", 20)
        
        # 排序：先Boss后大怪再中怪小怪
        priority = {"超级Boss": 0, "Boss": 1, "装甲怪": 2, "大怪物": 3, "快速怪": 4, "中怪物": 5, "小怪物": 6}
        sorted_monsters = sorted(self.monster_counts.items(), 
                                 key=lambda x: priority.get(x[0], 99))
        
        for monster_type, count in sorted_monsters:
            icon = self.icons.get(monster_type, "❓")
            text = f"{icon} {monster_type}: {count}只"
            
            # 动画效果：轻微摇摆
            shake_x = random.uniform(-2, 2) if self.animation_offset % 10 < 5 else 0
            
            text_surface = font.render(text, True, (220, 220, 220, alpha))
            screen.blit(text_surface, (panel_x + 30 + shake_x, y_offset))
            y_offset += 30
            
        # 底部提示
        time_left = int(self.max_preview_time - self.preview_time) + 1
        tip_text = f"准备好防御！ ({time_left}s)"
        tip_font = pygame.font.SysFont("simhei", 16)
        tip_surface = tip_font.render(tip_text, True, (150, 200, 255, alpha))
        tip_rect = tip_surface.get_rect(center=(panel_x + panel_width//2, panel_y + panel_height - 25))
        screen.blit(tip_surface, tip_rect)


class WavePreviewManager:
    """波次预览管理器（集成到游戏）"""
    
    def __init__(self):
        self.preview = WavePreview()
        self.countdown = 0
        self.countdown_active = False
        self.wave_started = False
        self.waves_config = []
        
    def set_waves_config(self, waves_config):
        """设置波次配置"""
        self.waves_config = waves_config
        
    def trigger_countdown(self, wave_num, waves_config, difficulty=1.0):
        """触发波次倒计时预览"""
        self.waves_config = waves_config
        self.preview.show_preview(wave_num, waves_config, difficulty)
        self.countdown_active = True
        self.wave_started = False
        
    def update(self, dt):
        """更新预览"""
        self.preview.update(dt)
        
        if self.preview.visible:
            # 预览进行中
            pass
        elif self.countdown_active and not self.wave_started:
            # 预览结束，开始波次
            self.wave_started = True
            self.countdown_active = False
            return True  # 返回True表示波次可以开始
            
        return False
        
    def draw(self, screen):
        """绘制预览"""
        self.preview.draw(screen)


# ========== 测试 ==========
if __name__ == "__main__":
    import sys
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("波次预览测试")
    clock = pygame.time.Clock()
    
    # 测试波次配置
    test_waves = [
        {"monsters": [("小怪物", 5)], "interval": 1.0},
        {"monsters": [("小怪物", 8), ("中怪物", 2)], "interval": 0.8},
        {"monsters": [("中怪物", 5), ("大怪物", 1)], "interval": 0.6},
        {"monsters": [("大怪物", 3), ("Boss", 1)], "interval": 0.5},
    ]
    
    manager = WavePreviewManager()
    manager.trigger_countdown(2, test_waves, difficulty=1.2)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    manager.trigger_countdown(0, test_waves)
        
        manager.update(dt)
        
        screen.fill((40, 40, 60))
        manager.draw(screen)
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()