/**
 * Core module demonstrating module exports.
 * This module provides utility classes to other modules.
 */
module com.example.core {
    // Line 6: Export the util package to all modules
    exports com.example.core.util;

    // Line 9: Export model package only to specific modules (qualified export)
    exports com.example.core.model to com.example.service, com.example.app;

    // Note: Internal packages (not exported) remain encapsulated
}
