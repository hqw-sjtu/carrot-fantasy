# -*- coding: utf-8 -*-
"""成就系统 - Achievement System

玩家达成特定目标时解锁成就，获得奖励和荣誉展示。
"""

import pygame
import json
import os
from datetime import datetime


class Achievement:
    """单个成就"""
    def __init__(self, id, name, description, icon, reward, condition):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.reward = reward  # 金币/钻石奖励
        self.condition = condition  # 解锁条件函数
        self.unlocked = False
        self.unlocked_time = None
    
    def unlock(self):
        if not self.unlocked:
            self.unlocked = True
            self.unlocked_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            return True
        return False


class AchievementManager:
    """成就管理器"""
    
    # 成就定义
    ACHIEVEMENTS = [
        # 击杀类成就
        {"id": "first_blood", "name": "初战告捷", "desc": "击杀第一只怪物", "icon": "⚔️", "reward": 50, 
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 1},
        {"id": "slayer_10", "name": "小试牛刀", "desc": "累计击杀10只怪物", "icon": "🗡️", "reward": 100,
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 10},
        {"id": "slayer_50", "name": "怪物猎人", "desc": "累计击杀50只怪物", "icon": "🏹", "reward": 300,
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 50},
        {"id": "slayer_100", "name": "传奇猎手", "desc": "累计击杀100只怪物", "icon": "💀", "reward": 500,
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 100},
        {"id": "slayer_500", "name": "毁灭者", "desc": "累计击杀500只怪物", "icon": "🔥", "reward": 1000,
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 500},
        {"id": "slayer_1000", "name": "收割者", "desc": "累计击杀1000只怪物", "icon": "🌾", "reward": 2000,
         "condition": lambda stats: stats.get("monsters_killed", 0) >= 1000},
        
        # 金币类成就
        {"id": "rich_1000", "name": "小有积蓄", "desc": "累计获得1000金币", "icon": "💰", "reward": 50,
         "condition": lambda stats: stats.get("total_coins", 0) >= 1000},
        {"id": "rich_10000", "name": "腰缠万贯", "desc": "累计获得10000金币", "icon": "💎", "reward": 200,
         "condition": lambda stats: stats.get("total_coins", 0) >= 10000},
        {"id": "rich_50000", "name": "富甲一方", "desc": "累计获得50000金币", "icon": "🏆", "reward": 500,
         "condition": lambda stats: stats.get("total_coins", 0) >= 50000},
        
        # 塔类成就
        {"id": "first_tower", "name": "初建防御", "desc": "建造第一座防御塔", "icon": "🗼", "reward": 50,
         "condition": lambda stats: stats.get("towers_built", 0) >= 1},
        {"id": "tower_master", "name": "建塔大师", "desc": "累计建造50座防御塔", "icon": "🏗️", "reward": 300,
         "condition": lambda stats: stats.get("towers_built", 0) >= 50},
        
        # 升级类成就
        {"id": "first_upgrade", "name": "初窥门径", "desc": "第一次升级防御塔", "icon": "⬆️", "reward": 50,
         "condition": lambda stats: stats.get("towers_upgraded", 0) >= 1},
        {"id": "upgrade_master", "name": "升级专家", "desc": "累计升级100次防御塔", "icon": "📈", "reward": 500,
         "condition": lambda stats: stats.get("towers_upgraded", 0) >= 100},
        
        # 波次类成就
        {"id": "wave_5", "name": "初战成名", "desc": "完成第5波", "icon": "⭐", "reward": 100,
         "condition": lambda stats: stats.get("max_wave", 0) >= 5},
        {"id": "wave_10", "name": "坚守阵地", "desc": "完成第10波", "icon": "🌟", "reward": 200,
         "condition": lambda stats: stats.get("max_wave", 0) >= 10},
        {"id": "wave_20", "name": "不败传说", "desc": "完成第20波", "icon": "💫", "reward": 500,
         "condition": lambda stats: stats.get("max_wave", 0) >= 20},
        
        # 特殊成就
        {"id": "no_damage_wave", "name": "完美防御", "desc": "无漏怪完成一波", "icon": "🛡️", "reward": 200,
         "condition": lambda stats: stats.get("perfect_waves", 0) >= 1},
        {"id": "combo_5", "name": "集火达人", "desc": "5塔同时集火同一目标", "icon": "🎯", "reward": 300,
         "condition": lambda stats: stats.get("max_combo", 0) >= 5},
        {"id": "speed_kill", "name": "闪电击杀", "desc": "3秒内击杀Boss", "icon": "⚡", "reward": 500,
         "condition": lambda stats: stats.get("boss_fast_kill", False)},
        # 连续击杀成就
        {"id": "streak_10", "name": "连杀初现", "desc": "单次连杀10只怪物", "icon": "🔥", "reward": 200,
         "condition": lambda stats: stats.get("max_kill_streak", 0) >= 10},
        {"id": "streak_30", "name": "杀戮成性", "desc": "单次连杀30只怪物", "icon": "💀", "reward": 500,
         "condition": lambda stats: stats.get("max_kill_streak", 0) >= 30},
        # 暴击成就
        {"id": "crit_10", "name": "暴击初现", "desc": "累计暴击10次", "icon": "💥", "reward": 100,
         "condition": lambda stats: stats.get("total_crits", 0) >= 10},
        {"id": "crit_100", "name": "暴击大师", "desc": "累计暴击100次", "icon": "💣", "reward": 500,
         "condition": lambda stats: stats.get("total_crits", 0) >= 100},
        # 商店成就
        {"id": "first_purchase", "name": "购物达人", "desc": "在商店购买第一件道具", "icon": "🛒", "reward": 50,
         "condition": lambda stats: stats.get("items_purchased", 0) >= 1},
        {"id": "shop_10", "name": "VIP客户", "desc": "累计购买10件道具", "icon": "💳", "reward": 300,
         "condition": lambda stats: stats.get("items_purchased", 0) >= 10},
    ]
    
    def __init__(self, save_path="achievements.json"):
        self.save_path = save_path
        self.achievements = {}
        self.stats = {
            "monsters_killed": 0,
            "total_coins": 0,
            "towers_built": 0,
            "towers_upgraded": 0,
            "max_wave": 0,
            "perfect_waves": 0,
            "max_combo": 0,
            "boss_fast_kill": False,
            "max_kill_streak": 0,
            "total_crits": 0,
            "items_purchased": 0,
        }
        self.newly_unlocked = []  # 新解锁的成就
        self._init_achievements()
        self._load()
    
    def _init_achievements(self):
        """初始化成就列表"""
        for a in self.ACHIEVEMENTS:
            self.achievements[a["id"]] = Achievement(
                a["id"], a["name"], a["desc"], a["icon"], a["reward"], a["condition"]
            )
    
    def _load(self):
        """加载存档"""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 恢复已解锁成就
                    for ach_id, ach_data in data.get("achievements", {}).items():
                        if ach_id in self.achievements:
                            self.achievements[ach_id].unlocked = ach_data.get("unlocked", False)
                            self.achievements[ach_id].unlocked_time = ach_data.get("unlocked_time")
                    # 恢复统计数据
                    self.stats = data.get("stats", self.stats)
            except Exception as e:
                print(f"加载成就数据失败: {e}")
    
    def save(self):
        """保存存档"""
        data = {
            "achievements": {
                ach_id: {"unlocked": ach.unlocked, "unlocked_time": ach.unlocked_time}
                for ach_id, ach in self.achievements.items()
            },
            "stats": self.stats
        }
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_stat(self, stat_name, value):
        """更新统计"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
            self._check_achievements()
    
    def increment_stat(self, stat_name, delta=1):
        """增加统计值"""
        if stat_name in self.stats:
            self.stats[stat_name] += delta
            self._check_achievements()
    
    def _check_achievements(self):
        """检查成就解锁"""
        self.newly_unlocked = []
        for ach in self.achievements.values():
            if not ach.unlocked and ach.condition(self.stats):
                ach.unlock()
                self.newly_unlocked.append(ach)
    
    def get_new_unlocks(self):
        """获取新解锁的成就"""
        return self.newly_unlocked
    
    def clear_new_unlocks(self):
        """清除新解锁标记"""
        self.newly_unlocked = []
    
    def get_unlocked_count(self):
        """获取已解锁数量"""
        return sum(1 for a in self.achievements.values() if a.unlocked)
    
    def get_total_count(self):
        """获取总成就数"""
        return len(self.achievements)
    
    def render(self, screen, font, small_font):
        """渲染成就面板"""
        x, y = 50, 50
        width, height = 700, 500
        
        # 背景
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (x, y))
        
        # 标题
        title = font.render(f"成就 {self.get_unlocked_count()}/{self.get_total_count()}", True, (255, 215, 0))
        screen.blit(title, (x + 20, y + 10))
        
        # 成就列表
        idx = 0
        for ach in self.achievements.values():
            row = idx // 2
            col = idx % 2
            ax = x + 20 + col * 340
            ay = y + 50 + row * 70
            
            # 成就背景
            bg_color = (60, 60, 60) if ach.unlocked else (30, 30, 30)
            pygame.draw.rect(screen, bg_color, (ax, ay, 320, 60), border_radius=8)
            
            # 图标和名称
            icon_color = (255, 255, 255) if ach.unlocked else (100, 100, 100)
            icon = small_font.render(ach.icon, True, icon_color)
            screen.blit(icon, (ax + 10, ay + 10))
            
            name_color = (255, 215, 0) if ach.unlocked else (150, 150, 150)
            name = small_font.render(ach.name, True, name_color)
            screen.blit(name, (ax + 50, ay + 5))
            
            desc = small_font.render(ach.description, True, (180, 180, 180))
            screen.blit(desc, (ax + 50, ay + 28))
            
            if ach.unlocked:
                check = small_font.render("✓", True, (0, 255, 0))
                screen.blit(check, (ax + 290, ay + 35))
            else:
                lock = small_font.render("🔒", True, (100, 100, 100))
                screen.blit(lock, (ax + 290, ay + 35))
            
            idx += 1
            if idx >= 10:  # 最多显示10个
                break


# 全局成就管理器实例
_achievement_manager = None


def get_achievement_manager():
    """获取成就管理器单例"""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager()
    return _achievement_manager