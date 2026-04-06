#!/usr/bin/env python3
"""保卫萝卜 - 游戏启动器"""

import subprocess
import sys
import os

def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║         🎮 保卫萝卜 v1.9 🎮           ║
    ╠═══════════════════════════════════════╣
    ║  [1] 开始游戏                          ║
    ║  [2] 游戏说明                          ║
    ║  [3] 按Enter退出                       ║
    ╚═══════════════════════════════════════╝
    """)
    
    choice = input("请选择: ").strip()
    
    if choice == "1":
        print("\n🎮 正在启动游戏...")
        os.chdir("src")
        subprocess.run([sys.executable, "main.py"])
    elif choice == "2":
        print("""
        
🎯 游戏说明：

【操作】
- 1-4: 选择塔类型
- 鼠标: 放置/选中塔
- U: 升级选中塔
- D: 出售选中塔
- 空格: 开始波次
- ESC: 暂停

【快捷键】
- I: 塔图鉴
- J: 怪物图鉴
- K: 每日签到
- T: 查看统计
- H: 切换血量显示

【难度】简单/普通/困难

【特色系统】
- 塔品质（史诗/优秀/普通）
- 随机事件（金币雨/双倍伤害/减速）
- 塔组合（相邻同类型+10%伤害）
- 成就系统
- 每日任务
        """)
        input("\n按Enter返回...")
        main()
    else:
        print("\n👋 再见!")
        return

if __name__ == "__main__":
    main()