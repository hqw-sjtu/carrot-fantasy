# -*- coding: utf-8 -*-
"""怪物图鉴系统 - Monster Bestiary

记录玩家见过的所有怪物，显示详细信息。按B键打开图鉴。
"""

import pygame
from typing import Dict, List, Optional, Tuple


class MonsterEntry:
    """怪物条目"""
    def __init__(self, monster_type: str, name: str, hp: int, speed: float, 
                 reward: int, weakness: str, description: str, icon: str):
        self.type = monster_type
        self.name = name
        self.max_hp = hp
        self.speed = speed
        self.reward = reward
        self.weakness = weakness
        self.description = description
        self.icon = icon
        self.kill_count = 0          # 击杀数量
        self.total_damage_dealt = 0  # 累计造成伤害
        self.first_seen_wave = 0     # 首次出现波次
        self.discovered = False      # 是否已发现
    
    def discover(self, wave: int):
        """发现怪物"""
        if not self.discovered:
            self.discovered = True
            self.first_seen_wave = wave
    
    def record_kill(self, damage_dealt: int = 0):
        """记录击杀"""
        self.kill_count += 1
        self.total_damage_dealt += damage_dealt


class BestiarySystem:
    """怪物图鉴系统"""
    
    # 怪物数据库
    MONSTER_DATABASE = {
        "slime": {
            "name": "史莱姆",
            "hp": 30,
            "speed": 1.0,
            "reward": 5,
            "weakness": "箭塔",
            "description": "最弱的怪物，皮糙肉厚但动作缓慢",
            "icon": "🟢"
        },
        "bat": {
            "name": "蝙蝠",
            "hp": 20,
            "speed": 2.5,
            "reward": 8,
            "weakness": "魔法塔",
            "description": "飞行速度快，难以瞄准",
            "icon": "🦇"
        },
        "wolf": {
            "name": "野狼",
            "hp": 50,
            "speed": 1.8,
            "reward": 12,
            "weakness": "炮塔",
            "description": "群居动物，攻击力高",
            "icon": "🐺"
        },
        "ghost": {
            "name": "幽灵",
            "hp": 40,
            "speed": 2.0,
            "reward": 15,
            "weakness": "冰霜塔",
            "description": "具有穿墙能力，魔法抗性高",
            "icon": "👻"
        },
        "boss_slime": {
            "name": "史莱姆王",
            "hp": 500,
            "speed": 0.8,
            "reward": 100,
            "weakness": "炮塔",
            "description": "巨大的史莱姆，免疫减速",
            "icon": "👑"
        },
        "boss_dragon": {
            "name": "巨龙",
            "hp": 1000,
            "speed": 1.2,
            "reward": 200,
            "weakness": "魔法塔",
            "description": "强大的Boss，具有高额伤害",
            "icon": "🐉"
        },
        "skeleton": {
            "name": "骷髅战士",
            "hp": 60,
            "speed": 1.5,
            "reward": 10,
            "weakness": "圣光",
            "description": "亡灵生物，物理抗性高",
            "icon": "💀"
        },
        "orc": {
            "name": "兽人",
            "hp": 80,
            "speed": 1.3,
            "reward": 15,
            "weakness": "冰霜",
            "description": "皮糙肉厚，攻击力强",
            "icon": "👹"
        },
    }
    
    def __init__(self):
        self.entries: Dict[str, MonsterEntry] = {}
        self.is_open = False
        self.selected_index = 0
        self._init_database()
    
    def _init_database(self):
        """初始化怪物数据库"""
        for monster_type, data in self.MONSTER_DATABASE.items():
            entry = MonsterEntry(
                monster_type=monster_type,
                name=data["name"],
                hp=data["hp"],
                speed=data["speed"],
                reward=data["reward"],
                weakness=data["weakness"],
                description=data["description"],
                icon=data["icon"]
            )
            self.entries[monster_type] = entry
    
    def discover_monster(self, monster_type: str, wave: int):
        """发现怪物"""
        if monster_type in self.entries:
            self.entries[monster_type].discover(wave)
    
    def record_kill(self, monster_type: str, damage_dealt: int = 0):
        """记录击杀"""
        if monster_type in self.entries:
            self.entries[monster_type].record_kill(damage_dealt)
    
    def get_discovered_monsters(self) -> List[MonsterEntry]:
        """获取已发现的怪物列表"""
        return [e for e in self.entries.values() if e.discovered]
    
    def get_all_monsters(self) -> List[MonsterEntry]:
        """获取所有怪物列表"""
        return list(self.entries.values())
    
    def get_statistics(self) -> Dict:
        """获取图鉴统计"""
        discovered = len(self.get_discovered_monsters())
        total = len(self.entries)
        total_kills = sum(e.kill_count for e in self.entries.values())
        return {
            "discovered": discovered,
            "total": total,
            "total_kills": total_kills,
            "completion": f"{discovered}/{total}"
        }
    
    def toggle(self):
        """切换图鉴显示"""
        self.is_open = not self.is_open
        if self.is_open:
            self.selected_index = 0
    
    def close(self):
        """关闭图鉴"""
        self.is_open = False
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """处理输入"""
        if not self.is_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            monsters = self.get_discovered_monsters()
            if not monsters:
                return True
            
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                self.close()
                return True
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(monsters)
                return True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(monsters)
                return True
        
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, 
             title_font: pygame.font.Font, small_font: pygame.font.Font):
        """绘制图鉴界面"""
        if not self.is_open:
            return
        
        screen_width, screen_height = screen.get_width(), screen.get_height()
        panel_w, panel_h = 700, 500
        panel_x = screen_width // 2 - panel_w // 2
        panel_y = screen_height // 2 - panel_h // 2
        
        # 半透明背景
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # 主面板背景
        bg_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg_surface.fill((20, 25, 40, 240))
        screen.blit(bg_surface, (panel_x, panel_y))
        
        # 边框
        pygame.draw.rect(screen, (100, 150, 220), 
                        (panel_x - 2, panel_y - 2, panel_w + 4, panel_h + 4), 
                        2, border_radius=12)
        pygame.draw.rect(screen, (80, 120, 180), 
                        (panel_x, panel_y, panel_w, panel_h), 
                        1, border_radius=10)
        
        # 标题
        stats = self.get_statistics()
        title = title_font.render("📖 怪物图鉴", True, (255, 215, 0))
        screen.blit(title, (panel_x + 20, panel_y + 15))
        
        # 统计信息
        stat_text = f"已发现: {stats['discovered']}/{stats['total']}  |  累计击杀: {stats['total_kills']}"
        stat_surf = small_font.render(stat_text, True, (180, 180, 200))
        screen.blit(stat_surf, (panel_x + panel_w - 280, panel_y + 20))
        
        # 关闭提示
        close_hint = small_font.render("[B/ESC] 关闭  [↑↓] 浏览", True, (120, 120, 140))
        screen.blit(close_hint, (panel_x + 20, panel_y + panel_h - 30))
        
        # 分割线
        pygame.draw.line(screen, (60, 80, 120), 
                        (panel_x + 20, panel_y + 55), 
                        (panel_x + panel_w - 20, panel_y + 55), 1)
        
        # 左侧怪物列表
        list_x = panel_x + 20
        list_y = panel_y + 70
        list_w, list_h = 180, panel_h - 120
        
        # 列表背景
        pygame.draw.rect(screen, (30, 35, 50), (list_x, list_y, list_w, list_h), border_radius=8)
        
        discovered = self.get_discovered_monsters()
        
        if not discovered:
            empty_text = font.render("暂无发现怪物", True, (120, 120, 140))
            screen.blit(empty_text, (list_x + 20, list_y + list_h // 2))
        else:
            item_h = 45
            visible_items = list_h // item_h
            start_idx = max(0, self.selected_index - visible_items + 1)
            end_idx = min(len(discovered), start_idx + visible_items)
            
            for i in range(start_idx, end_idx):
                entry = discovered[i]
                item_y = list_y + 10 + (i - start_idx) * item_h
                
                # 选中状态
                if i == self.selected_index:
                    pygame.draw.rect(screen, (60, 100, 160), 
                                   (list_x + 5, item_y, list_w - 10, item_h - 5), 
                                   border_radius=6)
                
                # 怪物图标
                icon_surf = font.render(entry.icon, True, (255, 255, 255))
                screen.blit(icon_surf, (list_x + 15, item_y + 8))
                
                # 怪物名称
                name_surf = small_font.render(entry.name, True, (220, 220, 220))
                screen.blit(name_surf, (list_x + 50, item_y + 10))
                
                # 击杀数
                kill_surf = small_font.render(f"×{entry.kill_count}", True, (150, 150, 150))
                screen.blit(kill_surf, (list_x + 50, item_y + 26))
        
        # 右侧详细信息
        detail_x = list_x + list_w + 15
        detail_w = panel_w - list_w - 50
        
        # 详情背景
        pygame.draw.rect(screen, (35, 40, 55), 
                        (detail_x, list_y, detail_w, list_h), border_radius=8)
        
        if discovered and self.selected_index < len(discovered):
            entry = discovered[self.selected_index]
            
            # 怪物大图标
            big_icon = title_font.render(entry.icon, True, (255, 255, 255))
            screen.blit(big_icon, (detail_x + 20, list_y + 15))
            
            # 名称
            name_text = title_font.render(entry.name, True, (255, 215, 0))
            screen.blit(name_text, (detail_x + 80, list_y + 20))
            
            # 描述
            desc_text = font.render(entry.description, True, (180, 180, 200))
            screen.blit(desc_text, (detail_x + 20, list_y + 75))
            
            # 属性信息
            info_y = list_y + 115
            line_height = 28
            
            # HP
            hp_text = font.render(f"❤️ 生命值: {entry.max_hp}", True, (255, 100, 100))
            screen.blit(hp_text, (detail_x + 20, info_y))
            
            # 速度
            speed_text = font.render(f"⚡ 速度: {entry.speed}", True, (100, 200, 255))
            screen.blit(speed_text, (detail_x + 20, info_y + line_height))
            
            # 奖励
            reward_text = font.render(f"💰 奖励: {entry.reward}金币", True, (255, 215, 0))
            screen.blit(reward_text, (detail_x + 20, info_y + line_height * 2))
            
            # 弱点
            weakness_text = font.render(f"🎯 弱点: {entry.weakness}", True, (200, 100, 255))
            screen.blit(weakness_text, (detail_x + 20, info_y + line_height * 3))
            
            # 首次出现
            if entry.first_seen_wave > 0:
                wave_text = font.render(f"📍 首次出现: 第{entry.first_seen_wave}波", True, (150, 200, 150))
                screen.blit(wave_text, (detail_x + 20, info_y + line_height * 4))
            
            # 累计击杀
            kill_text = font.render(f"☠️ 累计击杀: {entry.kill_count}", True, (255, 150, 150))
            screen.blit(kill_text, (detail_x + 20, info_y + line_height * 5))
            
            # 造成的伤害
            if entry.total_damage_dealt > 0:
                dmg_text = font.render(f"💥 造成伤害: {entry.total_damage_dealt}", True, (255, 200, 100))
                screen.blit(dmg_text, (detail_x + 20, info_y + line_height * 6))