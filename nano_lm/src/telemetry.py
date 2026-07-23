"""Background GPU/CPU sampler for live terminal charts during decode."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

from gpu_stats import GpuSnapshot, read_cpu_percents, read_gpu


@dataclass
class Telemetry:
    history: list[GpuSnapshot] = field(default_factory=list)
    cpu_cores: list[float] = field(default_factory=list)
    max_points: int = 48
    _stop: threading.Event = field(default_factory=threading.Event)
    _thread: threading.Thread | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def start(self, interval_s: float = 0.25) -> None:
        self.stop()
        self._stop = threading.Event()

        def loop() -> None:
            while not self._stop.wait(interval_s):
                snap = read_gpu()
                cores = read_cpu_percents()
                with self._lock:
                    self.history.append(snap)
                    if len(self.history) > self.max_points:
                        self.history = self.history[-self.max_points :]
                    self.cpu_cores = cores

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

    def snapshot(self) -> tuple[GpuSnapshot, list[GpuSnapshot], list[float]]:
        with self._lock:
            hist = list(self.history)
            cores = list(self.cpu_cores)
        latest = hist[-1] if hist else read_gpu()
        return latest, hist, cores
