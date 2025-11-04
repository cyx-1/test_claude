package com.example.core.util;

/**
 * Public utility class - exported to all modules
 */
public class Logger {
    private static int callCount = 0;

    // Line 9: Public method accessible to all modules that require com.example.core
    public static void log(String message) {
        callCount++;
        System.out.printf("[%03d] %s%n", callCount, message);
    }

    // Line 15: Public method showing module info
    public static void logModuleInfo(String moduleName) {
        log("📦 Module: " + moduleName);
        log("   ├─ Accessing: com.example.core.util.Logger");
        log("   └─ Status: ✅ Access granted (exported to ALL)");
    }
}
