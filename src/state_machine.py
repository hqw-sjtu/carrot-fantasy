"""
游戏状态机 - 管理游戏流程状态
"""
from enum import Enum, auto
from typing import Optional, Callable


class GameState(Enum):
    """游戏状态"""
    READY = auto()          # 准备开始（按空格开始第一波）
    PLAYING = auto()        # 游戏中
    PAUSED = auto()         # 暂停
    WAVE_COMPLETE = auto()  # 波次完成（显示波次完成信息）
    GAME_OVER = auto()      # 游戏结束


class GameStateMachine:
    """游戏状态机 - 管理游戏流程状态转换"""

    def __init__(self):
        self.current_state = GameState.READY
        self.state_listeners: dict[GameState, list[Callable]] = {
            state: [] for state in GameState
        }
        self.wave_complete_timer: float = 0.0  # 波次完成显示计时器

    def set_state(self, new_state: GameState):
        """切换状态"""
        if self.current_state == new_state:
            return

        old_state = self.current_state
        self.current_state = new_state

        # 触发状态切换回调
        for listener in self.state_listeners.get(new_state, []):
            listener(old_state, new_state)

    def update(self, dt: float, game_state) -> None:
        """
        根据当前状态更新状态机

        Args:
            dt: 时间增量（秒）
            game_state: 游戏状态对象（包含 lives, wave, monsters 等属性）
        """
        # 任意状态 → GAME_OVER: 生命值≤0
        if game_state.lives <= 0:
            self.set_state(GameState.GAME_OVER)
            return

        # WAVE_COMPLETE 状态处理：计时后自动进入下一波
        if self.current_state == GameState.WAVE_COMPLETE:
            self.wave_complete_timer += dt
            # 2秒后自动开始下一波（或等待玩家按空格）
            # 实际开始由 can_start_wave() 控制

    def can_start_wave(self) -> bool:
        """
        检查是否可以开始波次

        Returns:
            bool: 是否可以开始新波次
        """
        # READY 状态可以开始第一波
        if self.current_state == GameState.READY:
            return True
        # WAVE_COMPLETE 状态可以开始下一波
        if self.current_state == GameState.WAVE_COMPLETE:
            return True
        return False

    def start_wave(self) -> bool:
        """
        开始波次（从 READY 或 WAVE_COMPLETE 转换到 PLAYING）

        Returns:
            bool: 是否成功开始波次
        """
        if self.can_start_wave():
            self.set_state(GameState.PLAYING)
            self.wave_complete_timer = 0.0
            return True
        return False

    def pause(self) -> bool:
        """
        暂停游戏（PLAYING → PAUSED）

        Returns:
            bool: 是否成功暂停
        """
        if self.current_state == GameState.PLAYING:
            self.set_state(GameState.PAUSED)
            return True
        return False

    def resume(self) -> bool:
        """
        继续游戏（PAUSED → PLAYING）

        Returns:
            bool: 是否成功继续
        """
        if self.current_state == GameState.PAUSED:
            self.set_state(GameState.PLAYING)
            return True
        return False

    def toggle_pause(self) -> bool:
        """
        切换暂停状态（PLAYING ↔ PAUSED）

        Returns:
            bool: 是否成功切换
        """
        if self.current_state == GameState.PLAYING:
            return self.pause()
        elif self.current_state == GameState.PAUSED:
            return self.resume()
        return False

    def complete_wave(self) -> bool:
        """
        波次完成（PLAYING → WAVE_COMPLETE）

        Returns:
            bool: 是否成功完成波次
        """
        if self.current_state == GameState.PLAYING:
            self.set_state(GameState.WAVE_COMPLETE)
            self.wave_complete_timer = 0.0
            return True
        return False

    def game_over(self) -> None:
        """强制设置游戏结束状态"""
        self.set_state(GameState.GAME_OVER)

    def get_state(self) -> str:
        """
        获取当前状态字符串

        Returns:
            str: 当前状态名称
        """
        return self.current_state.name

    def is_playing(self) -> bool:
        """是否在游戏中"""
        return self.current_state == GameState.PLAYING

    def is_paused(self) -> bool:
        """是否暂停"""
        return self.current_state == GameState.PAUSED

    def is_game_over(self) -> bool:
        """是否游戏结束"""
        return self.current_state == GameState.GAME_OVER

    def is_ready(self) -> bool:
        """是否准备开始"""
        return self.current_state == GameState.READY

    def is_wave_complete(self) -> bool:
        """是否波次完成"""
        return self.current_state == GameState.WAVE_COMPLETE

    def on_state_change(self, state: GameState, callback: Callable):
        """注册状态切换回调"""
        self.state_listeners[state].append(callback)

    def reset(self):
        """重置到准备开始状态"""
        self.current_state = GameState.READY
        self.wave_complete_timer = 0.0

    def __repr__(self):
        return f"GameStateMachine({self.current_state.name})"