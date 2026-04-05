"""
UI面板系统 - 处理用户界面交互和显示
"""
import pygame
from typing import Optional, Tuple
from src.config_loader import get_config

class UIPanel:
    """UI面板管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.info_panel_rect = pygame.Rect(
            config.get('ui', {}).get('info_panel', {}).get('x', 10),
            config.get('ui', {}).get('info_panel', {}).get('y', 10),
            config.get('ui', {}).get('info_panel', {}).get('width', 150),
            config.get('ui', {}).get('info_panel', {}).get('height', 580)
        )
        self.tower_buttons_rect = pygame.Rect(
            config.get('ui', {}).get('tower_buttons', {}).get('x', 650),
            config.get('ui', {}).get('tower_buttons', {}).get('y', 10),
            config.get('ui', {}).get('tower_buttons', {}).get('width', 140),
            config.get('ui', {}).get('tower_buttons', {}).get('height', 580)
        )
        self.selected_tower_button = None
        
    def handle_event(self, event, game_state, tower_placement) -> bool:
        """处理UI事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # 检查是否点击了塔按钮
            tower_types = ['箭塔', '炮塔', '魔法塔']
            button_height = 30
            for i, tower_type in enumerate(tower_types):
                button_rect = pygame.Rect(
                    self.tower_buttons_rect.x,
                    self.tower_buttons_rect.y + i * button_height,
                    self.tower_buttons_rect.width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    tower_placement.select_tower(tower_type)
                    self.selected_tower_button = tower_type
                    return True
                    
        return False
        
    def update(self, dt: float, game_state, state_machine):
        """更新UI状态"""
        pass
        
    def draw(self, screen, game_state, state_machine):
        """绘制UI面板"""
        # 绘制信息面板背景（渐变效果）
        gradient_surface = pygame.Surface((self.info_panel_rect.width, self.info_panel_rect.height), pygame.SRCALPHA)
        # 从深蓝到透明的渐变
        for i in range(self.info_panel_rect.height):
            alpha = int(180 * (1 - i / self.info_panel_rect.height))
            pygame.draw.line(gradient_surface, (20, 30, 60, alpha), (0, i), (self.info_panel_rect.width, i))
        screen.blit(gradient_surface, (self.info_panel_rect.x, self.info_panel_rect.y))
        # 金色边框
        pygame.draw.rect(screen, (255, 215, 0), self.info_panel_rect, 2)
        
        # 绘制信息
        info_y = self.info_panel_rect.y + 10
        money_text = self.font.render(f"💰 {game_state.money}", True, (255, 255, 255))
        lives_text = self.font.render(f"❤️ {game_state.lives}", True, (255, 255, 255))
        wave_text = self.font.render(f"🌊 第{game_state.wave}波", True, (255, 255, 255))
        level_text = self.font.render(f"📺 {game_state.level}关", True, (255, 255, 255))
        
        screen.blit(money_text, (self.info_panel_rect.x + 10, info_y))
        screen.blit(lives_text, (self.info_panel_rect.x + 10, info_y + 30))
        screen.blit(wave_text, (self.info_panel_rect.x + 10, info_y + 60))
        screen.blit(level_text, (self.info_panel_rect.x + 10, info_y + 90))
        
        # 绘制选中塔的升级信息
        if hasattr(game_state, 'selected_tower') and game_state.selected_tower:
            tower = game_state.selected_tower
            upgrade_cost = tower.get_upgrade_cost()
            
            if tower.can_upgrade():
                upgrade_text = self.small_font.render(f"升级: 💰{upgrade_cost}", True, (255, 255, 0))
                upgrade_info = self.small_font.render(f"按U键升级", True, (255, 255, 255))
                
                screen.blit(upgrade_text, (self.info_panel_rect.x + 10, info_y + 120))
                screen.blit(upgrade_info, (self.info_panel_rect.x + 10, info_y + 140))
                
                level_text = self.small_font.render(f"等级: {tower.level}/{tower.max_level}", True, (255, 255, 255))
                screen.blit(level_text, (self.info_panel_rect.x + 10, info_y + 160))
            else:
                max_level_text = self.small_font.render(f"已满级 ({tower.max_level})", True, (255, 255, 0))
                screen.blit(max_level_text, (self.info_panel_rect.x + 10, info_y + 120))
        
        # 绘制塔按钮面板背景（渐变）
        gradient_surface2 = pygame.Surface((self.tower_buttons_rect.width, self.tower_buttons_rect.height), pygame.SRCALPHA)
        for i in range(self.tower_buttons_rect.height):
            alpha = int(180 * (1 - i / self.tower_buttons_rect.height))
            pygame.draw.line(gradient_surface2, (60, 30, 20, alpha), (0, i), (self.tower_buttons_rect.width, i))
        screen.blit(gradient_surface2, (self.tower_buttons_rect.x, self.tower_buttons_rect.y))
        # 金色边框
        pygame.draw.rect(screen, (255, 215, 0), self.tower_buttons_rect, 2)
        
        # 绘制塔选择按钮
        tower_types = ['箭塔', '炮塔', '魔法塔']
        button_height = 30
        for i, tower_type in enumerate(tower_types):
            button_rect = pygame.Rect(
                self.tower_buttons_rect.x,
                self.tower_buttons_rect.y + i * button_height,
                self.tower_buttons_rect.width,
                button_height
            )
            
            # 高亮选中的按钮
            if self.selected_tower_button == tower_type:
                pygame.draw.rect(screen, (255, 255, 0), button_rect)
            else:
                pygame.draw.rect(screen, (100, 100, 100), button_rect)
                
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 1)
            
            # 绘制按钮文本
            tower_info = self.config.get('towers', {}).get(tower_type, {})
            cost = tower_info.get('cost', 0)
            text = self.small_font.render(f"{tower_type} 💰{cost}", True, (255, 255, 255))
            screen.blit(text, (button_rect.x + 5, button_rect.y + 5))
            
        # 绘制波次信息
        if hasattr(game_state, 'wave_manager') and game_state.wave_manager:
            if game_state.wave_manager.is_waving:
                wave_text = self.font.render(f"🌊 波次 {game_state.wave_manager.current_wave + 1}", True, (255, 255, 255))
                screen.blit(wave_text, (screen.get_width() // 2 - 80, 50))
                
        # 绘制游戏结束画面
        if hasattr(game_state, 'game_over') and game_state.game_over:
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("💀 GAME OVER", True, (255, 0, 0))
            restart_text = self.small_font.render("按 R 重新开始", True, (255, 255, 255))
            
            screen.blit(game_over_text, (screen.get_width() // 2 - 100, screen.get_height() // 2 - 20))
            screen.blit(restart_text, (screen.get_width() // 2 - 60, screen.get_height() // 2 + 20))