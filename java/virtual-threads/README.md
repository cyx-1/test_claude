# Virtual Threads Example: Project Loom in Java 21

This example demonstrates Java Virtual Threads (Project Loom), a revolutionary feature introduced in Java 21 that enables lightweight concurrency with millions of threads.

## Key Concepts Illustrated

1. **Traditional vs Virtual Threads** - Understanding the difference and performance characteristics
2. **Massive Scalability** - Creating thousands of threads with minimal overhead
3. **Structured Concurrency** - Using ExecutorService with virtual threads
4. **Error Handling** - Graceful error management in concurrent code
5. **CPU-Bound vs I/O-Bound** - Understanding best use cases for virtual threads

## Running the Example

```bash
cd java/virtual-threads
javac Main.java
java Main
```

**Requirements:** Java 21 or higher (virtual threads are a stable feature in Java 21)

## Source Code and Output Analysis

### 1. Traditional Threads vs Virtual Threads

**Source Code (Main.java:48-71):**
```java
// Traditional Platform Threads
logTime("\n🐌 Traditional Platform Threads (3 tasks):");
Instant start = Instant.now();

Thread t1 = Thread.ofPlatform().start(() -> {          // Line 53: Platform thread
    try { fetchData("Task-1", 1); } catch (Exception e) { e.printStackTrace(); }
});
Thread t2 = Thread.ofPlatform().start(() -> {          // Line 56: Platform thread
    try { fetchData("Task-2", 1); } catch (Exception e) { e.printStackTrace(); }
});
Thread t3 = Thread.ofPlatform().start(() -> {          // Line 59: Platform thread
    try { fetchData("Task-3", 1); } catch (Exception e) { e.printStackTrace(); }
});

// Virtual Threads
logTime("🚀 Virtual Threads (3 tasks):");
start = Instant.now();

Thread v1 = Thread.startVirtualThread(() -> {          // Line 76: Virtual thread!
    try { fetchData("VTask-1", 1); } catch (Exception e) { e.printStackTrace(); }
});
Thread v2 = Thread.startVirtualThread(() -> {          // Line 79: Virtual thread!
    try { fetchData("VTask-2", 1); } catch (Exception e) { e.printStackTrace(); }
});
Thread v3 = Thread.startVirtualThread(() -> {          // Line 82: Virtual thread!
    try { fetchData("VTask-3", 1); } catch (Exception e) { e.printStackTrace(); }
});
```

**Output:**
```
[20:56:45.502] 🐌 Traditional Platform Threads (3 tasks):
[20:56:45.523] 📥 Starting to fetch Task-1...    ← Line 53: All three start
[20:56:45.523] 📥 Starting to fetch Task-2...    ← Line 56: concurrently
[20:56:45.524] 📥 Starting to fetch Task-3...    ← Line 59: (nearly simultaneous)
[20:56:46.525] ✅ Finished fetching Task-3       ← All complete after ~1s
[20:56:46.525] ✅ Finished fetching Task-1
[20:56:46.525] ✅ Finished fetching Task-2
[20:56:46.530] ⏱️  Platform threads time: 1011ms  ← Total: ~1 second

[20:56:46.530] 🚀 Virtual Threads (3 tasks):
[20:56:46.541] 📥 Starting to fetch VTask-1...   ← Line 76: All three start
[20:56:46.542] 📥 Starting to fetch VTask-3...   ← Line 82: concurrently
[20:56:46.541] 📥 Starting to fetch VTask-2...   ← Line 79: (nearly simultaneous)
[20:56:47.544] ✅ Finished fetching VTask-3      ← All complete after ~1s
[20:56:47.544] ✅ Finished fetching VTask-2
[20:56:47.544] ✅ Finished fetching VTask-1
[20:56:47.545] ⏱️  Virtual threads time: 1014ms   ← Total: ~1 second
```

**💡 Key Insight:**
- **Platform threads** (lines 53-59): Traditional OS threads, heavyweight but work fine for small numbers
- **Virtual threads** (lines 76-82): Managed by JVM, extremely lightweight
- **Performance**: For small numbers, both perform similarly (~1 second for 3 concurrent 1-second tasks)
- **Key difference**: Virtual threads can scale to MILLIONS while platform threads are limited to thousands

---

### 2. Massive Scalability - Creating 10,000 Threads

**Source Code (Main.java:100-118):**
```java
int taskCount = 10_000;
logTime("\n📊 Creating " + taskCount + " virtual threads...");

Instant start = Instant.now();
List<Thread> threads = new ArrayList<>();

for (int i = 0; i < taskCount; i++) {                    // Line 105: Create 10,000 threads!
    final int taskId = i;
    Thread thread = Thread.startVirtualThread(() -> {    // Line 107: Each is a virtual thread
        try {
            Thread.sleep(100); // Simulate work                // Line 109: All "sleep" 100ms
            if (taskId == 0 || taskId == taskCount - 1) {
                logTime("✅ Task " + taskId + " completed");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
    threads.add(thread);
}
```

**Output:**
```
[20:56:47.549] 📊 Creating 10000 virtual threads...
[20:56:47.652] ✅ Task 0 completed                ← Line 111: First task done
[20:56:47.708] ✅ Task 9999 completed             ← Line 111: Last task done
[20:56:47.715] ⏱️  All 10000 tasks completed in 159ms  ← Total time: ~160ms!
[20:56:47.715] 💡 Virtual threads are lightweight! Creating 10K threads is no problem.
```

**💡 Key Insight:**
- **Line 107:** Created 10,000 virtual threads - would crash with platform threads!
- **Line 109:** Each thread sleeps for 100ms (simulating I/O)
- **Total time:** ~160ms (not 100ms × 10,000 = 16 minutes!)
- **How?** Virtual threads are so lightweight, the JVM can run thousands concurrently
- **Memory:** Each virtual thread uses only a few KB vs ~1MB for platform threads
- **Try this with platform threads:** You'd run out of memory or hit OS limits

---

### 3. Structured Concurrency with ExecutorService

**Source Code (Main.java:129-150):**
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {  // Line 133
    Instant start = Instant.now();

    // Submit multiple tasks
    Future<String> future1 = executor.submit(() -> fetchData("API-1", 1));  // Line 137
    Future<String> future2 = executor.submit(() -> fetchData("API-2", 1));  // Line 138
    Future<String> future3 = executor.submit(() -> fetchData("API-3", 1));  // Line 139

    logTime("📋 Submitted 3 tasks to executor");

    // Get results (blocks until complete)
    String result1 = future1.get();                                         // Line 144
    String result2 = future2.get();                                         // Line 145
    String result3 = future3.get();                                         // Line 146

    logTime("\n📊 All results received");
    logTime("   Result 1: " + result1);                                     // Line 149
}  // Line 151: Executor automatically shuts down here
```

**Output:**
```
[20:56:47.716] 🔧 Using virtual thread ExecutorService:
[20:56:47.718] 📥 Starting to fetch API-1...     ← Line 137: Task 1 starts
[20:56:47.719] 📥 Starting to fetch API-2...     ← Line 138: Task 2 starts
[20:56:47.719] 📋 Submitted 3 tasks to executor
[20:56:47.719] 📥 Starting to fetch API-3...     ← Line 139: Task 3 starts

[20:56:48.720] ✅ Finished fetching API-1        ← Line 144: All complete
[20:56:48.720] ✅ Finished fetching API-3        ← Line 146: after ~1 second
[20:56:48.720] ✅ Finished fetching API-2        ← Line 145: (concurrent!)

[20:56:48.721] 📊 All results received in 1004ms
[20:56:48.721]    Result 1: Data from API-1      ← Line 149: Access results
[20:56:48.722]    Result 2: Data from API-2
[20:56:48.722]    Result 3: Data from API-3
[20:56:48.722] 🔒 ExecutorService automatically closed (structured concurrency)
```

**💡 Key Insight:**
- **Line 133:** `newVirtualThreadPerTaskExecutor()` creates a new virtual thread for each task
- **Lines 137-139:** Tasks are submitted and start executing immediately
- **Lines 144-146:** `future.get()` blocks until results are ready
- **Line 151:** `try-with-resources` ensures executor shuts down cleanly (structured concurrency)
- **Structured concurrency:** Parent scope waits for all child tasks before closing
- **Total time:** ~1 second for 3 concurrent 1-second tasks = perfect parallelism!

---

### 4. Error Handling in Virtual Threads

**Source Code (Main.java:160-181):**
```java
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = new ArrayList<>();

    // Submit tasks - one will fail
    futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-1", 300, false)));
    futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-2", 500, true))); // Line 168: Will fail!
    futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-3", 200, false)));

    logTime("📋 Submitted 3 operations (one will fail)");

    // Collect results
    logTime("\n📊 Results:");
    for (int i = 0; i < futures.size(); i++) {                      // Line 175
        try {
            String result = futures.get(i).get();                   // Line 177: Get result
            logTime("   Operation-" + (i + 1) + ": " + result);
        } catch (Exception e) {                                      // Line 179: Catch errors
            logTime("   Operation-" + (i + 1) + ": Exception caught - " + e.getMessage());
        }
    }
}
```

**fetchWithErrorHandling() function (Main.java:26-40):**
```java
private static String fetchWithErrorHandling(String name, int delayMs, boolean shouldFail) {
    try {
        logTime("🔄 Starting " + name + "...");
        Thread.sleep(delayMs);
        if (shouldFail) {                                            // Line 33
            throw new RuntimeException("Simulated error in " + name);  // Line 34: Throw error
        }
        logTime("✅ Completed " + name);
        return "Success: " + name;
    } catch (Exception e) {                                          // Line 38: Catch and handle
        logTime("❌ Error in " + name + ": " + e.getMessage());
        return "Failed: " + name;                                    // Line 40: Return failure message
    }
}
```

**Output:**
```
[20:56:48.722] 🔍 Testing error handling:
[20:56:48.723] 🔄 Starting Operation-1...        ← All three start
[20:56:48.723] 🔄 Starting Operation-2...        ← concurrently
[20:56:48.723] 📋 Submitted 3 operations (one will fail)
[20:56:48.723] 🔄 Starting Operation-3...

[20:56:48.925] ✅ Completed Operation-3          ← Fastest (200ms) completes first
[20:56:49.024] ✅ Completed Operation-1          ← Second fastest (300ms)
[20:56:49.224] ❌ Error in Operation-2: ...      ← Line 34: Error thrown, Line 40: handled!

[20:56:49.029]    Operation-1: Success: Operation-1   ← Line 177: Success result
[20:56:49.225]    Operation-2: Failed: Operation-2    ← Line 177: Failure result (not exception!)
[20:56:49.225]    Operation-3: Success: Operation-3   ← Line 177: Success result
[20:56:49.225] 💡 Other operations continued despite one failing
```

**💡 Key Insight:**
- **Line 168:** Operation-2 is configured to fail (shouldFail=true)
- **Line 34:** Exception is thrown in the virtual thread
- **Line 38-40:** Exception is caught and converted to a failure message
- **Line 177:** All results are retrieved, including the "failed" one
- **Key point:** One failure doesn't stop other operations - they all complete
- **Graceful degradation:** Operations complete in order of duration, not submission order

---

### 5. CPU-Bound vs I/O-Bound Work

**Source Code (Main.java:193-229):**
```java
// CPU-bound work
logTime("\n🧮 CPU-bound work (computing fibonacci):");
Instant start = Instant.now();

Thread cpuThread = Thread.startVirtualThread(() -> {     // Line 197
    logTime("🔢 Computing fibonacci(40)...");
    long result = fibonacci(40);                          // Line 199: CPU-intensive!
    logTime("✅ Fibonacci(40) = " + result);
});
cpuThread.join();

Duration cpuDuration = Duration.between(start, Instant.now());
logTime("⏱️  CPU-bound time: " + cpuDuration.toMillis() + "ms");

// I/O-bound work
logTime("\n📡 I/O-bound work (10 concurrent HTTP-like requests):");
start = Instant.now();

List<Thread> ioThreads = new ArrayList<>();
for (int i = 0; i < 10; i++) {                           // Line 213: 10 concurrent I/O tasks
    final int id = i;
    Thread thread = Thread.startVirtualThread(() -> {    // Line 215: Virtual thread
        try {
            Thread.sleep(500); // Simulate I/O wait           // Line 217: Blocking I/O
            if (id == 0 || id == 9) {
                logTime("✅ Request " + id + " completed");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
    ioThreads.add(thread);
}
```

**Output:**
```
[20:56:49.226] 🧮 CPU-bound work (computing fibonacci):
[20:56:49.226] 🔢 Computing fibonacci(40)...     ← Line 199: CPU computation starts
[20:56:49.699] ✅ Fibonacci(40) = 102334155      ← Line 199: Completes after ~473ms
[20:56:49.699] ⏱️  CPU-bound time: 473ms         ← CPU work takes time

[20:56:49.699] 📡 I/O-bound work (10 concurrent HTTP-like requests):
[20:56:50.202] ✅ Request 0 completed            ← Line 217: All complete together
[20:56:50.202] ✅ Request 9 completed            ← after ~500ms (not 5000ms!)
[20:56:50.203] ⏱️  I/O-bound time: 502ms         ← 10 tasks in parallel = ~500ms total
[20:56:50.203] 💡 Virtual threads excel at I/O-bound work (network, database, files)
```

**💡 Key Insight:**
- **CPU-bound (Line 199):** Fibonacci computation runs on actual CPU - no concurrency benefit
  - Virtual thread doesn't make CPU faster
  - Still takes ~473ms of actual CPU time
- **I/O-bound (Line 217):** 10 concurrent requests, each waiting 500ms
  - Total time: ~502ms (not 10 × 500ms = 5000ms!)
  - Virtual threads shine here: while one waits for I/O, others run
  - **10x throughput improvement** with concurrency!
- **When to use virtual threads:**
  - ✅ Network requests (HTTP, database, APIs)
  - ✅ File I/O operations
  - ✅ Any blocking operations where you wait
  - ❌ Pure CPU computation (no benefit)
  - ❌ Already async/non-blocking code (already efficient)

---

## Performance Summary

| Scenario | Thread Type | Count | Total Time | Notes |
|----------|-------------|-------|------------|-------|
| Basic concurrency | Platform | 3 | ~1011ms | Works fine for small numbers |
| Basic concurrency | Virtual | 3 | ~1014ms | Similar performance |
| **Scalability** | **Virtual** | **10,000** | **~159ms** | **Impossible with platform threads!** |
| Structured concurrency | Virtual | 3 | ~1004ms | Clean shutdown with try-with-resources |
| I/O-bound work | Virtual | 10 | ~502ms | 10x throughput vs sequential |
| CPU-bound work | Virtual | 1 | ~473ms | No concurrency benefit |

## Key Takeaways

1. **Lightweight:** Virtual threads use ~1KB vs ~1MB for platform threads - can create millions
2. **Easy to use:** `Thread.startVirtualThread(runnable)` - same API as regular threads
3. **Structured concurrency:** Use `ExecutorService` with try-with-resources for clean shutdown
4. **Perfect for I/O:** Network, database, file operations benefit massively
5. **Not magic:** CPU-bound work still takes CPU time, no performance improvement
6. **Error handling:** Failures in one thread don't affect others
7. **Blocking is OK:** Can use blocking APIs (unlike async/await) - virtual threads handle it

## When to Use Virtual Threads

✅ **Excellent for:**
- HTTP servers handling many concurrent requests
- Microservices making many API calls
- Database applications with concurrent queries
- File processing with I/O operations
- Any scenario with many concurrent blocking operations

❌ **Not necessary for:**
- CPU-intensive computations (no benefit)
- Applications with few concurrent tasks
- Code already using async/reactive patterns effectively

## Comparison with Other Languages

| Language | Feature | Virtual Threads Equivalent |
|----------|---------|---------------------------|
| Python | `asyncio` | Similar concept, but virtual threads use blocking APIs |
| JavaScript | `async/await` | Virtual threads = sync code that scales like async |
| Go | Goroutines | Very similar! Virtual threads = Java's goroutines |
| Kotlin | Coroutines | Similar lightweight concurrency |

**Key difference:** Virtual threads let you write **simple blocking code** that scales like asynchronous code!

## Java Version Requirements

- **Java 19-20:** Preview feature (requires `--enable-preview`)
- **Java 21+:** Stable feature (no flags needed)

This example uses Java 21 where virtual threads are a fully supported, stable feature.
