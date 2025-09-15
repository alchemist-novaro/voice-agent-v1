"""
Unit tests for BaseAgent class
"""

import pytest
from agentforce.core.base_agent import BaseAgent
from agentforce.core.field import Field, FieldType
from agentforce.exceptions import AgentError, ValidationError


class TestAgent(BaseAgent):
    """Test agent for testing purposes."""
    
    instructions = "Test agent instructions"
    
    def __init__(self, options=None):
        super().__init__(options)
        self.field("test_field", FieldType.STRING, "A test field")


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = TestAgent()
        assert agent.options == {}
        assert agent.response_id is None
        assert len(agent.tools) == 0
    
    def test_instructions_property(self):
        """Test instructions property."""
        assert TestAgent.instructions() == "Test agent instructions"
        
        TestAgent.instructions("New instructions")
        assert TestAgent.instructions() == "New instructions"
    
    def test_strict_property(self):
        """Test strict property."""
        assert TestAgent.strict() == True
        
        TestAgent.strict(False)
        assert TestAgent.strict() == False
    
    def test_field_definition(self):
        """Test field definition."""
        agent = TestAgent()
        fields = agent.fields()
        
        assert "test_field" in fields
        assert fields["test_field"].name == "test_field"
        assert fields["test_field"].field_type == FieldType.STRING
    
    def test_has_fields(self):
        """Test has_fields method."""
        agent = TestAgent()
        assert agent.has_fields() == True
        
        # Test agent with no fields
        class EmptyAgent(BaseAgent):
            pass
        
        empty_agent = EmptyAgent()
        assert empty_agent.has_fields() == False
    
    def test_schema_generation(self):
        """Test schema generation."""
        agent = TestAgent()
        schema = agent.schema()
        
        assert schema["type"] == "json_schema"
        assert schema["name"] == "testagent"
        assert schema["strict"] == True
        assert "properties" in schema["schema"]
        assert "test_field" in schema["schema"]["properties"]
    
    def test_tool_schema_empty(self):
        """Test tool schema with no tools."""
        agent = TestAgent()
        tool_schemas = agent.tool_schema()
        assert tool_schemas == []
    
    def test_process_input_default(self):
        """Test default input processing."""
        agent = TestAgent()
        result = agent._process_input("test input")
        assert result == "test input"
    
    def test_send_to_ai_placeholder(self):
        """Test AI sending placeholder."""
        agent = TestAgent()
        result = agent._send_to_ai("test input")
        
        assert "response" in result
        assert "response_id" in result
        assert result["response"] == "Processed input: test input"
    
    def test_is_complete_no_conversation(self):
        """Test is_complete with no conversation state."""
        agent = TestAgent()
        
        class MockConversation:
            pass
        
        conversation = MockConversation()
        assert agent.is_complete(conversation) == False
    
    def test_missing_fields_no_conversation(self):
        """Test missing_fields with no conversation state."""
        agent = TestAgent()
        
        class MockConversation:
            pass
        
        conversation = MockConversation()
        missing = agent.missing_fields(conversation)
        assert missing == ["test_field"]
    
    def test_missing_fields_message(self):
        """Test missing_fields_message."""
        agent = TestAgent()
        
        class MockConversation:
            pass
        
        conversation = MockConversation()
        messages = agent.missing_fields_message(conversation)
        assert len(messages) == 1
        assert "test_field" in messages[0]
