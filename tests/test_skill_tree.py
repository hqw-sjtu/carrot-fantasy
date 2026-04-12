# -*- coding: utf-8 -*-
"""测试技能树可视化系统"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None

from skill_tree_view import skill_tree_view, TOWER_SKILL_TREES, calculate_skill_node_pos


class TestSkillTreeDefinition:
    """测试技能树定义"""
    
    def test_all_towers_have_skill_trees(self):
        """所有塔类型都有技能树"""
        expected_towers = ["arrow", "cannon", "magic", "ice"]
        for tower in expected_towers:
            assert tower in TOWER_SKILL_TREES, f"{tower} 缺少技能树"
            
    def test_skill_tree_has_required_fields(self):
        """技能树包含必要字段"""
        for tree_id, tree in TOWER_SKILL_TREES.items():
            assert "name" in tree
            assert "color" in tree
            assert "skills" in tree
            assert len(tree["skills"]) > 0
            
    def test_skill_has_required_fields(self):
        """技能包含必要字段"""
        for tree_id, tree in TOWER_SKILL_TREES.items():
            for skill in tree["skills"]:
                assert "id" in skill
                assert "name" in skill
                assert "desc" in skill
                assert "req" in skill
                assert "pos" in skill


class TestSkillTreeView:
    """测试技能树视图"""
    
    def test_init(self):
        """初始化状态"""
        assert skill_tree_view.visible == False
        assert skill_tree_view.current_tree == "arrow"
        assert len(skill_tree_view.learned_skills) == 0
        
    def test_toggle(self):
        """切换显示"""
        skill_tree_view.visible = False
        skill_tree_view.toggle()
        assert skill_tree_view.visible == True
        skill_tree_view.toggle()
        assert skill_tree_view.visible == False
        
    def test_show_specific_tree(self):
        """显示指定技能树"""
        skill_tree_view.show("cannon")
        assert skill_tree_view.visible == True
        assert skill_tree_view.current_tree == "cannon"
        
    def test_show_invalid_tree(self):
        """显示无效技能树"""
        skill_tree_view.visible = False
        skill_tree_view.show("invalid")
        assert skill_tree_view.visible == False  # 不应显示
        
    def test_learn_skill(self):
        """学习技能"""
        skill_tree_view.learned_skills.clear()
        skill_tree_view.learn_skill("pierce")
        assert "pierce" in skill_tree_view.learned_skills
        
    def test_can_learn_no_prereqs(self):
        """无前置技能可学习"""
        skill_tree_view.current_tree = "arrow"
        skill_tree_view.learned_skills.clear()
        # 根技能应该可以学习
        assert skill_tree_view.can_learn("pierce") == True
        
    def test_cannot_learn_without_prereq(self):
        """未满足前置无法学习"""
        skill_tree_view.current_tree = "arrow"
        skill_tree_view.learned_skills.clear()
        # 需要前置的技能不能学习
        assert skill_tree_view.can_learn("pierce_plus") == False
        
    def test_can_learn_with_prereq(self):
        """满足前置可以学习"""
        skill_tree_view.current_tree = "arrow"
        skill_tree_view.learned_skills.clear()
        skill_tree_view.learn_skill("pierce")
        # 满足前置后可学习
        assert skill_tree_view.can_learn("pierce_plus") == True
        
    def test_cannot_relearn(self):
        """已学习无法重复学习"""
        skill_tree_view.current_tree = "arrow"
        skill_tree_view.learned_skills.clear()
        skill_tree_view.learn_skill("pierce")
        # 已学习的无法再学习
        assert skill_tree_view.can_learn("pierce") == False


class TestPositionCalculation:
    """测试位置计算"""
    
    def test_calculate_position(self):
        """计算技能节点位置"""
        x, y = calculate_skill_node_pos("arrow", "pierce", 400, 300)
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        
    def test_invalid_tree(self):
        """无效技能树返回中心位置"""
        x, y = calculate_skill_node_pos("invalid", "skill", 400, 300)
        assert x == 400
        assert y == 300
        
    def test_invalid_skill(self):
        """无效技能返回中心位置"""
        x, y = calculate_skill_node_pos("arrow", "invalid", 400, 300)
        assert x == 400
        assert y == 300


if __name__ == "__main__":
    pytest.main([__file__, "-v"])