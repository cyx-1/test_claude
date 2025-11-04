/**
 * Application module - the main entry point.
 * Demonstrates requires statements for module dependencies.
 */
module com.example.app {
    // Line 6: Require both core and service modules
    requires com.example.core;
    requires com.example.service;

    // Line 10: No exports needed - this is the application entry point
    // Note: Main class doesn't need to be exported
}
