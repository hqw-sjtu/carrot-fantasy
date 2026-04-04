"""
防御塔放置系统 - 处理防御塔的选择和放置
"""
import pygame
from typing import Optional, Tuple, List

class TowerPlacement:
    """防御塔放置管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.selected_tower: Optional[str] = None
        self.placement_valid = False
        self.hover_pos: Optional[Tuple[int, int]] = None
        self.upgrade_mode = False
        self.selected_tower_obj = None
        
    def select_tower(self, tower_type: str):
        """选择防御塔类型"""
        self.selected_tower = tower_type
        self.upgrade_mode = False
        self.selected_tower_obj = None
    
    def select_tower_for_upgrade(self, tower):
        """选择要升级的防御塔"""
        self.selected_tower = None
        self.upgrade_mode = True
        self.selected_tower_obj = tower
    
    def get_selected_tower(self) -> Optional[str]:
        """获取当前选择的防御塔"""
        return self.selected_tower
        
    def clear_selection(self):
        """清除选择"""
        self.selected_tower = None
        
    def get_selected_tower(self) -> Optional[str]:
        """获取当前选择的防御塔"""
        return self.selected_tower
    
    def is_in_play_area(self, x: int, y: int) -> bool:
        """检查是否在可放置区域"""
        path = self.config.get('path', {})
        start = path.get('start', [100, 300])
        path_width = path.get('width', 100)
        
        # 检查是否在路径上
        if start[1] - path_width//2 <= y <= start[1] + path_width//2:
            if start[0] - 300 <= x <= start[0] + 300:
                return False
        
        # 检查是否在游戏区域
        screen = self.config.get('screen', {})
        return 0 <= x < screen.get('SCREEN_WIDTH', 800) and 0 <= y < screen.get('SCREEN_HEIGHT', 600)
    
    def can_place(self, x: int, y: int, existing_towers: List) -> bool:
        """检查是否可以放置防御塔"""
        if not self.selected_tower:
            return False
            
        if not self.is_in_play_area(x, y):
            return False
            
        # 检查与其他防御塔的距离
        for tower in existing_towers:
            dx = tower.x - x
            dy = tower.y - y
            if (dx*dx + dy*dy) ** 0.5 < 30:  # 最小间距
                return False
                
        return True
    
    def handle_event(self, event, game_state) -> bool:
        """处理事件，返回是否放置了防御塔或升级了防御塔"""
        if event.type == pygame.MOUSEMOTION:
            self.hover_pos = event.pos
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 升级模式：选择要升级的防御塔
            if self.upgrade_mode:
                x, y = event.pos
                for tower in game_state.towers:
                    dx = tower.x - x
                    dy = tower.y - y
                    if (dx*dx + dy*dy) ** 0.5 < 15:  # 点击防御塔范围内
                        self.selected_tower_obj = tower
                        return True  # 选择了要升级的防御塔
                return False
                
            # 放置模式：放置防御塔
            elif self.selected_tower:
                x, y = event.pos
                
                # 检查金币是否足够
                tower_info = self.config.get('towers', {}).get(self.selected_tower, {})
                cost = tower_info.get('cost', 0)
                
                if game_state.money >= cost and self.can_place(x, y, game_state.towers):
                    return True  # 允许放置
                    
        return False
    
    def draw_placement_preview(self, screen, game_state):
        """绘制放置预览和升级预览"""
        if not self.hover_pos:
            return
            
        x, y = self.hover_pos
        
        # 升级模式：绘制选中的防御塔高亮
        if self.upgrade_mode and self.selected_tower_obj:
            tower = self.selected_tower_obj
            # 绘制升级高亮
            pygame.draw.circle(screen, (255, 255, 0), (tower.x, tower.y), 22, 3)
            
        # 放置模式：绘制防御塔预览
        elif self.selected_tower:
            can_place = self.can_place(x, y, game_state.towers)
            
            # 绘制预览圆圈
            color = (0, 255, 0) if can_place else (255, 0, 0)
            alpha = 100 if can_place else 50
            
            # 获取防御塔范围
            tower_info = self.config.get('towers', {}).get(self.selected_tower, {})
            radius = int(tower_info.get('range', 2.0) * 50)
            
            # 绘制半透明预览
            preview_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(preview_surface, (*color, alpha), (radius, radius), radius)
            screen.blit(preview_surface, (x - radius, y - radius))
            
            # 绘制防御塔预览
            tower_color = tower_info.get('color', 'BLUE')
            color_map = {'BLUE': (0, 0, 255), 'RED': (255, 0, 0), 'PURPLE': (128, 0, 128)}
            pygame.draw.circle(screen, color_map.get(tower_color, (0, 0, 255)), (x, y), 15)