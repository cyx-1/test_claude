# Java Module System (JPMS): Module Import Declarations

This example demonstrates the **Java Platform Module System (JPMS)**, introduced in Java 9, which revolutionized how Java applications organize and access code through explicit module declarations and import statements.

## Key Concepts Illustrated

1. **Module Declarations** - Using `module-info.java` to define modules
2. **Module Dependencies** - Using `requires` to import modules
3. **Package Exports** - Using `exports` to expose APIs
4. **Qualified Exports** - Exporting to specific modules only
5. **Strong Encapsulation** - Hiding internal implementation details

## Project Structure

```
java/modules/
├── com.example.core/          # Core utilities module
│   └── src/
│       ├── module-info.java   # Module declaration
│       └── com/example/core/
│           ├── util/          # Public API (exported to ALL)
│           ├── model/         # Qualified export (to specific modules)
│           └── internal/      # Encapsulated (NOT exported)
│
├── com.example.service/       # Service layer module
│   └── src/
│       ├── module-info.java   # Requires com.example.core
│       └── com/example/service/
│
└── com.example.app/           # Application module
    └── src/
        ├── module-info.java   # Requires core + service
        └── com/example/app/
```

## Running the Example

```bash
cd java/modules

# Build all modules
./build.sh

# Run the application
./run.sh

# Clean compiled files
./clean.sh
```

## Source Code and Output Analysis

### 1. Module Declaration with Exports

**Source Code (com.example.core/src/module-info.java:1-13):**
```java
/**
 * Core module demonstrating module exports.
 */
module com.example.core {
    // Line 6: Export the util package to all modules
    exports com.example.core.util;

    // Line 9: Export model package only to specific modules (qualified export)
    exports com.example.core.model to com.example.service, com.example.app;

    // Note: Internal packages (not exported) remain encapsulated
}
```

**💡 Key Insight:**
- **Line 6:** `exports com.example.core.util` makes this package accessible to ALL modules that require com.example.core
- **Line 10:** `exports ... to ...` is a **qualified export** - only specified modules can access it
- **Unlisted packages** (like `com.example.core.internal`) are completely hidden from other modules

---

### 2. Module Dependencies with Requires

**Source Code (com.example.service/src/module-info.java:1-14):**
```java
/**
 * Service module demonstrating module requirements.
 */
module com.example.service {
    // Line 5: Require (import) the core module
    requires com.example.core;

    // Line 8: Export service package to all modules
    exports com.example.service;
}
```

**Source Code (com.example.app/src/module-info.java:1-12):**
```java
/**
 * Application module - the main entry point.
 */
module com.example.app {
    // Line 6: Require both core and service modules
    requires com.example.core;
    requires com.example.service;

    // Line 10: No exports needed - this is the application entry point
}
```

**💡 Key Insight:**
- **Line 5 (service):** `requires com.example.core` creates a module dependency
- **Line 6-7 (app):** Multiple `requires` statements create the module graph
- **Compilation order:** Core → Service → App (based on dependencies)

---

### 3. Using Imported Modules and Packages

**Source Code (com.example.app/src/com/example/app/Main.java:3-6):**
```java
// Line 3-5: Import from different modules
import com.example.core.util.Logger;
import com.example.service.UserService;
import com.example.core.model.User;
```

**Output:**
```
[001] ╔════════════════════════════════════════════════════════╗
[002] ║  Java Module System (JPMS) - Import Declaration Demo  ║
[003] ╚════════════════════════════════════════════════════════╝
[004] 📦 Module: com.example.app
[005]    ├─ Accessing: com.example.core.util.Logger
[006]    └─ Status: ✅ Access granted (exported to ALL)
```

**💡 Key Insight:**
- **Line 3:** Can import `Logger` because `com.example.core.util` is exported to ALL
- **Line 5:** Can import `User` because it's in the qualified export list
- **Module imports work** because of `requires` statements in module-info.java

---

### 4. Module Dependency Graph

**Source Code (com.example.app/src/com/example/app/Main.java:48-60):**
```java
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
```

**Output:**
```
[007] 📊 Module Dependency Graph:
[008]    com.example.app
[009]    ├── requires com.example.core
[010]    │   ├── exports com.example.core.util → ALL
[011]    │   ├── exports com.example.core.model → com.example.service
[012]    │   └── (encapsulates com.example.core.internal)
[013]    └── requires com.example.service
[014]        ├── requires com.example.core
[015]        └── exports com.example.service → ALL
```

**💡 Key Insight:**
- **Visual representation** of module dependencies
- **com.example.app** depends on both core and service
- **com.example.service** also depends on core
- **Transitive dependencies** are visible in the graph

---

### 5. Qualified Exports - Controlled API Exposure

**Source Code (com.example.app/src/com/example/app/Main.java:62-69):**
```java
// Line 62: Method to demonstrate qualified exports
private static void demonstrateQualifiedExports() {
    Logger.log("🔐 Qualified Exports Demonstration:");
    Logger.log("   ┌─ com.example.core.model.User");
    Logger.log("   ├─ Exported to: com.example.service ✅");
    Logger.log("   ├─ Why app can use it: app requires both modules");
    Logger.log("   └─ Benefit: Controlled API exposure");
}
```

**Output:**
```
[016] 🔐 Qualified Exports Demonstration:
[017]    ┌─ com.example.core.model.User
[018]    ├─ Exported to: com.example.service ✅
[019]    ├─ Why app can use it: app requires both modules
[020]    └─ Benefit: Controlled API exposure
```

**💡 Key Insight:**
- **Qualified exports** let you expose APIs to specific modules only
- **Fine-grained access control** at compile time
- **Better than classpath:** No accidental access to internal packages

---

### 6. Using Services from Different Modules

**Source Code (com.example.app/src/com/example/app/Main.java:32-36):**
```java
// Line 32: Create users using service
Logger.log("🚀 Creating users via UserService:");
User user1 = UserService.createUser("Alice Johnson", "alice@example.com");
User user2 = UserService.createUser("Bob Smith", "bob@example.com");
```

**Source Code (com.example.service/src/com/example/service/UserService.java:12-22):**
```java
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
```

**Output:**
```
[021] 🚀 Creating users via UserService:
[022] 🔧 UserService.createUser() called
[023]    ├─ Creating user: Alice Johnson
[024]    └─ Email: alice@example.com
[025] ✅ User created successfully
[026] 🔧 UserService.createUser() called
[027]    ├─ Creating user: Bob Smith
[028]    └─ Email: bob@example.com
[029] ✅ User created successfully

[030] 👥 Created Users:
[031]    • User{name='Alice Johnson', email='alice@example.com'}
[032]    • User{name='Bob Smith', email='bob@example.com'}
```

**💡 Key Insight:**
- **Main.java (Line 34):** App calls service from different module
- **UserService.java (Line 18):** Service uses model from core module
- **Cross-module communication** works seamlessly through explicit imports
- **Logger usage** shows all modules can access exported utilities

---

### 7. Strong Encapsulation - What You CANNOT Access

**Source Code (com.example.service/src/com/example/service/UserService.java:25-34):**
```java
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
```

**Output:**
```
[033] 🔍 Module Access Demonstration:
[034] ✅ Can access: com.example.core.util (exported to ALL)
[035] ✅ Can access: com.example.core.model (exported to com.example.service)
[036] ❌ Cannot access: com.example.core.internal (NOT exported)
```

**Internal Package (com.example.core/src/com/example/core/internal/Helper.java:1-11):**
```java
package com.example.core.internal;

/**
 * Internal helper class - NOT exported (encapsulated)
 * This class cannot be accessed by other modules
 */
public class Helper {
    // Line 8: This method is only accessible within com.example.core module
    public static String getInternalData() {
        return "This is internal data - cannot be accessed from other modules!";
    }
}
```

**💡 Key Insight:**
- **Line 32-33:** Attempting to use `com.example.core.internal` would fail at **compile time**
- **Strong encapsulation:** Even though Helper is `public`, it's in a non-exported package
- **Better than classpath:** On classpath, any public class could be accessed
- **Benefit:** True hiding of implementation details

---

## Compilation and Module Path

### Building Modules

**Source Code (build.sh:6-13):**
```bash
# Line 6: Compile core module
echo "📦 Compiling com.example.core..."
javac -d com.example.core/bin \
    com.example.core/src/module-info.java \
    com.example.core/src/com/example/core/util/Logger.java \
    com.example.core/src/com/example/core/model/User.java \
    com.example.core/src/com/example/core/internal/Helper.java
```

**Source Code (build.sh:15-20):**
```bash
# Line 15: Compile service module (requires core)
echo "📦 Compiling com.example.service..."
javac --module-path com.example.core/bin \
    -d com.example.service/bin \
    com.example.service/src/module-info.java \
    com.example.service/src/com/example/service/UserService.java
```

**💡 Key Insight:**
- **Line 8:** Core has no dependencies, compiles independently
- **Line 17:** Service compilation uses `--module-path` to find core module
- **Dependency order:** Must compile dependencies before dependents
- **Module path:** Replaces classpath for module-aware compilation

---

### Running Modular Applications

**Source Code (run.sh:4-9):**
```bash
# Line 4: Run the application with module path
echo "🚀 Running Java Module System Example..."
echo

java --module-path com.example.core/bin:com.example.service/bin:com.example.app/bin \
    --module com.example.app/com.example.app.Main
```

**💡 Key Insight:**
- **Line 8:** `--module-path` specifies where to find modules (colon-separated on Unix)
- **Line 9:** `--module <module>/<main-class>` specifies entry point
- **Module resolution:** JVM validates all module dependencies at startup
- **Fail fast:** Missing or incompatible modules are detected before execution

---

## Key Benefits of Java Module System

### 1. Strong Encapsulation
```
Before JPMS (Classpath):
  ✗ Any public class accessible from anywhere
  ✗ Internal APIs accidentally become public APIs
  ✗ No way to truly hide implementation

With JPMS (Module Path):
  ✓ Only exported packages accessible
  ✓ Internal packages truly hidden
  ✓ Compile-time enforcement
```

### 2. Explicit Dependencies
```
Before JPMS:
  ✗ Dependencies implicit (discovered at runtime)
  ✗ ClassNotFoundException at runtime
  ✗ Version conflicts hard to detect

With JPMS:
  ✓ Dependencies declared in module-info.java
  ✓ Missing dependencies caught at compile time
  ✓ Module graph validated at startup
```

### 3. Reliable Configuration
```
Before JPMS:
  ✗ Classpath hell (order matters, duplicates cause issues)
  ✗ Split packages (same package in multiple JARs)
  ✗ Circular dependencies hard to detect

With JPMS:
  ✓ Module path resolves modules reliably
  ✓ No split packages allowed
  ✓ Circular dependencies detected at compile time
```

---

## Module Declaration Syntax Reference

### Basic Module Declaration
```java
module module.name {
    // Module body
}
```

### Exports
```java
// Export to all modules
exports com.example.package;

// Qualified export (only to specific modules)
exports com.example.package to module1, module2;
```

### Requires
```java
// Regular dependency
requires module.name;

// Transitive dependency (re-exported)
requires transitive module.name;

// Static dependency (optional at runtime)
requires static module.name;
```

### Opens (for reflection)
```java
// Open package for reflection
opens com.example.package;

// Open only to specific modules
opens com.example.package to framework.module;
```

---

## Comparison: JPMS vs Traditional Classpath

| Feature | Classpath | Module Path (JPMS) |
|---------|-----------|-------------------|
| Encapsulation | `public` = accessible everywhere | Only exported packages accessible |
| Dependencies | Implicit, runtime discovery | Explicit in module-info.java |
| Validation | Runtime ClassNotFoundException | Compile-time + startup validation |
| Package splitting | Allowed (causes conflicts) | Forbidden (compile error) |
| Access control | Package-private, public | Module-level + qualified exports |
| Introduced | Java 1.0 (1996) | Java 9 (2017) |

---

## When to Use JPMS

✅ **Good for:**
- Large applications with multiple components
- Libraries that want to hide internal APIs
- Projects requiring strong API boundaries
- Microservices needing clear module boundaries

❌ **May skip for:**
- Small, simple applications
- Rapid prototyping
- Legacy codebases (migration can be complex)
- When using libraries without module support

---

## Common Module System Patterns

### 1. Layered Architecture
```
┌─────────────────┐
│  Presentation   │ (com.app.ui)
├─────────────────┤
│    Service      │ (com.app.service)
├─────────────────┤
│   Repository    │ (com.app.repository)
├─────────────────┤
│     Domain      │ (com.app.domain)
└─────────────────┘

Each layer = separate module with explicit dependencies
```

### 2. API/Implementation Separation
```
com.example.api (exports interfaces)
         ↑
         │ requires
         │
com.example.impl (hidden implementation)
```

### 3. Service Provider Interface (SPI)
```java
module api.module {
    exports com.example.api;
    uses com.example.api.Service;
}

module impl.module {
    requires api.module;
    provides com.example.api.Service
        with com.example.impl.ServiceImpl;
}
```

---

## Migration Path from Classpath to Modules

1. **Unnamed Module** - Legacy JARs run as unnamed module
2. **Automatic Module** - JAR with `Automatic-Module-Name` in MANIFEST.MF
3. **Named Module** - Full module with module-info.java
4. **Best Practice** - Migrate bottom-up (dependencies first)

---

## Key Takeaways

1. **module-info.java** - Heart of JPMS, declares module metadata
2. **exports** - Makes packages accessible to other modules
3. **requires** - Declares dependencies on other modules
4. **Qualified exports** - Fine-grained access control (exports to specific modules)
5. **Strong encapsulation** - Non-exported packages are truly hidden
6. **Compile-time safety** - Dependency validation before runtime
7. **Explicit is better** - No more classpath guessing games

## Further Reading

- [JEP 261: Module System](https://openjdk.java.net/jeps/261)
- [Java Module System (JPMS) Tutorial](https://www.oracle.com/corporate/features/understanding-java-9-modules.html)
- [Migration Guide](https://docs.oracle.com/javase/9/migrate/toc.htm)
