"""
timer.py — Chess clock logic as a pure Python class.
No terminal/tty dependencies. Designed to be used by Flask.
"""

import time


class ChessClock:
    def __init__(self, seconds_p1=600, seconds_p2=600):
        self.times = {1: float(seconds_p1), 2: float(seconds_p2)}
        self.turn = 1                  # whose turn it is (1 or 2)
        self.running = False
        self._last_tick = None         # wall-clock time of last update

    def start(self):
        """Start or resume the clock."""
        if not self.running:
            self.running = True
            self._last_tick = time.time()

    def stop(self):
        """Pause the clock."""
        if self.running:
            self._tick()
            self.running = False
            self._last_tick = None

    def switch_turn(self):
        """Switch which player's clock is running (like pressing spacebar)."""
        if self.running:
            self._tick()
        self.turn = 2 if self.turn == 1 else 1
        if self.running:
            self._last_tick = time.time()

    def reset(self, seconds_p1=600, seconds_p2=600):
        """Reset both clocks."""
        self.stop()
        self.times = {1: float(seconds_p1), 2: float(seconds_p2)}
        self.turn = 1

    def _tick(self):
        if not self.running or self._last_tick is None:
            return
        now = time.time()
        elapsed = now - self._last_tick
        self._last_tick = now
        self.times[self.turn] = max(0.0, self.times[self.turn] - elapsed)

    def get_state(self):
        """Return current timer state as a dict (safe to jsonify)."""
        self._tick()

        timeout_player = None
        if self.times[1] <= 0:
            timeout_player = 1
            self.running = False
        elif self.times[2] <= 0:
            timeout_player = 2
            self.running = False

        return {
            "p1": self._fmt(self.times[1]),
            "p2": self._fmt(self.times[2]),
            "p1_seconds": round(self.times[1], 2),
            "p2_seconds": round(self.times[2], 2),
            "turn": self.turn,
            "running": self.running,
            "timeout": timeout_player,
        }

    @staticmethod
    def _fmt(sec):
        sec = max(0, int(sec))
        return f"{sec // 60:02d}:{sec % 60:02d}"