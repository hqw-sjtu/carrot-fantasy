# UI美化功能集合

import pygame
import math

# UI动画系统
ui_animations = {}
ui_pulse_time = 0

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """创建渐变表面"""
    surface = pygame.Surface((width, height))
    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
    return surface

def draw_rounded_rect(surface, color, rect, radius, border=0, border_color=None):
    """绘制圆角矩形"""
    x, y, w, h = rect
    # 绘制主体
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    # 绘制边框
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

def add_glow_effect(surface, x, y, radius, color, intensity=0.3):
    """添加发光效果"""
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i in range(int(radius * 2), 0, -2):
        alpha = int(intensity * 255 * (1 - i / (radius * 2)))
        pygame.draw.circle(glow_surf, (*color, max(0, alpha)), (radius * 2, radius * 2), i)
    surface.blit(glow_surf, (x - radius * 2, y - radius * 2))

def draw_ui_panel_bg(x, y, w, h, radius=15, alpha=220):
    """绘制带阴影和渐变的UI面板背景"""
    # 阴影
    shadow_offset = 4
    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (0, 0, w, h), border_radius=radius)
    SCREEN.blit(shadow_surf, (x + shadow_offset, y + shadow_offset))
    
    # 主体背景（半透明渐变）
    bg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # 渐变背景
    gradient = create_gradient_surface(w, h, (40, 50, 70), (30, 35, 50))
    bg_surf.blit(gradient, (0, 0))
    # 添加半透明遮罩
    for px in range(w):
        for py in range(h):
            r, g, b = bg_surf.get_at((px, py))[:3]
            bg_surf.set_at((px, py), (r, g, b, alpha))
    SCREEN.blit(bg_surf, (x, y))
    # 边框
    pygame.draw.rect(SCREEN, (100, 120, 160), (x, y, w, h), 2, border_radius=radius)
    # 高光边框
    pygame.draw.rect(SCREEN, (80, 90, 110), (x + 1, y + 1, w - 2, h - 2), 1, border_radius=radius - 1)