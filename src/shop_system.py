"""
商店系统 - 购买道具和特殊能力
"""
import pygame
import json
from typing import Dict, List, Optional


class ShopItem:
    """商店物品"""
    
    def __init__(self, item_id: str, name: str, name_cn: str, price: int, 
                 description: str, icon: str, effect_type: str, effect_value: float):
        self.id = item_id
        self.name = name
        self.name_cn = name_cn
        self.price = price
        self.description = description
        self.icon = icon
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.count = 0  # 玩家已购买数量


class ShopSystem:
    """商店系统"""
    
    def __init__(self, game):
        self.game = game
        self.items: Dict[str, ShopItem] = {}
        self.is_open = False
        self.selected_item = None
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 48)
        
        # UI颜色
        self.bg_color = (40, 35, 50, 230)
        self.item_bg_color = (60, 55, 75)
        self.item_hover_color = (90, 85, 110)
        self.selected_color = (100, 160, 220)
        self.text_color = (255, 255, 255)
        self.gold_color = (255, 215, 0)
        self.btn_color = (70, 130, 180)
        self.btn_hover_color = (100, 160, 200)
        
        self._init_items()
    
    def _init_items(self):
        """初始化商店物品"""
        items_data = [
            # 立即生效类
            ("damage_boost", "Damage Boost", "伤害提升", 200, 
             "接下来10秒内所有塔伤害+50%", "⚔️", "damage_multiplier", 1.5),
            ("speed_boost", "Speed Boost", "攻速提升", 150,
             "接下来10秒内所有塔攻速+30%", "🏹", "attack_speed_multiplier", 1.3),
            ("gold_boost", "Gold Boost", "金币提升", 300,
             "接下来30秒内击杀怪物获得2倍金币", "💰", "gold_multiplier", 2.0),
            ("freeze", "Freeze Time", "冰冻时间", 500,
             "冻结所有怪物5秒", "❄️", "freeze_time", 5.0),
            ("nuke", "Nuke", "核弹打击", 1000,
             "立即消灭屏幕上所有怪物", "💥", "nuke", 1.0),
            
            # 防御塔类
            ("extra_range", "Extra Range", "视野提升", 100,
             "所有塔攻击范围+20%", "👁️", "range_multiplier", 1.2),
            ("extra_damage", "Extra Damage", "伤害提升", 150,
             "所有塔伤害+25%", "⚔️", "damage_bonus", 0.25),
            
            # 特殊类
            ("save_lives", "Save Lives", "拯救萝卜", 800,
             "萝卜生命+1", "❤️", "lives", 1),
            ("skip_wave", "Skip Wave", "跳过波次", 600,
             "直接进入下一波", "⏭️", "skip_wave", 1),
            ("slow_all", "Global Slow", "全局减速", 400,
             "所有怪物减速50%持续15秒", "🐌", "global_slow", 0.5),
        ]
        
        for item in items_data:
            self.items[item[0]] = ShopItem(*item)
    
    def open(self):
        """打开商店"""
        self.is_open = True
        self.selected_item = None
    
    def close(self):
        """关闭商店"""
        self.is_open = False
        self.selected_item = None
    
    def toggle(self):
        """切换商店开关"""
        if self.is_open:
            self.close()
        else:
            self.open()
    
    def buy_item(self, item_id: str) -> bool:
        """购买物品"""
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        if self.game.gold < item.price:
            return False
        
        self.game.gold -= item.price
        item.count += 1
        
        # 应用效果
        self._apply_item_effect(item)
        
        # 显示购买成功特效
        self._show_purchase_effect(item)
        
        return True
    
    def _apply_item_effect(self, item: ShopItem):
        """应用物品效果"""
        effect = item.effect_type
        value = item.effect_value
        
        if effect == "damage_multiplier":
            self.game.activate_boost("damage", value, 10)
        elif effect == "attack_speed_multiplier":
            self.game.activate_boost("attack_speed", value, 10)
        elif effect == "gold_multiplier":
            self.game.activate_boost("gold", value, 30)
        elif effect == "freeze_time":
            self.game.freeze_monsters(value)
        elif effect == "nuke":
            self.game.nuke_all_monsters()
        elif effect == "range_multiplier":
            self.game.activate_boost("range", value, 15)
        elif effect == "damage_bonus":
            self.game.activate_boost("damage", 1 + value, 20)
        elif effect == "lives":
            self.game.lives += int(value)
        elif effect == "skip_wave":
            self.game.skip_wave()
        elif effect == "global_slow":
            self.game.activate_global_slow(value, 15)
    
    def _show_purchase_effect(self, item: ShopItem):
        """显示购买成功特效"""
        if hasattr(self.game, 'effects'):
            # 金钱花费特效
            for _ in range(10):
                self.game.effects.spawn_particle(
                    self.game.screen.get_width() // 2,
                    self.game.screen.get_height() // 2,
                    "gold_coin",
                    count=1
                )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理商店事件"""
        if not self.is_open:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            return self._handle_click(pos)
        
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            self._handle_hover(pos)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
        
        return False
    
    def _handle_click(self, pos: tuple) -> bool:
        """处理点击"""
        screen_w = self.game.screen.get_width()
        screen_h = self.game.screen.get_height()
        
        # 商店区域
        shop_rect = pygame.Rect(
            screen_w // 2 - 400,
            screen_h // 2 - 300,
            800, 600
        )
        
        if not shop_rect.collidepoint(pos):
            self.close()
            return True
        
        # 点击物品
        item_x = shop_rect.x + 50
        item_y = shop_rect.y + 100
        item_width = 160
        item_height = 180
        gap = 20
        
        for idx, item in enumerate(self.items.values()):
            col = idx % 4
            row = idx // 4
            
            item_rect = pygame.Rect(
                item_x + col * (item_width + gap),
                item_y + row * (item_height + gap),
                item_width,
                item_height
            )
            
            if item_rect.collidepoint(pos):
                self.selected_item = item
                self.buy_item(item.id)
                return True
        
        # 关闭按钮
        close_rect = pygame.Rect(shop_rect.right - 50, shop_rect.y + 10, 40, 40)
        if close_rect.collidepoint(pos):
            self.close()
            return True
        
        return True
    
    def _handle_hover(self, pos: tuple):
        """处理悬停"""
        screen_w = self.game.screen.get_width()
        screen_h = self.game.screen.get_height()
        
        shop_rect = pygame.Rect(
            screen_w // 2 - 400,
            screen_h // 2 - 300,
            800, 600
        )
        
        item_x = shop_rect.x + 50
        item_y = shop_rect.y + 100
        item_width = 160
        item_height = 180
        gap = 20
        
        for idx, item in enumerate(self.items.values()):
            col = idx % 4
            row = idx // 4
            
            item_rect = pygame.Rect(
                item_x + col * (item_width + gap),
                item_y + row * (item_height + gap),
                item_width,
                item_height
            )
            
            if item_rect.collidepoint(pos):
                self.selected_item = item
                return
    
    def render(self, surface: pygame.Surface):
        """渲染商店"""
        if not self.is_open:
            return
        
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        
        # 半透明背景
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # 商店面板
        shop_rect = pygame.Rect(
            screen_w // 2 - 400,
            screen_h // 2 - 300,
            800, 600
        )
        
        # 绘制背景
        panel = pygame.Surface((shop_rect.width, shop_rect.height), pygame.SRCALPHA)
        panel.fill(self.bg_color)
        
        # 边框
        pygame.draw.rect(panel, (100, 160, 220), (0, 0, shop_rect.width, shop_rect.height), 3)
        pygame.draw.rect(panel, (80, 130, 180), (5, 5, shop_rect.width - 10, shop_rect.height - 10), 2)
        
        # 标题
        title = self.title_font.render("商店 / Shop", True, self.text_color)
        panel.blit(title, (shop_rect.width // 2 - title.get_width() // 2, 20))
        
        # 金币显示
        gold_text = self.font.render(f"💰 {self.game.gold}", True, self.gold_color)
        panel.blit(gold_text, (shop_rect.width - 150, 25))
        
        # 物品网格
        item_x = 50
        item_y = 100
        item_width = 160
        item_height = 180
        gap = 20
        
        mouse_pos = pygame.mouse.get_pos()
        
        for idx, item in enumerate(self.items.values()):
            col = idx % 4
            row = idx // 4
            
            item_rect = pygame.Rect(
                item_x + col * (item_width + gap),
                item_y + row * (item_height + gap),
                item_width,
                item_height
            )
            
            # 背景
            color = self.item_hover_color if item_rect.collidepoint(mouse_pos) else self.item_bg_color
            pygame.draw.rect(panel, color, item_rect, border_radius=10)
            pygame.draw.rect(panel, (80, 80, 100), item_rect, 2, border_radius=10)
            
            # 图标
            icon_text = pygame.font.Font(None, 50).render(item.icon, True, self.text_color)
            panel.blit(icon_text, (item_rect.centerx - icon_text.get_width() // 2, item_rect.y + 20))
            
            # 名称
            name_text = self.font.render(item.name_cn, True, self.text_color)
            panel.blit(name_text, (item_rect.centerx - name_text.get_width() // 2, item_rect.y + 70))
            
            # 价格
            price_color = self.gold_color if self.game.gold >= item.price else (150, 80, 80)
            price_text = self.font.render(f"💰 {item.price}", True, price_color)
            panel.blit(price_text, (item_rect.centerx - price_text.get_width() // 2, item_rect.y + 105))
            
            # 已购数量
            if item.count > 0:
                count_text = self.font.render(f"已购: {item.count}", True, (150, 255, 150))
                panel.blit(count_text, (item_rect.centerx - count_text.get_width() // 2, item_rect.y + 140))
        
        # 关闭按钮
        close_rect = pygame.Rect(shop_rect.width - 50, 10, 40, 40)
        close_text = self.font.render("✕", True, self.text_color)
        panel.blit(close_text, (close_rect.centerx - close_text.get_width() // 2, 
                               close_rect.centery - close_text.get_height() // 2))
        
        surface.blit(panel, (shop_rect.x, shop_rect.y))
        
        # 选中物品描述
        if self.selected_item:
            desc_panel = pygame.Surface((400, 100), pygame.SRCALPHA)
            desc_panel.fill((30, 25, 40, 240))
            desc_rect = desc_panel.get_rect()
            desc_rect.bottomleft = (shop_rect.left + 20, shop_rect.bottom - 20)
            
            name = self.font.render(self.selected_item.name_cn, True, self.text_color)
            desc_panel.blit(name, (20, 10))
            
            desc = self.font.render(self.selected_item.description, True, (200, 200, 200))
            desc_panel.blit(desc, (20, 40))
            
            if self.game.gold >= self.selected_item.price:
                hint = self.font.render("点击购买", True, (150, 255, 150))
            else:
                hint = self.font.render("金币不足!", True, (255, 100, 100))
            desc_panel.blit(hint, (20, 70))
            
            surface.blit(desc_panel, desc_rect)


# 注册商店快捷键
SHOP_KEY = pygame.K_s  # 按S打开商店