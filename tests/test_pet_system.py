"""
保卫萝卜 - 宠物系统测试
Carrot Fantasy - Pet System Tests
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pytest.skip("pygame not available", allow_module_level=True)

from pet_system import Pet, PetSystem, get_pet_system


class TestPet:
    """宠物单元测试"""
    
    def test_pet_init(self):
        """测试宠物初始化"""
        pet = Pet("cat", 100, 200)
        assert pet.pet_type == "cat"
        assert pet.x == 100
        assert pet.y == 200
        assert pet.state == "idle"
        assert pet.direction == 1
    
    def test_pet_update_idle(self):
        """测试宠物空闲状态 - 当玩家位置足够近时"""
        pet = Pet("cat", 100, 200)
        # 宠物位置100,200，玩家位置60,180
        # 目标位置 = 60+40=100, 180+20=200
        # 距离 = 0，宠物应该在目标位置
        pet.update(0.1, (60, 180))
        assert pet.state == "idle"
    
    def test_pet_update_walking(self):
        """测试宠物行走状态"""
        pet = Pet("cat", 100, 200)
        pet.update(0.1, (200, 200))  # 远离玩家，触发行走
        assert pet.state == "walking"
        assert pet.direction == 1  # 向右
    
    def test_pet_update_left_direction(self):
        """测试宠物向左移动"""
        pet = Pet("cat", 200, 200)
        pet.update(0.1, (100, 200))
        assert pet.direction == -1
    
    def test_pet_animation_frames(self):
        """测试宠物动画帧更新"""
        pet = Pet("cat", 100, 200)
        initial_frame = pet.animation_frame
        pet.update(0.2, (100, 200))  # 超过0.15秒间隔
        assert pet.animation_frame != initial_frame or pet.animation_frame == 0


class TestPetSystem:
    """宠物系统测试"""
    
    def test_pet_system_init(self):
        """测试宠物系统初始化"""
        system = PetSystem()
        assert len(system.active_pets) == 0
        assert system.bonus_multipliers["gold"] == 1.0
        assert system.bonus_multipliers["experience"] == 1.0
        assert system.bonus_multipliers["attack_speed"] == 1.0
    
    def test_add_pet(self):
        """测试添加宠物"""
        system = PetSystem()
        result = system.add_pet("cat", 100, 200)
        assert result is True
        assert len(system.active_pets) == 1
        assert system.active_pets[0].pet_type == "cat"
    
    def test_add_multiple_pets(self):
        """测试添加多只宠物"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        system.add_pet("dog", 150, 200)
        system.add_pet("rabbit", 200, 200)
        assert len(system.active_pets) == 3
    
    def test_max_pets_limit(self):
        """测试宠物数量上限"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        system.add_pet("dog", 150, 200)
        system.add_pet("rabbit", 200, 200)
        # 尝试添加第4只
        result = system.add_pet("cat", 250, 200)
        assert result is False
        assert len(system.active_pets) == 3
    
    def test_remove_pet(self):
        """测试移除宠物"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        system.add_pet("dog", 150, 200)
        result = system.remove_pet("cat")
        assert result is True
        assert len(system.active_pets) == 1
        assert system.active_pets[0].pet_type == "dog"
    
    def test_pet_bonuses(self):
        """测试宠物增益效果"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        assert system.bonus_multipliers["gold"] == 1.05
        
        system.add_pet("dog", 150, 200)
        assert system.bonus_multipliers["experience"] == 1.03
        
        system.add_pet("rabbit", 200, 200)
        assert system.bonus_multipliers["attack_speed"] == 1.02
    
    def test_apply_gold_bonus(self):
        """测试金币增益应用"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        # 基础金币100，+5%加成 = 105
        result = system.apply_gold_bonus(100)
        assert result == 105
    
    def test_apply_exp_bonus(self):
        """测试经验增益应用"""
        system = PetSystem()
        system.add_pet("dog", 100, 200)
        # 基础经验50，+3%加成 = 51
        result = system.apply_exp_bonus(50)
        assert result == 51
    
    def test_pet_types_config(self):
        """测试宠物类型配置"""
        system = PetSystem()
        assert "cat" in system.PET_TYPES
        assert "dog" in system.PET_TYPES
        assert "rabbit" in system.PET_TYPES
        assert system.PET_TYPES["cat"]["bonus"] == "+5% 金币获取"
        assert system.PET_TYPES["dog"]["bonus"] == "+3% 经验获取"
        assert system.PET_TYPES["rabbit"]["bonus"] == "+2% 攻速加成"
    
    def test_get_pet_info(self):
        """测试获取宠物信息"""
        system = PetSystem()
        system.add_pet("cat", 100, 200)
        info = system.get_pet_info()
        assert len(info) == 1
        assert info[0]["type"] == "cat"
        assert info[0]["name"] == "🐱 小喵"
    
    def test_unlock_pet(self):
        """测试宠物解锁"""
        system = PetSystem()
        assert system.pet_unlocked["dog"] is False
        system.unlock_pet("dog")
        assert system.pet_unlocked["dog"] is True


class TestPetGlobalInstance:
    """全局宠物系统实例测试"""
    
    def test_get_pet_system_singleton(self):
        """测试全局单例"""
        system1 = get_pet_system()
        system2 = get_pet_system()
        assert system1 is system2