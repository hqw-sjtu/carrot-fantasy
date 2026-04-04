#!/usr/bin/env python3
"""
测试背景美化效果
"""
import pygame
import sys
import time

# 初始化pygame
pygame.init()
pygame.font.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("背景美化测试")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GRASS_DARK = (0, 100, 0)
GRASS_LIGHT = (50, 205, 50)
PATH_BROWN = (139, 69, 19)
PATH_LIGHT_BROWN = (160, 120, 90)
FLOWER_PINK = (255, 182, 193)
FLOWER_YELLOW = (255, 255, 0)
STONE_GRAY = (105, 105, 105)

# 复制主文件中的背景绘制函数
def draw_gradient_sky():
    """绘制渐变天空"""
    for y in range(0, 300):  # 天空部分高度
        # 计算渐变比例
        ratio = y / 300.0
        # 从浅蓝色到白色渐变
        r = int(SKY_BLUE[0] * (1 - ratio) + WHITE[0] * ratio)
        g = int(SKY_BLUE[1] * (1 - ratio) + WHITE[1] * ratio)
        b = int(SKY_BLUE[2] * (1 - ratio) + WHITE[2] * ratio)
        color = (r, g, b)
        pygame.draw.line(SCREEN, color, (0, y), (SCREEN_WIDTH, y))

def draw_grass_texture():
    """绘制草地纹理"""
    # 先绘制基础草地颜色
    pygame.draw.rect(SCREEN, GRASS_LIGHT, (0, 300, SCREEN_WIDTH, SCREEN_HEIGHT - 300))
    
    # 添加草地质感小方块
    for i in range(0, SCREEN_WIDTH, 10):
        for j in range(300, SCREEN_HEIGHT, 10):
            # 随机深浅绿色
            if (i + j) % 20 < 10:
                grass_color = GRASS_DARK
            else:
                grass_color = GRASS_LIGHT
            
            # 随机偏移使草地看起来更自然
            offset_x = (i + j) % 7 - 3
            offset_y = (i * 2 - j) % 5 - 2
            
            pygame.draw.rect(SCREEN, grass_color, 
                            (i + offset_x, j + offset_y, 8, 8))

def draw_path_with_details():
    """绘制带细节的路径"""
    # 主路径
    pygame.draw.rect(SCREEN, PATH_BROWN, (100, 250, 600, 100))
    
    # 路径边缘细节
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (95, 245, 610, 10))  # 上边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (95, 345, 610, 10))  # 下边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (90, 250, 10, 100))  # 左边缘
    pygame.draw.rect(SCREEN, PATH_LIGHT_BROWN, (695, 250, 10, 100))  # 右边缘
    
    # 路径纹理细节
    for i in range(10):
        x = 120 + i * 60
        y = 270 + (i % 3) * 20
        pygame.draw.ellipse(SCREEN, PATH_LIGHT_BROWN, (x, y, 40, 15))

def draw_decorations():
    """绘制装饰元素"""
    # 随机位置的小花
    flower_positions = [
        (50, 400), (150, 450), (250, 380), (350, 420), 
        (450, 390), (550, 440), (650, 410), (750, 380)
    ]
    
    for x, y in flower_positions:
        # 随机选择花色
        if (x + y) % 3 == 0:
            flower_color = FLOWER_PINK
        else:
            flower_color = FLOWER_YELLOW
        
        # 绘制花朵
        pygame.draw.circle(SCREEN, flower_color, (x, y), 6)
        # 绘制花心
        pygame.draw.circle(SCREEN, FLOWER_YELLOW, (x, y), 2)
    
    # 随机位置的小石头
    stone_positions = [
        (80, 500), (180, 520), (280, 480), (380, 511),
        (480, 490), (580, 530), (680, 495), (780, 515)
    ]
    
    for x, y in stone_positions:
        pygame.draw.ellipse(SCREEN, STONE_GRAY, (x - 5, y - 3, 10, 6))

def draw_sunlight_effect():
    """绘制暖色调光照效果"""
    # 创建一个半透明的表面来添加暖色调
    sunlight_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    # 使用RGBA颜色填充表面
    sunlight_surface.fill((255, 255, 200, 64))
    SCREEN.blit(sunlight_surface, (0, 0))

def draw_test_background():
    """绘制测试背景"""
    # 清屏
    SCREEN.fill(BLACK)
    
    # 绘制背景美化元素
    draw_gradient_sky()
    draw_grass_texture()
    draw_path_with_details()
    draw_decorations()
    draw_sunlight_effect()
    
    # 绘制说明文字
    font = pygame.font.Font(None, 36)
    text = font.render("背景美化测试 - 按ESC退出", True, WHITE)
    SCREEN.blit(text, (200, 100))

# 主测试循环
def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 绘制背景
        draw_test_background()
        
        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()