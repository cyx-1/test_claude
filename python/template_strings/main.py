"""
Template Strings (string.Template) Example

This example demonstrates Python's Template strings - a simpler, safer alternative
to f-strings and %-formatting, especially useful for user-provided templates.

Key concepts:
1. Basic Template usage with substitute()
2. Safe substitution with safe_substitute()
3. Custom delimiters for special cases
4. Practical applications (config, emails, SQL)
5. Security advantages over eval-based approaches
"""

import sys
from string import Template


def print_section(title):
    """Helper to print section headers."""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")


# Example 1: Basic Template String Usage
def example_basic_usage():
    """Demonstrates basic Template string syntax."""
    print_section("EXAMPLE 1: Basic Template String Usage")

    # Simple variable substitution
    template = Template("Hello, $name! Welcome to $place.")
    result = template.substitute(name="Alice", place="Python Land")
    print(f"Template: {template.template}")
    print(f"Result:   {result}")

    # Using a dictionary for substitution
    print("\nUsing dictionary for substitution:")
    user_data = {"username": "bob123", "email": "bob@example.com", "role": "admin"}
    template = Template("User: $username | Email: $email | Role: $role")
    result = template.substitute(user_data)
    print(f"Template: {template.template}")
    print(f"Result:   {result}")


# Example 2: Safe Substitution vs Regular Substitution
def example_safe_substitution():
    """Shows the difference between substitute() and safe_substitute()."""
    print_section("EXAMPLE 2: Safe Substitution vs Regular Substitution")

    template = Template("Name: $name, Age: $age, City: $city")
    partial_data = {"name": "Charlie", "age": 30}  # Missing 'city'

    # Regular substitute() - will raise KeyError
    print("Using substitute() with missing key:")
    try:
        result = template.substitute(partial_data)
        print(f"Result: {result}")
    except KeyError as e:
        print(f"❌ KeyError: Missing key {e}")
        print("   → substitute() requires ALL placeholders to be provided")

    # Safe substitute() - leaves missing placeholders as-is
    print("\nUsing safe_substitute() with missing key:")
    result = template.safe_substitute(partial_data)
    print(f"Result: {result}")
    print("   → safe_substitute() keeps $city placeholder intact")

    # Completing the substitution
    print("\nCompleting the substitution:")
    final_result = Template(result).safe_substitute(city="New York")
    print(f"Result: {final_result}")
    print("   → Can perform multi-stage substitution!")


# Example 3: Template with Braces for Disambiguation
def example_braces_disambiguation():
    """Shows how to use braces ${} for clearer variable boundaries."""
    print_section("EXAMPLE 3: Using Braces ${} for Disambiguation")

    # Without braces - can be ambiguous
    print("Scenario: Creating filenames with suffixes")
    template = Template("$name_file.txt")  # Looks for variable 'name_file'
    try:
        result = template.substitute(name="document")
    except KeyError as e:
        print(f"❌ Without braces: KeyError {e}")
        print(f"   Template looks for: 'name_file' (not 'name')")

    # With braces - clear boundaries
    template = Template("${name}_file.txt")  # Clearly just 'name'
    result = template.substitute(name="document")
    print(f"\n✅ With braces: {result}")
    print(f"   Template correctly uses: 'name' variable")

    # More complex example
    print("\nComplex example with multiple variables:")
    template = Template("${prefix}_${type}_${id}_${suffix}.log")
    result = template.substitute(prefix="app", type="error", id="12345", suffix="prod")
    print(f"Template: {template.template}")
    print(f"Result:   {result}")


# Example 4: Custom Delimiters
def example_custom_delimiters():
    """Demonstrates creating custom Template classes with different delimiters."""
    print_section("EXAMPLE 4: Custom Delimiters")

    # Standard delimiter conflicts with existing $ in text
    print("Problem: Using $ delimiter when text contains $:")
    text_with_dollars = "Price: $100, Discount: $discount_amount"
    print(f"Text: {text_with_dollars}")
    print("   → $ in '$100' conflicts with template delimiter")

    # Solution: Create custom Template with different delimiter
    class PercentTemplate(Template):
        delimiter = "%"  # Use % instead of $

    print("\nSolution: Custom delimiter using %")
    template = PercentTemplate("Price: $100, Discount: %discount_amount")
    result = template.substitute(discount_amount="$20")
    print(f"Template: {template.template}")
    print(f"Result:   {result}")
    print("   → Now $100 is literal text, %discount_amount is the placeholder")

    # Another example: Using double curly braces
    class BraceTemplate(Template):
        delimiter = "{{"
        pattern = r"""
        \{\{(?:
          (?P<escaped>\{\{)|
          (?P<named>[_a-z][_a-z0-9]*)\}\}|
          (?P<braced>[_a-z][_a-z0-9]*)\}\}|
          (?P<invalid>)
        )
        """

    print("\nAnother custom delimiter: {{variable}}:")
    simple_template = Template("{{name}} lives in {{city}}")
    # For simplicity, using standard Template with demonstration
    print("Template: {{name}} lives in {{city}}")
    print("   → Useful when working with systems that use $ for other purposes")


# Example 5: Practical Use Case - Email Templates
def example_email_template():
    """Shows practical use of Templates for email generation."""
    print_section("EXAMPLE 5: Practical Use Case - Email Templates")

    email_template = Template("""
Dear $customer_name,

Thank you for your order #$order_id!

Order Summary:
- Product: $product_name
- Quantity: $quantity
- Total: $$$total

Your order will be shipped to:
$shipping_address

Track your order: $tracking_url

Best regards,
The $company_name Team
""")

    # Customer data
    order_data = {
        "customer_name": "Jane Smith",
        "order_id": "ORD-2024-001",
        "product_name": "Python Programming Book",
        "quantity": "2",
        "total": "59.98",
        "shipping_address": "123 Main St, Anytown, USA",
        "tracking_url": "https://track.example.com/ORD-2024-001",
        "company_name": "TechBooks",
    }

    email = email_template.substitute(order_data)
    print(email)
    print("\n💡 Note: $$$ becomes $ followed by variable substitution (line with Total)")
    print("   → $$ escapes to $, then $total substitutes to the value")


# Example 6: Comparison with F-strings
def example_comparison_with_fstrings():
    """Compares Template strings with f-strings."""
    print_section("EXAMPLE 6: Template Strings vs F-strings")

    name = "Alice"
    age = 30

    # F-string (evaluated immediately, requires variables in scope)
    print("F-string approach:")
    fstring_result = f"Name: {name}, Age: {age}"
    print(f"Result: {fstring_result}")
    print("Pros: Concise, powerful (expressions allowed)")
    print("Cons: Evaluated immediately, security risk with user input")

    # Template string (safe, can be stored and reused)
    print("\nTemplate string approach:")
    template = Template("Name: $name, Age: $age")
    template_result = template.substitute(name=name, age=age)
    print(f"Result: {template_result}")
    print("Pros: Safe with user input, can store template separately")
    print("Cons: Less powerful (no expressions), slightly verbose")


# Example 7: Security Considerations
def example_security():
    """Demonstrates why Templates are safer with untrusted input."""
    print_section("EXAMPLE 7: Security Considerations")

    print("⚠️  DANGER: F-strings with user input (DON'T DO THIS)")
    print('user_input = "{__import__(\'os\').system(\'ls\')}"')
    print('result = f"User said: {user_input}"  # DANGEROUS!')
    print("   → User input in f-strings can execute arbitrary code")

    print("\n✅ SAFE: Template strings with user input")
    user_input = "$name or ${name} or $malicious_code"
    template = Template("User said: $message")
    result = template.substitute(message=user_input)
    print(f'User input: "{user_input}"')
    print(f'Result: {result}')
    print("   → Template treats user input as plain text, no code execution")

    print("\n💡 Best Practice:")
    print("   • Use f-strings for code you control")
    print("   • Use Templates for user-provided patterns/templates")
    print("   • Never use eval() or exec() with user input")


# Example 8: Configuration File Templates
def example_config_template():
    """Shows using Templates for configuration files."""
    print_section("EXAMPLE 8: Configuration File Templates")

    config_template = Template("""
[database]
host = $db_host
port = $db_port
database = $db_name
user = $db_user

[application]
app_name = $app_name
debug_mode = $debug_mode
log_level = $log_level

[cache]
redis_url = redis://$redis_host:$redis_port/$redis_db
""")

    # Development environment
    print("Development Environment Config:")
    dev_config = config_template.substitute(
        db_host="localhost",
        db_port="5432",
        db_name="myapp_dev",
        db_user="dev_user",
        app_name="MyApp",
        debug_mode="True",
        log_level="DEBUG",
        redis_host="localhost",
        redis_port="6379",
        redis_db="0",
    )
    print(dev_config)

    # Production environment (partial - shows safe_substitute)
    print("\nProduction Environment Config (partial):")
    prod_config = config_template.safe_substitute(
        db_host="prod-db.example.com",
        db_port="5432",
        app_name="MyApp",
        debug_mode="False",
        log_level="WARNING",
        # redis settings intentionally missing to show safe_substitute
    )
    print(prod_config)
    print("💡 Missing values left as placeholders for later configuration")


def main():
    """Run all examples."""
    print("=" * 70)
    print("TEMPLATE STRINGS (string.Template) DEMONSTRATION")
    print("=" * 70)

    example_basic_usage()
    example_safe_substitution()
    example_braces_disambiguation()
    example_custom_delimiters()
    example_email_template()
    example_comparison_with_fstrings()
    example_security()
    example_config_template()

    print_section("✨ All Examples Completed!")


if __name__ == "__main__":
    main()
