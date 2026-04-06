#!/usr/bin/env python3

with open('/home/qw/.openclaw/workspace/projects/carrot-fantasy/src/main.py', 'r') as f:
    content = f.read()

# 查找插入位置
lines = content.split('\n')
insert_pos = -1

for i, line in enumerate(lines):
    if '# 计算FPS' in line:
        insert_pos = i
        break

if insert_pos != -1:
    # 插入签到处理代码
    new_lines = lines[:insert_pos+1]
    new_lines.extend([
        '        # 处理签到事件',
        '        for event in pygame.event.get():',
        '            if event.type == pygame.KEYDOWN:',
        '                if event.key == pygame.K_k:',
        '                    success, reward = try_checkin()',
        '                    if success:',
        '                        state.money += reward',
        '                        print(f"✅ 签到成功! 连续{checkin_data[\'streak\']}天, 奖励{reward}金币")',
        '                    else:',
        '                        print("⚠️ 今日已签到")',
        '',
        '        # 绘制游戏画面',
        '        if level_select_mode:',
        '            draw_level_select()',
        '        elif not difficulty_selected:',
        '            draw_difficulty_screen()',
        '        else:',
        '            draw_game()',
        '',
        '        # 绘制签到面板',
        '        draw_checkin_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GOLD, YELLOW)',
    ])
    new_lines.extend(lines[insert_pos+1:])
    
    with open('/home/qw/.openclaw/workspace/projects/carrot-fantasy/src/main.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("成功修改main.py文件")
else:
    print("未能找到插入位置")