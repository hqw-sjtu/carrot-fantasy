import pytest
import os
import sys
import json
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tower_bestiary import TowerBestiary, get_bestiary


class TestTowerBestiary:
    """测试防御塔图鉴系统"""
    
    def setup_method(self):
        """每个测试前创建临时图鉴"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_path = None
        # 启用测试模式并传入临时路径
        TowerBestiary.enable_test_mode()
        temp_path = os.path.join(self.temp_dir, "bestiary.json")
        self.bestiary = TowerBestiary(path=temp_path)
    
    def teardown_method(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        TowerBestiary.reset_instance()
    
    def test_bestiary_init(self):
        """测试图鉴初始化"""
        assert self.bestiary is not None
        assert isinstance(self.bestiary.unlocked_towers, set)
        assert self.bestiary.get_unlocked_count() == 0
    
    def test_unlock_tower(self):
        """测试解锁塔"""
        result = self.bestiary.unlock_tower("箭塔")
        assert result is True
        assert "箭塔" in self.bestiary.unlocked_towers
        assert self.bestiary.get_unlocked_count() == 1
    
    def test_unlock_tower_duplicate(self):
        """测试重复解锁"""
        self.bestiary.unlock_tower("箭塔")
        result = self.bestiary.unlock_tower("箭塔")
        assert result is False
        assert self.bestiary.get_unlocked_count() == 1
    
    def test_is_unlocked(self):
        """测试检查是否解锁"""
        assert not self.bestiary.is_unlocked("箭塔")
        self.bestiary.unlock_tower("箭塔")
        assert self.bestiary.is_unlocked("箭塔")
    
    def test_record_kill(self):
        """测试记录击杀"""
        self.bestiary.record_kill("箭塔")
        self.bestiary.record_kill("箭塔")
        stats = self.bestiary.get_tower_stats("箭塔")
        assert stats['kills'] == 2
    
    def test_record_damage(self):
        """测试记录伤害"""
        self.bestiary.record_damage("箭塔", 100)
        self.bestiary.record_damage("箭塔", 50)
        stats = self.bestiary.get_tower_stats("箭塔")
        assert stats['damage'] == 150
    
    def test_reset(self):
        """测试重置图鉴"""
        self.bestiary.unlock_tower("箭塔")
        self.bestiary.unlock_tower("炮塔")
        self.bestiary.record_kill("箭塔")
        
        self.bestiary.reset()
        
        assert self.bestiary.get_unlocked_count() == 0
        assert len(self.bestiary.tower_stats) == 0
    
    def test_multiple_towers(self):
        """测试多个塔"""
        towers = ["箭塔", "炮塔", "魔法塔", "冰霜塔"]
        for t in towers:
            self.bestiary.unlock_tower(t)
            self.bestiary.record_kill(t)
        
        assert self.bestiary.get_unlocked_count() == 4
        for t in towers:
            assert self.bestiary.is_unlocked(t)
    
    def test_save_and_load(self):
        """测试保存加载"""
        self.bestiary.unlock_tower("箭塔")
        self.bestiary.record_kill("箭塔")
        self.bestiary.record_damage("箭塔", 100)
        
        # 重新创建实例应该能读取 - 使用相同路径
        new_bestiary = TowerBestiary(path=self.bestiary.bestiary_path)
        
        assert new_bestiary.is_unlocked("箭塔")
        stats = new_bestiary.get_tower_stats("箭塔")
        assert stats['kills'] == 1
        assert stats['damage'] == 100


class TestBestiarySingleton:
    """测试单例模式"""
    
    def setup_method(self):
        TowerBestiary._instance = None
    
    def teardown_method(self):
        TowerBestiary._instance = None
    
    def test_singleton(self):
        """测试单例"""
        b1 = get_bestiary()
        b2 = get_bestiary()
        assert b1 is b2