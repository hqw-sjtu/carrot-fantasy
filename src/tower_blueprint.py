"""
保卫萝卜 - 防御塔蓝图系统
允许玩家保存、加载和分享防御塔配置
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class TowerBlueprint:
    """防御塔蓝图数据"""
    name: str
    tower_type: str
    level: int = 1
    quality: str = "Normal"
    position: tuple = (0, 0)
    skills: List[str] = field(default_factory=list)
    skin: str = "default"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['position'] = list(self.position)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TowerBlueprint':
        """从字典创建"""
        if 'position' in data and isinstance(data['position'], list):
            data['position'] = tuple(data['position'])
        return cls(**data)


class BlueprintLibrary:
    """蓝图库管理器"""
    
    def __init__(self, save_dir: str = "blueprints"):
        self.save_dir = save_dir
        self.blueprints: Dict[str, TowerBlueprint] = {}
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_blueprint(self, blueprint: TowerBlueprint) -> bool:
        """保存蓝图到文件"""
        try:
            filepath = os.path.join(self.save_dir, f"{blueprint.name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blueprint.to_dict(), f, indent=2, ensure_ascii=False)
            self.blueprints[blueprint.name] = blueprint
            return True
        except Exception as e:
            print(f"保存蓝图失败: {e}")
            return False
    
    def load_blueprint(self, name: str) -> Optional[TowerBlueprint]:
        """从文件加载蓝图"""
        if name in self.blueprints:
            return self.blueprints[name]
        
        try:
            filepath = os.path.join(self.save_dir, f"{name}.json")
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            blueprint = TowerBlueprint.from_dict(data)
            self.blueprints[name] = blueprint
            return blueprint
        except Exception as e:
            print(f"加载蓝图失败: {e}")
            return None
    
    def delete_blueprint(self, name: str) -> bool:
        """删除蓝图"""
        try:
            filepath = os.path.join(self.save_dir, f"{name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if name in self.blueprints:
                del self.blueprints[name]
            return True
        except Exception as e:
            print(f"删除蓝图失败: {e}")
            return False
    
    def list_blueprints(self) -> List[str]:
        """列出所有蓝图"""
        try:
            files = [f[:-5] for f in os.listdir(self.save_dir) if f.endswith('.json')]
            return sorted(files)
        except Exception as e:
            print(f"列出蓝图失败: {e}")
            return []
    
    def get_all_blueprints(self) -> Dict[str, TowerBlueprint]:
        """获取所有蓝图"""
        for name in self.list_blueprints():
            if name not in self.blueprints:
                self.load_blueprint(name)
        return self.blueprints.copy()


class BlueprintManager:
    """全局蓝图管理器(单例)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._library = BlueprintLibrary()
        return cls._instance
    
    @property
    def library(self) -> BlueprintLibrary:
        return self._library


# 便捷函数
def get_blueprint_manager() -> BlueprintManager:
    """获取蓝图管理器单例"""
    return BlueprintManager()