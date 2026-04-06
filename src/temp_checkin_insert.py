        # 计算FPS
        fps_counter += 1
        fps_timer += dt
        if fps_timer >= 1.0:
            fps = int(fps_counter / fps_timer)
            fps_counter = 0
            fps_timer = 0

        # 处理签到事件
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    success, reward = try_checkin()
                    if success:
                        state.money += reward
                        print(f"✅ 签到成功! 连续{checkin_data['streak']}天, 奖励{reward}金币")
                    else:
                        print("⚠️ 今日已签到")

        # 绘制游戏画面
        if level_select_mode:
            draw_level_select()
        elif not difficulty_selected:
            draw_difficulty_screen()
        else:
            draw_game()
            
        # 绘制签到面板
        draw_checkin_panel(SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GOLD, YELLOW)

        # 暂停时显示详细信息