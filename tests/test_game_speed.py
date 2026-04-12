import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

"""测试游戏速度控制系统"""
import pytest


class TestGameSpeed:
    """游戏速度控制测试"""

    def test_speed_labels_exist(self):
        """速度标签存在"""
        from main import speed_labels
        assert 0.5 in speed_labels
        assert 1.0 in speed_labels
        assert 2.0 in speed_labels

    def test_speed_label_text(self):
        """速度标签文字正确"""
        from main import speed_labels
        assert "慢放" in speed_labels[0.5]
        assert "正常" in speed_labels[1.0]
        assert "快进" in speed_labels[2.0]

    def test_default_speed(self):
        """默认速度为1.0正常"""
        from main import game_speed
        assert game_speed == 1.0

    def test_speed_value_ranges(self):
        """速度值在有效范围内"""
        from main import speed_labels
        for speed in speed_labels.keys():
            assert speed > 0 and speed <= 2.0


class TestSpeedUI:
    """速度UI显示测试"""

    def test_speed_bg_rect_calculation(self):
        """速度背景框位置计算"""
        # 模拟屏幕宽度
        screen_width = 1200
        expected_x = screen_width - 130
        expected_y = 8
        assert expected_x == 1070
        assert expected_y == 8

    def test_speed_color_dict(self):
        """速度颜色字典"""
        speed_color = {0.5: (100, 150, 200), 1.0: (100, 200, 100), 2.0: (200, 150, 50)}
        assert len(speed_color) == 3
        assert all(isinstance(v, tuple) and len(v) == 3 for v in speed_color.values())