"""
pytest配置 - 初始化pygame
Pytest config - Initialize pygame
"""
import pytest
import pygame

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """初始化pygame（session级别只执行一次）"""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield

try:
    import pygame
    _font_init = pygame.font.get_init()
except:
    _font_init = True

@pytest.fixture(autouse=True)
def ensure_pygame():
    """确保pygame可用（每次测试前检查）"""
    if not pygame.get_init():
        pygame.init()
        pygame.display.set_mode((800, 600))
    elif not pygame.font.get_init():
        pygame.font.init()
    yield