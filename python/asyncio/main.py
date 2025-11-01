"""
Asyncio Example: Demonstrating Concurrent Asynchronous Programming

This example showcases key asyncio concepts:
1. Basic async/await syntax
2. Concurrent task execution with asyncio.gather()
3. Task creation and management
4. Async context managers
5. Performance benefits of concurrency
"""

import asyncio
import sys
import time
from datetime import datetime

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def log_time(msg):
    """Helper function to print timestamped messages."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}")


# Example 1: Basic async function
async def fetch_data(name, delay):
    """Simulates fetching data from an API with a delay."""
    log_time(f"📥 Starting to fetch {name}...")
    await asyncio.sleep(delay)  # Simulates I/O operation
    log_time(f"✅ Finished fetching {name}")
    return f"Data from {name}"


# Example 2: Async function with error handling
async def fetch_with_error_handling(name, delay, should_fail=False):
    """Demonstrates error handling in async functions."""
    try:
        log_time(f"🔄 Starting {name}...")
        await asyncio.sleep(delay)
        if should_fail:
            raise ValueError(f"Simulated error in {name}")
        log_time(f"✅ Completed {name}")
        return f"Success: {name}"
    except ValueError as e:
        log_time(f"❌ Error in {name}: {e}")
        return f"Failed: {name}"


# Example 3: Async context manager
class AsyncResourceManager:
    """Demonstrates async context manager usage."""

    def __init__(self, name):
        self.name = name

    async def __aenter__(self):
        log_time(f"🔓 Opening resource: {self.name}")
        await asyncio.sleep(0.1)  # Simulates resource initialization
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        log_time(f"🔒 Closing resource: {self.name}")
        await asyncio.sleep(0.1)  # Simulates resource cleanup

    async def use(self):
        log_time(f"⚙️  Using resource: {self.name}")
        await asyncio.sleep(0.2)


# Example 4: Running tasks concurrently
async def demonstrate_concurrent_execution():
    """Shows the power of concurrent execution."""
    log_time("=" * 60)
    log_time("EXAMPLE 1: Concurrent vs Sequential Execution")
    log_time("=" * 60)

    # Sequential execution (slow)
    log_time("\n🐌 Sequential Execution:")
    start = time.time()
    result1 = await fetch_data("API-1", 1.0)
    result2 = await fetch_data("API-2", 1.0)
    result3 = await fetch_data("API-3", 1.0)
    sequential_time = time.time() - start
    log_time(f"⏱️  Sequential time: {sequential_time:.2f}s\n")

    # Concurrent execution (fast)
    log_time("🚀 Concurrent Execution (using asyncio.gather):")
    start = time.time()
    results = await asyncio.gather(
        fetch_data("API-1", 1.0),
        fetch_data("API-2", 1.0),
        fetch_data("API-3", 1.0),
    )
    concurrent_time = time.time() - start
    log_time(f"⏱️  Concurrent time: {concurrent_time:.2f}s")
    log_time(f"⚡ Speedup: {sequential_time / concurrent_time:.2f}x faster!\n")


# Example 5: Task management
async def demonstrate_task_management():
    """Shows how to create and manage tasks."""
    log_time("=" * 60)
    log_time("EXAMPLE 2: Task Creation and Management")
    log_time("=" * 60)

    # Create tasks
    task1 = asyncio.create_task(fetch_data("Task-1", 0.5))
    task2 = asyncio.create_task(fetch_data("Task-2", 0.3))
    task3 = asyncio.create_task(fetch_data("Task-3", 0.7))

    log_time(f"📋 Created 3 tasks")
    log_time(f"   Task-1 status: {task1.done()}")
    log_time(f"   Task-2 status: {task2.done()}")
    log_time(f"   Task-3 status: {task3.done()}\n")

    # Wait for all tasks
    await asyncio.gather(task1, task2, task3)

    log_time(f"\n📋 All tasks completed!")
    log_time(f"   Task-1 result: {task1.result()}")
    log_time(f"   Task-2 result: {task2.result()}")
    log_time(f"   Task-3 result: {task3.result()}\n")


# Example 6: Error handling with gather
async def demonstrate_error_handling():
    """Shows error handling in concurrent operations."""
    log_time("=" * 60)
    log_time("EXAMPLE 3: Error Handling in Async Code")
    log_time("=" * 60)

    # Using return_exceptions=True to handle errors gracefully
    results = await asyncio.gather(
        fetch_with_error_handling("Operation-1", 0.3, should_fail=False),
        fetch_with_error_handling("Operation-2", 0.5, should_fail=True),
        fetch_with_error_handling("Operation-3", 0.2, should_fail=False),
        return_exceptions=True,
    )

    log_time(f"\n📊 Results:")
    for i, result in enumerate(results, 1):
        log_time(f"   Operation-{i}: {result}\n")


# Example 7: Async context manager
async def demonstrate_async_context_manager():
    """Shows usage of async context managers."""
    log_time("=" * 60)
    log_time("EXAMPLE 4: Async Context Manager")
    log_time("=" * 60)

    async with AsyncResourceManager("Database Connection") as resource:
        await resource.use()
    log_time("")


# Main function
async def main():
    """Main entry point for all examples."""
    log_time("🚀 Asyncio Examples - Starting Demonstrations\n")

    await demonstrate_concurrent_execution()
    await demonstrate_task_management()
    await demonstrate_error_handling()
    await demonstrate_async_context_manager()

    log_time("=" * 60)
    log_time("✨ All demonstrations completed!")
    log_time("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
