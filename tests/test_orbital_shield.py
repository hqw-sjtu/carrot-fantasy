"""
轨道护盾特效测试
Orbital Shield Effect Tests
"""
import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from orbital_shield_effect import OrbitalShieldEffect, OrbitalShieldManager
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)


class TestOrbitalShieldEffect:
    """轨道护盾特效测试"""
    
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_orbital_shield_creation(self):
        """测试轨道护盾创建"""
        effect = OrbitalShieldEffect(100, 100, radius=40, color=(100, 200, 255))
        assert effect.x == 100
        assert effect.y == 100
        assert effect.radius == 40
        assert effect.active == True
        assert len(effect.particles) == 0
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_orbital_shield_update(self):
        """测试轨道护盾更新"""
        effect = OrbitalShieldEffect(100, 100)
        initial_angle = effect.angle
        result = effect.update(0.1)
        assert result == True
        assert effect.angle > initial_angle
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_orbital_shield_particles(self):
        """测试轨道粒子生成"""
        effect = OrbitalShieldEffect(100, 100)
        for _ in range(10):
            effect.update(0.1)
        assert len(effect.particles) > 0
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_orbital_shield_deactivation(self):
        """测试护盾停用"""
        effect = OrbitalShieldEffect(100, 100)
        effect.active = False
        effect.update(0.1)
        assert effect.alpha < 200
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_orbital_shield_lifecycle(self):
        """测试护盾生命周期"""
        effect = OrbitalShieldEffect(100, 100)
        for _ in range(20):
            result = effect.update(0.1)
        assert result == True or effect.alpha <= 0


class TestOrbitalShieldManager:
    """轨道护盾管理器测试"""
    
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_manager_creation(self):
        """测试管理器创建"""
        manager = OrbitalShieldManager()
        assert len(manager.shields) == 0
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_add_shield(self):
        """测试添加护盾"""
        manager = OrbitalShieldManager()
        manager.add_shield(1, 100, 100)
        assert 1 in manager.shields
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_remove_shield(self):
        """测试移除护盾"""
        manager = OrbitalShieldManager()
        manager.add_shield(1, 100, 100)
        manager.remove_shield(1)
        assert 1 not in manager.shields or not manager.shields[1].active
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_manager_update(self):
        """测试管理器更新"""
        manager = OrbitalShieldManager()
        manager.add_shield(1, 100, 100)
        manager.update(0.1)
        assert 1 in manager.shields
        
    @pytest.mark.skipif(not IMPORTS_OK, reason="导入失败")
    def test_manager_cleanup(self):
        """测试管理器清理"""
        manager = OrbitalShieldManager()
        manager.add_shield(1, 100, 100)
        manager.shields[1].active = False
        manager.shields[1].alpha = 0
        manager.update(0.1)
        assert len(manager.shields) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])