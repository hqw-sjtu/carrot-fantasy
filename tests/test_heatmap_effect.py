"""
测试 - 热力图特效系统
"""
import sys
sys.path.insert(0, 'src')
from heatmap_effect import EnemyHeatmap, TowerRangeIndicator, PathHeatmapOverlay


def test_heatmap_init():
    """测试热力图初始化"""
    hm = EnemyHeatmap(800, 600, cell_size=20)
    assert hm.cols == 40
    assert hm.rows == 30
    assert len(hm.heatmap) == 30
    print("✅ 热力图初始化测试通过")


def test_heatmap_update():
    """测试热力图更新"""
    hm = EnemyHeatmap(800, 600)
    
    # 模拟怪物
    class MockMonster:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    monsters = [MockMonster(100, 100), MockMonster(150, 120)]
    hm.update(0.016, monsters)  # 1帧
    
    assert hm.heatmap[5][5] > 0 or hm.heatmap[6][5] > 0
    print("✅ 热力图更新测试通过")


def test_tower_range_indicator():
    """测试防御塔范围指示器"""
    indicator = TowerRangeIndicator(400, 300, 100)
    assert indicator.x == 400
    assert indicator.y == 300
    assert indicator.attack_range == 100
    print("✅ 防御塔范围指示器测试通过")


def test_path_heatmap():
    """测试路径热力图"""
    path = [(0, 300), (200, 300), (400, 200), (800, 200)]
    phm = PathHeatmapOverlay(path, 800, 600)
    assert phm.path_points == path
    print("✅ 路径热力图测试通过")


if __name__ == '__main__':
    test_heatmap_init()
    test_heatmap_update()
    test_tower_range_indicator()
    test_path_heatmap()
    print("\n🎉 所有热力图测试通过!")