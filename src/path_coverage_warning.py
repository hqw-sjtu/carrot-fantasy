"""
保卫萝卜 - 路径覆盖预警系统
防御塔放置时显示攻击范围是否覆盖怪物路径
"""
import pygame
import math


class PathCoverageWarning:
    """路径覆盖预警 - 防御塔放置时显示路径覆盖情况"""
    
    def __init__(self):
        self.active = False
        self.tower_pos = None
        self.tower_range = 0
        self.path_segments = []  # 怪物路径段
        self.coverage_ratio = 0  # 覆盖比例 0-1
        
    def set_path(self, path_points):
        """设置怪物路径点"""
        self.path_points = path_points
        self._calculate_path_segments()
        
    def _calculate_path_segments(self):
        """计算路径段（从路径点生成线段）"""
        if not hasattr(self, 'path_points') or len(self.path_points) < 2:
            return
            
        self.path_segments = []
        for i in range(len(self.path_points) - 1):
            self.path_segments.append({
                'start': self.path_points[i],
                'end': self.path_points[i + 1]
            })
    
    def update_preview(self, tower_x, tower_y, tower_range, grid_size=40):
        """更新预览状态"""
        self.active = True
        self.tower_pos = (tower_x, tower_y)
        self.tower_range = tower_range * grid_size  # 转换为像素
        
        # 计算路径覆盖
        self._calculate_coverage()
        
    def _calculate_coverage(self):
        """计算防御塔范围对路径的覆盖程度"""
        if not self.path_segments or not self.tower_pos:
            self.coverage_ratio = 0
            return
            
        covered_length = 0
        total_length = 0
        
        for segment in self.path_segments:
            # 线段长度
            dx = segment['end'][0] - segment['start'][0]
            dy = segment['end'][1] - segment['start'][1]
            length = math.sqrt(dx*dx + dy*dy)
            total_length += length
            
            # 检查线段与圆的距离
            if self._segment_intersects_circle(segment, self.tower_pos, self.tower_range):
                covered_length += length
                
        self.coverage_ratio = covered_length / total_length if total_length > 0 else 0
        
    def _segment_intersects_circle(self, segment, circle_center, radius):
        """检查线段是否与圆相交"""
        # 使用距离公式判断
        ax, ay = segment['start']
        bx, by = segment['end']
        cx, cy = circle_center
        
        # 线段向量
        ab_x = bx - ax
        ab_y = by - ay
        
        # 起点到圆心向量
        ac_x = cx - ax
        ac_y = cy - ay
        
        # 投影长度
        t = (ac_x * ab_x + ac_y * ab_y) / (ab_x * ab_x + ab_y * ab_y + 1e-6)
        t = max(0, min(1, t))
        
        # 最近点
        nearest_x = ax + t * ab_x
        nearest_y = ay + t * ab_y
        
        # 距离
        dist = math.sqrt((nearest_x - cx)**2 + (nearest_y - cy)**2)
        
        return dist <= radius
    
    def draw(self, screen):
        """绘制路径覆盖预警"""
        if not self.active or not self.tower_pos:
            return
            
        x, y = self.tower_pos
        radius = self.tower_range
        
        # 根据覆盖程度选择颜色
        if self.coverage_ratio >= 0.7:
            # 高度覆盖 - 绿色（最佳位置）
            fill_color = (50, 200, 50, 40)
            border_color = (50, 200, 50, 180)
            status = "⭐ 最佳位置！"
        elif self.coverage_ratio >= 0.4:
            # 中度覆盖 - 黄色（良好位置）
            fill_color = (255, 200, 50, 40)
            border_color = (255, 200, 50, 180)
            status = "✓ 良好位置"
        else:
            # 低覆盖 - 红色（警告）
            fill_color = (255, 100, 100, 40)
            border_color = (255, 100, 100, 180)
            status = "⚠ 覆盖不足"
        
        # 绘制填充圆
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, fill_color, (radius, radius), radius)
        screen.blit(s, (x - radius, y - radius))
        
        # 绘制边框
        pygame.draw.circle(screen, border_color, (x, y), radius, 3)
        
        # 绘制路径覆盖区域（高亮显示被覆盖的路径段）
        self._draw_covered_path(screen)
        
        # 显示覆盖率文字
        font = pygame.font.Font(None, 24)
        text = font.render(f"{status} {int(self.coverage_ratio*100)}%", True, border_color[:3])
        screen.blit(text, (x + radius + 10, y - 10))
        
    def _draw_covered_path(self, screen):
        """绘制被覆盖的路径段"""
        if not self.path_segments:
            return
            
        for segment in self.path_segments:
            if self._segment_intersects_circle(segment, self.tower_pos, self.tower_range):
                # 高亮被覆盖的路径段
                pygame.draw.line(screen, (255, 255, 0), 
                               segment['start'], segment['end'], 4)
                
    def clear(self):
        """清除预览"""
        self.active = False
        self.tower_pos = None


# 全局实例（供主游戏调用）
_global_warning = None

def get_path_coverage_warning():
    """获取全局路径覆盖预警实例"""
    global _global_warning
    if _global_warning is None:
        _global_warning = PathCoverageWarning()
    return _global_warning