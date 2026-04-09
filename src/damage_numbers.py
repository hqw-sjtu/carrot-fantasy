"""
保卫萝卜 - 伤害数字系统
Carrot Fantasy - Damage Numbers System
"""
import pygame
import random


class DamageNumber:
    """伤害数字"""
    
    def __init__(self, x, y, damage, is_crit=False, is_heal=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_crit = is_crit
        self.is_heal = is_heal
        self.lifetime = 1.0  # 存活时间（秒）
        self.max_lifetime = 1.0
        self.vy = -50  # 向上飘动速度
        self.scale = 1.5 if is_crit else 1.0
        
    def update(self, dt):
        """更新位置和透明度"""
        self.y += self.vy * dt
        self.lifetime -= dt
        # 减速
        self.vy *= 0.95
        return self.lifetime > 0
    
    def draw(self, screen):
        """绘制伤害数字"""
        if self.lifetime <= 0:
            return
            
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # 选择颜色
        if self.is_heal:
            color = (50, 255, 50)  # 绿色（治疗）
        elif self.is_crit:
            color = (255, 100, 0)  # 橙色（暴击）
        else:
            color = (255, 255, 255)  # 白色（普通伤害）
        
        # 字体大小
        base_size = 24 if self.is_crit else 18
        font = pygame.font.Font(None, int(base_size * self.scale * 2))
        
        # 暴击时添加闪光特效
        if self.is_crit:
            # 绘制闪光背景
            flash_radius = 20 + (self.lifetime / self.max_lifetime) * 15
            flash_surface = pygame.Surface((int(flash_radius * 4), int(flash_radius * 4)), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (255, 200, 0, 100), (int(flash_radius * 2), int(flash_radius * 2)), int(flash_radius))
            screen.blit(flash_surface, (self.x - flash_radius * 2, self.y - flash_radius * 2))
        
        # 创建带阴影的文字
        text = str(int(self.damage))
        
        # 阴影
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_surf.set_alpha(alpha)
        screen.blit(shadow_surf, (self.x + 2, self.y + 2))
        
        # 主文字
        main_surf = font.render(text, True, color)
        main_surf.set_alpha(alpha)
        screen.blit(main_surf, (self.x, self.y))
        
        # 暴击特效（星星）
        if self.is_crit and self.lifetime > self.max_lifetime * 0.5:
            star_size = int(8 * (self.lifetime / self.max_lifetime))
            pygame.draw.polygon(screen, (255, 255, 0), [
                (self.x - 15, self.y + 10),
                (self.x - 10, self.y + 5),
                (self.x - 15, self.y),
                (self.x - 10, self.y + 5),
            ])


class DamageNumberManager:
    """伤害数字管理器"""
    
    def __init__(self):
        self.damage_numbers = []
        self.max_count = 50  # 最多显示50个
        # 连击系统
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_max_time = 2.0  # 连击有效时间（秒）
        self.combo_display_x = 0
        self.combo_display_y = 0
        
    def add_damage(self, x, y, damage, is_crit=False, is_heal=False):
        """添加伤害数字"""
        if len(self.damage_numbers) >= self.max_count:
            # 移除最旧的
            self.damage_numbers.pop(0)
        
        # 随机偏移，避免重叠
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-5, 5)
        
        dmg = DamageNumber(x + offset_x, y + offset_y, damage, is_crit, is_heal)
        self.damage_numbers.append(dmg)
        
        # 更新连击显示位置
        self.combo_display_x = x
        self.combo_display_y = y - 30
        
        # 如果不是治疗，更新连击
        if not is_heal:
            if self.combo_timer > 0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.combo_timer = self.combo_max_time
    
    def update(self, dt):
        """更新所有伤害数字"""
        self.damage_numbers = [dmg for dmg in self.damage_numbers if dmg.update(dt)]
        # 更新连击计时器
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
        
    def draw(self, screen):
        """绘制所有伤害数字"""
        for dmg in self.damage_numbers:
            dmg.draw(screen)
        
        # 绘制连击数
        if self.combo_count >= 2 and self.combo_timer > 0:
            self._draw_combo(screen)
    
    def _draw_combo(self, screen):
        """绘制连击数显示"""
        import pygame
        font = pygame.font.Font(None, 36)
        combo_text = f"{self.combo_count}x COMBO!"
        
        # 根据连击数变色
        if self.combo_count >= 10:
            color = (255, 0, 255)  # 紫色
        elif self.combo_count >= 5:
            color = (255, 215, 0)  # 金色
        else:
            color = (0, 255, 255)  # 青色
        
        # 闪烁效果
        pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250
        scale = 1.0 + pulse * 0.2
        
        # 阴影
        shadow = font.render(combo_text, True, (0, 0, 0))
        screen.blit(shadow, (self.combo_display_x + 2, self.combo_display_y + 2))
        
        # 主文字
        text = font.render(combo_text, True, color)
        # 放大效果
        if scale > 1.0:
            w, h = text.get_size()
            text = pygame.transform.scale(text, (int(w * scale), int(h * scale)))
        screen.blit(text, (self.combo_display_x, self.combo_display_y))
    
    def clear(self):
        """清空所有伤害数字"""
        self.damage_numbers.clear()
        self.combo_count = 0
        self.combo_timer = 0