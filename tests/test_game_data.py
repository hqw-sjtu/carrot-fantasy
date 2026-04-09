#!/usr/bin/env python3
"""
游戏数据模块测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import GameData
from state_machine import GameStateMachine

def test_game_data_creation():
    """测试游戏数据创建"""
    game_data = GameData()
    assert game_data.money == 200
    assert game_data.lives == 10
    assert game_data.wave == 0
    assert game_data.level == 1
    assert game_data.towers == []
    assert game_data.monsters == []
    assert game_data.projectiles == []
    assert game_data.selected_tower is None
    assert game_data.game_over == False
    assert hasattr(game_data, 'wave_manager')
    assert game_data.wave_complete == False
    assert game_data.mouse_preview is None
    assert game_data.paused == False
    print("✓ GameData 创建测试通过")

def test_game_data_reset():
    """测试游戏数据重置"""
    game_data = GameData()
    game_data.money = 500
    game_data.lives = 5
    game_data.reset()
    
    assert game_data.money == 200
    assert game_data.lives == 10
    assert game_data.wave == 0
    assert game_data.level == 1
    print("✓ GameData 重置测试通过")

def test_game_state_machine():
    """测试游戏状态机"""
    state_machine = GameStateMachine()
    assert state_machine.current_state.name == 'READY'
    print("✓ GameStateMachine 测试通过")

if __name__ == "__main__":
    test_game_data_creation()
    test_game_data_reset()
    test_game_state_machine()
    print("🎉 所有测试通过!")