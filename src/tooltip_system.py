"""
保卫萝卜 - 提示系统 (Tooltip System)
工艺品级别细节：鼠标悬停显示详细信息
"""

import pygame

# 全局提示系统实例
_tooltip_instance = None

class TooltipSystem:
    """鼠标悬停提示系统"""
    
    def __init__(self):
        self.font_title = None
        self.font_desc = None
        self.font_stats = None
        self._initialized = False
        self._load_fonts()
    
    def _load_fonts(self):
        """加载字体"""
        try:
            # 尝试加载中文字体
            import os
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            ]
            font_loaded = False
            for fp in font_paths:
                if os.path.exists(fp):
                    try:
                        self.font_title = pygame.font.Font(fp, 18)
                        self.font_desc = pygame.font.Font(fp, 14)
                        self.font_stats = pygame.font.Font(fp, 12)
                        font_loaded = True
                        break
                    except:
                        continue
            
            if not font_loaded:
                self.font_title = pygame.font.SysFont("microsoftyahei", 18)
                self.font_desc = pygame.font.SysFont("microsoftyahei", 14)
                self.font_stats = pygame.font.SysFont("microsoftyahei", 12)
            
            self._initialized = True
        except Exception as e:
            # 回退到默认字体
            self.font_title = pygame.font.SysFont("arial", 18)
            self.font_desc = pygame.font.SysFont("arial", 14)
            self.font_stats = pygame.font.SysFont("arial", 12)
            self._initialized = True
    
    def get_tooltip(self, mouse_pos, towers, monsters, state):
        """获取当前鼠标位置的提示信息
        
        Returns:
            tuple: (title, description, stats) or None if无需显示
        """
        mx, my = mouse_pos
        
        # 检查是否悬停在防御塔上
        for tower in towers:
            tx, ty = tower.x, tower.y
            # 塔的范围大约是50x50
            if abs(mx - tx) < 30 and abs(my - ty) < 30:
                return self._get_tower_tooltip(tower, state)
        
        # 检查是否悬停在怪物上
        for monster in monsters:
            mx_pos, my_pos = monster.x, monster.y
            if abs(mx - mx_pos) < 25 and abs(my - my_pos) < 25:
                return self._get_monster_tooltip(monster)
        
        return None
    
    def _get_tower_tooltip(self, tower, state):
        """获取防御塔提示信息"""
        # 塔类型中文名
        tower_names = {
            "箭塔": "🏹 Arrow Tower",
            "炮塔": "💣 Cannon Tower", 
            "魔法塔": "✨ Magic Tower",
            "冰霜塔": "❄️ Ice Tower",
        }
        
        title = tower_names.get(tower.name, tower.name)
        
        # 品质前缀
        quality_prefix = {"epic": "⭐⭐", "rare": "⭐", "normal": ""}
        quality_name = {"epic": "史诗", "rare": "优秀", "normal": "普通"}
        
        title = f"{quality_prefix.get(tower.quality, '')} {title} Lv.{tower.level}"
        if tower.quality != "normal":
            title += f" [{quality_name.get(tower.quality, '')}]"
        
        # 描述
        desc = f"成本: {tower.cost} | 售价: {tower.get_sell_price()}"
        if tower.skill_name:
            desc += f"\n技能: {tower.skill_name}"
        
        # 属性
        stats = []
        stats.append(f"伤害: {tower.damage}")
        stats.append(f"射程: {tower.range}")
        stats.append(f"攻速: {tower.attack_speed:.1f}/秒")
        if tower.slow_factor < 1.0:
            stats.append(f"减速: {(1-tower.slow_factor)*100:.0f}%")
        
        # 专精信息
        if tower.specialized and tower.specialization:
            spec_names = {
                "damage": "⚔️ 伤害专精",
                "range": "🎯 射程专精", 
                "speed": "⚡ 攻速专精",
                "aoe": "💥 范围专精"
            }
            stats.append(f"专精: {spec_names.get(tower.specialization, tower.specialization)}")
        
        return title, desc, stats
    
    def _get_monster_tooltip(self, monster):
        """获取怪物提示信息"""
        # 怪物类型
        monster_names = {
            "basic": "👾 小怪",
            "fast": "💨 快速怪",
            "tank": "🛡️ 坦克怪",
            "boss": "👹 Boss",
        }
        
        name = monster_names.get(monster.type, monster.type)
        if monster.boss:
            name = "👹 Boss"
        
        title = f"{name}"
        
        desc = f"赏金: {monster.reward}💰"
        
        stats = []
        stats.append(f"生命: {monster.hp}/{monster.max_hp}")
        if monster.boss:
            stats.append(f"⭐ Boss单位")
        if monster.frozen > 0:
            stats.append(f"❄️ 冰冻中")
        if monster.slowed:
            stats.append(f"⏪ 减速中")
        
        return title, desc, stats
    
    def draw_tooltip(self, screen, mouse_pos, tooltip_data):
        """绘制提示框
        
        Args:
            screen: pygame屏幕
            mouse_pos: 鼠标位置
            tooltip_data: get_tooltip返回的数据
        """
        if not tooltip_data or not self._initialized:
            return
        
        title, desc, stats = tooltip_data
        
        # 提示框参数
        padding = 12
        line_height = 18
        corner_radius = 8
        
        # 计算框的宽度和高度
        title_surf = self.font_title.render(title, True, (255, 255, 255))
        desc_surf = self.font_desc.render(desc, True, (200, 200, 200))
        
        max_width = max(title_surf.get_width(), desc_surf.get_width())
        for stat in stats:
            stat_surf = self.font_stats.render(stat, True, (180, 180, 180))
            max_width = max(max_width, stat_surf.get_width())
        
        width = max_width + padding * 2 + 20
        height = padding * 2 + title_surf.get_height() + 8
        
        # 描述可能有多行
        desc_lines = desc.split('\n')
        for line in desc_lines:
            height += line_height
        
        for stat in stats:
            height += line_height
        
        # 位置：鼠标右侧，如果超出屏幕则左侧
        mx, my = mouse_pos
        x = mx + 20
        y = my + 20
        
        if x + width > screen.get_width():
            x = mx - width - 10
        if y + height > screen.get_height():
            y = screen.get_height() - height - 10
        
        # 绘制半透明背景
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 背景渐变效果（深色到稍亮）
        for i in range(height):
            alpha = 220
            r = max(0, 30 - i // 10)
            g = max(0, 30 - i // 10)  
            b = max(0, 40 - i // 10)
            pygame.draw.line(bg_surface, (r, g, b, alpha), (0, i), (width, i))
        
        # 边框
        pygame.draw.rect(bg_surface, (100, 120, 180, 255), 
                        (0, 0, width, height), 2, border_radius=corner_radius)
        
        # 绘制圆角矩形背景
        pygame.draw.rect(bg_surface, (20, 25, 35, 230), 
                        (2, 2, width-4, height-4), border_radius=corner_radius-2)
        
        screen.blit(bg_surface, (x, y))
        
        # 绘制标题
        screen.blit(title_surf, (x + padding, y + padding))
        
        # 绘制分隔线
        py = y + padding + title_surf.get_height() + 6
        pygame.draw.line(screen, (80, 90, 120), (x + padding, py), 
                        (x + width - padding, py), 1)
        
        # 绘制描述
        dy = py + 8
        for line in desc_lines:
            desc_s = self.font_desc.render(line, True, (200, 200, 200))
            screen.blit(desc_s, (x + padding, dy))
            dy += line_height
        
        # 绘制属性
        for stat in stats:
            stat_surf = self.font_stats.render(stat, True, (150, 200, 255))
            screen.blit(stat_surf, (x + padding, dy))
            dy += line_height


def get_tooltip_system():
    """获取提示系统全局实例"""
    global _tooltip_instance
    if _tooltip_instance is None:
        _tooltip_instance = TooltipSystem()
    return _tooltip_instance