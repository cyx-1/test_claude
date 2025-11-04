import java.time.Duration;
import java.time.Instant;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Main {
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");

    // Helper method to log with timestamp
    private static void logTime(String message) {
        System.out.println("[" + LocalTime.now().format(TIME_FORMATTER) + "] " + message);
    }

    // Simulate a blocking I/O operation
    private static String fetchData(String name, int delaySeconds) throws InterruptedException {
        logTime("📥 Starting to fetch " + name + "...");
        Thread.sleep(delaySeconds * 1000L);
        logTime("✅ Finished fetching " + name);
        return "Data from " + name;
    }

    // Simulate an operation that might fail
    private static String fetchWithErrorHandling(String name, int delayMs, boolean shouldFail) {
        try {
            logTime("🔄 Starting " + name + "...");
            Thread.sleep(delayMs);
            if (shouldFail) {
                throw new RuntimeException("Simulated error in " + name);
            }
            logTime("✅ Completed " + name);
            return "Success: " + name;
        } catch (Exception e) {
            logTime("❌ Error in " + name + ": " + e.getMessage());
            return "Failed: " + name;
        }
    }

    // Demo 1: Traditional Threads vs Virtual Threads
    private static void demo1TraditionalVsVirtual() throws InterruptedException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("Demo 1: Traditional Threads vs Virtual Threads");
        System.out.println("=".repeat(80));

        // Traditional Platform Threads
        logTime("\n🐌 Traditional Platform Threads (3 tasks):");
        Instant start = Instant.now();

        Thread t1 = Thread.ofPlatform().start(() -> {
            try { fetchData("Task-1", 1); } catch (Exception e) { e.printStackTrace(); }
        });
        Thread t2 = Thread.ofPlatform().start(() -> {
            try { fetchData("Task-2", 1); } catch (Exception e) { e.printStackTrace(); }
        });
        Thread t3 = Thread.ofPlatform().start(() -> {
            try { fetchData("Task-3", 1); } catch (Exception e) { e.printStackTrace(); }
        });

        t1.join();
        t2.join();
        t3.join();

        Duration platformDuration = Duration.between(start, Instant.now());
        logTime("⏱️  Platform threads time: " + platformDuration.toMillis() + "ms\n");

        // Virtual Threads
        logTime("🚀 Virtual Threads (3 tasks):");
        start = Instant.now();

        Thread v1 = Thread.startVirtualThread(() -> {
            try { fetchData("VTask-1", 1); } catch (Exception e) { e.printStackTrace(); }
        });
        Thread v2 = Thread.startVirtualThread(() -> {
            try { fetchData("VTask-2", 1); } catch (Exception e) { e.printStackTrace(); }
        });
        Thread v3 = Thread.startVirtualThread(() -> {
            try { fetchData("VTask-3", 1); } catch (Exception e) { e.printStackTrace(); }
        });

        v1.join();
        v2.join();
        v3.join();

        Duration virtualDuration = Duration.between(start, Instant.now());
        logTime("⏱️  Virtual threads time: " + virtualDuration.toMillis() + "ms");
        logTime("💡 Both complete in ~1 second (concurrent execution)");
    }

    // Demo 2: Scalability - Creating Many Threads
    private static void demo2Scalability() throws InterruptedException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("Demo 2: Scalability - Creating 10,000 Threads");
        System.out.println("=".repeat(80));

        int taskCount = 10_000;
        logTime("\n📊 Creating " + taskCount + " virtual threads...");

        Instant start = Instant.now();
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < taskCount; i++) {
            final int taskId = i;
            Thread thread = Thread.startVirtualThread(() -> {
                try {
                    Thread.sleep(100); // Simulate work
                    if (taskId == 0 || taskId == taskCount - 1) {
                        logTime("✅ Task " + taskId + " completed");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            threads.add(thread);
        }

        // Wait for all to complete
        for (Thread thread : threads) {
            thread.join();
        }

        Duration duration = Duration.between(start, Instant.now());
        logTime("⏱️  All " + taskCount + " tasks completed in " + duration.toMillis() + "ms");
        logTime("💡 Virtual threads are lightweight! Creating 10K threads is no problem.");
    }

    // Demo 3: Structured Concurrency with ExecutorService
    private static void demo3StructuredConcurrency() throws InterruptedException, ExecutionException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("Demo 3: Structured Concurrency with ExecutorService");
        System.out.println("=".repeat(80));

        logTime("\n🔧 Using virtual thread ExecutorService:");

        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            Instant start = Instant.now();

            // Submit multiple tasks
            Future<String> future1 = executor.submit(() -> fetchData("API-1", 1));
            Future<String> future2 = executor.submit(() -> fetchData("API-2", 1));
            Future<String> future3 = executor.submit(() -> fetchData("API-3", 1));

            logTime("📋 Submitted 3 tasks to executor");

            // Get results (blocks until complete)
            String result1 = future1.get();
            String result2 = future2.get();
            String result3 = future3.get();

            Duration duration = Duration.between(start, Instant.now());
            logTime("\n📊 All results received in " + duration.toMillis() + "ms");
            logTime("   Result 1: " + result1);
            logTime("   Result 2: " + result2);
            logTime("   Result 3: " + result3);
        } // Executor automatically shuts down here

        logTime("🔒 ExecutorService automatically closed (structured concurrency)");
    }

    // Demo 4: Error Handling
    private static void demo4ErrorHandling() throws InterruptedException, ExecutionException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("Demo 4: Error Handling in Virtual Threads");
        System.out.println("=".repeat(80));

        logTime("\n🔍 Testing error handling:");

        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Future<String>> futures = new ArrayList<>();

            // Submit tasks - one will fail
            futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-1", 300, false)));
            futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-2", 500, true))); // Will fail!
            futures.add(executor.submit(() -> fetchWithErrorHandling("Operation-3", 200, false)));

            logTime("📋 Submitted 3 operations (one will fail)");

            // Collect results
            logTime("\n📊 Results:");
            for (int i = 0; i < futures.size(); i++) {
                try {
                    String result = futures.get(i).get();
                    logTime("   Operation-" + (i + 1) + ": " + result);
                } catch (Exception e) {
                    logTime("   Operation-" + (i + 1) + ": Exception caught - " + e.getMessage());
                }
            }

            logTime("💡 Other operations continued despite one failing");
        }
    }

    // Demo 5: CPU-Bound vs I/O-Bound Work
    private static void demo5CPUvsIO() throws InterruptedException {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("Demo 5: Virtual Threads Best Use Cases");
        System.out.println("=".repeat(80));

        logTime("\n🧮 CPU-bound work (computing fibonacci):");
        Instant start = Instant.now();

        Thread cpuThread = Thread.startVirtualThread(() -> {
            logTime("🔢 Computing fibonacci(40)...");
            long result = fibonacci(40);
            logTime("✅ Fibonacci(40) = " + result);
        });
        cpuThread.join();

        Duration cpuDuration = Duration.between(start, Instant.now());
        logTime("⏱️  CPU-bound time: " + cpuDuration.toMillis() + "ms");

        // I/O-bound work
        logTime("\n📡 I/O-bound work (10 concurrent HTTP-like requests):");
        start = Instant.now();

        List<Thread> ioThreads = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            final int id = i;
            Thread thread = Thread.startVirtualThread(() -> {
                try {
                    Thread.sleep(500); // Simulate I/O wait
                    if (id == 0 || id == 9) {
                        logTime("✅ Request " + id + " completed");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            ioThreads.add(thread);
        }

        for (Thread thread : ioThreads) {
            thread.join();
        }

        Duration ioDuration = Duration.between(start, Instant.now());
        logTime("⏱️  I/O-bound time: " + ioDuration.toMillis() + "ms");
        logTime("💡 Virtual threads excel at I/O-bound work (network, database, files)");
    }

    // Helper: Fibonacci (CPU-intensive)
    private static long fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    // Main method
    public static void main(String[] args) {
        try {
            System.out.println("\n╔═══════════════════════════════════════════════════════════════════════════╗");
            System.out.println("║         Java Virtual Threads: Project Loom Demonstration                 ║");
            System.out.println("╔═══════════════════════════════════════════════════════════════════════════╗");

            demo1TraditionalVsVirtual();
            demo2Scalability();
            demo3StructuredConcurrency();
            demo4ErrorHandling();
            demo5CPUvsIO();

            System.out.println("\n" + "=".repeat(80));
            System.out.println("✅ All demonstrations completed!");
            System.out.println("=".repeat(80));
            System.out.println("\n🎯 Key Takeaways:");
            System.out.println("   1. Virtual threads are lightweight (millions possible)");
            System.out.println("   2. Created easily with Thread.startVirtualThread()");
            System.out.println("   3. Use ExecutorService for structured concurrency");
            System.out.println("   4. Perfect for I/O-bound operations");
            System.out.println("   5. Not a replacement for traditional threads in all cases");
            System.out.println();

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
