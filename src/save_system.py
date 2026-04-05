"""存档系统"""
import json
import os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "..", "save.json")

def save_game(state):
    """保存游戏状态"""
    data = {
        "money": state.money,
        "lives": state.lives,
        "wave": state.wave,
        "level": state.level,
        "towers": [
            {"name": t.name, "x": t.x, "y": t.y, "level": t.level}
            for t in state.towers
        ]
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)
    return True

def load_game():
    """加载游戏状态"""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def has_save():
    """检查是否有存档"""
    return os.path.exists(SAVE_FILE)