# -*- coding: utf-8 -*-
"""防御塔覆盖范围可视化系统
显示所有防御塔的攻击范围和覆盖热力图
"""
import pygame
import math

# 延迟导入 main 以避免循环依赖
def _get_main():
    import main
    return main


class CoverageVisualizer:
    """防御塔覆盖范围可视化"""
    
    def __init__(self):
        self.enabled = False
        self.show_heatmap = True  # 热力图
        self.show_ranges = True   # 范围圈
        self.show_gaps = True     # 空白区域警告
        self.alpha = 200
        self.grid_size = 20  # 热力图网格大小
    
    def toggle(self):
        """切换显示状态"""
        self.enabled = not self.enabled
        return self.enabled
    
    def draw(self, screen, towers, path_points):
        """绘制覆盖可视化"""
        if not self.enabled:
            return
        
        if self.show_heatmap:
            self._draw_heatmap(screen, towers)
        
        if self.show_ranges:
            self._draw_ranges(screen, towers)
        
        if self.show_gaps:
            self._draw_gaps(screen, towers, path_points)
    
    def _draw_heatmap(self, screen, towers):
        """绘制热力图"""
        # 创建网格
        main = _get_main()
        grid_cols = main.SCREEN_WIDTH // self.grid_size
        grid_rows = main.SCREEN_HEIGHT // self.grid_size
        
        # 计算每个格子的覆盖次数
        heatmap = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]
        
        for tower in towers:
            if not tower.alive:
                continue
            range_pixels = tower.range
            
            # 转换塔位置到网格坐标
            tower_grid_x = int(tower.x / self.grid_size)
            tower_grid_y = int(tower.y / self.grid_size)
            range_grids = int(range_pixels / self.grid_size)
            
            # 标记覆盖区域
            for gy in range(max(0, tower_grid_y - range_grids), 
                          min(grid_rows, tower_grid_y + range_grids + 1)):
                for gx in range(max(0, tower_grid_x - range_grids),
                              min(grid_cols, tower_grid_x + range_grids + 1)):
                    dist = math.sqrt((gx - tower_grid_x)**2 + (gy - tower_grid_y)**2)
                    if dist <= range_grids:
                        heatmap[gy][gx] += 1
        
        # 绘制热力图
        for gy in range(grid_rows):
            for gx in range(grid_cols):
                count = heatmap[gy][gx]
                if count > 0:
                    # 颜色从绿到红
                    intensity = min(count / 5, 1.0)
                    color = (
                        int(0 + 255 * intensity),
                        int(255 - 200 * intensity),
                        0,
                        self.alpha // 2
                    )
                    rect = pygame.Rect(
                        gx * self.grid_size,
                        gy * self.grid_size,
                        self.grid_size,
                        self.grid_size
                    )
                    surf = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
                    surf.fill(color)
                    screen.blit(surf, rect)
    
    def _draw_ranges(self, screen, towers):
        """绘制每个塔的范围圈"""
        for tower in towers:
            if not tower.alive:
                continue
            
            # 外圈 - 半透明
            range_surf = pygame.Surface((tower.range * 2, tower.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (*tower.color, 50), 
                             (tower.range, tower.range), tower.range)
            screen.blit(range_surf, (tower.x - tower.range, tower.y - tower.range))
            
            # 边框
            pygame.draw.circle(screen, (*tower.color, 180), 
                             (int(tower.x), int(tower.y)), 
                             int(tower.range), 2)
    
    def _draw_gaps(self, screen, towers, path_points):
        """绘制路径上的空白区域（未被覆盖的危险区域）"""
        if not path_points or not towers:
            return
        
        # 简化：只检查路径上的关键点
        step = max(1, len(path_points) // 20)
        
        for i in range(0, len(path_points), step):
            px, py = path_points[i]
            
            # 检查这个点是否被任何塔覆盖
            covered = False
            for tower in towers:
                if not tower.alive:
                    continue
                dist = math.sqrt((px - tower.x)**2 + (py - tower.y)**2)
                if dist <= tower.range:
                    covered = True
                    break
            
            # 未覆盖显示警告
            if not covered:
                # 闪烁效果
                import time
                if int(time.time() * 3) % 2 == 0:
                    pygame.draw.circle(screen, (255, 50, 50), 
                                     (int(px), int(py)), 8, 2)


# 全局实例
coverage_visualizer = CoverageVisualizer()