"""
保卫萝卜 - 波次公告系统
新波次开始时的视觉公告特效
"""
import pygame
import main


class WaveAnnouncement:
    """波次公告 - 新波次开始时的全屏公告"""
    
    def __init__(self, wave_num, total_waves, monsters_info):
        self.wave_num = wave_num
        self.total_waves = total_waves
        self.monsters_info = monsters_info  # 怪物类型列表
        
        # 动画参数
        self.lifetime = 2.5  # 公告持续时间(秒)
        self.timer = 0
        self.active = True
        
        # 位置和尺寸
        self.center_x = main.SCREEN_WIDTH // 2
        self.center_y = main.SCREEN_HEIGHT // 2
        
        # 缩放动画
        self.scale = 0.0
        self.target_scale = 1.0
        self.scale_speed = 3.0
        
        # 透明度
        self.alpha = 255
        self.fade_start = 1.8  # 开始淡出时间
        
        # 背景框
        self.bg_padding = 40
        
    def update(self, dt):
        """更新公告状态"""
        self.timer += dt
        
        # 缩放动画
        if self.scale < self.target_scale:
            self.scale += dt * self.scale_speed
            self.scale = min(self.scale, self.target_scale)
        
        # 淡出效果
        if self.timer > self.fade_start:
            fade_progress = (self.timer - self.fade_start) / (self.lifetime - self.fade_start)
            self.alpha = int(255 * (1 - fade_progress))
        
        # 结束
        if self.timer >= self.lifetime:
            self.active = False
            
    def draw(self, screen):
        """绘制公告"""
        if not self.active:
            return
            
        # 计算位置
        x = self.center_x
        y = self.center_y
        
        # 背景 - 半透明黑色
        bg_width = 400
        bg_height = 200
        bg_rect = pygame.Rect(
            x - bg_width // 2,
            y - bg_height // 2,
            bg_width,
            bg_height
        )
        
        # 创建半透明背景
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        
        # 缩放变换
        scaled_bg = pygame.transform.smoothscale(
            bg_surface,
            (int(bg_width * self.scale), int(bg_height * self.scale))
        )
        
        # 绘制背景
        scaled_rect = scaled_bg.get_rect(center=(x, y))
        screen.blit(scaled_bg, scaled_rect)
        
        # 边框
        border_rect = scaled_rect.inflate(-10, -10)
        pygame.draw.rect(screen, (255, 200, 50), border_rect, 3, border_radius=10)
        
        # 波次标题
        title_font = pygame.font.SysFont("microsoftyahei", 48, bold=True)
        title_text = f"第 {self.wave_num} 波"
        title_color = (255, 220, 100)
        
        # 临时字体回退
        try:
            title_surface = title_font.render(title_text, True, title_color)
        except:
            title_font = pygame.font.Font(None, 48)
            title_surface = title_font.render(title_text, True, title_color)
            
        title_rect = title_surface.get_rect(center=(x, y - 50))
        title_surface.set_alpha(self.alpha)
        screen.blit(title_surface, title_rect)
        
        # 怪物信息
        info_font = pygame.font.SysFont("microsoftyahei", 24)
        monster_count = len(self.monsters_info)
        info_text = f"来犯: {monster_count} 只怪物"
        
        try:
            info_surface = info_font.render(info_text, True, (200, 200, 200))
        except:
            info_font = pygame.font.Font(None, 24)
            info_surface = info_font.render(info_text, True, (200, 200, 200))
            
        info_rect = info_surface.get_rect(center=(x, y + 20))
        info_surface.set_alpha(self.alpha)
        screen.blit(info_surface, info_rect)
        
        # 底部提示
        tip_font = pygame.font.SysFont("microsoftyahei", 20)
        tip_text = "准备应战!"
        
        try:
            tip_surface = tip_font.render(tip_text, True, (255, 100, 100))
        except:
            tip_font = pygame.font.Font(None, 20)
            tip_surface = tip_font.render(tip_text, True, (255, 100, 100))
            
        tip_rect = tip_surface.get_rect(center=(x, y + 60))
        tip_surface.set_alpha(self.alpha)
        screen.blit(tip_surface, tip_rect)


class WaveAnnouncementManager:
    """波次公告管理器"""
    
    def __init__(self):
        self.announcements = []
        
    def add_announcement(self, wave_num, total_waves, monsters_info):
        """添加新的波次公告"""
        announcement = WaveAnnouncement(wave_num, total_waves, monsters_info)
        self.announcements.append(announcement)
        
    def update(self, dt):
        """更新所有公告"""
        for announcement in self.announcements:
            announcement.update(dt)
            
        # 清理已结束的公告
        self.announcements = [a for a in self.announcements if a.active]
        
    def draw(self, screen):
        """绘制所有公告"""
        for announcement in self.announcements:
            announcement.draw(screen)
            
    def has_active(self):
        """检查是否有活跃公告"""
        return len(self.announcements) > 0


# 全局实例
wave_announcement_manager = WaveAnnouncementManager()