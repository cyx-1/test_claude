package com.example.app;

// Line 3-5: Import from different modules
import com.example.core.util.Logger;
import com.example.service.UserService;
import com.example.core.model.User;

/**
 * Main application demonstrating Java Module System (JPMS)
 * Shows module dependencies and import declarations
 */
public class Main {
    public static void main(String[] args) {
        // Line 15: Print header
        Logger.log("╔════════════════════════════════════════════════════════╗");
        Logger.log("║  Java Module System (JPMS) - Import Declaration Demo  ║");
        Logger.log("╚════════════════════════════════════════════════════════╝");

        // Line 20: Show module info
        Logger.logModuleInfo("com.example.app");
        System.out.println();

        // Line 24: Demonstrate module graph
        demonstrateModuleGraph();
        System.out.println();

        // Line 28: Demonstrate qualified exports
        demonstrateQualifiedExports();
        System.out.println();

        // Line 32: Create users using service
        Logger.log("🚀 Creating users via UserService:");
        User user1 = UserService.createUser("Alice Johnson", "alice@example.com");
        User user2 = UserService.createUser("Bob Smith", "bob@example.com");
        System.out.println();

        // Line 38: Display users
        Logger.log("👥 Created Users:");
        Logger.log("   • " + user1);
        Logger.log("   • " + user2);
        System.out.println();

        // Line 44: Demonstrate module access
        UserService.demonstrateModuleAccess();
    }

    // Line 48: Method to demonstrate module graph
    private static void demonstrateModuleGraph() {
        Logger.log("📊 Module Dependency Graph:");
        Logger.log("   com.example.app");
        Logger.log("   ├── requires com.example.core");
        Logger.log("   │   ├── exports com.example.core.util → ALL");
        Logger.log("   │   ├── exports com.example.core.model → com.example.service");
        Logger.log("   │   └── (encapsulates com.example.core.internal)");
        Logger.log("   └── requires com.example.service");
        Logger.log("       ├── requires com.example.core");
        Logger.log("       └── exports com.example.service → ALL");
    }

    // Line 62: Method to demonstrate qualified exports
    private static void demonstrateQualifiedExports() {
        Logger.log("🔐 Qualified Exports Demonstration:");
        Logger.log("   ┌─ com.example.core.model.User");
        Logger.log("   ├─ Exported to: com.example.service ✅");
        Logger.log("   ├─ Why app can use it: app requires both modules");
        Logger.log("   └─ Benefit: Controlled API exposure");
    }
}
