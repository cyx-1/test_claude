# Advanced Asyncio: Production-Ready Patterns

This example demonstrates advanced asyncio concepts essential for production applications.

## Topics Covered

1. **Synchronization Primitives** - Lock, Semaphore, Event
2. **Queue-Based Patterns** - Producer/Consumer with asyncio.Queue
3. **Timeouts and Cancellation** - wait_for, cancel, CancelledError
4. **Advanced Task Management** - as_completed, wait with strategies
5. **Async Iteration** - Async generators and async for loops
6. **Blocking Code** - Running blocking operations in executors
7. **Real-World Patterns** - Rate limiting and retry logic

## Running the Example

```bash
uv run python main.py
```

---

## 1. Synchronization Primitives

### 1a. Lock - Protecting Shared Resources

**Source Code (main.py:31-38):**
```python
async def increment_counter(worker_id, iterations):
    global shared_counter
    for i in range(iterations):
        async with counter_lock:  # Line 34: Only one task at a time
            current = shared_counter
            await asyncio.sleep(0.01)  # Line 36: Simulate work
            shared_counter = current + 1
            log_time(f"🔒 Worker-{worker_id}: Counter = {shared_counter}")
```

**Output:**
```
[08:49:08.869] 🔒 Worker-1: Counter = 1   ← Worker-1 holds lock
[08:49:08.885] 🔒 Worker-2: Counter = 2   ← Worker-2 gets lock after Worker-1 releases
[08:49:08.901] 🔒 Worker-1: Counter = 3   ← They alternate (mutual exclusion)
[08:49:08.917] 🔒 Worker-2: Counter = 4
[08:49:08.933] 🔒 Worker-1: Counter = 5
[08:49:08.949] 🔒 Worker-2: Counter = 6
[08:49:08.949]    Final counter value: 6  ← Correct! (Without lock, would be wrong)
```

**💡 Key Insight:**
- **Line 34:** `async with counter_lock` ensures only one task modifies `shared_counter` at a time
- **Line 36:** Even with simulated work between read and write, the lock prevents race conditions
- **Result:** Counter reaches correct value (6) because updates are atomic

---

### 1b. Semaphore - Limiting Concurrent Operations

**Source Code (main.py:42-48):**
```python
async def download_file(file_id, semaphore):
    async with semaphore:  # Line 44: Only N tasks can be here
        log_time(f"📥 Downloading file-{file_id}...")
        await asyncio.sleep(random.uniform(0.5, 1.0))
        log_time(f"✅ Downloaded file-{file_id}")
        return f"file-{file_id}.data"
```

**Usage (main.py:70-72):**
```python
semaphore = asyncio.Semaphore(2)  # Line 70: Max 2 concurrent
await asyncio.gather(*[download_file(i, semaphore) for i in range(5)])
```

**Output:**
```
[08:49:08.949] 📥 Downloading file-0...  ← First 2 start immediately
[08:49:08.949] 📥 Downloading file-1...
[08:49:09.588] ✅ Downloaded file-0      ← file-0 finishes, slot opens
[08:49:09.588] 📥 Downloading file-2...  ← file-2 starts (using file-0's slot)
[08:49:09.766] ✅ Downloaded file-1      ← file-1 finishes, slot opens
[08:49:09.766] 📥 Downloading file-3...  ← file-3 starts (using file-1's slot)
[08:49:10.501] ✅ Downloaded file-2
[08:49:10.501] 📥 Downloading file-4...  ← file-4 starts
[08:49:10.693] ✅ Downloaded file-3
[08:49:11.014] ✅ Downloaded file-4
```

**💡 Key Insight:**
- **Line 70:** `Semaphore(2)` allows max 2 concurrent downloads
- **Notice:** Only 2 "Downloading" messages appear at a time
- **Use Case:** Prevent overwhelming external APIs or system resources

---

### 1c. Event - Coordinating Multiple Tasks

**Source Code (main.py:52-57):**
```python
async def waiter(event, waiter_id):
    log_time(f"⏳ Waiter-{waiter_id}: Waiting for signal...")
    await event.wait()  # Line 54: Block until event is set
    log_time(f"🎉 Waiter-{waiter_id}: Received signal! Proceeding...")
```

**Source Code (main.py:60-64):**
```python
async def signaler(event, delay):
    log_time(f"⏰ Signaler: Will send signal in {delay}s...")
    await asyncio.sleep(delay)
    event.set()  # Line 63: Wake up all waiters
    log_time(f"📢 Signaler: Signal sent!")
```

**Output:**
```
[08:49:11.014] ⏳ Waiter-1: Waiting for signal...  ← Line 54: All 3 waiters
[08:49:11.014] ⏳ Waiter-2: Waiting for signal...  ← block here
[08:49:11.014] ⏳ Waiter-3: Waiting for signal...
[08:49:11.014] ⏰ Signaler: Will send signal in 1.0s...
[08:49:12.015] 📢 Signaler: Signal sent!           ← Line 63: Event set!
[08:49:12.015] 🎉 Waiter-1: Received signal! Proceeding...  ← All wake up
[08:49:12.015] 🎉 Waiter-2: Received signal! Proceeding...  ← simultaneously
[08:49:12.015] 🎉 Waiter-3: Received signal! Proceeding...
```

**💡 Key Insight:**
- **Line 54:** All waiters block at `event.wait()`
- **Line 63:** `event.set()` releases ALL waiting tasks simultaneously
- **Use Case:** Coordinating initialization (e.g., wait for DB connection before processing requests)

---

## 2. Queue-Based Producer/Consumer Pattern

**Source Code - Producer (main.py:92-99):**
```python
async def producer(queue, producer_id, items):
    for i in range(items):
        item = f"Item-{producer_id}-{i}"
        await queue.put(item)  # Line 95: Add to queue
        log_time(f"📦 Producer-{producer_id}: Added {item} (queue size: {queue.qsize()})")
        await asyncio.sleep(random.uniform(0.1, 0.3))
    log_time(f"✅ Producer-{producer_id}: Finished")
```

**Source Code - Consumer (main.py:102-112):**
```python
async def consumer(queue, consumer_id):
    while True:
        item = await queue.get()  # Line 104: Block until item available
        if item is None:  # Line 105: Poison pill to stop
            queue.task_done()
            log_time(f"🛑 Consumer-{consumer_id}: Shutting down")
            break
        log_time(f"📨 Consumer-{consumer_id}: Processing {item}")
        await asyncio.sleep(random.uniform(0.2, 0.4))
        queue.task_done()  # Line 111: Mark item as processed
```

**Output:**
```
[08:49:12.016] 📦 Producer-0: Added Item-0-0 (queue size: 1)  ← Added to queue
[08:49:12.016] 📦 Producer-1: Added Item-1-0 (queue size: 2)
[08:49:12.016] 📨 Consumer-0: Processing Item-0-0             ← Line 104: Consumer gets it
[08:49:12.016] 📨 Consumer-1: Processing Item-1-0
[08:49:12.146] 📦 Producer-0: Added Item-0-1 (queue size: 1)
[08:49:12.273] 📦 Producer-0: Added Item-0-2 (queue size: 2)
[08:49:12.273] 📨 Consumer-0: Processing Item-0-1
...
[08:49:12.997] 📋 All items processed!                         ← queue.join() completed
[08:49:12.997] 🛑 Consumer-0: Shutting down                    ← Line 105: Poison pill
[08:49:12.997] 🛑 Consumer-1: Shutting down
```

**💡 Key Insight:**
- **Line 95:** Producers add items to shared queue
- **Line 104:** `queue.get()` blocks until an item is available
- **Line 111:** `task_done()` is crucial for `queue.join()` to know when all work is complete
- **Line 105:** Poison pill pattern (`None`) gracefully shuts down consumers

---

## 3. Timeouts and Cancellation

### 3a. Timeout with wait_for

**Source Code (main.py:143-147):**
```python
log_time("\n⏱️  Timeout Example (2s timeout for 3s task):")
try:
    result = await asyncio.wait_for(slow_operation(3, "SlowTask"), timeout=2.0)
except asyncio.TimeoutError:
    log_time("⏰ Task timed out!\n")
```

**Output:**
```
[08:49:12.997] ⏱️  Timeout Example (2s timeout for 3s task):
[08:49:12.997] 🐌 SlowTask: Starting (will take 3s)...
[08:49:15.012] ❌ SlowTask: Was cancelled!  ← After 2s, wait_for cancels it
[08:49:15.012] ⏰ Task timed out!
```

**💡 Key Insight:**
- `wait_for()` automatically cancels the task after timeout
- The cancelled task receives `CancelledError` for cleanup

---

### 3b. Manual Cancellation

**Source Code (main.py:162-169):**
```python
log_time("🛑 Manual Cancellation Example:")
task = asyncio.create_task(slow_operation(5, "LongTask"))  # Line 163
await asyncio.sleep(0.5)
task.cancel()  # Line 165: Cancel the task
try:
    await task
except asyncio.CancelledError:
    log_time("🚫 Task was successfully cancelled!\n")
```

**Output:**
```
[08:49:16.017] 🛑 Manual Cancellation Example:
[08:49:16.017] 🐌 LongTask: Starting (will take 5s)...
[08:49:16.522] ❌ LongTask: Was cancelled!  ← Line 165: Cancelled after 0.5s
[08:49:16.522] 🚫 Task was successfully cancelled!
```

**💡 Key Insight:**
- **Line 165:** `task.cancel()` requests cancellation
- Task must `await` something to actually be cancelled
- Always handle `CancelledError` for proper cleanup

---

## 4. Advanced Task Management

### 4a. as_completed - Process Results as They Arrive

**Source Code (main.py:189-197):**
```python
log_time("\n🏃 as_completed - Process Results as They Finish:")
tasks = [
    fetch_data("API-A", 1.5),  # Slowest
    fetch_data("API-B", 0.5),  # Fastest
    fetch_data("API-C", 1.0),  # Medium
]

for coro in asyncio.as_completed(tasks):  # Line 195
    result = await coro
    log_time(f"✅ Received: {result}")
```

**Output:**
```
[08:49:16.522] 🏃 as_completed - Process Results as They Finish:
[08:49:17.024] ✅ Received: Data from API-B  ← Fastest finishes first (0.5s)
[08:49:17.537] ✅ Received: Data from API-C  ← Medium next (1.0s)
[08:49:18.035] ✅ Received: Data from API-A  ← Slowest last (1.5s)
```

**💡 Key Insight:**
- **Line 195:** `as_completed()` yields tasks in **completion order**, not creation order
- Use when you want to process results as soon as available (e.g., displaying search results)

---

### 4b. wait with FIRST_COMPLETED

**Source Code (main.py:200-209):**
```python
log_time("\n🥇 wait(return_when=FIRST_COMPLETED):")
tasks = {
    asyncio.create_task(fetch_data("Source-1", 2.0)),
    asyncio.create_task(fetch_data("Source-2", 0.8)),  # Fastest
    asyncio.create_task(fetch_data("Source-3", 1.5)),
}

done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
log_time(f"📋 {len(done)} task(s) completed, {len(pending)} pending")
for task in done:
    log_time(f"✅ Result: {task.result()}")
```

**Output:**
```
[08:49:18.035] 🥇 wait(return_when=FIRST_COMPLETED):
[08:49:18.851] 📋 1 task(s) completed, 2 pending  ← Only fastest completed
[08:49:18.851] ✅ Result: Data from Source-2      ← Got result from fastest
```

**💡 Key Insight:**
- `wait()` returns as soon as **one** task completes
- Returns `(done, pending)` sets for further processing
- Use when you need the first successful result (e.g., racing multiple data sources)

---

## 5. Async Iteration and Generators

**Source Code (main.py:221-227):**
```python
async def async_range(count: int) -> AsyncGenerator[int, None]:
    for i in range(count):
        log_time(f"🔢 Generating number: {i}")
        await asyncio.sleep(0.2)  # Line 224: Async work between yields
        yield i  # Line 225: Yield values asynchronously
```

**Usage (main.py:243-245):**
```python
async for num in async_range(4):  # Line 243: Async for loop
    log_time(f"   Received: {num}")
```

**Output:**
```
[08:49:18.851] 🔁 Async Range Generator:
[08:49:18.856] 🔢 Generating number: 0  ← Line 224: Generate
[08:49:19.060]    Received: 0           ← Line 225: Yield, Line 243: Consume
[08:49:19.060] 🔢 Generating number: 1  ← Next iteration
[08:49:19.268]    Received: 1
[08:49:19.268] 🔢 Generating number: 2
[08:49:19.476]    Received: 2
[08:49:19.476] 🔢 Generating number: 3
[08:49:19.683]    Received: 3
```

**💡 Key Insight:**
- **Line 224:** Can perform async operations between yields
- **Line 225:** `yield` produces values one at a time
- **Line 243:** `async for` consumes async generators
- **Use Case:** Streaming data (paginated APIs, file reading, websockets)

---

## 6. Running Blocking Code in Executor

**Source Code (main.py:263-268):**
```python
def blocking_io_operation(duration, operation_name):
    """NOT an async function - uses blocking time.sleep"""
    log_time(f"🔨 {operation_name}: Starting blocking operation...")
    time.sleep(duration)  # Line 265: BLOCKING (not asyncio.sleep!)
    log_time(f"✅ {operation_name}: Completed!")
    return f"{operation_name} result"
```

**Usage (main.py:279-286):**
```python
loop = asyncio.get_running_loop()

tasks = [
    loop.run_in_executor(None, blocking_io_operation, 0.5, "FileRead"),     # Line 282
    loop.run_in_executor(None, blocking_io_operation, 0.3, "DatabaseQuery"),
    loop.run_in_executor(None, blocking_io_operation, 0.4, "APICall"),
]
```

**Output:**
```
[08:49:20.598] 🧵 Running 3 blocking operations concurrently in threads:
[08:49:20.604] 🔨 FileRead: Starting blocking operation...       ← All 3 start
[08:49:20.604] 🔨 DatabaseQuery: Starting blocking operation...  ← at same time
[08:49:20.605] 🔨 APICall: Starting blocking operation...        ← in threads!
[08:49:20.905] ✅ DatabaseQuery: Completed!  ← Fastest finishes first
[08:49:21.006] ✅ APICall: Completed!
[08:49:21.104] ✅ FileRead: Completed!
```

**💡 Key Insight:**
- **Line 265:** Regular blocking code (e.g., `time.sleep`, file I/O)
- **Line 282:** `run_in_executor(None, ...)` runs in default thread pool
- **Result:** Blocking operations run concurrently without blocking the event loop
- **Use Case:** Legacy libraries, CPU-bound work, blocking I/O

---

## 7. Real-World Patterns

### 7a. Rate Limiting with Token Bucket

**Source Code (main.py:296-317):**
```python
class RateLimiter:
    def __init__(self, rate: int, per: float):
        self.rate = rate  # Number of operations
        self.per = per    # Per time period (seconds)
        self.allowance = rate
        ...

    async def acquire(self):
        async with self.lock:
            ...
            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                log_time(f"⏸️  Rate limit: Sleeping for {sleep_time:.2f}s")  # Line 313
                await asyncio.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0
```

**Usage (main.py:351-353):**
```python
rate_limiter = RateLimiter(rate=2, per=1.0)  # 2 requests per second
await asyncio.gather(*[rate_limited_request(i, rate_limiter) for i in range(5)])
```

**Output:**
```
[08:49:21.104] 🚦 Rate Limiting (2 requests/second):
[08:49:21.104] 🌐 Request-0: Sending...  ← First 2 allowed immediately
[08:49:21.104] 🌐 Request-1: Sending...
[08:49:21.104] ⏸️  Rate limit: Sleeping for 0.50s  ← Line 313: Throttle next batch
[08:49:21.211] ✅ Request-0: Done
[08:49:21.211] ✅ Request-1: Done
[08:49:21.613] 🌐 Request-2: Sending...  ← After 0.5s delay
[08:49:21.613] 🌐 Request-3: Sending...
[08:49:21.613] ⏸️  Rate limit: Sleeping for 0.49s
```

**💡 Key Insight:**
- Token bucket algorithm ensures max 2 requests/second
- **Line 313:** Automatically sleeps when limit exceeded
- **Use Case:** Respecting API rate limits, preventing server overload

---

### 7b. Retry Logic with Exponential Backoff

**Source Code (main.py:336-350):**
```python
async def retry_with_backoff(operation_id, max_retries=3):
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
            backoff = 2**attempt  # Line 347: Exponential: 1s, 2s, 4s
            log_time(f"⚠️  Operation-{operation_id}: Failed, retrying in {backoff}s...")
            await asyncio.sleep(backoff)
```

**Output:**
```
[08:49:22.220] 🔁 Retry with Exponential Backoff:
[08:49:22.220] 🔄 Operation-1: Attempt 1/3
[08:49:22.220] ⚠️  Operation-1: Failed, retrying in 1s...   ← Line 347: 2^0 = 1s
[08:49:23.229] 🔄 Operation-1: Attempt 2/3
[08:49:23.229] ⚠️  Operation-1: Failed, retrying in 2s...   ← Line 347: 2^1 = 2s
[08:49:25.242] 🔄 Operation-1: Attempt 3/3
[08:49:25.242] ❌ Operation-1: All retries failed           ← All attempts exhausted
```

**💡 Key Insight:**
- **Line 347:** Backoff delays: 1s, 2s, 4s (exponential growth)
- Reduces load on failing services
- **Use Case:** Network requests, database operations, external APIs

---

## Summary Table

| Concept | Use Case | Key Benefit |
|---------|----------|-------------|
| **Lock** | Protect shared state | Prevents race conditions |
| **Semaphore** | Limit concurrency | Control resource usage |
| **Event** | Coordinate tasks | Synchronize multiple waiters |
| **Queue** | Producer/Consumer | Decouple producers from consumers |
| **wait_for** | Timeouts | Prevent hanging forever |
| **as_completed** | Process ASAP | Handle results as they arrive |
| **wait(FIRST_COMPLETED)** | Race patterns | Use fastest result |
| **Async generators** | Streaming data | Memory-efficient iteration |
| **run_in_executor** | Blocking code | Don't block event loop |
| **Rate limiting** | API throttling | Respect rate limits |
| **Retry with backoff** | Fault tolerance | Gracefully handle transient failures |

## When to Use These Patterns

✅ **Use Lock when:**
- Multiple tasks modify shared state
- Need mutual exclusion

✅ **Use Semaphore when:**
- Need to limit concurrent access (e.g., DB connections, API calls)

✅ **Use Event when:**
- Need to signal multiple waiters simultaneously
- Coordinating initialization or shutdown

✅ **Use Queue when:**
- Implementing producer/consumer patterns
- Need backpressure control with bounded queues

✅ **Use as_completed when:**
- Want to process results immediately as they arrive
- Order doesn't matter

✅ **Use Executor when:**
- Working with blocking libraries (requests, legacy code)
- CPU-bound work in limited amounts

✅ **Use Rate Limiting when:**
- External APIs have rate limits
- Need to control load on services

✅ **Use Retry Logic when:**
- Dealing with unreliable external services
- Transient failures are expected
