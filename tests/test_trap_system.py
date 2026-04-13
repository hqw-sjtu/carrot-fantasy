"""
保卫萝卜 - 陷阱系统测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src.trap_system import Trap, SpikeTrap, PoisonTrap, FreezeTrap, TrapSystem, get_trap_system


class MockMonster:
    """模拟怪物"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.speed = 2
        self.original_speed = 2
        self.status_effects = {}
        
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            
    def apply_status(self, status_type, duration, multiplier):
        self.status_effects[status_type] = {
            'duration': duration,
            'multiplier': multiplier,
            'end_time': pygame.time.get_ticks() + duration
        }
        
    def remove_status(self, status_type):
        if status_type in self.status_effects:
            del self.status_effects[status_type]


@pytest.fixture
def pygame_init():
    """初始化pygame"""
    if not pygame.get_init():
        pygame.init()
    yield


class TestTrapTypes:
    """陷阱类型测试"""
    def test_trap_types_exist(self):
        """陷阱类型定义存在"""
        assert 'spike' in Trap.TRAP_TYPES
        assert 'poison' in Trap.TRAP_TYPES
        assert 'freeze' in Trap.TRAP_TYPES
        
    def test_trap_type_config(self):
        """陷阱类型配置正确"""
        spike = Trap.TRAP_TYPES['spike']
        assert spike['name'] == '尖刺陷阱'
        assert spike['damage'] == 5
        assert spike['cost'] == 50


class TestSpikeTrap:
    """尖刺陷阱测试"""
    def test_spike_trap_creation(self, pygame_init):
        """创建尖刺陷阱"""
        trap = SpikeTrap(100, 100)
        assert trap.trap_type == 'spike'
        assert trap.x == 100
        assert trap.y == 100
        assert trap.level == 1
        
    def test_spike_trap_upgrade(self, pygame_init):
        """升级尖刺陷阱"""
        trap = SpikeTrap(100, 100)
        initial_damage = trap.damage
        
        trap.upgrade()
        assert trap.level == 2
        assert trap.damage > initial_damage
        
    def test_spike_trap_max_level(self, pygame_init):
        """最大等级限制"""
        trap = SpikeTrap(100, 100)
        for _ in range(5):
            trap.upgrade()
        assert trap.level == 3


class TestPoisonTrap:
    """毒陷阱测试"""
    def test_poison_trap_creation(self, pygame_init):
        """创建毒陷阱"""
        trap = PoisonTrap(100, 100)
        assert trap.trap_type == 'poison'
        assert trap.name == '毒陷阱'
        
    def test_poison_effect(self, pygame_init):
        """毒效果应用"""
        trap = PoisonTrap(100, 100)
        monster = MockMonster(100, 100)  # 在陷阱范围内
        
        current_time = pygame.time.get_ticks()
        trap.update(current_time, [monster])
        
        # 效果应该在monster身上
        assert len(trap.affected_monsters) > 0


class TestFreezeTrap:
    """冰霜陷阱测试"""
    def test_freeze_trap_creation(self, pygame_init):
        """创建冰霜陷阱"""
        trap = FreezeTrap(100, 100)
        assert trap.trap_type == 'freeze'
        assert trap.name == '冰霜陷阱'


class TestTrapSystem:
    """陷阱系统测试"""
    def test_trap_system_creation(self):
        """创建陷阱系统"""
        system = TrapSystem()
        assert len(system.traps) == 0
        
    def test_add_trap(self, pygame_init):
        """添加陷阱"""
        system = TrapSystem()
        trap = system.add_trap('spike', 100, 100)
        assert len(system.traps) == 1
        assert trap.trap_type == 'spike'
        
    def test_get_trap_at(self, pygame_init):
        """获取位置处的陷阱"""
        system = TrapSystem()
        trap = system.add_trap('spike', 100, 100)
        
        found = system.get_trap_at(100, 100)
        assert found == trap
        
    def test_remove_trap(self, pygame_init):
        """移除陷阱"""
        system = TrapSystem()
        trap = system.add_trap('spike', 100, 100)
        system.remove_trap(trap)
        assert len(system.traps) == 0
        
    def test_trap_update(self, pygame_init):
        """陷阱更新"""
        system = TrapSystem()
        system.add_trap('spike', 100, 100)
        
        monster = MockMonster(100, 100)
        current_time = pygame.time.get_ticks()
        
        system.update(current_time, [monster])
        
    def test_save_load(self, pygame_init):
        """保存和加载"""
        system = TrapSystem()
        system.add_trap('spike', 100, 100)
        system.add_trap('poison', 200, 200)
        
        # 升级一个陷阱
        system.traps[0].level = 2
        
        # 保存
        data = system.save()
        
        # 加载
        new_system = TrapSystem()
        new_system.load(data)
        
        assert len(new_system.traps) == 2
        assert new_system.traps[0].level == 2


class TestGlobalInstance:
    """全局单例测试"""
    def test_get_trap_system(self):
        """获取全局陷阱系统"""
        global _trap_system
        _trap_system = None  # 重置
        
        system1 = get_trap_system()
        system2 = get_trap_system()
        assert system1 is system2


class TestTrapDraw:
    """陷阱绘制测试"""
    def test_draw_spike_trap(self, pygame_init):
        """绘制尖刺陷阱"""
        screen = pygame.Surface((400, 400))
        trap = SpikeTrap(200, 200)
        
        # 不报错即通过
        trap.draw(screen)
        
    def test_draw_multiple_traps(self, pygame_init):
        """绘制多个陷阱"""
        screen = pygame.Surface((400, 400))
        system = TrapSystem()
        system.add_trap('spike', 100, 100)
        system.add_trap('poison', 200, 200)
        system.add_trap('freeze', 300, 300)
        
        system.draw(screen)


class TestTrapInfo:
    """陷阱信息测试"""
    def test_get_info(self, pygame_init):
        """获取陷阱信息"""
        trap = SpikeTrap(100, 100)
        info = trap.get_info()
        
        assert info['type'] == 'spike'
        assert info['name'] == '尖刺陷阱'
        assert info['level'] == 1
        assert 'damage' in info
        assert 'range' in info
        assert 'cost' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])