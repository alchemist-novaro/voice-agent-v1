"""
Integration tests for agent workflows
"""

import pytest
from conversation_manager import IntentAgent, NewAppointmentAgent
from call_agents import SummarizerAgent


class TestAgentWorkflow:
    """Integration tests for agent workflows."""
    
    def test_intent_agent_workflow(self):
        """Test complete intent agent workflow."""
        agent = IntentAgent()
        
        # Test agent creation
        assert agent is not None
        assert agent.has_fields() == False  # Intent agent doesn't define fields directly
        
        # Test instruction formatting
        instructions = agent.format_instructions(
            account_friendly_name="Test Company",
            account_services="plumbing, HVAC"
        )
        assert "Test Company" in instructions
        assert "plumbing, HVAC" in instructions
        
        # Test schema generation
        schema = agent.schema()
        assert schema["type"] == "json_schema"
        assert schema["name"] == "intentagent"
        
        # Test tool schema
        tool_schemas = agent.tool_schema()
        assert len(tool_schemas) > 0
        
        # Test input processing
        class MockConversation:
            def __init__(self):
                self.messages = [MockMessage("I need help with my AC")]
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        conversation = MockConversation()
        processed_input = agent.process_input(conversation)
        assert processed_input == "I need help with my AC"
    
    def test_new_appointment_agent_workflow(self):
        """Test new appointment agent workflow."""
        agent = NewAppointmentAgent()
        
        # Test agent creation
        assert agent is not None
        
        # Test instruction formatting
        instructions = agent.format_instructions(
            account_friendly_name="Test Company",
            account_services="plumbing, HVAC",
            account_full_address="123 Test St",
            account_phone="555-123-4567",
            account_time_zone="America/New_York",
            customer_information='{"full_name": "John Doe"}',
            current_time="2024-01-15T10:30:00Z"
        )
        assert "Test Company" in instructions
        assert "plumbing, HVAC" in instructions
        
        # Test tool schema
        tool_schemas = agent.tool_schema()
        assert len(tool_schemas) > 0
        
        # Test input processing
        class MockConversation:
            def __init__(self):
                self.messages = [MockMessage("I need to schedule an appointment")]
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        conversation = MockConversation()
        processed_input = agent.process_input(conversation)
        assert processed_input == "I need to schedule an appointment"
    
    def test_summarizer_agent_workflow(self):
        """Test call summarizer agent workflow."""
        agent = SummarizerAgent()
        
        # Test agent creation
        assert agent is not None
        
        # Test input processing
        class MockCall:
            def __init__(self):
                self.transcription = "Customer: Hi, my water heater is leaking. Agent: I understand, let me help you with that."
        
        call = MockCall()
        processed_input = agent.process_input(call)
        assert "water heater" in processed_input
        assert "leaking" in processed_input
    
    def test_agent_schema_consistency(self):
        """Test that agent schemas are consistent."""
        agents = [
            IntentAgent(),
            NewAppointmentAgent(),
            SummarizerAgent()
        ]
        
        for agent in agents:
            schema = agent.schema()
            
            # All schemas should have required fields
            assert "type" in schema
            assert "name" in schema
            assert "strict" in schema
            assert "schema" in schema
            
            # Schema should be valid JSON schema
            assert schema["type"] == "json_schema"
            assert isinstance(schema["strict"], bool)
            assert isinstance(schema["schema"], dict)
    
    def test_tool_schema_consistency(self):
        """Test that tool schemas are consistent."""
        agents = [
            IntentAgent(),
            NewAppointmentAgent()
        ]
        
        for agent in agents:
            tool_schemas = agent.tool_schema()
            
            for tool_schema in tool_schemas:
                # All tool schemas should have required fields
                assert "type" in tool_schema
                assert "name" in tool_schema
                assert "description" in tool_schema
                assert "strict" in tool_schema
                assert "parameters" in tool_schema
                
                # Tool schema should be valid function schema
                assert tool_schema["type"] == "function"
                assert isinstance(tool_schema["strict"], bool)
                assert isinstance(tool_schema["parameters"], dict)
