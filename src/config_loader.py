"""
配置加载器 - 从 JSON 加载游戏配置
"""
import json
import os

_config = None

def load_config(config_path=None):
    """加载配置文件"""
    global _config
    if _config is not None:
        return _config
    
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        _config = json.load(f)
    return _config

def get_config():
    """获取配置（必须先调用 load_config）"""
    if _config is None:
        load_config()
    return _config

def get_tower_config(name):
    """获取防御塔配置"""
    cfg = get_config()
    return cfg["towers"].get(name)

def get_monster_config(name):
    """获取怪物配置"""
    cfg = get_config()
    return cfg["monsters"].get(name)

def get_wave_config(index):
    """获取波次配置"""
    cfg = get_config()
    if 0 <= index < len(cfg["waves"]):
        return cfg["waves"][index]
    return None

def get_wave_count():
    """获取波次总数"""
    cfg = get_config()
    return len(cfg["waves"])