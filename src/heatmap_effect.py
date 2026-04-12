"""
保卫萝卜 - 敌人分布热力图系统
显示防御塔攻击范围内的敌人密度分布
"""
import pygame
import math


class EnemyHeatmap:
    """敌人分布热力图"""
    
    def __init__(self, screen_width, screen_height, cell_size=20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size
        self.cols = (screen_width + cell_size - 1) // cell_size
        self.rows = (screen_height + cell_size - 1) // cell_size
        self.heatmap = [[0.0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.decay_rate = 0.5  # 热力图衰减速率
        self.max_heat = 1.0
        
    def update(self, dt, monsters):
        """更新热力图 - 基于怪物位置"""
        # 衰减现有热力
        for row in range(self.rows):
            for col in range(self.cols):
                self.heatmap[row][col] = max(0, self.heatmap[row][col] - self.decay_rate * dt)
        
        # 添加怪物热源
        for monster in monsters:
            if hasattr(monster, 'x') and hasattr(monster, 'y'):
                col = int(monster.x / self.cell_size)
                row = int(monster.y / self.cell_size)
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    # 怪物位置及周围添加热量
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                                dist = math.sqrt(dr*dr + dc*dc)
                                if dist <= 2:
                                    heat = 1.0 - dist * 0.4
                                    self.heatmap[nr][nc] = min(self.max_heat, 
                                                                self.heatmap[nr][nc] + heat)
    
    def draw(self, screen, alpha=60):
        """绘制热力图（半透明）"""
        for row in range(self.rows):
            for col in range(self.cols):
                heat = self.heatmap[row][col]
                if heat > 0.1:
                    # 颜色从绿色(低)到红色(高)
                    r = int(255 * heat)
                    g = int(255 * (1 - heat))
                    b = 50
                    color = (r, g, b, int(alpha * heat))
                    
                    rect = pygame.Rect(
                        col * self.cell_size,
                        row * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    # 创建半透明表面
                    surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    pygame.draw.rect(surf, color, surf.get_rect())
                    screen.blit(surf, rect)


class TowerRangeIndicator:
    """防御塔攻击范围指示器 - 带敌人密度显示"""
    
    def __init__(self, tower_x, tower_y, attack_range):
        self.x = tower_x
        self.y = tower_y
        self.attack_range = attack_range
        self.pulse_phase = 0
        self.show_enemies = True  # 是否显示范围内敌人
        
    def update(self, dt):
        """更新动画相位"""
        self.pulse_phase += dt * 2
        if self.pulse_phase > 2 * math.pi:
            self.pulse_phase -= 2 * math.pi
    
    def draw(self, screen, enemy_count=0):
        """绘制范围指示器"""
        # 外圈脉动效果
        pulse = 1.0 + 0.1 * math.sin(self.pulse_phase)
        radius = int(self.attack_range * pulse)
        
        # 范围圈底色
        range_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        
        # 根据敌人数量改变颜色
        if enemy_count == 0:
            # 无敌人 - 淡蓝色
            pygame.draw.circle(range_surf, (100, 150, 255, 30), 
                             (radius, radius), radius)
            pygame.draw.circle(range_surf, (100, 150, 255, 60), 
                             (radius, radius), radius, 2)
        elif enemy_count <= 2:
            # 少量敌人 - 黄色
            pygame.draw.circle(range_surf, (255, 200, 100, 40), 
                             (radius, radius), radius)
            pygame.draw.circle(range_surf, (255, 200, 100, 80), 
                             (radius, radius), radius, 2)
        else:
            # 大量敌人 - 红色警告
            pygame.draw.circle(range_surf, (255, 100, 100, 50), 
                             (radius, radius), radius)
            pygame.draw.circle(range_surf, (255, 100, 100, 100), 
                             (radius, radius), radius, 3)
        
        # 显示范围内敌人数量
        if enemy_count > 0 and self.show_enemies:
            font = pygame.font.SysFont("simhei", 16, bold=True)
            text = font.render(f"{enemy_count}", True, (255, 255, 255))
            text_bg = pygame.Surface((text.get_width() + 8, text.get_height() + 4), 
                                    pygame.SRCALPHA)
            pygame.draw.rect(text_bg, (0, 0, 0, 150), text_bg.get_rect())
            text_bg.blit(text, (4, 2))
            screen.blit(text_bg, (self.x - text_bg.get_width() // 2, 
                                 self.y - radius - 25))
        
        screen.blit(range_surf, (self.x - radius, self.y - radius))


class PathHeatmapOverlay:
    """路径热力图覆盖层 - 高亮显示怪物行走路径"""
    
    def __init__(self, path_points, screen_width, screen_height):
        self.path_points = path_points  # [(x, y), ...]
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.intensity = 0.3  # 路径显示强度
        
    def draw(self, screen, active=True):
        """绘制路径热力图"""
        if not active or not self.path_points:
            return
            
        if len(self.path_points) < 2:
            return
            
        # 绘制路径热力线
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            
            # 路径中心线
            pygame.draw.line(screen, (255, 200, 0, 80), p1, p2, 8)
            # 路径发光效果
            pygame.draw.line(screen, (255, 200, 0, 40), p1, p2, 16)
            
        # 标记起点和终点
        start = self.path_points[0]
        end = self.path_points[-1]
        
        # 起点标记 - 绿色
        pygame.draw.circle(screen, (0, 255, 100), start, 12)
        pygame.draw.circle(screen, (0, 255, 100, 100), start, 18)
        
        # 终点标记 - 红色
        pygame.draw.circle(screen, (255, 50, 50), end, 12)
        pygame.draw.circle(screen, (255, 50, 50, 100), end, 18)