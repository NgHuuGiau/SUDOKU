"""
Performance profiling and optimization utilities for Sudoku.
Provides profiling, benchmarking, memory tracking, and optimization tools.
"""
import cProfile
import functools
import gc
import io
import json
import pstats
import statistics
import threading
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class ProfileResult:
    """Result of a profiling session."""
    function_name: str
    call_count: int
    total_time: float
    cumulative_time: float
    per_call_time: float
    timestamp: str
    metadata: dict = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    timestamp: str
    current_mb: float
    peak_mb: float
    growth_mb: float
    object_count: int
    gc_counts: tuple[int, int, int]


class Profiler:
    """Advanced profiler for function performance analysis."""

    def __init__(self):
        self._profiles: Dict[str, List[ProfileResult]] = {}
        self._lock = threading.Lock()
        self._profiling_active = False
        self._profiler: Optional[cProfile.Profile] = None

    @contextmanager
    def profile(self, name: str = "default", metadata: Optional[dict] = None):
        """Context manager for profiling a code block."""
        profiler = cProfile.Profile()
        profiler.enable()
        start_time = time.perf_counter()

        try:
            yield
        finally:
            profiler.disable()
            elapsed = time.perf_counter() - start_time

            # Get stats
            stats = pstats.Stats(profiler).sort_stats('cumulative')
            stream = io.StringIO()
            stats.print_stats(20)
            _ = stream.getvalue()

            # Parse stats
            total_calls = stats.total_calls
            total_time = elapsed

            result = ProfileResult(
                function_name=name,
                call_count=total_calls,
                total_time=total_time,
                cumulative_time=total_time,
                per_call_time=total_time / max(total_calls, 1),
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )

            with self._lock:
                if name not in self._profiles:
                    self._profiles[name] = []
                self._profiles[name].append(result)

    def profile_function(self, name: Optional[str] = None, metadata: Optional[dict] = None):
        """Decorator for profiling a function."""
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            profile_name = name or f"{func.__module__}.{func.__qualname__}"

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                with self.profile(profile_name, metadata):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    def start_profiling(self):
        """Start global profiling."""
        if self._profiling_active:
            return
        self._profiler = cProfile.Profile()
        self._profiler.enable()
        self._profiling_active = True

    def stop_profiling(self, name: str = "global") -> ProfileResult:
        """Stop global profiling and return results."""
        if not self._profiling_active or not self._profiler:
            return ProfileResult(
                function_name=name,
                call_count=0,
                total_time=0,
                cumulative_time=0,
                per_call_time=0,
                timestamp=datetime.now().isoformat()
            )

        self._profiler.disable()
        self._profiling_active = False

        stats = pstats.Stats(self._profiler).sort_stats('cumulative')
        total_calls = stats.total_calls
        total_time = sum(stats.stats[func][3] for func in stats.stats)

        result = ProfileResult(
            function_name=name,
            call_count=total_calls,
            total_time=total_time,
            cumulative_time=total_time,
            per_call_time=total_time / max(total_calls, 1),
            timestamp=datetime.now().isoformat()
        )

        with self._lock:
            if name not in self._profiles:
                self._profiles[name] = []
            self._profiles[name].append(result)

        return result

    def get_stats(self, name: str) -> Dict[str, Any]:
        """Get profiling statistics for a function."""
        with self._lock:
            profiles = self._profiles.get(name, [])

        if not profiles:
            return {"count": 0}

        times = [p.total_time for p in profiles]
        return {
            "count": len(profiles),
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times),
            "median_time": statistics.median(times),
            "stdev_time": statistics.stdev(times) if len(times) > 1 else 0,
        }

    def export_profiles(self, filepath: str):
        """Export all profiles to JSON."""
        with self._lock:
            data = {
                name: [asdict(p) for p in profiles]
                for name, profiles in self._profiles.items()
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class MemoryTracker:
    """Advanced memory tracking and leak detection."""

    def __init__(self):
        self._snapshots: List[MemorySnapshot] = []
        self._lock = threading.Lock()
        self._baseline: Optional[MemorySnapshot] = None
        self._tracking = False
        self._track_thread: Optional[threading.Thread] = None
        self._interval = 1.0
        self._max_snapshots = 10000

    def set_baseline(self):
        """Set current memory as baseline."""
        snapshot = self._take_snapshot()
        with self._lock:
            self._baseline = snapshot
            self._snapshots = [snapshot]

    def _take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        # Force garbage collection for accurate reading
        gc.collect()

        current, peak = tracemalloc.get_traffic()
        current_mb = current / 1024 / 1024
        peak_mb = peak / 1024 / 1024

        # Get object count
        obj_count = len(gc.get_objects())

        # Get GC counts
        gc_counts = gc.get_count()

        growth = 0.0
        if self._baseline:
            growth = current_mb - self._baseline.current_mb

        return MemorySnapshot(
            timestamp=datetime.now().isoformat(),
            current_mb=current_mb,
            peak_mb=peak_mb,
            growth_mb=growth,
            object_count=obj_count,
            gc_counts=gc_counts
        )

    def start_tracking(self, interval: float = 1.0):
        """Start automatic memory tracking."""
        if self._tracking:
            return

        if not tracemalloc.is_tracing():
            tracemalloc.start()

        self._interval = interval
        self._tracking = True
        self.set_baseline()

        self._track_thread = threading.Thread(target=self._track_loop, daemon=True)
        self._track_thread.start()

    def stop_tracking(self):
        """Stop automatic memory tracking."""
        self._tracking = False
        if self._track_thread:
            self._track_thread.join(timeout=2.0)
            self._track_thread = None

    def _track_loop(self):
        while self._tracking:
            time.sleep(self._interval)
            if self._tracking:
                snapshot = self._take_snapshot()
                with self._lock:
                    self._snapshots.append(snapshot)
                    if len(self._snapshots) > self._max_snapshots:
                        self._snapshots = self._snapshots[-self._max_snapshots:]

    def take_snapshot(self) -> MemorySnapshot:
        """Manually take a memory snapshot."""
        snapshot = self._take_snapshot()
        with self._lock:
            self._snapshots.append(snapshot)
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots = self._snapshots[-self._max_snapshots:]
        return snapshot

    def get_snapshots(self, limit: int = 100) -> List[MemorySnapshot]:
        """Get recent memory snapshots."""
        with self._lock:
            return self._snapshots[-limit:]

    def detect_leaks(self, threshold_mb: float = 10.0, window: int = 100) -> List[Dict[str, Any]]:
        """Detect potential memory leaks."""
        with self._lock:
            snapshots = self._snapshots

        if len(snapshots) < window + 1:
            return []

        leaks = []
        for i in range(window, len(snapshots)):
            window_snapshots = snapshots[i-window:i]
            current = snapshots[i]

            avg_growth = sum(s.growth_mb for s in window_snapshots) / len(window_snapshots)
            if current.growth_mb - avg_growth > threshold_mb:
                leaks.append({
                    "timestamp": current.timestamp,
                    "growth_mb": current.growth_mb,
                    "threshold_exceeded": current.growth_mb - avg_growth,
                    "object_count": current.object_count,
                    "suspected_leak": True
                })

        return leaks

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        with self._lock:
            snapshots = self._snapshots

        if not snapshots:
            return {}

        latest = snapshots[-1]
        growths = [s.growth_mb for s in snapshots]

        return {
            "current_mb": latest.current_mb,
            "peak_mb": latest.peak_mb,
            "total_growth_mb": latest.growth_mb,
            "object_count": latest.object_count,
            "snapshot_count": len(snapshots),
            "avg_growth_mb": statistics.mean(growths) if growths else 0,
            "max_growth_mb": max(growths) if growths else 0,
            "gc_counts": latest.gc_counts,
        }

    def export_snapshots(self, filepath: str):
        """Export memory snapshots to JSON."""
        with self._lock:
            data = [asdict(s) for s in self._snapshots]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self):
        """Clear all snapshots."""
        with self._lock:
            self._snapshots = []
            self._baseline = None


class PerformanceOptimizer:
    """Performance optimization utilities."""

    @staticmethod
    def optimize_imports():
        """Pre-import commonly used modules."""

    @staticmethod
    def enable_fast_math():
        """Enable fast math operations."""
        import math
        # Enable fast math optimizations where available
        if hasattr(math, 'fma'):
            pass  # Use fused multiply-add

    @staticmethod
    def optimize_gc():
        """Optimize garbage collection for performance."""
        # Disable automatic collection, use manual
        gc.disable()
        # Set thresholds for generational GC
        gc.set_threshold(1000, 20, 20)

    @staticmethod
    def manual_gc():
        """Manual garbage collection with timing."""
        start = time.perf_counter()
        collected = gc.collect()
        elapsed = (time.perf_counter() - start) * 1000
        return {"collected": collected, "time_ms": elapsed}

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get detailed memory usage."""
        import psutil
        process = psutil.Process()
        mem = process.memory_info()

        return {
            "rss_mb": mem.rss / 1024 / 1024,
            "vms_mb": mem.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }

    @staticmethod
    def profile_code(code: str, globals_dict: Optional[dict] = None) -> Dict[str, Any]:
        """Profile a code snippet."""
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            exec(code, globals_dict or {})
        finally:
            profiler.disable()

        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stream = io.StringIO()
        stats.print_stats(20)

        return {
            "total_calls": profiler.total_calls,
            "prim_calls": profiler.prim_calls,
            "total_time": sum(s[3] for s in profiler.stats.values()),
            "stats_output": stream.getvalue(),
        }


# Global instances
profiler = Profiler()
memory_tracker = MemoryTracker()
optimizer = PerformanceOptimizer()


# Decorators
def profile(name: Optional[str] = None, metadata: Optional[dict] = None):
    """Profile a function."""
    return profiler.profile_function(name, metadata)


def track_memory():
    """Decorator to track memory before/after function."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            gc.collect()
            before = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
            result = func(*args, **kwargs)
            gc.collect()
            after = tracemalloc.get_traced_memory()[0] if tracemalloc.is_tracing() else 0
            diff = (after - before) / 1024 / 1024
            if diff > 1:  # Log if > 1MB
                import logging
                logging.warning(f"Memory growth in {func.__name__}: {diff:.2f}MB")
            return result
        return wrapper
    return decorator


def time_it(name: Optional[str] = None):
    """Decorator to time function execution."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            if elapsed > 100:  # Log if > 100ms
                import logging
                logging.warning(f"Slow function {func.__name__}: {elapsed:.1f}ms")
            return result
        return wrapper
    return decorator


@contextmanager
def profile_block(name: str):
    """Context manager for profiling a code block."""
    profiler.start_profiling()
    try:
        yield
    finally:
        result = profiler.stop_profiling(name)
        if result.total_time > 0.1:
            import logging
            logging.warning(f"Block {name} took {result.total_time:.3f}s")


def benchmark(func: Callable, iterations: int = 100, warmup: int = 10) -> Dict[str, Any]:
    """Benchmark a function."""
    # Warmup
    for _ in range(warmup):
        func()

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append((time.perf_counter() - start) * 1000)

    return {
        "iterations": iterations,
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "total_ms": sum(times),
        "ops_per_sec": 1000 / statistics.mean(times) if times else 0,
    }


# Global instances
profiler_instance = Profiler()
memory_tracker_instance = MemoryTracker()


# Export
__all__ = [
    "Profiler",
    "MemoryTracker",
    "PerformanceOptimizer",
    "ProfileResult",
    "MemorySnapshot",
    "profiler",
    "memory_tracker",
    "optimizer",
    "profile",
    "track_memory",
    "time_it",
    "profile_block",
    "benchmark",
    "profiler_instance",
    "memory_tracker_instance",
    "optimizer",
]
