# Abstract Base Classes (ABC) Example

This example demonstrates Python's `abc` module for defining abstract base classes, which provide a way to define interfaces and enforce that derived classes implement particular methods.

## Key Concepts Illustrated

1. **Basic Abstract Methods** - Defining abstract methods that must be implemented
2. **Abstract Properties** - Using properties in abstract classes
3. **Abstract Class and Static Methods** - Class-level abstract methods
4. **Multiple Inheritance** - Implementing multiple abstract interfaces
5. **Type Safety** - Using ABCs for type checking and validation
6. **Cannot Instantiate** - Preventing instantiation of incomplete implementations

## Running the Example

```bash
uv run python main.py
```

## Source Code and Output Analysis

### 1. Basic Abstract Base Classes

**Source Code (main.py:25-49):**
```python
class Shape(ABC):
    """Abstract base class for geometric shapes."""

    def __init__(self, name):
        self.name = name

    @abstractmethod                        # Line 32: Abstract method decorator
    def area(self):
        """Calculate and return the area of the shape."""
        pass

    @abstractmethod                        # Line 37: Another abstract method
    def perimeter(self):
        """Calculate and return the perimeter of the shape."""
        pass

    def description(self):                 # Line 42: Concrete method
        """Concrete method available to all shapes."""
        return f"This is a {self.name}"
```

**Concrete Implementation (main.py:52-68):**
```python
class Rectangle(Shape):
    """Concrete implementation of Shape for rectangles."""

    def __init__(self, width, height):
        super().__init__("Rectangle")      # Line 56: Call parent constructor
        self.width = width
        self.height = height

    def area(self):                        # Line 60: Implement abstract method
        """Implements abstract method."""
        return self.width * self.height

    def perimeter(self):                   # Line 64: Implement abstract method
        """Implements abstract method."""
        return 2 * (self.width + self.height)
```

**Output:**
```
📐 Creating concrete shapes:
   Rectangle(5, 3) created                 ← Line 56: Rectangle initialized
   Circle(4) created

📏 Calculating areas and perimeters:
   Rectangle: area = 15, perimeter = 16   ← Lines 60, 64: Abstract methods called
   Circle: area = 50.27, perimeter = 25.13

📝 Using concrete method from abstract class:
   This is a Rectangle                     ← Line 42: Concrete method inherited
   This is a Circle

❌ Attempting to instantiate abstract class:
   TypeError: Can't instantiate abstract class Shape without an implementation
   for abstract methods 'area', 'perimeter'  ← Lines 32, 37: Missing implementations
   ✅ Cannot instantiate abstract class!
```

**💡 Key Insight:**
- **Line 32, 37:** `@abstractmethod` decorator marks methods that MUST be implemented by subclasses
- **Lines 60, 64:** Rectangle provides concrete implementations of abstract methods
- **Line 42:** Concrete methods in ABCs work normally and are inherited by all subclasses
- **Error message:** Python prevents instantiation of `Shape` directly since abstract methods aren't implemented

---

### 2. Abstract Properties

**Source Code (main.py:89-104):**
```python
class Vehicle(ABC):
    """Abstract base class demonstrating abstract properties."""

    def __init__(self, brand):
        self._brand = brand

    @property                              # Line 95: Property decorator
    @abstractmethod                        # Line 96: Abstract property!
    def max_speed(self):
        """Abstract property for maximum speed."""
        pass

    @property                              # Line 102: Concrete property
    def brand(self):
        """Concrete property."""
        return self._brand
```

**Concrete Implementation (main.py:113-127):**
```python
class Car(Vehicle):
    """Concrete implementation of Vehicle."""

    def __init__(self, brand, speed):
        super().__init__(brand)
        self._max_speed = speed

    @property                              # Line 120: Implement abstract property
    def max_speed(self):
        """Implements abstract property."""
        return self._max_speed

    def start_engine(self):                # Line 124: Implement abstract method
        """Implements abstract method."""
        return f"{self.brand} car engine started! 🚗"
```

**Output:**
```
🚗 Creating vehicles with abstract properties:
   Car: Tesla (max speed: 200 km/h)       ← Line 120: max_speed property accessed
   Motorcycle: Harley (max speed: 180 km/h)

🔑 Starting engines:
   Tesla car engine started! 🚗           ← Line 124: start_engine() called
   Harley motorcycle engine started! 🏍️

❌ Attempting to instantiate Vehicle without implementing properties:
   class IncompleteVehicle(Vehicle):
       def start_engine(self): return 'Started'
   # Missing max_speed property implementation!
   TypeError: Can't instantiate abstract class...  ← Line 96: max_speed not implemented
   ✅ Must implement all abstract properties!
```

**💡 Key Insight:**
- **Lines 95-96:** Combining `@property` and `@abstractmethod` creates an abstract property
- **Line 120:** Subclasses must implement the property with the `@property` decorator
- **Line 102:** Concrete properties work normally and don't need to be overridden
- **Error:** Python checks that ALL abstract properties are implemented before allowing instantiation

---

### 3. Abstract Class Methods and Static Methods

**Source Code (main.py:150-168):**
```python
class DataProcessor(ABC):
    """Abstract base class with class and static methods."""

    @classmethod                           # Line 153: Class method
    @abstractmethod                        # Line 154: Abstract class method
    def from_file(cls, filename):
        """Abstract class method to create instance from file."""
        pass

    @staticmethod                          # Line 159: Static method
    @abstractmethod                        # Line 160: Abstract static method
    def validate_data(data):
        """Abstract static method to validate data."""
        pass

    @abstractmethod                        # Line 165: Regular abstract method
    def process(self):
        """Abstract instance method to process data."""
        pass
```

**Concrete Implementation (main.py:171-189):**
```python
class JSONProcessor(DataProcessor):
    """Concrete implementation for JSON data processing."""

    def __init__(self, data):
        self.data = data

    @classmethod                           # Line 177: Implement abstract classmethod
    def from_file(cls, filename):
        """Implements abstract class method."""
        return cls(f"Data from {filename}.json")

    @staticmethod                          # Line 182: Implement abstract staticmethod
    def validate_data(data):
        """Implements abstract static method."""
        return isinstance(data, str) and len(data) > 0

    def process(self):                     # Line 187: Implement abstract method
        """Implements abstract instance method."""
        return f"Processing JSON: {self.data}"
```

**Output:**
```
📊 Using class method to create instance:
   Created: JSONProcessor                  ← Line 177: from_file() creates instance
   Data: Data from config.json            ← Line 180: Constructor called with data

✅ Validating data with static method:
   JSONProcessor.validate_data('sample data') = True   ← Line 182: Static method
   JSONProcessor.validate_data('') = False

⚙️  Processing data:
   Processing JSON: Data from config.json  ← Line 187: process() method
```

**💡 Key Insight:**
- **Lines 153-154:** `@classmethod` + `@abstractmethod` creates abstract class method
- **Lines 159-160:** `@staticmethod` + `@abstractmethod` creates abstract static method
- **Line 177:** Subclass implements abstract class method (receives `cls` as first parameter)
- **Line 182:** Subclass implements abstract static method (no `self` or `cls`)
- **Factory pattern:** Abstract class methods are perfect for factory methods like `from_file()`

---

### 4. Multiple Inheritance with ABCs

**Source Code (main.py:192-212):**
```python
class Drawable(ABC):
    """Abstract interface for drawable objects."""

    @abstractmethod
    def draw(self):
        """Draw the object."""
        pass


class Moveable(ABC):
    """Abstract interface for moveable objects."""

    @abstractmethod
    def move(self, x, y):
        """Move the object to new coordinates."""
        pass


class GameSprite(Drawable, Moveable):      # Line 209: Multiple inheritance
    """Concrete class implementing multiple abstract interfaces."""

    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0

    def draw(self):                        # Line 217: Implement Drawable
        """Implements Drawable.draw()."""
        return f"Drawing {self.name} at ({self.x}, {self.y})"

    def move(self, x, y):                  # Line 221: Implement Moveable
        """Implements Moveable.move()."""
        self.x = x
        self.y = y
        return f"Moved {self.name} to ({self.x}, {self.y})"
```

**Output:**
```
🎮 Creating game sprite with multiple abstract interfaces:
   Created: Player                         ← Line 209: Inherits from both ABCs

🎨 Using Drawable interface:
   Drawing Player at (0, 0)                ← Line 217: draw() implemented

🏃 Using Moveable interface:
   Moved Player to (10, 20)                ← Line 221: move() implemented
   Drawing Player at (10, 20)              ← Updated position

✅ GameSprite implements both Drawable and Moveable interfaces!
```

**💡 Key Insight:**
- **Line 209:** Python allows inheriting from multiple ABCs (multiple interfaces)
- **Lines 217, 221:** Must implement ALL abstract methods from ALL parent ABCs
- **Interface segregation:** Small, focused ABCs are better than large, monolithic ones
- **Duck typing meets contracts:** ABCs provide the structure while maintaining Python's flexibility

---

### 5. Type Checking with ABCs

**Source Code (main.py:315-331):**
```python
def demonstrate_isinstance_checks():
    """Demonstrates isinstance checks with ABCs."""
    section_header("EXAMPLE 5: Type Checking with ABCs")

    rect = Rectangle(5, 3)                 # Line 319: Create instances
    car = Car("Toyota", 180)
    sprite = GameSprite("Enemy")

    print("\n🔍 Checking isinstance with abstract base classes:")
    print(f"   isinstance(rect, Shape) = {isinstance(rect, Shape)}")        # Line 324
    print(f"   isinstance(rect, Rectangle) = {isinstance(rect, Rectangle)}")
    print(f"   isinstance(car, Vehicle) = {isinstance(car, Vehicle)}")      # Line 326
    print(f"   isinstance(car, Shape) = {isinstance(car, Shape)}")          # Line 327
```

**Output:**
```
🔍 Checking isinstance with abstract base classes:
   isinstance(rect, Shape) = True          ← Line 324: Rectangle IS a Shape
   isinstance(rect, Rectangle) = True
   isinstance(car, Vehicle) = True         ← Line 326: Car IS a Vehicle
   isinstance(car, Shape) = False          ← Line 327: Car is NOT a Shape

🔍 Checking multiple inheritance:
   isinstance(sprite, Drawable) = True     ← Sprite IS Drawable
   isinstance(sprite, Moveable) = True     ← Sprite IS Moveable
   isinstance(sprite, GameSprite) = True   ← Sprite IS GameSprite

✅ ABCs provide clear type hierarchies and contracts!
```

**💡 Key Insight:**
- **Line 324:** `isinstance()` works with ABCs just like regular classes
- **Line 327:** Type checking correctly identifies that `car` is NOT a `Shape`
- **Multiple inheritance:** Objects can be instances of multiple ABCs simultaneously
- **Runtime validation:** Use ABCs to validate objects implement required interfaces

---

### 6. Subclass Checking with ABCs

**Source Code (main.py:343-358):**
```python
def demonstrate_subclass_checks():
    """Demonstrates subclass checks with ABCs."""
    section_header("EXAMPLE 6: Subclass Checking with ABCs")

    print("\n🔍 Checking if classes are subclasses of ABCs:")
    print(f"   issubclass(Rectangle, Shape) = {issubclass(Rectangle, Shape)}")      # Line 348
    print(f"   issubclass(Circle, Shape) = {issubclass(Circle, Shape)}")
    print(f"   issubclass(Car, Vehicle) = {issubclass(Car, Vehicle)}")
    print(f"   issubclass(GameSprite, Drawable) = {issubclass(GameSprite, Drawable)}")  # Line 351
    print(f"   issubclass(GameSprite, Moveable) = {issubclass(GameSprite, Moveable)}")   # Line 352
```

**Output:**
```
🔍 Checking if classes are subclasses of ABCs:
   issubclass(Rectangle, Shape) = True     ← Line 348: Rectangle subclass of Shape
   issubclass(Circle, Shape) = True
   issubclass(Car, Vehicle) = True
   issubclass(GameSprite, Drawable) = True ← Line 351: GameSprite subclass of Drawable
   issubclass(GameSprite, Moveable) = True ← Line 352: GameSprite subclass of Moveable

✅ issubclass() works with abstract base classes!
```

**💡 Key Insight:**
- **Line 348:** `issubclass()` checks class relationships at the class level (not instance level)
- **Lines 351-352:** Works correctly with multiple inheritance
- **Design validation:** Use `issubclass()` in frameworks to validate plugin/extension classes
- **Static analysis:** Enables better type hints and IDE autocomplete

---

## Complete Example Overview

### Class Hierarchy Diagram

```
ABC (from abc module)
├── Shape (abstract)
│   ├── Rectangle (concrete)
│   └── Circle (concrete)
├── Vehicle (abstract)
│   ├── Car (concrete)
│   └── Motorcycle (concrete)
├── DataProcessor (abstract)
│   └── JSONProcessor (concrete)
├── Drawable (abstract)
│   └── GameSprite (concrete) ┐
└── Moveable (abstract)        │  Multiple
    └── GameSprite (concrete) ─┘  Inheritance
```

## Key Takeaways

1. **`@abstractmethod`** - Decorator to mark methods that must be implemented by subclasses
2. **Cannot instantiate** - Python prevents instantiation of classes with unimplemented abstract methods
3. **Abstract properties** - Combine `@property` and `@abstractmethod` for required properties
4. **Abstract class methods** - Use `@classmethod` + `@abstractmethod` for factory patterns
5. **Abstract static methods** - Use `@staticmethod` + `@abstractmethod` for utility validators
6. **Multiple inheritance** - Classes can implement multiple abstract interfaces
7. **Type checking** - Use `isinstance()` and `issubclass()` for runtime validation

## When to Use Abstract Base Classes

✅ **Good for:**
- Defining interfaces and contracts for plugin systems
- Ensuring subclasses implement required methods
- Creating framework base classes with optional hooks
- Documenting expected class structure
- Type checking and validation in libraries
- Multiple inheritance of behavior contracts

❌ **Not ideal for:**
- Simple inheritance where all methods have implementations
- When you just need a regular parent class
- Over-engineering simple code
- When duck typing is sufficient

## Design Patterns Using ABCs

1. **Template Method Pattern** - Define algorithm structure with abstract steps
2. **Strategy Pattern** - Define family of interchangeable algorithms
3. **Factory Pattern** - Use abstract class methods for object creation
4. **Plugin Architecture** - Define interfaces for plugins to implement
5. **Dependency Injection** - Inject dependencies typed as ABCs

## Comparison: ABC vs Protocol (PEP 544)

| Feature | ABC | Protocol (typing.Protocol) |
|---------|-----|----------------------------|
| Inheritance required | Yes | No (structural subtyping) |
| Runtime checking | Yes | No (static only) |
| Prevents instantiation | Yes | No |
| Multiple inheritance | Yes | Yes |
| Best for | Libraries, frameworks | Type hints, static analysis |

## Additional Resources

- [PEP 3119 - Introducing Abstract Base Classes](https://www.python.org/dev/peps/pep-3119/)
- [Python abc module documentation](https://docs.python.org/3/library/abc.html)
- [Abstract Base Classes in Python (Real Python)](https://realpython.com/python-interface/)
