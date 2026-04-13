"""
保卫萝卜 - Boss战斗阶段系统
Boss出现时切换到特殊战斗阶段，增强紧张感和视觉效果
"""
import pygame
import random

class BossPhaseSystem:
    """Boss战斗阶段管理系统"""
    
    def __init__(self):
        self.active = False
        self.boss = None
        self.phase = "normal"  # "normal", "warning", "boss_battle", "victory"
        self.warning_timer = 0
        self.boss_timer = 0
        self.flash_intensity = 0
        self.screen_shake = 0
        self.vignette_alpha = 0
        self.particles = []  # 战斗粒子效果
        self.victory_timer = 0
        
    def start_warning(self):
        """开始Boss警告阶段"""
        if self.phase == "normal":
            self.phase = "warning"
            self.warning_timer = 0
            
    def activate_boss_battle(self, boss):
        """激活Boss战斗阶段"""
        self.boss = boss
        self.phase = "boss_battle"
        self.boss_timer = 0
        self.flash_intensity = 1.0
        self.vignette_alpha = 150
        self.screen_shake = 5
        # 生成战斗粒子
        self._spawn_battle_particles()
        
    def victory(self):
        """Boss战胜/击败"""
        self.phase = "victory"
        self.victory_timer = 0
        self.boss = None
        self.vignette_alpha = 0
        self._spawn_victory_particles()
        
    def reset(self):
        """重置到正常阶段"""
        self.active = False
        self.phase = "normal"
        self.boss = None
        self.particles = []
        
    def update(self, dt):
        """更新阶段状态"""
        if self.phase == "warning":
            self.warning_timer += dt
            self.flash_intensity = 0.3 + 0.7 * (self.warning_timer % 1.0)  # 脉动闪烁
            if self.warning_timer >= 3.0:  # 3秒警告后进入Boss战
                # 实际的Boss激活由外部调用activate_boss_battle处理
                pass
                
        elif self.phase == "boss_battle":
            self.boss_timer += dt
            
            # 更新闪烁
            if self.flash_intensity > 0.3:
                self.flash_intensity -= dt * 0.2
                
            # 更新屏幕震动
            if self.screen_shake > 0:
                self.screen_shake -= dt * 3
                
            # 更新暗角
            if self.vignette_alpha > 50:
                self.vignette_alpha -= dt * 10
                
            # 更新粒子
            self._update_particles(dt)
            
        elif self.phase == "victory":
            self.victory_timer += dt
            self._update_particles(dt)
            if self.victory_timer >= 3.0:
                self.phase = "normal"
                self.particles = []
                
    def _spawn_battle_particles(self):
        """生成战斗粒子"""
        for _ in range(30):
            self.particles.append({
                "x": random.randint(0, 800),
                "y": random.randint(0, 600),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "life": 2.0,
                "color": random.choice([(255, 100, 50), (255, 200, 0), (255, 50, 50)]),
                "size": random.randint(3, 8)
            })
            
    def _spawn_victory_particles(self):
        """生成胜利粒子"""
        for _ in range(50):
            self.particles.append({
                "x": random.randint(0, 800),
                "y": 600,
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-8, -3),
                "life": 3.0,
                "color": random.choice([(255, 215, 0), (255, 255, 100), (100, 255, 100)]),
                "size": random.randint(4, 10),
                "gravity": 0.1
            })
            
    def _update_particles(self, dt):
        """更新粒子"""
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= dt
            if "gravity" in p:
                p["vy"] += p["gravity"]
            if p["life"] <= 0:
                self.particles.remove(p)
                
    def get_screen_offset(self):
        """获取屏幕震动偏移"""
        if self.screen_shake > 0:
            return (
                random.randint(-int(self.screen_shake), int(self.screen_shake)),
                random.randint(-int(self.screen_shake), int(self.screen_shake))
            )
        return (0, 0)
        
    def draw(self, screen):
        """绘制阶段效果"""
        if self.phase == "warning":
            # 警告闪烁
            if int(self.warning_timer * 10) % 2 == 0:
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, int(30 * self.flash_intensity)))
                screen.blit(overlay, (0, 0))
                
        elif self.phase == "boss_battle":
            # 暗角效果
            if self.vignette_alpha > 0:
                self._draw_vignette(screen)
                
            # 战斗粒子
            for p in self.particles:
                pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])
                
        elif self.phase == "victory":
            # 胜利粒子
            for p in self.particles:
                alpha = min(255, int(p["life"] * 85))
                color = (*p["color"][:3], alpha)
                s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
                pygame.draw.circle(s, color, (p["size"], p["size"]), p["size"])
                screen.blit(s, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]))
                
    def _draw_vignette(self, screen):
        """绘制暗角效果"""
        width, height = screen.get_width(), screen.get_height()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 创建径向渐变暗角
        center_x, center_y = width // 2, height // 2
        for r in range(0, max(width, height), 20):
            alpha = min(255, int(self.vignette_alpha * (1 - r / max(width, height))))
            color = (0, 0, 0, alpha)
            pygame.draw.circle(overlay, color, (center_x, center_y), r)
            
        screen.blit(overlay, (0, 0))


# 全局单例
_boss_phase_system = None

def get_boss_phase_system():
    """获取Boss阶段系统单例"""
    global _boss_phase_system
    if _boss_phase_system is None:
        _boss_phase_system = BossPhaseSystem()
    return _boss_phase_system