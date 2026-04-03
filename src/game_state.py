"""
保卫萝卜 - 游戏状态管理
使用状态机模式管理游戏流程
"""
from enum import Enum, auto
from typing import Optional

class GameState(Enum):
    """游戏状态"""
    MENU = auto()      # 主菜单
    PLAYING = auto()   # 游戏中
    PAUSED = auto()    # 暂停
    GAME_OVER = auto() # 游戏结束
    VICTORY = auto()   # 胜利

class GameManager:
    """游戏管理器"""
    
    def __init__(self):
        self.state = GameState.MENU
        self.score = 0
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.level = 1
        self.towers_placed = []
        
    def reset(self):
        """重置游戏"""
        self.score = 0
        self.money = 200
        self.lives = 10
        self.wave = 0
        self.towers_placed = []
        self.state = GameState.PLAYING
        
    def next_level(self):
        """下一关"""
        self.level += 1
        self.wave = 0
        self.towers_placed = []
        
    def add_money(self, amount: int):
        """加钱"""
        self.money += amount
        self.score += amount
        
    def take_damage(self, damage: int = 1):
        """扣血"""
        self.lives -= damage
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
            
    def __repr__(self):
        return f"GameManager(state={self.state.name}, money={self.money}, lives={self.lives}, wave={self.wave})"

# 全局游戏管理器
game = GameManager()