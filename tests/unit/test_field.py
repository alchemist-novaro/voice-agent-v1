"""
Unit tests for Field class
"""

import pytest
from agentforce.core.field import Field, FieldType
from agentforce.exceptions import ValidationError


class TestField:
    """Test cases for Field class."""
    
    def test_field_initialization(self):
        """Test field initialization."""
        field = Field("test_field", FieldType.STRING, "A test field")
        
        assert field.name == "test_field"
        assert field.field_type == FieldType.STRING
        assert field.description == "A test field"
        assert field.required == True
        assert field.default is None
        assert field.enum_values is None
    
    def test_field_with_options(self):
        """Test field initialization with options."""
        field = Field(
            "test_field", 
            FieldType.STRING, 
            "A test field",
            required=False,
            default="default_value",
            enum=["value1", "value2"]
        )
        
        assert field.required == False
        assert field.default == "default_value"
        assert field.enum_values == ["value1", "value2"]
    
    def test_string_field_casting(self):
        """Test string field value casting."""
        field = Field("test_field", FieldType.STRING, "A test field")
        
        # String value should remain string
        assert field.cast_value("test") == "test"
        
        # Non-string should be converted to string
        assert field.cast_value(123) == "123"
        assert field.cast_value(True) == "True"
    
    def test_number_field_casting(self):
        """Test number field value casting."""
        field = Field("test_field", FieldType.NUMBER, "A test field")
        
        # Valid numbers
        assert field.cast_value(123) == 123
        assert field.cast_value(123.45) == 123.45
        assert field.cast_value("123.45") == 123.45
        
        # Invalid numbers should raise error
        with pytest.raises(ValidationError):
            field.cast_value("not a number")
    
    def test_integer_field_casting(self):
        """Test integer field value casting."""
        field = Field("test_field", FieldType.INTEGER, "A test field")
        
        # Valid integers
        assert field.cast_value(123) == 123
        assert field.cast_value("123") == 123
        
        # Invalid integers should raise error
        with pytest.raises(ValidationError):
            field.cast_value(123.45)
        with pytest.raises(ValidationError):
            field.cast_value("not a number")
    
    def test_boolean_field_casting(self):
        """Test boolean field value casting."""
        field = Field("test_field", FieldType.BOOLEAN, "A test field")
        
        # Valid booleans
        assert field.cast_value(True) == True
        assert field.cast_value(False) == False
        
        # String conversions
        assert field.cast_value("true") == True
        assert field.cast_value("1") == True
        assert field.cast_value("yes") == True
        assert field.cast_value("on") == True
        assert field.cast_value("false") == False
        assert field.cast_value("0") == False
        assert field.cast_value("no") == False
        assert field.cast_value("off") == False
        
        # Invalid booleans should raise error
        with pytest.raises(ValidationError):
            field.cast_value("maybe")
    
    def test_array_field_casting(self):
        """Test array field value casting."""
        field = Field("test_field", FieldType.ARRAY, "A test field")
        
        # Valid arrays
        assert field.cast_value([1, 2, 3]) == [1, 2, 3]
        assert field.cast_value(["a", "b", "c"]) == ["a", "b", "c"]
        
        # Invalid arrays should raise error
        with pytest.raises(ValidationError):
            field.cast_value("not an array")
    
    def test_object_field_casting(self):
        """Test object field value casting."""
        field = Field("test_field", FieldType.OBJECT, "A test field")
        
        # Valid objects
        assert field.cast_value({"key": "value"}) == {"key": "value"}
        
        # Invalid objects should raise error
        with pytest.raises(ValidationError):
            field.cast_value("not an object")
    
    def test_null_field_casting(self):
        """Test null field value casting."""
        field = Field("test_field", FieldType.NULL, "A test field")
        
        # Only None should be valid
        assert field.cast_value(None) == None
        
        # Any other value should raise error
        with pytest.raises(ValidationError):
            field.cast_value("not null")
    
    def test_required_field_validation(self):
        """Test required field validation."""
        field = Field("test_field", FieldType.STRING, "A test field", required=True)
        
        # None should raise error for required field
        with pytest.raises(ValidationError):
            field.cast_value(None)
    
    def test_optional_field_validation(self):
        """Test optional field validation."""
        field = Field("test_field", FieldType.STRING, "A test field", required=False)
        
        # None should be valid for optional field
        assert field.cast_value(None) == None
    
    def test_default_value(self):
        """Test default value handling."""
        field = Field("test_field", FieldType.STRING, "A test field", default="default")
        
        # None should return default value
        assert field.cast_value(None) == "default"
        
        # Other values should work normally
        assert field.cast_value("test") == "test"
    
    def test_enum_validation(self):
        """Test enum validation."""
        field = Field("test_field", FieldType.STRING, "A test field", enum=["a", "b", "c"])
        
        # Valid enum values
        assert field.cast_value("a") == "a"
        assert field.cast_value("b") == "b"
        assert field.cast_value("c") == "c"
        
        # Invalid enum values should raise error
        with pytest.raises(ValidationError):
            field.cast_value("d")
    
    def test_callable_enum_validation(self):
        """Test callable enum validation."""
        def get_enum_values():
            return ["x", "y", "z"]
        
        field = Field("test_field", FieldType.STRING, "A test field", enum=get_enum_values)
        
        # Valid enum values
        assert field.cast_value("x") == "x"
        assert field.cast_value("y") == "y"
        assert field.cast_value("z") == "z"
        
        # Invalid enum values should raise error
        with pytest.raises(ValidationError):
            field.cast_value("w")
    
    def test_json_schema_generation(self):
        """Test JSON schema generation."""
        field = Field("test_field", FieldType.STRING, "A test field")
        schema = field.to_json_schema()
        
        assert schema["type"] == "string"
        assert schema["description"] == "A test field"
    
    def test_json_schema_with_enum(self):
        """Test JSON schema generation with enum."""
        field = Field("test_field", FieldType.STRING, "A test field", enum=["a", "b"])
        schema = field.to_json_schema()
        
        assert schema["type"] == "string"
        assert schema["description"] == "A test field"
        assert schema["enum"] == ["a", "b"]
    
    def test_json_schema_with_default(self):
        """Test JSON schema generation with default."""
        field = Field("test_field", FieldType.STRING, "A test field", default="default")
        schema = field.to_json_schema()
        
        assert schema["type"] == "string"
        assert schema["description"] == "A test field"
        assert schema["default"] == "default"
    
    def test_json_schema_array_with_items(self):
        """Test JSON schema generation for array with items schema."""
        field = Field("test_field", FieldType.ARRAY, "A test field", items_schema={"type": "string"})
        schema = field.to_json_schema()
        
        assert schema["type"] == "array"
        assert schema["description"] == "A test field"
        assert schema["items"] == {"type": "string"}
