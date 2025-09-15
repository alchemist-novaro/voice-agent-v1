"""
Unit tests for BaseTool class
"""

import pytest
import json
from agentforce.core.base_tool import BaseTool
from agentforce.core.field import Field, FieldType
from agentforce.exceptions import ToolError, ValidationError


class TestTool(BaseTool):
    """Test tool for testing purposes."""
    
    description = "A test tool"
    strict = True
    
    def __init__(self, options=None):
        super().__init__(options)
        self.field("test_param", FieldType.STRING, "A test parameter")
    
    def execute(self, **kwargs):
        """Execute the test tool."""
        return self.success(result="test_success")


class TestBaseTool:
    """Test cases for BaseTool class."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = TestTool()
        assert tool.options == {}
        assert tool.params == {}
    
    def test_description_property(self):
        """Test description property."""
        assert TestTool.description() == "A test tool"
        
        TestTool.description("New description")
        assert TestTool.description() == "New description"
    
    def test_name_property(self):
        """Test name property."""
        # Name should be generated from class name
        assert TestTool.name() == "testtool"
    
    def test_strict_property(self):
        """Test strict property."""
        assert TestTool.strict() == True
        
        TestTool.strict(False)
        assert TestTool.strict() == False
    
    def test_field_definition(self):
        """Test field definition."""
        tool = TestTool()
        fields = tool.fields()
        
        assert "test_param" in fields
        assert fields["test_param"].name == "test_param"
        assert fields["test_param"].field_type == FieldType.STRING
    
    def test_json_schema_generation(self):
        """Test JSON schema generation."""
        tool = TestTool()
        schema = tool.to_json_schema()
        
        assert schema["type"] == "function"
        assert schema["name"] == "testtool"
        assert schema["description"] == "A test tool"
        assert schema["strict"] == True
        assert "parameters" in schema
        assert "test_param" in schema["parameters"]["properties"]
    
    def test_handle_tool_call_success(self):
        """Test successful tool call handling."""
        tool = TestTool()
        arguments = '{"test_param": "test_value"}'
        
        result = tool.handle_tool_call(arguments)
        
        assert result["result"] == "success"
        assert result["test_result"] == "test_success"
        assert tool.params["test_param"] == "test_value"
    
    def test_handle_tool_call_invalid_json(self):
        """Test tool call with invalid JSON."""
        tool = TestTool()
        arguments = "invalid json"
        
        with pytest.raises(ValidationError):
            tool.handle_tool_call(arguments)
    
    def test_handle_tool_call_invalid_arguments_type(self):
        """Test tool call with invalid arguments type."""
        tool = TestTool()
        arguments = 123  # Not a string
        
        with pytest.raises(ValidationError):
            tool.handle_tool_call(arguments)
    
    def test_handle_tool_call_non_dict_arguments(self):
        """Test tool call with non-dict arguments."""
        tool = TestTool()
        arguments = '"not a dict"'
        
        with pytest.raises(ValidationError):
            tool.handle_tool_call(arguments)
    
    def test_handle_tool_call_unknown_field_strict(self):
        """Test tool call with unknown field in strict mode."""
        tool = TestTool()
        arguments = '{"unknown_field": "value"}'
        
        with pytest.raises(ValidationError):
            tool.handle_tool_call(arguments)
    
    def test_handle_tool_call_unknown_field_non_strict(self):
        """Test tool call with unknown field in non-strict mode."""
        TestTool.strict(False)
        tool = TestTool()
        arguments = '{"unknown_field": "value", "test_param": "test_value"}'
        
        result = tool.handle_tool_call(arguments)
        
        assert result["result"] == "success"
        assert tool.params["test_param"] == "test_value"
        # Unknown field should be ignored in non-strict mode
    
    def test_success_helper(self):
        """Test success helper method."""
        tool = TestTool()
        result = tool.success(test_key="test_value")
        
        assert result["result"] == "success"
        assert result["test_key"] == "test_value"
    
    def test_failure_helper(self):
        """Test failure helper method."""
        tool = TestTool()
        errors = ["Error 1", "Error 2"]
        result = tool.failure(errors=errors, test_key="test_value")
        
        assert result["result"] == "failure"
        assert result["errors"] == errors
        assert result["test_key"] == "test_value"
    
    def test_execute_abstract(self):
        """Test that BaseTool is abstract."""
        with pytest.raises(TypeError):
            BaseTool()
