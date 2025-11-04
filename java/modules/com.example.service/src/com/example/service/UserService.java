package com.example.service;

// Line 3: Import from com.example.core module
import com.example.core.util.Logger;
import com.example.core.model.User;

/**
 * Service class demonstrating module imports and usage
 */
public class UserService {
    // Line 12: Use imported classes from com.example.core
    public static User createUser(String name, String email) {
        Logger.log("🔧 UserService.createUser() called");
        Logger.log("   ├─ Creating user: " + name);
        Logger.log("   └─ Email: " + email);

        // Line 18: Instantiate User from com.example.core.model
        User user = new User(name, email);

        Logger.log("✅ User created successfully");
        return user;
    }

    // Line 25: Method demonstrating module access
    public static void demonstrateModuleAccess() {
        Logger.log("\n🔍 Module Access Demonstration:");
        Logger.log("✅ Can access: com.example.core.util (exported to ALL)");
        Logger.log("✅ Can access: com.example.core.model (exported to com.example.service)");
        Logger.log("❌ Cannot access: com.example.core.internal (NOT exported)");

        // Line 32: This would cause compilation error:
        // com.example.core.internal.Helper.getInternalData();
        // Error: package com.example.core.internal is not visible
    }
}
