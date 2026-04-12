"""
保卫萝卜 - 防御塔皮肤系统
Carrot Fantasy - Tower Skins System
"""
import pygame
import random


class TowerSkin:
    """防御塔皮肤"""
    
    # 皮肤类型
    CLASSIC = "classic"      # 经典
    GOLD = "gold"            # 金色
    CRYSTAL = "crystal"      # 水晶
    NEON = "neon"            # 霓虹
    SHADOW = "shadow"        # 暗影
    RAINBOW = "rainbow"      # 彩虹
    
    SKINS = {
        CLASSIC: {
            "name": "经典",
            "outline": (100, 100, 100),
            "highlight": (150, 150, 150),
            "shadow": (50, 50, 50),
            "glow": None,
        },
        GOLD: {
            "name": "黄金",
            "outline": (255, 215, 0),
            "highlight": (255, 255, 150),
            "shadow": (180, 140, 0),
            "glow": (255, 215, 0, 80),
        },
        CRYSTAL: {
            "name": "水晶",
            "outline": (100, 200, 255),
            "highlight": (200, 240, 255),
            "shadow": (50, 100, 180),
            "glow": (100, 200, 255, 60),
        },
        NEON: {
            "name": "霓虹",
            "outline": (255, 0, 255),
            "highlight": (255, 150, 255),
            "shadow": (150, 0, 150),
            "glow": (255, 0, 255, 100),
        },
        SHADOW: {
            "name": "暗影",
            "outline": (80, 80, 90),
            "highlight": (140, 140, 160),
            "shadow": (20, 20, 30),
            "glow": (50, 50, 60, 40),
        },
    }
    
    def __init__(self, skin_type=CLASSIC):
        self.skin_type = skin_type
        self.skin_data = self.SKINS.get(skin_type, self.SKINS[self.CLASSIC])
        self.rainbow_phase = 0  # 彩虹皮肤动画相位
    
    def get_colors(self, base_color):
        """获取皮肤颜色配置"""
        if self.skin_type == self.RAINBOW:
            # 动态彩虹色
            import math
            phase = self.rainbow_phase
            r = int(128 + 127 * math.sin(phase))
            g = int(128 + 127 * math.sin(phase + 2*math.pi/3))
            b = int(128 + 127 * math.sin(phase + 4*math.pi/3))
            return {
                "outline": (r, g, b),
                "highlight": (min(255, r+60), min(255, g+60), min(255, b+60)),
                "shadow": (max(0, r-60), max(0, g-60), max(0, b-60)),
                "glow": (r, g, b, 100),
            }
        return {
            "outline": self.skin_data["outline"],
            "highlight": self.skin_data["highlight"],
            "shadow": self.skin_data["shadow"],
            "glow": self.skin_data["glow"],
        }
    
    def update(self, dt):
        """更新皮肤动画"""
        if self.skin_type == self.RAINBOW:
            self.rainbow_phase += dt * 3  # 彩虹循环速度
    
    def draw_tower(self, screen, x, y, size, base_color, level):
        """绘制带皮肤的防御塔"""
        colors = self.get_colors(base_color)
        
        # 绘制发光效果
        if colors["glow"]:
            glow_surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
            glow_color = colors["glow"]
            pygame.draw.circle(glow_surf, glow_color, (size*3//2, size*3//2), size)
            screen.blit(glow_surf, (x - size, y - size))
        
        # 绘制阴影
        shadow_offset = size // 6
        pygame.draw.circle(screen, colors["shadow"], 
                          (x + shadow_offset, y + shadow_offset), size)
        
        # 绘制主体
        pygame.draw.circle(screen, colors["outline"], (x, y), size)
        
        # 绘制高光
        highlight_size = size * 0.7
        pygame.draw.circle(screen, colors["highlight"], 
                          (x - size//4, y - size//4), highlight_size)
        
        # 绘制等级标识
        if level > 1:
            level_colors = {
                2: (255, 200, 0),    # 金色
                3: (255, 100, 0),    # 橙色
            }
            level_color = level_colors.get(level, (255, 200, 0))
            star_x = x + size // 2
            star_y = y - size // 3
            # 简单星形
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                px = star_x + 6 * 3.14159 * 0.4 * 0.4 * 3.14159 / 180
                px = star_x + (size//5) * (i - 2)
                px = x + size//2 + (i - 2) * 4
                py = y - size//2 + 2
                pygame.draw.circle(screen, level_color, (px, py), 2)


class TowerSkinSystem:
    """防御塔皮肤管理系统"""
    
    def __init__(self):
        self.owned_skins = {skin_type: False for skin_type in TowerSkin.SKINS}
        self.owned_skins[TowerSkin.CLASSIC] = True  # 经典皮肤默认拥有
        self.equipped_skins = {}  # tower_id -> skin_type
        self.skin_prices = {
            TowerSkin.CLASSIC: 0,
            TowerSkin.GOLD: 500,
            TowerSkin.CRYSTAL: 800,
            TowerSkin.NEON: 1200,
            TowerSkin.SHADOW: 1500,
            TowerSkin.RAINBOW: 2000,
        }
    
    def buy_skin(self, skin_type, coins):
        """购买皮肤"""
        if skin_type in self.owned_skins and self.owned_skins[skin_type]:
            return False, "已拥有此皮肤"
        
        price = self.skin_prices.get(skin_type, 99999)
        if coins < price:
            return False, f"金币不足，需要{price}金币"
        
        self.owned_skins[skin_type] = True
        return True, f"购买成功！花费{price}金币"
    
    def equip_skin(self, tower_id, skin_type):
        """装备皮肤"""
        if skin_type not in self.owned_skins or not self.owned_skins[skin_type]:
            return False, "未拥有此皮肤"
        self.equipped_skins[tower_id] = skin_type
        return True, f"已装备{TowerSkin.SKINS[skin_type]['name']}皮肤"
    
    def get_skin(self, tower_id):
        """获取塔的皮肤"""
        skin_type = self.equipped_skins.get(tower_id, TowerSkin.CLASSIC)
        return TowerSkin(skin_type)
    
    def get_owned_skins(self):
        """获取已拥有的皮肤列表"""
        return [skin_type for skin_type, owned in self.owned_skins.items() if owned]
    
    def get_skin_shop_data(self):
        """获取皮肤商店数据"""
        return [
            {
                "type": skin_type,
                "name": data["name"],
                "price": self.skin_prices[skin_type],
                "owned": self.owned_skins[skin_type],
            }
            for skin_type, data in TowerSkin.SKINS.items()
        ]


# 导出
__all__ = ['TowerSkin', 'TowerSkinSystem']