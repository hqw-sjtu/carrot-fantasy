"""
保卫萝卜核心功能测试套件
Carrot Fantasy Core Test Suite
"""
import sys
import os
import pytest

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMonsters:
    """怪物系统测试"""
    
    def test_monster_init(self):
        """测试怪物初始化"""
        from monsters import Monster
        monster = Monster(100, 200, 1)
        assert monster.x == 100
        assert monster.y == 200
        assert monster.hp == 100
        assert monster.alive is True
    
    def test_monster_take_damage(self):
        """测试怪物受伤"""
        from monsters import Monster
        monster = Monster(100, 200, 1)
        monster.take_damage(30)
        assert monster.hp == 70
    
    def test_monster_death(self):
        """测试怪物死亡"""
        from monsters import Monster
        monster = Monster(100, 200, 1)
        monster.take_damage(100)
        assert monster.alive is False


class TestTowers:
    """防御塔系统测试"""
    
    def test_tower_init(self):
        """测试防御塔初始化"""
        from towers import Tower
        tower = Tower(200, 200, '箭塔')
        assert tower.x == 200
        assert tower.y == 200
        assert tower.tower_type == '箭塔'
        assert tower.damage > 0
    
    def test_tower_attack_range(self):
        """测试攻击范围"""
        from towers import Tower
        tower = Tower(200, 200, '炮塔')
        assert tower.attack_range > 0
    
    def test_tower_find_target(self):
        """测试目标查找"""
        from towers import Tower
        from monsters import Monster
        tower = Tower(200, 200, '箭塔')
        monster = Monster(220, 220, 1)  # 在攻击范围内
        targets = tower.find_targets([monster])
        assert len(targets) > 0


class TestProjectiles:
    """子弹系统测试"""
    
    def test_projectile_init(self):
        """测试子弹初始化"""
        from projectiles import Projectile
        proj = Projectile(100, 100, 200, 200, 10, 'arrow')
        assert proj.x == 100
        assert proj.y == 100
        assert proj.damage == 10
    
    def test_projectile_movement(self):
        """测试子弹移动"""
        from projectiles import Projectile
        proj = Projectile(100, 100, 200, 200, 10, 'arrow')
        initial_x, initial_y = proj.x, proj.y
        proj.move()
        # 子弹应该向目标移动
        assert proj.x != initial_x or proj.y != initial_y


class TestWaves:
    """波次系统测试"""
    
    def test_wave_init(self):
        """测试波次初始化"""
        from waves import WaveManager
        wm = WaveManager()
        assert wm.current_wave == 0
        assert wm.wave_in_progress is False
    
    def test_wave_start(self):
        """测试波次开始"""
        from waves import WaveManager
        wm = WaveManager()
        wm.start_wave(1)
        assert wm.current_wave == 1
        assert wm.wave_in_progress is True


class TestConfig:
    """配置系统测试"""
    
    def test_config_load(self):
        """测试配置加载"""
        from config_loader import load_config
        config = load_config()
        assert config is not None
        assert 'game_mode' in config


class TestTowerPlacement:
    """塔放置系统测试"""
    
    def test_can_place_tower(self):
        """测试塔放置检查"""
        from tower_placement import can_place_tower
        # 假设(100,100)不在路径上，可以放置
        result = can_place_tower(100, 100, [])
        assert isinstance(result, bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])