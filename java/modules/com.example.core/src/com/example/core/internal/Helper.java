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
