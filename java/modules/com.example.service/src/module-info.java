/**
 * Service module demonstrating module requirements and qualified exports.
 */
module com.example.service {
    // Line 5: Require (import) the core module
    requires com.example.core;

    // Line 8: Export service package to all modules
    exports com.example.service;

    // Line 11: Demonstrate transitive requires
    // (Any module that requires com.example.service also gets com.example.core)
    // We use non-transitive here to show explicit requires
}
