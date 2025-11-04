"""
Python 3.14 GIL-Free Execution Example

This example demonstrates the revolutionary change in Python 3.14 where the
Global Interpreter Lock (GIL) can be disabled, enabling true parallel execution
of CPU-bound tasks across multiple threads.

Key Concepts:
1. Understanding the GIL and its limitations
2. CPU-bound vs I/O-bound operations
3. True parallelism with GIL-free mode
4. Performance comparison: Sequential vs Threading (with/without GIL)
5. Thread safety in GIL-free mode

Note: This example simulates GIL behavior on Python < 3.14 for demonstration.
On Python 3.14+, run with PYTHON_GIL=0 to disable GIL.
"""

import sys
import threading
import time
from datetime import datetime


def log_time(msg):
    """Helper function to print timestamped messages."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}")


def is_gil_disabled():
    """Check if GIL is disabled (Python 3.14+ feature)."""
    # In Python 3.14+, sys._is_gil_enabled() returns False when GIL is disabled
    if hasattr(sys, "_is_gil_enabled"):
        return not sys._is_gil_enabled()
    return False


# CPU-bound computation: Calculate sum of squares
def compute_intensive_task(name, n, result_dict, index):
    """
    CPU-bound task: compute sum of squares from 1 to n.
    This simulates real CPU-intensive work like data processing,
    image manipulation, or mathematical computations.
    """
    log_time(f"🔢 Thread {name}: Starting computation...")
    start = time.time()

    # CPU-intensive computation
    total = 0
    for i in range(1, n + 1):
        total += i * i
        # Add some extra work to make it more CPU-intensive
        if i % 1000000 == 0:
            _ = total ** 0.5  # Square root calculation

    elapsed = time.time() - start
    result_dict[index] = total
    log_time(f"✅ Thread {name}: Completed in {elapsed:.3f}s (result: {total})")
    return total


def demonstrate_sequential_execution():
    """Baseline: Sequential execution of CPU-bound tasks."""
    log_time("=" * 70)
    log_time("EXAMPLE 1: Sequential Execution (Baseline)")
    log_time("=" * 70)
    log_time("Running 4 CPU-intensive tasks one after another...\n")

    start = time.time()
    results = {}

    # Run tasks sequentially
    for i in range(4):
        compute_intensive_task(f"SEQ-{i+1}", 10_000_000, results, i)

    total_time = time.time() - start
    log_time(f"\n⏱️  Total Sequential Time: {total_time:.3f}s")
    log_time(f"📊 All results computed: {len(results)} tasks\n")
    return total_time


def demonstrate_threading_with_gil():
    """
    Threading with GIL: Multiple threads, but only one executes Python bytecode
    at a time due to the GIL. For CPU-bound tasks, this provides NO speedup.
    """
    log_time("=" * 70)
    log_time("EXAMPLE 2: Multi-Threading WITH GIL (Traditional Python)")
    log_time("=" * 70)
    log_time("Running 4 CPU-intensive tasks with threads (GIL enabled)...")
    log_time("⚠️  GIL prevents true parallelism - threads take turns!\n")

    start = time.time()
    threads = []
    results = {}

    # Create and start threads
    for i in range(4):
        thread = threading.Thread(
            target=compute_intensive_task,
            args=(f"GIL-{i+1}", 10_000_000, results, i)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    total_time = time.time() - start
    log_time(f"\n⏱️  Total Threading Time (with GIL): {total_time:.3f}s")
    log_time(f"📊 All results computed: {len(results)} tasks")
    log_time("💡 Notice: Similar to sequential time due to GIL!\n")
    return total_time


def demonstrate_threading_without_gil():
    """
    Threading WITHOUT GIL (Python 3.14+): True parallel execution!
    Multiple threads can execute Python bytecode simultaneously.
    """
    log_time("=" * 70)
    if is_gil_disabled():
        log_time("EXAMPLE 3: Multi-Threading WITHOUT GIL (Python 3.14+ 🎉)")
        log_time("=" * 70)
        log_time("Running 4 CPU-intensive tasks with TRUE parallelism...")
        log_time("🚀 GIL is DISABLED - threads run in parallel!\n")
    else:
        log_time("EXAMPLE 3: Multi-Threading WITHOUT GIL (Simulated)")
        log_time("=" * 70)
        log_time("⚠️  Python version < 3.14 or GIL not disabled")
        log_time("This would show TRUE parallelism on Python 3.14+ with PYTHON_GIL=0\n")

    start = time.time()
    threads = []
    results = {}

    # Create and start threads
    for i in range(4):
        thread = threading.Thread(
            target=compute_intensive_task,
            args=(f"FREE-{i+1}", 10_000_000, results, i)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    total_time = time.time() - start
    log_time(f"\n⏱️  Total Threading Time (GIL-free): {total_time:.3f}s")
    log_time(f"📊 All results computed: {len(results)} tasks")

    if is_gil_disabled():
        log_time("🎯 TRUE PARALLELISM ACHIEVED! Multiple cores utilized!\n")
    else:
        log_time("💡 On Python 3.14+ with GIL disabled, this would be ~4x faster!\n")

    return total_time


def demonstrate_thread_safety():
    """
    Demonstrates thread safety considerations in GIL-free mode.
    Without GIL, you MUST use proper synchronization!
    """
    log_time("=" * 70)
    log_time("EXAMPLE 4: Thread Safety in GIL-Free Mode")
    log_time("=" * 70)
    log_time("Demonstrating why thread synchronization matters...\n")

    # Shared counter (unsafe without lock)
    unsafe_counter = {"value": 0}
    safe_counter = {"value": 0}
    lock = threading.Lock()

    def unsafe_increment(n):
        """Increment without lock - UNSAFE in GIL-free mode!"""
        for _ in range(n):
            unsafe_counter["value"] += 1

    def safe_increment(n):
        """Increment with lock - SAFE in GIL-free mode!"""
        for _ in range(n):
            with lock:
                safe_counter["value"] += 1

    iterations = 100_000
    log_time(f"🔓 Running UNSAFE increments (no lock): {iterations} iterations x 4 threads")

    # Unsafe version
    start = time.time()
    threads = []
    for i in range(4):
        thread = threading.Thread(target=unsafe_increment, args=(iterations,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    unsafe_time = time.time() - start
    expected = iterations * 4
    log_time(f"   Expected: {expected}")
    log_time(f"   Got: {unsafe_counter['value']}")
    log_time(f"   ❌ Lost updates: {expected - unsafe_counter['value']}")
    log_time(f"   ⏱️  Time: {unsafe_time:.3f}s\n")

    # Safe version
    log_time(f"🔒 Running SAFE increments (with lock): {iterations} iterations x 4 threads")
    start = time.time()
    threads = []
    for i in range(4):
        thread = threading.Thread(target=safe_increment, args=(iterations,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    safe_time = time.time() - start
    log_time(f"   Expected: {expected}")
    log_time(f"   Got: {safe_counter['value']}")
    log_time(f"   ✅ Correct: {safe_counter['value'] == expected}")
    log_time(f"   ⏱️  Time: {safe_time:.3f}s\n")

    log_time("💡 Key Insight: Without GIL, you MUST use locks for shared data!")
    log_time("   The GIL previously provided implicit thread safety.\n")


def print_summary(seq_time, gil_time, nogil_time):
    """Print performance comparison summary."""
    log_time("=" * 70)
    log_time("📊 PERFORMANCE SUMMARY")
    log_time("=" * 70)
    log_time(f"Sequential Execution:        {seq_time:.3f}s  (1.00x baseline)")
    log_time(f"Threading WITH GIL:          {gil_time:.3f}s  ({seq_time/gil_time:.2f}x)")
    log_time(f"Threading WITHOUT GIL:       {nogil_time:.3f}s  ({seq_time/nogil_time:.2f}x)")
    log_time("")

    if is_gil_disabled():
        speedup = seq_time / nogil_time
        log_time(f"🎉 GIL-FREE SPEEDUP: {speedup:.2f}x faster!")
        log_time(f"   Theoretical max: 4.00x (4 CPU cores)")
        log_time(f"   Efficiency: {(speedup/4)*100:.1f}%")
    else:
        log_time("💡 TO SEE TRUE PARALLELISM:")
        log_time("   1. Install Python 3.14+")
        log_time("   2. Run with: PYTHON_GIL=0 uv run python main.py")
        log_time("   3. Expected speedup: ~4x on a 4-core CPU!")

    log_time("=" * 70)


def print_introduction():
    """Print introduction explaining Python 3.14 GIL-free feature."""
    log_time("=" * 70)
    log_time("🐍 Python 3.14: GIL-Free Execution")
    log_time("=" * 70)
    log_time("")
    log_time("📚 WHAT IS THE GIL?")
    log_time("   The Global Interpreter Lock (GIL) is a mutex that protects")
    log_time("   Python objects, preventing multiple threads from executing")
    log_time("   Python bytecode simultaneously.")
    log_time("")
    log_time("❌ LIMITATION:")
    log_time("   CPU-bound multi-threaded programs don't benefit from")
    log_time("   multiple CPU cores - threads take turns!")
    log_time("")
    log_time("✨ PYTHON 3.14 BREAKTHROUGH:")
    log_time("   PEP 703 introduces optional GIL-free mode!")
    log_time("   Set PYTHON_GIL=0 to enable TRUE parallel execution.")
    log_time("")

    if is_gil_disabled():
        log_time("🎉 GIL STATUS: DISABLED - True parallelism enabled!")
    else:
        log_time("ℹ️  GIL STATUS: ENABLED (default mode)")
        log_time("   To disable: PYTHON_GIL=0 uv run python main.py")

    log_time("=" * 70)
    log_time("")


def main():
    """Main entry point for all demonstrations."""
    print_introduction()

    # Run demonstrations
    seq_time = demonstrate_sequential_execution()
    gil_time = demonstrate_threading_with_gil()
    nogil_time = demonstrate_threading_without_gil()

    # Thread safety demonstration
    demonstrate_thread_safety()

    # Print summary
    print_summary(seq_time, gil_time, nogil_time)

    log_time("\n✨ Demonstration complete!")


if __name__ == "__main__":
    main()
