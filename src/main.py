"""
保卫萝卜 - Carrot Fantasy
A Tower Defense Game
"""

import pygame
import sys

# 初始化 Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("保卫萝卜 - Carrot Fantasy")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
ORANGE = (255, 165, 0)
YELLOW = (255, 215, 0)

# 游戏状态
def main():
    clock = pygame.time.Clock()
    running = True
    
    # 萝卜位置
    carrot_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
    
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 绘制
        SCREEN.fill(GREEN)
        
        # 绘制萝卜
        pygame.draw.circle(SCREEN, ORANGE, carrot_pos, 30)
        pygame.draw.circle(SCREEN, YELLOW, carrot_pos, 20)
        
        # 绘制文字
        font = pygame.font.Font(None, 36)
        text = font.render("保卫萝卜 - Carrot Fantasy", True, WHITE)
        SCREEN.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()