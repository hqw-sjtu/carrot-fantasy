"""
游戏反馈系统 - Game Feedback System
整合屏幕震动、镜头效果、音效提示等
"""
import pygame
from screen_shake import get_screen_shake, trigger_screen_shake, ShakePresets
import random


class GameFeedback:
    """游戏反馈管理器"""
    
    def __init__(self):
        self.screen_shake = get_screen_shake()
        self.flash_timer = 0
        self.flash_color = (255, 255, 255)
        self.flash_alpha = 0
        self.slow_motion = False
        self.slow_motion_factor = 1.0
        
    def on_tower_attack(self, tower, target):
        """防御塔攻击反馈"""
        pass
        
    def on_monster_hit(self, monster, damage, is_critical=False):
        """怪物受击反馈"""
        if is_critical:
            trigger_screen_shake(*ShakePresets.CRITICAL)
        elif damage > 50:
            trigger_screen_shake(*ShakePresets.MEDIUM)
            
    def on_monster_death(self, monster):
        """怪物死亡反馈"""
        trigger_screen_shake(*ShakePresets.LIGHT)
        
    def on_boss_hit(self, boss, damage):
        """Boss受击反馈"""
        trigger_screen_shake(*ShakePresets.BOSS_HIT)
        
    def on_wave_start(self, wave_num):
        """波次开始反馈"""
        trigger_screen_shake(*ShakePresets.WAVE_START)
        
    def on_tower_upgrade(self, tower):
        """防御塔升级反馈"""
        trigger_screen_shake(*ShakePresets.LIGHT)
        
    def on_tower_sell(self, tower):
        """防御塔出售反馈"""
        trigger_screen_shake(0.15, 0.08)
        
    def flash_screen(self, color=(255, 255, 255), duration=0.1, alpha=100):
        """屏幕闪烁"""
        self.flash_color = color
        self.flash_alpha = alpha
        self.flash_timer = pygame.time.get_ticks() + int(duration * 1000)
        
    def update(self):
        """更新反馈效果"""
        self.screen_shake.update()
        
    def apply_to_surface(self, surface: pygame.Surface):
        """应用震动到表面"""
        offset = self.screen_shake.current_offset
        if offset != (0, 0):
            # 创建偏移后的表面
            return surface
        return surface


# 全局实例
_game_feedback = None

def get_game_feedback() -> GameFeedback:
    """获取全局游戏反馈实例"""
    global _game_feedback
    if _game_feedback is None:
        _game_feedback = GameFeedback()
    return _game_feedback


# 便捷函数
def on_critical_hit():
    """暴击反馈"""
    trigger_screen_shake(*ShakePresets.CRITICAL)
    
def on_boss_damage():
    """Boss伤害反馈"""
    trigger_screen_shake(*ShakePresets.BOSS_HIT)
    
def on_wave_complete():
    """波次完成反馈"""
    trigger_screen_shake(*ShakePresets.MEDIUM)