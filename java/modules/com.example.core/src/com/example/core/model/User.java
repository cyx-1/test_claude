package com.example.core.model;

/**
 * Model class - exported only to specific modules (com.example.service)
 */
public class User {
    private final String name;
    private final String email;

    // Line 10: Constructor
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    // Line 16: Getters
    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    @Override
    public String toString() {
        return String.format("User{name='%s', email='%s'}", name, email);
    }
}
