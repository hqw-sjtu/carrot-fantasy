"""测试连击链特效"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()

from particle_system import ComboChainEffect


class TestComboChainEffect:
    """连击链特效测试"""
    
    def test_combo_chain_init(self):
        """测试连击链初始化"""
        effect = ComboChainEffect(400, 300, 5)
        assert effect.combo_count == 5
        assert effect.x == 400
        assert effect.y == 300
        assert effect.max_life == 45
        assert effect.life == 45
        assert len(effect.sparks) > 0
        print("✅ test_combo_chain_init PASSED")
    
    def test_combo_chain_update(self):
        """测试连击链更新"""
        effect = ComboChainEffect(400, 300, 10)
        initial_life = effect.life
        result = effect.update(16)
        assert result == True
        assert effect.life < initial_life
        print("✅ test_combo_chain_update PASSED")
    
    def test_combo_chain_multiple_kills(self):
        """测试多次击杀连击"""
        for combo in [3, 5, 10, 15, 20]:
            effect = ComboChainEffect(400, 300, combo)
            assert effect.combo_count == combo
            # 连击数越多，火花越多
            assert len(effect.sparks) >= combo
        print("✅ test_combo_chain_multiple_kills PASSED")
    
    def test_combo_chain_lifecycle(self):
        """测试连击链生命周期"""
        effect = ComboChainEffect(400, 300, 5)
        # 模拟多帧更新
        for _ in range(100):
            effect.update(16)
        # 生命结束时应返回False
        assert effect.life <= 0 or not any(s['life'] > 0 for s in effect.sparks)
        print("✅ test_combo_chain_lifecycle PASSED")


def run_tests():
    suite = TestComboChainEffect()
    suite.test_combo_chain_init()
    suite.test_combo_chain_update()
    suite.test_combo_chain_multiple_kills()
    suite.test_combo_chain_lifecycle()
    print("\n🎉 All ComboChainEffect tests passed!")


if __name__ == "__main__":
    run_tests()