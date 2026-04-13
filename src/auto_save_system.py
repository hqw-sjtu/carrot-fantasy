"""自动存档系统 - 智能存档管理与云同步提示"""
import json
import os
import time
from datetime import datetime

SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")
AUTO_SAVE_INTERVAL = 300  # 5分钟自动存档
MAX_SAVE_SLOTS = 5  # 最多保留5个存档槽

def ensure_save_dir():
    """确保存档目录存在"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def get_save_files():
    """获取所有存档文件（按修改时间排序）"""
    ensure_save_dir()
    files = []
    for f in os.listdir(SAVE_DIR):
        if f.endswith('.json'):
            path = os.path.join(SAVE_DIR, f)
            files.append({
                'name': f,
                'path': path,
                'mtime': os.path.getmtime(path),
                'size': os.path.getsize(path)
            })
    return sorted(files, key=lambda x: x['mtime'], reverse=True)

def auto_save(state, slot=None):
    """自动存档
    
    Args:
        state: 游戏状态对象
        slot: 存档槽位 (0-4), 为None时自动选择最早的槽
    
    Returns:
        str: 存档文件名
    """
    ensure_save_dir()
    
    # 确定存档槽
    if slot is None:
        files = get_save_files()
        if len(files) >= MAX_SAVE_SLOTS:
            # 使用最旧的存档槽
            slot = len(files) - 1
            oldest = files[-1]
            # 删除最旧的存档
            try:
                os.remove(oldest['path'])
            except:
                pass
        else:
            slot = len(files)
    
    # 生成存档数据
    timestamp = int(time.time())
    save_name = f"autosave_{slot}_{timestamp}.json"
    save_path = os.path.join(SAVE_DIR, save_name)
    
    data = {
        "version": "2.5.0",
        "timestamp": timestamp,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "slot": slot,
        "money": state.money,
        "lives": state.lives,
        "wave": state.wave,
        "level": state.level,
        "score": getattr(state, 'score', 0),
        "towers": [
            {
                "name": t.name, 
                "x": t.x, 
                "y": t.y, 
                "level": t.level,
                "quality": getattr(t, 'quality', '普通')
            }
            for t in state.towers
        ] if hasattr(state, 'towers') else []
    }
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return save_name

def load_save(save_path):
    """加载存档
    
    Args:
        save_path: 存档文件路径
    
    Returns:
        dict: 存档数据, 失败返回None
    """
    if not os.path.exists(save_path):
        return None
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载存档失败: {e}")
        return None

def get_save_info(save_path):
    """获取存档信息摘要"""
    data = load_save(save_path)
    if not data:
        return None
    return {
        "version": data.get("version", "unknown"),
        "datetime": data.get("datetime", "unknown"),
        "money": data.get("money", 0),
        "lives": data.get("lives", 0),
        "wave": data.get("wave", 0),
        "level": data.get("level", 1),
        "tower_count": len(data.get("towers", []))
    }

def cleanup_old_saves(keep=MAX_SAVE_SLOTS):
    """清理旧存档，保留最新的N个"""
    files = get_save_files()
    if len(files) <= keep:
        return 0
    
    removed = 0
    for f in files[keep:]:
        try:
            os.remove(f['path'])
            removed += 1
        except:
            pass
    return removed

class AutoSaveManager:
    """自动存档管理器"""
    
    def __init__(self, state):
        self.state = state
        self.last_save_time = time.time()
        self.save_notifications = []  # 存档提示队列
    
    def update(self, dt):
        """更新自动存档
        
        Args:
            dt: 距离上次调用的时间(秒)
        """
        current_time = time.time()
        elapsed = current_time - self.last_save_time
        
        if elapsed >= AUTO_SAVE_INTERVAL:
            self.do_auto_save()
            self.last_save_time = current_time
    
    def do_auto_save(self):
        """执行自动存档"""
        try:
            save_name = auto_save(self.state)
            self.save_notifications.append({
                "type": "success",
                "message": f"✅ 自动存档: {save_name[:20]}...",
                "time": time.time()
            })
            # 清理超过10秒的提示
            self.save_notifications = [
                n for n in self.save_notifications 
                if time.time() - n["time"] < 10
            ]
        except Exception as e:
            self.save_notifications.append({
                "type": "error",
                "message": f"❌ 存档失败: {str(e)[:30]}",
                "time": time.time()
            })
    
    def get_notification(self):
        """获取当前显示的提示"""
        if self.save_notifications:
            return self.save_notifications[0]
        return None
    
    def force_save(self):
        """强制立即存档"""
        self.last_save_time = 0  # 重置计时器
        self.do_auto_save()
        return len(self.save_notifications) > 0