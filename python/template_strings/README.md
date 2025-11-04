# Template Strings (string.Template) Example

This example demonstrates Python's `string.Template` class - a simpler, safer alternative to f-strings and %-formatting, especially useful for user-provided templates and configuration.

## Key Concepts Illustrated

1. **Basic Template Usage** - Simple variable substitution with `$` placeholders
2. **Safe Substitution** - Handling missing variables gracefully
3. **Braces for Disambiguation** - Using `${var}` for clearer variable boundaries
4. **Custom Delimiters** - Creating templates with different placeholder syntax
5. **Practical Applications** - Email templates, configuration files
6. **Security Advantages** - Why Templates are safer than f-strings with user input

## Running the Example

```bash
uv run python main.py
```

## Source Code and Output Analysis

### 1. Basic Template String Usage

**Source Code (main.py:25-27):**
```python
template = Template("Hello, $name! Welcome to $place.")
result = template.substitute(name="Alice", place="Python Land")
print(f"Result:   {result}")
```

**Output:**
```
Template: Hello, $name! Welcome to $place.
Result:   Hello, Alice! Welcome to Python Land.
```

**💡 Key Insight:**
- **Line 25:** Create a Template with `$variable` placeholders
- **Line 26:** Call `.substitute()` with keyword arguments or a dictionary
- **Simple syntax:** Just use `$name` - no braces or formatting specifiers needed

---

### 2. Safe Substitution vs Regular Substitution

**Source Code (main.py:45-53):**
```python
template = Template("Name: $name, Age: $age, City: $city")
partial_data = {"name": "Charlie", "age": 30}  # Missing 'city'

# Regular substitute() - will raise KeyError
try:
    result = template.substitute(partial_data)    # Line 49: Missing 'city' key
except KeyError as e:
    print(f"❌ KeyError: Missing key {e}")

# Safe substitute() - leaves missing placeholders as-is
result = template.safe_substitute(partial_data)   # Line 53: Works!
```

**Output:**
```
Using substitute() with missing key:
❌ KeyError: Missing key 'city'                   ← Line 49: substitute() is strict
   → substitute() requires ALL placeholders to be provided

Using safe_substitute() with missing key:
Result: Name: Charlie, Age: 30, City: $city      ← Line 53: $city left as-is
   → safe_substitute() keeps $city placeholder intact
```

**💡 Key Insight:**
- **`substitute()`** - Strict: raises `KeyError` if any placeholder is missing
- **`safe_substitute()`** - Lenient: leaves missing placeholders intact
- **Use case:** `safe_substitute()` enables multi-stage template processing

---

### 3. Using Braces ${} for Disambiguation

**Source Code (main.py:63-73):**
```python
# Without braces - ambiguous
template = Template("$name_file.txt")              # Line 63: Looks for 'name_file'
try:
    result = template.substitute(name="document")  # Line 65: KeyError!
except KeyError as e:
    print(f"❌ Without braces: KeyError {e}")

# With braces - clear boundaries
template = Template("${name}_file.txt")            # Line 70: Clearly just 'name'
result = template.substitute(name="document")      # Line 71: Works!
```

**Output:**
```
Scenario: Creating filenames with suffixes
❌ Without braces: KeyError 'name_file'            ← Line 65: Template looks for wrong variable
   Template looks for: 'name_file' (not 'name')

✅ With braces: document_file.txt                  ← Line 71: Correct result
   Template correctly uses: 'name' variable
```

**Complex Example (main.py:75-77):**
```python
template = Template("${prefix}_${type}_${id}_${suffix}.log")  # Line 75
result = template.substitute(prefix="app", type="error",
                             id="12345", suffix="prod")        # Line 76
```

**Output:**
```
Template: ${prefix}_${type}_${id}_${suffix}.log
Result:   app_error_12345_prod.log                ← Line 77: All variables clearly delimited
```

**💡 Key Insight:**
- **`$name_file`** - Python looks for variable named "name_file"
- **`${name}_file`** - Python looks for variable "name", then adds "_file" as literal text
- **Best practice:** Use `${var}` when followed by alphanumeric characters or underscores

---

### 4. Custom Delimiters

**Source Code (main.py:106-114):**
```python
# Problem: $ conflicts with dollar amounts
text_with_dollars = "Price: $100, Discount: $discount_amount"  # Line 106

# Solution: Custom delimiter
class PercentTemplate(Template):
    delimiter = "%"                                             # Line 110: Use % instead

template = PercentTemplate("Price: $100, Discount: %discount_amount")  # Line 113
result = template.substitute(discount_amount="$20")                    # Line 114
```

**Output:**
```
Problem: Using $ delimiter when text contains $:
Text: Price: $100, Discount: $discount_amount
   → $ in '$100' conflicts with template delimiter

Solution: Custom delimiter using %
Template: Price: $100, Discount: %discount_amount
Result:   Price: $100, Discount: $20               ← Line 114: $100 is literal, %discount_amount substituted
   → Now $100 is literal text, %discount_amount is the placeholder
```

**💡 Key Insight:**
- **Default:** `$` delimiter works for most cases
- **Custom delimiters:** Useful when your content contains literal `$` symbols
- **Implementation:** Override the `delimiter` class attribute
- **Common alternatives:** `%`, `{{}}`, `@@`, etc.

---

### 5. Practical Use Case - Email Templates

**Source Code (main.py:150-168):**
```python
email_template = Template("""
Dear $customer_name,

Thank you for your order #$order_id!

Order Summary:
- Product: $product_name
- Quantity: $quantity
- Total: $$$total                                   # Line 158: $$$ for $+variable

Your order will be shipped to:
$shipping_address

Track your order: $tracking_url
""")

email = email_template.substitute(order_data)       # Line 181
```

**Output:**
```
Dear Jane Smith,

Thank you for your order #ORD-2024-001!

Order Summary:
- Product: Python Programming Book
- Quantity: 2
- Total: $59.98                                      ← Line 158: $$$ → $ + 59.98

Your order will be shipped to:
123 Main St, Anytown, USA

Track your order: https://track.example.com/ORD-2024-001

Best regards,
The TechBooks Team
```

**💡 Key Insight:**
- **`$$$total`** - First `$$` escapes to `$`, then `$total` substitutes to value
- **Separation of concerns:** Template definition separate from data
- **Reusability:** Same template works for all orders
- **Maintainability:** Non-programmers can edit template files

---

### 6. Template Strings vs F-strings

**Source Code (main.py:195-209):**
```python
# F-string (evaluated immediately)
fstring_result = f"Name: {name}, Age: {age}"        # Line 196: Requires variables in scope

# Template string (safe, reusable)
template = Template("Name: $name, Age: $age")       # Line 201: Can store separately
template_result = template.substitute(name=name, age=age)  # Line 202: Evaluate later
```

**Output:**
```
F-string approach:
Result: Name: Alice, Age: 30
Pros: Concise, powerful (expressions allowed)
Cons: Evaluated immediately, security risk with user input

Template string approach:
Result: Name: Alice, Age: 30
Pros: Safe with user input, can store template separately
Cons: Less powerful (no expressions), slightly verbose
```

**💡 Key Insight:**

| Feature | F-strings | Template Strings |
|---------|-----------|------------------|
| **Syntax** | `f"{var}"` | `Template("$var")` |
| **When evaluated** | Immediately | When `.substitute()` called |
| **Expressions** | ✅ Yes | ❌ No (simple substitution only) |
| **User input safety** | ❌ Dangerous | ✅ Safe |
| **Storage** | ❌ Hard to store | ✅ Easy (just a string) |
| **Best for** | Developer code | User-provided templates |

---

### 7. Security Considerations

**Source Code (main.py:219-231):**
```python
print("⚠️  DANGER: F-strings with user input (DON'T DO THIS)")
print('user_input = "{__import__(\'os\').system(\'ls\')}"')
print('result = f"User said: {user_input}"  # DANGEROUS!')   # Line 221

print("\n✅ SAFE: Template strings with user input")
user_input = "$name or ${name} or $malicious_code"
template = Template("User said: $message")                   # Line 226
result = template.substitute(message=user_input)             # Line 227
```

**Output:**
```
⚠️  DANGER: F-strings with user input (DON'T DO THIS)
user_input = "{__import__('os').system('ls')}"
result = f"User said: {user_input}"  # DANGEROUS!
   → User input in f-strings can execute arbitrary code

✅ SAFE: Template strings with user input
User input: "$name or ${name} or $malicious_code"
Result: User said: $name or ${name} or $malicious_code      ← Line 227: Treated as plain text
   → Template treats user input as plain text, no code execution
```

**💡 Key Insight:**
- **F-strings are dangerous** with user input - they can evaluate arbitrary expressions
- **Templates are safe** - user input is always treated as plain text
- **Best practice:**
  - ✅ Use f-strings for code you control
  - ✅ Use Templates for user-provided patterns/templates
  - ❌ Never use `eval()` or `exec()` with user input

---

### 8. Configuration File Templates

**Source Code (main.py:242-275):**
```python
config_template = Template("""
[database]
host = $db_host
port = $db_port
database = $db_name

[application]
app_name = $app_name
debug_mode = $debug_mode
log_level = $log_level
""")

# Production environment (partial - shows safe_substitute)
prod_config = config_template.safe_substitute(              # Line 267
    db_host="prod-db.example.com",
    db_port="5432",
    app_name="MyApp",
    debug_mode="False",
    log_level="WARNING",
    # redis settings intentionally missing
)
```

**Output:**
```
Development Environment Config:

[database]
host = localhost
port = 5432
database = myapp_dev

[application]
app_name = MyApp
debug_mode = True
log_level = DEBUG


Production Environment Config (partial):

[database]
host = prod-db.example.com
port = 5432
database = $db_name                                  ← Line 267: Missing values preserved
user = $db_user

[application]
app_name = MyApp
debug_mode = False
log_level = WARNING

[cache]
redis_url = redis://$redis_host:$redis_port/$redis_db
```

**💡 Key Insight:**
- **Single template** for all environments
- **`safe_substitute()`** allows partial configuration
- **Missing values** remain as placeholders for later completion
- **Use cases:**
  - Configuration management
  - Docker/Kubernetes templates
  - CI/CD pipeline configurations
  - Multi-stage deployments

---

## Comparison Table

| Method | Syntax | Evaluation | Safety | Storage | Use Case |
|--------|--------|------------|--------|---------|----------|
| **F-strings** | `f"{var}"` | Immediate | ❌ Unsafe with user input | Hard | Developer code |
| **%-formatting** | `"%s" % var` | On demand | ⚠️ Some risks | Medium | Legacy code |
| **str.format()** | `"{}".format(var)` | On demand | ⚠️ Some risks | Easy | General purpose |
| **Template** | `Template("$var")` | On demand | ✅ Safe | Very easy | User templates |

## Key Takeaways

1. **`Template("$var")`** - Simple, safe string substitution
2. **`.substitute()`** - Strict substitution (all placeholders required)
3. **`.safe_substitute()`** - Lenient substitution (missing values OK)
4. **`${var}`** - Use braces when followed by alphanumeric/underscore
5. **`$$`** - Escape sequence for literal `$` character
6. **Custom delimiters** - Override `delimiter` attribute for special cases
7. **Security** - Templates are safe with user input (unlike f-strings)

## When to Use Template Strings

✅ **Good for:**
- User-provided template patterns
- Configuration file generation
- Email/message templates
- SQL query templates (with parameter binding)
- Multi-stage template processing
- Any scenario where template is stored separately from data

❌ **Not ideal for:**
- Simple string formatting in your own code (use f-strings)
- Complex expressions or calculations (use f-strings)
- Performance-critical code (f-strings are faster)
- When you need format specifiers (use f-strings or .format())

## Security Best Practices

1. **User input:** Always use Template strings, never f-strings
2. **SQL queries:** Use Templates + parameterized queries, never string concatenation
3. **Shell commands:** Use Templates + proper escaping/sanitization
4. **File paths:** Use Templates with path validation
5. **Configuration:** Use Templates with safe_substitute() for partial configs

## Related Documentation

- Python docs: [`string.Template`](https://docs.python.org/3/library/string.html#template-strings)
- PEP 292: [Simpler String Substitutions](https://www.python.org/dev/peps/pep-0292/)
- Security: [Common injection vulnerabilities](https://owasp.org/www-community/attacks/Code_Injection)
