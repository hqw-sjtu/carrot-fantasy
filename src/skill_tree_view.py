# -*- coding: utf-8 -*-
"""塔技能树可视化系统 - Skill Tree Visualization

显示防御塔的技能树发展路径，玩家可直观了解升级路线。
"""

import pygame

# 技能树定义
TOWER_SKILL_TREES = {
    "arrow": {
        "name": "⚔️ 箭塔",
        "color": (255, 180, 0),
        "skills": [
            {"id": "pierce", "name": "穿透射击", "desc": "子弹穿透多个目标", "req": [], "pos": (2, 0)},
            {"id": "snipe", "name": "狙击大师", "desc": "射程+50%, 伤害+30%", "req": [], "pos": (0, 1)},
            {"id": "rapid", "name": "急速射击", "desc": "攻速+40%", "req": [], "pos": (4, 1)},
            {"id": "pierce_plus", "name": "穿透强化", "desc": "穿透数+2", "req": ["pierce"], "pos": (2, 1)},
            {"id": "deadly", "name": "致命一击", "desc": "暴击率+20%", "req": ["snipe"], "pos": (0, 2)},
            {"id": "multishot", "name": "多重箭", "desc": "同时发射3支箭", "req": ["rapid"], "pos": (4, 2)},
        ]
    },
    "cannon": {
        "name": "💣 炮塔",
        "color": (255, 80, 0),
        "skills": [
            {"id": "explosion", "name": "毁灭轰炸", "desc": "范围伤害+50%", "req": [], "pos": (2, 0)},
            {"id": "long_range", "name": "远程轰炸", "desc": "射程+40%", "req": [], "pos": (0, 1)},
            {"id": "rapid_fire", "name": "速射炮", "desc": "攻速+30%", "req": [], "pos": (4, 1)},
            {"id": "mega", "name": "巨型炸弹", "desc": "暴击范围翻倍", "req": ["explosion"], "pos": (2, 1)},
            {"id": "cluster", "name": "子母弹", "desc": "分裂多个小爆炸", "req": ["long_range"], "pos": (0, 2)},
            {"id": "fire_rate", "name": "极速射击", "desc": "攻速再+30%", "req": ["rapid_fire"], "pos": (4, 2)},
        ]
    },
    "magic": {
        "name": "✨ 魔法塔",
        "color": (180, 100, 255),
        "skills": [
            {"id": "arcane", "name": "奥术爆发", "desc": "范围奥术伤害", "req": [], "pos": (2, 0)},
            {"id": "leech", "name": "能量汲取", "desc": "攻击回复生命", "req": [], "pos": (0, 1)},
            {"id": "chain", "name": "连锁闪电", "desc": "攻击弹跳3次", "req": [], "pos": (4, 1)},
            {"id": "void", "name": "虚空冲击", "desc": "范围+30%", "req": ["arcane"], "pos": (2, 1)},
            {"id": "vampire", "name": "吸血强化", "desc": "吸血+100%", "req": ["leech"], "pos": (0, 2)},
            {"id": "storm", "name": "闪电风暴", "desc": "链跳次数+3", "req": ["chain"], "pos": (4, 2)},
        ]
    },
    "ice": {
        "name": "❄️ 冰霜塔",
        "color": (100, 200, 255),
        "skills": [
            {"id": "freeze", "name": "冰封千里", "desc": "大范围减速", "req": [], "pos": (2, 0)},
            {"id": "chill", "name": "寒冰之气", "desc": "被动减速加强", "req": [], "pos": (0, 1)},
            {"id": "brittle", "name": "冰脆易碎", "desc": "减速目标易暴击", "req": [], "pos": (4, 1)},
            {"id": "absolute", "name": "绝对零度", "desc": "100%冻结2秒", "req": ["freeze"], "pos": (2, 1)},
            {"id": "frost_nova", "name": "冰霜新星", "desc": "周期性冰环", "req": ["chill"], "pos": (0, 2)},
            {"id": "shatter", "name": "粉碎", "desc": "击杀冻结目标=范围伤害", "req": ["brittle"], "pos": (4, 2)},
        ]
    }
}

# 技能树节点位置计算
def calculate_skill_node_pos(tree_id, skill_id, center_x, center_y, spacing_x=80, spacing_y=90):
    """计算技能节点在屏幕上的位置"""
    tree = TOWER_SKILL_TREES.get(tree_id)
    if not tree:
        return center_x, center_y
    
    for skill in tree["skills"]:
        if skill["id"] == skill_id:
            row, col = skill["pos"]
            x = center_x + (col - 2) * spacing_x
            y = center_y + row * spacing_y
            return x, y
    return center_x, center_y


class SkillTreeView:
    """技能树查看器"""
    
    def __init__(self):
        self.visible = False
        self.current_tree = "arrow"
        self.learned_skills = set()  # 已学习的技能
        self.hovered_skill = None
        self.animation_time = 0
        
    def toggle(self):
        """切换显示状态"""
        self.visible = not self.visible
        self.animation_time = 0
        
    def show(self, tree_id):
        """显示指定技能树"""
        if tree_id in TOWER_SKILL_TREES:
            self.current_tree = tree_id
            self.visible = True
            self.animation_time = 0
            
    def learn_skill(self, skill_id):
        """学习技能"""
        self.learned_skills.add(skill_id)
        
    def can_learn(self, skill_id):
        """检查是否可以学习该技能"""
        tree = TOWER_SKILL_TREES.get(self.current_tree)
        if not tree:
            return False
            
        for skill in tree["skills"]:
            if skill["id"] == skill_id:
                # 检查前置技能
                for req in skill["req"]:
                    if req not in self.learned_skills:
                        return False
                return skill["id"] not in self.learned_skills
        return False
        
    def update(self, dt):
        """更新动画"""
        self.animation_time += dt
        
    def draw(self, screen, font_small=None, font_medium=None):
        """绘制技能树"""
        if not self.visible:
            return
            
        if font_small is None:
            font_small = pygame.font.Font(None, 18)
        if font_medium is None:
            font_medium = pygame.font.Font(None, 24)
            
        screen_width, screen_height = screen.get_size()
        
        # 背景面板
        panel_w, panel_h = 500, 400
        panel_x = (screen_width - panel_w) // 2
        panel_y = (screen_height - panel_h) // 2
        
        # 绘制背景
        bg_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg_surface.fill((20, 20, 40, 230))
        pygame.draw.rect(bg_surface, (100, 100, 150), (0, 0, panel_w, panel_h), 3, border_radius=10)
        screen.blit(bg_surface, (panel_x, panel_y))
        
        # 标题
        tree = TOWER_SKILL_TREES[self.current_tree]
        title = font_medium.render(f"🎓 {tree['name']} 技能树", True, tree["color"])
        screen.blit(title, (panel_x + 20, panel_y + 15))
        
        # 关闭提示
        close_hint = font_small.render("[ESC] 关闭 | [Tab] 切换技能树", True, (150, 150, 150))
        screen.blit(close_hint, (panel_x + 20, panel_y + panel_h - 25))
        
        # 绘制连线
        center_x = panel_x + panel_w // 2
        center_y = panel_y + 100
        
        for skill in tree["skills"]:
            for req_id in skill["req"]:
                # 找到前置技能位置
                for req_skill in tree["skills"]:
                    if req_skill["id"] == req_id:
                        x1, y1 = calculate_skill_node_pos(self.current_tree, req_id, center_x, center_y)
                        x2, y2 = calculate_skill_node_pos(self.current_tree, skill_id, center_x, center_y)
                        
                        # 根据学习状态决定颜色
                        if req_id in self.learned_skills and skill["id"] in self.learned_skills:
                            line_color = (100, 255, 100)
                        elif req_id in self.learned_skills:
                            line_color = (255, 200, 0)
                        else:
                            line_color = (80, 80, 80)
                        
                        pygame.draw.line(screen, line_color, (x1 + 20, y1 + 20), (x2 + 20, y2 + 20), 2)
                        break
        
        # 绘制技能节点
        self.hovered_skill = None
        mouse_pos = pygame.mouse.get_pos()
        
        for skill in tree["skills"]:
            x, y = calculate_skill_node_pos(self.current_tree, skill_id, center_x, center_y)
            
            # 确定节点状态
            learned = skill["id"] in self.learned_skills
            available = self.can_learn(skill["id"])
            locked = not learned and not available
            
            # 节点颜色
            if learned:
                node_color = (100, 255, 100)
                border_color = (50, 200, 50)
            elif available:
                node_color = (255, 200, 0)
                border_color = (255, 150, 0)
            else:
                node_color = (80, 80, 80)
                border_color = (60, 60, 60)
            
            # 绘制节点
            node_rect = pygame.Rect(x, y, 40, 40)
            
            # 悬停检测
            if node_rect.collidepoint(mouse_pos):
                self.hovered_skill = skill
                pygame.draw.rect(screen, (255, 255, 255), node_rect, 3)
            else:
                pygame.draw.rect(screen, border_color, node_rect, 2)
            
            pygame.draw.rect(screen, node_color, node_rect.inflate(-4, -4), border_radius=8)
            
            # 技能图标(首字)
            icon = font_small.render(skill["name"][0], True, (255, 255, 255))
            screen.blit(icon, (x + 13, y + 8))
            
        # 绘制悬停提示
        if self.hovered_skill:
            self._draw_skill_tooltip(screen, self.hovered_skill, mouse_pos, font_small)
            
    def _draw_skill_tooltip(self, screen, skill, pos, font):
        """绘制技能提示"""
        tooltip_w, tooltip_h = 200, 70
        tip_x = min(pos[0] + 20, screen.get_width() - tooltip_w - 10)
        tip_y = min(pos[1] + 20, screen.get_height() - tooltip_h - 10)
        
        # 背景
        tip_bg = pygame.Surface((tooltip_w, tooltip_h), pygame.SRCALPHA)
        tip_bg.fill((0, 0, 0, 220))
        pygame.draw.rect(tip_bg, (150, 150, 50), (0, 0, tooltip_w, tooltip_h), 2, border_radius=5)
        screen.blit(tip_bg, (tip_x, tip_y))
        
        # 技能名
        name = font.render(skill["name"], True, (255, 200, 0))
        screen.blit(name, (tip_x + 10, tip_y + 8))
        
        # 描述
        desc = font.render(skill["desc"], True, (200, 200, 200))
        screen.blit(desc, (tip_x + 10, tip_y + 30))
        
        # 状态
        learned = skill["id"] in self.learned_skills
        available = self.can_learn(skill["id"])
        
        if learned:
            status = "✅ 已掌握"
            status_color = (100, 255, 100)
        elif available:
            status = "⭐ 可学习"
            status_color = (255, 200, 0)
        else:
            status = "🔒 未解锁"
            status_color = (150, 150, 150)
            
        status_text = font.render(status, True, status_color)
        screen.blit(status_text, (tip_x + 10, tip_y + 50))
        

# 全局实例
skill_tree_view = SkillTreeView()