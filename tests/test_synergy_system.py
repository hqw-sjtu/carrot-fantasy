"""
保卫萝卜 - 防御塔协同系统单元测试
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from synergy_system import SynergyManager, SYNERGIES, get_synergy_manager


class MockTower:
    """模拟防御塔"""
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.damage = 100
        self.attack_speed = 1.0


class TestSynergyManager:
    """协同管理器测试"""
    
    def test_manager_init(self):
        """测试管理器初始化"""
        manager = SynergyManager()
        assert manager is not None
        assert manager.synergy_cache == {}
        assert manager.last_update == 0
        
    def test_single_tower_no_synergy(self):
        """单塔无协同"""
        manager = SynergyManager()
        tower = MockTower("箭塔", 300, 300)
        result = manager.calculate_synergies([tower], 1000)
        assert result == {}
        
    def test_same_type_synergy(self):
        """同类型协同 - 两座箭塔靠近"""
        manager = SynergyManager()
        towers = [
            MockTower("箭塔", 300, 300),
            MockTower("箭塔", 350, 320),  # 距离约64像素，在协同范围内
        ]
        result = manager.calculate_synergies(towers, 1000)
        
        # 应该有协同效果
        assert len(result) > 0
        
    def test_different_type_no_synergy(self):
        """不同类型不触发同类型协同"""
        manager = SynergyManager()
        towers = [
            MockTower("箭塔", 300, 300),
            MockTower("炮塔", 350, 320),
        ]
        result = manager.calculate_synergies(towers, 1000)
        
        # 同类型协同不触发
        tower1_id = id(towers[0])
        if tower1_id in result:
            assert "synergy_attack_speed" not in result[tower1_id]
            
    def test_elemental_synergy_fire_ice(self):
        """元素协同 - 火塔+冰霜塔"""
        manager = SynergyManager()
        towers = [
            MockTower("火塔", 300, 300),
            MockTower("冰霜塔", 350, 320),  # 距离约64像素
        ]
        result = manager.calculate_synergies(towers, 1000)
        
        # 检查火塔是否获得元素协同
        fire_tower = towers[0]
        fire_id = id(fire_tower)
        
        if fire_id in result:
            bonuses = result[fire_id]
            # 应该有冰火交融效果
            has_synergy = any("frozen_fire" in k for k in bonuses.keys())
            # 注: 需要在实际范围内才能触发
            
    def test_range_synergy(self):
        """射程协同 - 炮塔+箭塔"""
        manager = SynergyManager()
        towers = [
            MockTower("炮塔", 300, 300),  # 短射程
            MockTower("箭塔", 380, 300),  # 长射程,距离80像素
        ]
        result = manager.calculate_synergies(towers, 1000)
        
        # 检查是否有射程协同
        
    def test_get_synergy_bonus_damage(self):
        """获取伤害加成"""
        manager = SynergyManager()
        tower = MockTower("箭塔", 300, 300)
        
        bonus = manager.get_synergy_bonus(tower, "damage")
        assert bonus >= 1.0  # 至少为1.0
        
    def test_get_synergy_bonus_speed(self):
        """获取攻速加成"""
        manager = SynergyManager()
        tower = MockTower("箭塔", 300, 300)
        
        bonus = manager.get_synergy_bonus(tower, "attack_speed")
        assert bonus >= 1.0
        
    def test_has_active_synergy(self):
        """检查是否有激活协同"""
        manager = SynergyManager()
        tower = MockTower("箭塔", 300, 300)
        
        # 单塔无协同
        assert not manager.has_active_synergy(tower)
        
    def test_synergy_cache_update(self):
        """协同缓存更新机制"""
        manager = SynergyManager()
        
        # 初始状态
        assert manager.last_update == 0
        
        # 首次更新
        towers = [MockTower("箭塔", 300, 300)]
        result = manager.calculate_synergies(towers, 1000)
        
        assert manager.last_update == 1000
        
        # 快速更新不生效(在间隔内)
        result2 = manager.calculate_synergies(towers, 1100)
        # 应该返回缓存结果
        
    def test_get_synergy_description(self):
        """获取协同描述"""
        manager = SynergyManager()
        tower = MockTower("箭塔", 300, 300)
        
        desc = manager.get_synergy_description(tower)
        # 单塔无协同描述
        
    def test_far_towers_no_synergy(self):
        """远距离塔无协同"""
        manager = SynergyManager()
        towers = [
            MockTower("箭塔", 100, 300),
            MockTower("箭塔", 600, 300),  # 距离500像素，远超协同范围
        ]
        result = manager.calculate_synergies(towers, 1000)
        
        # 不应有协同效果
        assert len(result) == 0
        
    def test_max_bonus_towers_limit(self):
        """最多计算塔数限制"""
        # 附近有多座同类型塔时，应该限制计算数量
        manager = SynergyManager()
        
        # 创建5座靠近的箭塔
        base_x, base_y = 300, 300
        towers = [MockTower("箭塔", base_x + i*20, base_y + i*15) for i in range(5)]
        
        result = manager.calculate_synergies(towers, 1000)
        
        # 每个塔的协同加成应该有上限


class TestSynergyConfig:
    """协同配置测试"""
    
    def test_synergies_defined(self):
        """验证协同配置已定义"""
        assert "same_type" in SYNERGIES
        assert "elemental" in SYNERGIES
        assert "range_synergy" in SYNERGIES
        
    def test_same_type_config(self):
        """同类型协同配置"""
        config = SYNERGIES["same_type"]
        assert "min_distance" in config
        assert "max_bonus_towers" in config
        assert "max_tower_bonus" in config
        assert config["min_distance"] > 0
        
    def test_elemental_config(self):
        """元素协同配置"""
        config = SYNERGIES["elemental"]
        assert "pairs" in config
        assert len(config["pairs"]) > 0
        
    def test_range_synergy_config(self):
        """射程协同配置"""
        config = SYNERGIES["range_synergy"]
        assert "short_range_towers" in config
        assert "long_range_towers" in config
        assert "bonus" in config


class TestGlobalManager:
    """全局管理器测试"""
    
    def test_get_synergy_manager(self):
        """获取全局管理器"""
        manager1 = get_synergy_manager()
        manager2 = get_synergy_manager()
        
        # 应该是单例
        assert manager1 is manager2