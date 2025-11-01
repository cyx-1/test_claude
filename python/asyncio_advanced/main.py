"""
Advanced Asyncio Examples: Production-Ready Patterns

This example demonstrates advanced asyncio concepts:
1. Synchronization primitives (Lock, Semaphore, Event)
2. Queue-based producer/consumer patterns
3. Timeouts and task cancellation
4. Advanced task management (as_completed, wait)
5. Async iteration and generators
6. Running blocking code in executors
7. Real-world patterns (rate limiting, retry logic)
"""

import asyncio
import random
import sys
import time
from datetime import datetime
from typing import AsyncGenerator

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def log_time(msg):
    """Helper function to print timestamped messages."""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}")


# ============================================================================
# EXAMPLE 1: Synchronization Primitives
# ============================================================================

# Example 1a: Lock - Mutual Exclusion
shared_counter = 0
counter_lock = asyncio.Lock()


async def increment_counter(worker_id, iterations):
    """Demonstrates using Lock to protect shared resources."""
    global shared_counter
    for i in range(iterations):
        async with counter_lock:  # Only one task can hold the lock
            current = shared_counter
            await asyncio.sleep(0.01)  # Simulate some work
            shared_counter = current + 1
            log_time(f"🔒 Worker-{worker_id}: Counter = {shared_counter}")


# Example 1b: Semaphore - Limit Concurrent Access
async def download_file(file_id, semaphore):
    """Demonstrates using Semaphore to limit concurrent operations."""
    async with semaphore:  # Only N tasks can be here at once
        log_time(f"📥 Downloading file-{file_id}...")
        await asyncio.sleep(random.uniform(0.5, 1.0))
        log_time(f"✅ Downloaded file-{file_id}")
        return f"file-{file_id}.data"


# Example 1c: Event - Signaling Between Tasks
async def waiter(event, waiter_id):
    """Demonstrates waiting for an event signal."""
    log_time(f"⏳ Waiter-{waiter_id}: Waiting for signal...")
    await event.wait()  # Block until event is set
    log_time(f"🎉 Waiter-{waiter_id}: Received signal! Proceeding...")


async def signaler(event, delay):
    """Demonstrates setting an event to wake up waiters."""
    log_time(f"⏰ Signaler: Will send signal in {delay}s...")
    await asyncio.sleep(delay)
    event.set()  # Wake up all waiters
    log_time(f"📢 Signaler: Signal sent!")


async def demonstrate_synchronization():
    """Demonstrates Lock, Semaphore, and Event."""
    global shared_counter
    log_time("=" * 60)
    log_time("EXAMPLE 1: Synchronization Primitives")
    log_time("=" * 60)

    # 1a: Lock
    log_time("\n🔐 Lock Example - Protecting Shared Counter:")
    shared_counter = 0
    await asyncio.gather(
        increment_counter(1, 3),
        increment_counter(2, 3),
    )
    log_time(f"   Final counter value: {shared_counter}\n")

    # 1b: Semaphore - Limit to 2 concurrent downloads
    log_time("🚦 Semaphore Example - Max 2 Concurrent Downloads:")
    semaphore = asyncio.Semaphore(2)
    await asyncio.gather(*[download_file(i, semaphore) for i in range(5)])
    log_time("")

    # 1c: Event
    log_time("📣 Event Example - Coordinating Tasks:")
    event = asyncio.Event()
    await asyncio.gather(
        waiter(event, 1),
        waiter(event, 2),
        waiter(event, 3),
        signaler(event, 1.0),
    )
    log_time("")


# ============================================================================
# EXAMPLE 2: Queue-Based Producer/Consumer Pattern
# ============================================================================


async def producer(queue, producer_id, items):
    """Produces items and puts them in the queue."""
    for i in range(items):
        item = f"Item-{producer_id}-{i}"
        await queue.put(item)
        log_time(f"📦 Producer-{producer_id}: Added {item} (queue size: {queue.qsize()})")
        await asyncio.sleep(random.uniform(0.1, 0.3))
    log_time(f"✅ Producer-{producer_id}: Finished")


async def consumer(queue, consumer_id):
    """Consumes items from the queue."""
    while True:
        item = await queue.get()  # Wait for an item
        if item is None:  # Poison pill to stop
            queue.task_done()
            log_time(f"🛑 Consumer-{consumer_id}: Shutting down")
            break
        log_time(f"📨 Consumer-{consumer_id}: Processing {item}")
        await asyncio.sleep(random.uniform(0.2, 0.4))  # Simulate work
        queue.task_done()


async def demonstrate_queue_pattern():
    """Demonstrates producer/consumer pattern with asyncio.Queue."""
    log_time("=" * 60)
    log_time("EXAMPLE 2: Queue-Based Producer/Consumer Pattern")
    log_time("=" * 60)

    queue = asyncio.Queue(maxsize=3)  # Bounded queue

    # Start producers and consumers
    producers = [producer(queue, i, 3) for i in range(2)]
    consumers = [asyncio.create_task(consumer(queue, i)) for i in range(2)]

    # Wait for all producers to finish
    await asyncio.gather(*producers)

    # Wait for queue to be empty
    await queue.join()
    log_time("📋 All items processed!")

    # Send poison pills to stop consumers
    for _ in consumers:
        await queue.put(None)

    # Wait for consumers to finish
    await asyncio.gather(*consumers)
    log_time("")


# ============================================================================
# EXAMPLE 3: Timeouts and Cancellation
# ============================================================================


async def slow_operation(duration, task_name):
    """A slow operation that might be cancelled or timeout."""
    try:
        log_time(f"🐌 {task_name}: Starting (will take {duration}s)...")
        await asyncio.sleep(duration)
        log_time(f"✅ {task_name}: Completed!")
        return f"{task_name} result"
    except asyncio.CancelledError:
        log_time(f"❌ {task_name}: Was cancelled!")
        raise  # Re-raise to properly handle cancellation


async def demonstrate_timeouts_and_cancellation():
    """Demonstrates timeouts and task cancellation."""
    log_time("=" * 60)
    log_time("EXAMPLE 3: Timeouts and Cancellation")
    log_time("=" * 60)

    # 3a: Timeout with wait_for
    log_time("\n⏱️  Timeout Example (2s timeout for 3s task):")
    try:
        result = await asyncio.wait_for(slow_operation(3, "SlowTask"), timeout=2.0)
    except asyncio.TimeoutError:
        log_time("⏰ Task timed out!\n")

    # 3b: Successful completion within timeout
    log_time("⏱️  Successful Completion (2s timeout for 1s task):")
    try:
        result = await asyncio.wait_for(slow_operation(1, "FastTask"), timeout=2.0)
        log_time(f"📊 Result: {result}\n")
    except asyncio.TimeoutError:
        log_time("⏰ Task timed out!\n")

    # 3c: Manual cancellation
    log_time("🛑 Manual Cancellation Example:")
    task = asyncio.create_task(slow_operation(5, "LongTask"))
    await asyncio.sleep(0.5)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        log_time("🚫 Task was successfully cancelled!\n")


# ============================================================================
# EXAMPLE 4: Advanced Task Management
# ============================================================================


async def fetch_data(source, delay):
    """Simulates fetching data from a source."""
    await asyncio.sleep(delay)
    return f"Data from {source}"


async def demonstrate_advanced_task_management():
    """Demonstrates as_completed and wait with different strategies."""
    log_time("=" * 60)
    log_time("EXAMPLE 4: Advanced Task Management")
    log_time("=" * 60)

    # 4a: Process results as they complete (fastest first)
    log_time("\n🏃 as_completed - Process Results as They Finish:")
    tasks = [
        fetch_data("API-A", 1.5),
        fetch_data("API-B", 0.5),
        fetch_data("API-C", 1.0),
    ]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        log_time(f"✅ Received: {result}")

    # 4b: Wait with FIRST_COMPLETED strategy
    log_time("\n🥇 wait(return_when=FIRST_COMPLETED):")
    tasks = {
        asyncio.create_task(fetch_data("Source-1", 2.0)),
        asyncio.create_task(fetch_data("Source-2", 0.8)),
        asyncio.create_task(fetch_data("Source-3", 1.5)),
    }

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    log_time(f"📋 {len(done)} task(s) completed, {len(pending)} pending")
    for task in done:
        log_time(f"✅ Result: {task.result()}")

    # Cancel remaining tasks
    for task in pending:
        task.cancel()
    log_time("")


# ============================================================================
# EXAMPLE 5: Async Iteration and Generators
# ============================================================================


async def async_range(count: int) -> AsyncGenerator[int, None]:
    """An async generator that yields numbers."""
    for i in range(count):
        log_time(f"🔢 Generating number: {i}")
        await asyncio.sleep(0.2)  # Simulate async work
        yield i


async def fetch_pages(num_pages: int) -> AsyncGenerator[dict, None]:
    """Simulates fetching paginated data."""
    for page in range(1, num_pages + 1):
        log_time(f"📄 Fetching page {page}...")
        await asyncio.sleep(0.3)
        yield {"page": page, "data": [f"item-{page}-{i}" for i in range(3)]}


async def demonstrate_async_iteration():
    """Demonstrates async generators and async for loops."""
    log_time("=" * 60)
    log_time("EXAMPLE 5: Async Iteration and Generators")
    log_time("=" * 60)

    # 5a: Simple async generator
    log_time("\n🔁 Async Range Generator:")
    async for num in async_range(4):
        log_time(f"   Received: {num}")

    # 5b: Paginated data fetching
    log_time("\n📚 Async Pagination:")
    async for page_data in fetch_pages(3):
        log_time(f"   Page {page_data['page']}: {len(page_data['data'])} items")
    log_time("")


# ============================================================================
# EXAMPLE 6: Running Blocking Code in Executor
# ============================================================================


def blocking_io_operation(duration, operation_name):
    """A blocking I/O operation (e.g., file I/O, legacy library)."""
    log_time(f"🔨 {operation_name}: Starting blocking operation...")
    time.sleep(duration)  # Blocking sleep (not asyncio.sleep!)
    log_time(f"✅ {operation_name}: Completed!")
    return f"{operation_name} result"


async def demonstrate_executor():
    """Demonstrates running blocking code in a thread pool."""
    log_time("=" * 60)
    log_time("EXAMPLE 6: Running Blocking Code in Executor")
    log_time("=" * 60)

    log_time("\n🧵 Running 3 blocking operations concurrently in threads:")
    loop = asyncio.get_running_loop()

    # Run blocking operations in thread pool
    tasks = [
        loop.run_in_executor(None, blocking_io_operation, 0.5, "FileRead"),
        loop.run_in_executor(None, blocking_io_operation, 0.3, "DatabaseQuery"),
        loop.run_in_executor(None, blocking_io_operation, 0.4, "APICall"),
    ]

    results = await asyncio.gather(*tasks)
    log_time(f"📊 All blocking operations completed!")
    for result in results:
        log_time(f"   {result}")
    log_time("")


# ============================================================================
# EXAMPLE 7: Real-World Patterns
# ============================================================================


# 7a: Rate Limiting
class RateLimiter:
    """A token bucket rate limiter."""

    def __init__(self, rate: int, per: float):
        self.rate = rate  # Number of operations
        self.per = per  # Per time period (seconds)
        self.allowance = rate
        self.last_check = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to proceed (with rate limiting)."""
        async with self.lock:
            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current
            self.allowance += time_passed * (self.rate / self.per)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                log_time(f"⏸️  Rate limit: Sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0


async def rate_limited_request(request_id, rate_limiter):
    """Makes a rate-limited request."""
    await rate_limiter.acquire()
    log_time(f"🌐 Request-{request_id}: Sending...")
    await asyncio.sleep(0.1)  # Simulate request
    log_time(f"✅ Request-{request_id}: Done")


# 7b: Retry Logic with Exponential Backoff
async def unreliable_operation(operation_id, failure_rate=0.7):
    """An operation that might fail."""
    if random.random() < failure_rate:
        raise Exception(f"Operation-{operation_id} failed!")
    return f"Success-{operation_id}"


async def retry_with_backoff(operation_id, max_retries=3):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            log_time(f"🔄 Operation-{operation_id}: Attempt {attempt + 1}/{max_retries}")
            result = await unreliable_operation(operation_id)
            log_time(f"✅ Operation-{operation_id}: {result}")
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                log_time(f"❌ Operation-{operation_id}: All retries failed")
                raise
            backoff = 2**attempt  # Exponential: 1s, 2s, 4s
            log_time(f"⚠️  Operation-{operation_id}: Failed, retrying in {backoff}s...")
            await asyncio.sleep(backoff)


async def demonstrate_real_world_patterns():
    """Demonstrates rate limiting and retry logic."""
    log_time("=" * 60)
    log_time("EXAMPLE 7: Real-World Patterns")
    log_time("=" * 60)

    # 7a: Rate Limiting - Max 2 requests per second
    log_time("\n🚦 Rate Limiting (2 requests/second):")
    rate_limiter = RateLimiter(rate=2, per=1.0)
    await asyncio.gather(*[rate_limited_request(i, rate_limiter) for i in range(5)])

    # 7b: Retry Logic with Exponential Backoff
    log_time("\n🔁 Retry with Exponential Backoff:")
    try:
        await retry_with_backoff(1, max_retries=3)
    except Exception:
        pass
    log_time("")


# ============================================================================
# Main Function
# ============================================================================


async def main():
    """Main entry point for all advanced examples."""
    log_time("🚀 Advanced Asyncio Examples - Starting Demonstrations\n")

    await demonstrate_synchronization()
    await demonstrate_queue_pattern()
    await demonstrate_timeouts_and_cancellation()
    await demonstrate_advanced_task_management()
    await demonstrate_async_iteration()
    await demonstrate_executor()
    await demonstrate_real_world_patterns()

    log_time("=" * 60)
    log_time("✨ All advanced demonstrations completed!")
    log_time("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
