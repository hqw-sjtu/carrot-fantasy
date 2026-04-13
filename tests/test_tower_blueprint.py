"""
保卫萝卜 - 防御塔蓝图系统测试
"""
import pytest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pytest.skip("Pygame not available", allow_module_level=True)

from tower_blueprint import TowerBlueprint, BlueprintLibrary, BlueprintManager


class TestTowerBlueprint:
    """测试防御塔蓝图"""
    
    def test_blueprint_creation(self):
        """测试蓝图创建"""
        bp = TowerBlueprint(
            name="强力箭塔",
            tower_type="arrow",
            level=3,
            quality="Epic",
            position=(100, 200)
        )
        assert bp.name == "强力箭塔"
        assert bp.tower_type == "arrow"
        assert bp.level == 3
        assert bp.quality == "Epic"
        assert bp.position == (100, 200)
    
    def test_blueprint_to_dict(self):
        """测试蓝图转字典"""
        bp = TowerBlueprint(
            name="测试塔",
            tower_type="cannon",
            position=(50, 60)
        )
        data = bp.to_dict()
        assert data['name'] == "测试塔"
        assert data['tower_type'] == "cannon"
        assert isinstance(data['position'], list)
    
    def test_blueprint_from_dict(self):
        """测试从字典创建蓝图"""
        data = {
            'name': '魔法塔',
            'tower_type': 'magic',
            'level': 2,
            'quality': 'Rare',
            'position': [100, 150],
            'skills': ['fire', 'ice'],
            'skin': 'golden',
            'description': '强力魔法塔'
        }
        bp = TowerBlueprint.from_dict(data)
        assert bp.name == '魔法塔'
        assert bp.position == (100, 150)
        assert bp.skills == ['fire', 'ice']


class TestBlueprintLibrary:
    """测试蓝图库"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)
    
    def test_library_creation(self, temp_dir):
        """测试库创建"""
        lib = BlueprintLibrary(temp_dir)
        assert os.path.exists(temp_dir)
        assert lib.save_dir == temp_dir
    
    def test_save_and_load_blueprint(self, temp_dir):
        """测试保存和加载蓝图"""
        lib = BlueprintLibrary(temp_dir)
        bp = TowerBlueprint(
            name="炮塔配置",
            tower_type="cannon",
            level=3,
            quality="Epic"
        )
        
        # 保存
        assert lib.save_blueprint(bp) == True
        assert os.path.exists(os.path.join(temp_dir, "炮塔配置.json"))
        
        # 加载
        loaded = lib.load_blueprint("炮塔配置")
        assert loaded is not None
        assert loaded.name == bp.name
        assert loaded.level == bp.level
    
    def test_delete_blueprint(self, temp_dir):
        """测试删除蓝图"""
        lib = BlueprintLibrary(temp_dir)
        bp = TowerBlueprint(name="删除测试", tower_type="arrow")
        lib.save_blueprint(bp)
        
        assert lib.delete_blueprint("删除测试") == True
        assert os.path.exists(os.path.join(temp_dir, "删除测试.json")) == False
    
    def test_list_blueprints(self, temp_dir):
        """测试列出蓝图"""
        lib = BlueprintLibrary(temp_dir)
        
        bp1 = TowerBlueprint(name="塔A", tower_type="arrow")
        bp2 = TowerBlueprint(name="塔B", tower_type="cannon")
        
        lib.save_blueprint(bp1)
        lib.save_blueprint(bp2)
        
        names = lib.list_blueprints()
        assert "塔A" in names
        assert "塔B" in names
    
    def test_blueprint_not_found(self, temp_dir):
        """测试加载不存在的蓝图"""
        lib = BlueprintLibrary(temp_dir)
        assert lib.load_blueprint("不存在的蓝图") is None


class TestBlueprintManager:
    """测试全局管理器"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        mgr1 = BlueprintManager()
        mgr2 = BlueprintManager()
        assert mgr1 is mgr2
    
    def test_get_blueprint_manager(self):
        """测试便捷获取方法"""
        from tower_blueprint import get_blueprint_manager
        mgr = get_blueprint_manager()
        assert isinstance(mgr, BlueprintManager)


class TestBlueprintIntegration:
    """集成测试"""
    
    @pytest.fixture
    def temp_dir(self):
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)
    
    def test_full_workflow(self, temp_dir):
        """完整工作流测试"""
        lib = BlueprintLibrary(temp_dir)
        
        # 创建多个蓝图
        blueprints = [
            TowerBlueprint(name="箭塔", tower_type="arrow", level=1),
            TowerBlueprint(name="炮塔", tower_type="cannon", level=2),
            TowerBlueprint(name="魔法塔", tower_type="magic", level=3),
        ]
        
        # 保存所有
        for bp in blueprints:
            lib.save_blueprint(bp)
        
        # 验证数量
        assert len(lib.list_blueprints()) == 3
        
        # 获取所有
        all_bp = lib.get_all_blueprints()
        assert len(all_bp) == 3
        
        # 验证数据完整性
        for bp in blueprints:
            loaded = all_bp.get(bp.name)
            assert loaded is not None
            assert loaded.tower_type == bp.tower_type
            assert loaded.level == bp.level