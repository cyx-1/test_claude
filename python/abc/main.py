"""
Abstract Base Classes (ABC) Example: Demonstrating Python's ABC Module

This example showcases key ABC concepts:
1. Basic abstract methods with @abstractmethod
2. Abstract properties with @property and @abstractmethod
3. Abstract class methods and static methods
4. Multiple inheritance with ABCs
5. Preventing instantiation of abstract classes
6. Concrete implementations of abstract classes
"""

from abc import ABC, abstractmethod
import sys

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# Example 1: Basic Abstract Base Class
class Shape(ABC):
    """Abstract base class for geometric shapes."""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def area(self):
        """Calculate and return the area of the shape."""
        pass

    @abstractmethod
    def perimeter(self):
        """Calculate and return the perimeter of the shape."""
        pass

    def description(self):
        """Concrete method available to all shapes."""
        return f"This is a {self.name}"


# Example 2: Concrete implementation of Shape
class Rectangle(Shape):
    """Concrete implementation of Shape for rectangles."""

    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def area(self):
        """Implements abstract method."""
        return self.width * self.height

    def perimeter(self):
        """Implements abstract method."""
        return 2 * (self.width + self.height)


class Circle(Shape):
    """Concrete implementation of Shape for circles."""

    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        """Implements abstract method."""
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        """Implements abstract method (circumference)."""
        return 2 * 3.14159 * self.radius


# Example 3: Abstract Properties
class Vehicle(ABC):
    """Abstract base class demonstrating abstract properties."""

    def __init__(self, brand):
        self._brand = brand

    @property
    @abstractmethod
    def max_speed(self):
        """Abstract property for maximum speed."""
        pass

    @property
    def brand(self):
        """Concrete property."""
        return self._brand

    @abstractmethod
    def start_engine(self):
        """Abstract method to start the vehicle."""
        pass


class Car(Vehicle):
    """Concrete implementation of Vehicle."""

    def __init__(self, brand, speed):
        super().__init__(brand)
        self._max_speed = speed

    @property
    def max_speed(self):
        """Implements abstract property."""
        return self._max_speed

    def start_engine(self):
        """Implements abstract method."""
        return f"{self.brand} car engine started! 🚗"


class Motorcycle(Vehicle):
    """Another concrete implementation of Vehicle."""

    def __init__(self, brand, speed):
        super().__init__(brand)
        self._max_speed = speed

    @property
    def max_speed(self):
        """Implements abstract property."""
        return self._max_speed

    def start_engine(self):
        """Implements abstract method."""
        return f"{self.brand} motorcycle engine started! 🏍️"


# Example 4: Abstract Class Methods and Static Methods
class DataProcessor(ABC):
    """Abstract base class with class and static methods."""

    @classmethod
    @abstractmethod
    def from_file(cls, filename):
        """Abstract class method to create instance from file."""
        pass

    @staticmethod
    @abstractmethod
    def validate_data(data):
        """Abstract static method to validate data."""
        pass

    @abstractmethod
    def process(self):
        """Abstract instance method to process data."""
        pass


class JSONProcessor(DataProcessor):
    """Concrete implementation for JSON data processing."""

    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, filename):
        """Implements abstract class method."""
        return cls(f"Data from {filename}.json")

    @staticmethod
    def validate_data(data):
        """Implements abstract static method."""
        return isinstance(data, str) and len(data) > 0

    def process(self):
        """Implements abstract instance method."""
        return f"Processing JSON: {self.data}"


# Example 5: Multiple Inheritance with ABCs
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


class GameSprite(Drawable, Moveable):
    """Concrete class implementing multiple abstract interfaces."""

    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0

    def draw(self):
        """Implements Drawable.draw()."""
        return f"Drawing {self.name} at ({self.x}, {self.y})"

    def move(self, x, y):
        """Implements Moveable.move()."""
        self.x = x
        self.y = y
        return f"Moved {self.name} to ({self.x}, {self.y})"


# Demonstration functions
def demonstrate_basic_abc():
    """Demonstrates basic ABC usage with Shape classes."""
    section_header("EXAMPLE 1: Basic Abstract Base Classes")

    print("\n📐 Creating concrete shapes:")
    rect = Rectangle(5, 3)
    circle = Circle(4)

    print(f"   Rectangle(5, 3) created")
    print(f"   Circle(4) created")

    print("\n📏 Calculating areas and perimeters:")
    print(f"   Rectangle: area = {rect.area()}, perimeter = {rect.perimeter()}")
    print(f"   Circle: area = {circle.area():.2f}, perimeter = {circle.perimeter():.2f}")

    print("\n📝 Using concrete method from abstract class:")
    print(f"   {rect.description()}")
    print(f"   {circle.description()}")

    print("\n❌ Attempting to instantiate abstract class:")
    try:
        shape = Shape("Generic")  # This will fail!
        print(f"   Created: {shape}")
    except TypeError as e:
        print(f"   TypeError: {e}")
        print(f"   ✅ Cannot instantiate abstract class!")


def demonstrate_abstract_properties():
    """Demonstrates abstract properties."""
    section_header("EXAMPLE 2: Abstract Properties")

    print("\n🚗 Creating vehicles with abstract properties:")
    car = Car("Tesla", 200)
    motorcycle = Motorcycle("Harley", 180)

    print(f"   Car: {car.brand} (max speed: {car.max_speed} km/h)")
    print(f"   Motorcycle: {motorcycle.brand} (max speed: {motorcycle.max_speed} km/h)")

    print("\n🔑 Starting engines:")
    print(f"   {car.start_engine()}")
    print(f"   {motorcycle.start_engine()}")

    print("\n❌ Attempting to instantiate Vehicle without implementing properties:")
    print("   class IncompleteVehicle(Vehicle):")
    print("       def start_engine(self): return 'Started'")
    print("   # Missing max_speed property implementation!")
    try:

        class IncompleteVehicle(Vehicle):
            def start_engine(self):
                return "Started"

        vehicle = IncompleteVehicle("Generic")
    except TypeError as e:
        print(f"   TypeError: Can't instantiate abstract class...")
        print(f"   ✅ Must implement all abstract properties!")


def demonstrate_abstract_class_methods():
    """Demonstrates abstract class and static methods."""
    section_header("EXAMPLE 3: Abstract Class Methods and Static Methods")

    print("\n📊 Using class method to create instance:")
    processor = JSONProcessor.from_file("config")
    print(f"   Created: {processor.__class__.__name__}")
    print(f"   Data: {processor.data}")

    print("\n✅ Validating data with static method:")
    test_data = "sample data"
    is_valid = JSONProcessor.validate_data(test_data)
    print(f"   JSONProcessor.validate_data('{test_data}') = {is_valid}")

    empty_data = ""
    is_valid = JSONProcessor.validate_data(empty_data)
    print(f"   JSONProcessor.validate_data('') = {is_valid}")

    print("\n⚙️  Processing data:")
    result = processor.process()
    print(f"   {result}")


def demonstrate_multiple_inheritance():
    """Demonstrates multiple inheritance with ABCs."""
    section_header("EXAMPLE 4: Multiple Inheritance with ABCs")

    print("\n🎮 Creating game sprite with multiple abstract interfaces:")
    sprite = GameSprite("Player")
    print(f"   Created: {sprite.name}")

    print("\n🎨 Using Drawable interface:")
    print(f"   {sprite.draw()}")

    print("\n🏃 Using Moveable interface:")
    print(f"   {sprite.move(10, 20)}")
    print(f"   {sprite.draw()}")

    print("\n✅ GameSprite implements both Drawable and Moveable interfaces!")


def demonstrate_isinstance_checks():
    """Demonstrates isinstance checks with ABCs."""
    section_header("EXAMPLE 5: Type Checking with ABCs")

    rect = Rectangle(5, 3)
    car = Car("Toyota", 180)
    sprite = GameSprite("Enemy")

    print("\n🔍 Checking isinstance with abstract base classes:")
    print(f"   isinstance(rect, Shape) = {isinstance(rect, Shape)}")
    print(f"   isinstance(rect, Rectangle) = {isinstance(rect, Rectangle)}")
    print(f"   isinstance(car, Vehicle) = {isinstance(car, Vehicle)}")
    print(f"   isinstance(car, Shape) = {isinstance(car, Shape)}")

    print("\n🔍 Checking multiple inheritance:")
    print(f"   isinstance(sprite, Drawable) = {isinstance(sprite, Drawable)}")
    print(f"   isinstance(sprite, Moveable) = {isinstance(sprite, Moveable)}")
    print(f"   isinstance(sprite, GameSprite) = {isinstance(sprite, GameSprite)}")

    print("\n✅ ABCs provide clear type hierarchies and contracts!")


def demonstrate_subclass_checks():
    """Demonstrates subclass checks with ABCs."""
    section_header("EXAMPLE 6: Subclass Checking with ABCs")

    print("\n🔍 Checking if classes are subclasses of ABCs:")
    print(f"   issubclass(Rectangle, Shape) = {issubclass(Rectangle, Shape)}")
    print(f"   issubclass(Circle, Shape) = {issubclass(Circle, Shape)}")
    print(f"   issubclass(Car, Vehicle) = {issubclass(Car, Vehicle)}")
    print(f"   issubclass(GameSprite, Drawable) = {issubclass(GameSprite, Drawable)}")
    print(f"   issubclass(GameSprite, Moveable) = {issubclass(GameSprite, Moveable)}")

    print("\n✅ issubclass() works with abstract base classes!")


def main():
    """Main entry point for all examples."""
    print("\n" + "=" * 70)
    print("  🎯 Python ABC (Abstract Base Classes) Examples")
    print("=" * 70)

    demonstrate_basic_abc()
    demonstrate_abstract_properties()
    demonstrate_abstract_class_methods()
    demonstrate_multiple_inheritance()
    demonstrate_isinstance_checks()
    demonstrate_subclass_checks()

    print("\n" + "=" * 70)
    print("  ✨ All demonstrations completed!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
