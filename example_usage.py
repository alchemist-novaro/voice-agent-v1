"""
Example usage of the Python AgentForce framework.
This demonstrates how to use the agents similar to the Ruby implementation.
"""

from conversation_manager import (
    IntentAgent,
    NewAppointmentAgent, 
    EscalationHandoffAgent,
    GenerateSummaryAgent,
    OpportunityScoringAgent
)
from call_agents import SummarizerAgent


def example_intent_agent():
    """Example of using the IntentAgent."""
    print("=== Intent Agent Example ===")
    
    # Create agent instance
    agent = IntentAgent()
    
    # Format instructions with account data
    instructions = agent.format_instructions(
        account_friendly_name="ABC Home Services",
        account_services="plumbing, HVAC, electrical"
    )
    
    print("Instructions formatted with account data:")
    print(instructions[:200] + "...")
    
    # Example conversation data
    class MockConversation:
        def __init__(self):
            self.messages = [
                MockMessage("Hi, my water heater is leaking!")
            ]
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
    
    conversation = MockConversation()
    
    # Process input
    processed_input = agent.process_input(conversation)
    print(f"\nProcessed input: {processed_input}")
    
    # Get agent schema
    schema = agent.schema()
    print(f"\nAgent schema: {schema}")
    
    # Get tool schemas
    tool_schemas = agent.tool_schema()
    print(f"\nTool schemas count: {len(tool_schemas)}")


def example_new_appointment_agent():
    """Example of using the NewAppointmentAgent."""
    print("\n=== New Appointment Agent Example ===")
    
    # Create agent instance
    agent = NewAppointmentAgent()
    
    # Format instructions with account data
    instructions = agent.format_instructions(
        account_friendly_name="ABC Home Services",
        account_services="plumbing, HVAC, electrical",
        account_full_address="123 Main St, City, State 12345",
        account_phone="(555) 123-4567",
        account_time_zone="America/New_York",
        customer_information='{"full_name": "John Doe", "phone_number": "555-123-4567"}',
        current_time="2024-01-15T10:30:00Z"
    )
    
    print("Instructions formatted with account data:")
    print(instructions[:200] + "...")
    
    # Get tool schemas
    tool_schemas = agent.tool_schema()
    print(f"\nTool schemas count: {len(tool_schemas)}")
    
    # Example customer data
    class MockConversation:
        def __init__(self):
            self.customer_used_contacts = []
            self.initiator_channel = {'account': {}}
            self.customer = {'full_name': 'John Doe', 'primary_phone_number': '555-123-4567', 'primary_email_address': 'john@example.com', 'locations': []}
    
    customer_data = agent.build_initial_data(MockConversation())
    print(f"\nCustomer data: {customer_data}")


def example_escalation_handoff_agent():
    """Example of using the EscalationHandoffAgent."""
    print("\n=== Escalation Handoff Agent Example ===")
    
    # Create agent instance
    agent = EscalationHandoffAgent()
    
    # Format instructions with account data
    instructions = agent.format_instructions(
        account_friendly_name="ABC Home Services",
        account_full_address="123 Main St, City, State 12345",
        account_phone="(555) 123-4567",
        account_services="plumbing, HVAC, electrical",
        account_time_zone="America/New_York",
        current_time="2024-01-15T10:30:00Z",
        customer_information='{"full_name": "John Doe", "phone_number": "555-123-4567"}'
    )
    
    print("Instructions formatted with account data:")
    print(instructions[:200] + "...")
    
    # Get tool schemas
    tool_schemas = agent.tool_schema()
    print(f"\nTool schemas count: {len(tool_schemas)}")


def example_summary_agent():
    """Example of using the GenerateSummaryAgent."""
    print("\n=== Generate Summary Agent Example ===")
    
    # Create agent instance
    agent = GenerateSummaryAgent()
    
    # Example conversation data
    class MockConversation:
        def __init__(self):
            self.messages = [
                MockMessage("Hi, I need help with my AC", True),
                MockMessage("I'd be happy to help! What's the issue?", False),
                MockMessage("It's not cooling properly", True)
            ]
            self.calls = []
    
    class MockMessage:
        def __init__(self, content, role_lead=False):
            self.content = content
            self.role_lead = role_lead
            self.created_at = 0
    
    conversation = MockConversation()
    
    # Process input
    processed_input = agent.process_input(conversation)
    print(f"Processed input: {processed_input}")


def example_opportunity_scoring_agent():
    """Example of using the OpportunityScoringAgent."""
    print("\n=== Opportunity Scoring Agent Example ===")
    
    # Create agent instance
    agent = OpportunityScoringAgent()
    
    # Example opportunity data
    class MockOpportunity:
        def __init__(self):
            self.qualification_questions = [
                "What type of service do you need?",
                "What's the urgency level?",
                "Are you an existing customer?"
            ]
    
    opportunity = MockOpportunity()
    
    # Process input
    processed_input = agent.process_input(opportunity)
    print(f"Processed input: {processed_input}")
    
    # Get agent schema
    schema = agent.schema()
    print(f"\nAgent schema: {schema}")


def example_call_summarizer_agent():
    """Example of using the SummarizerAgent."""
    print("\n=== Call Summarizer Agent Example ===")
    
    # Create agent instance
    agent = SummarizerAgent()
    
    # Example call data
    class MockCall:
        def __init__(self):
            self.transcription = "Customer: Hi, my water heater is leaking. Agent: I understand, let me help you with that. Customer: It's been going on for a few days now."
    
    call = MockCall()
    
    # Process input
    processed_input = agent.process_input(call)
    print(f"Processed input: {processed_input}")


def main():
    """Run all examples."""
    print("Python AgentForce Framework - Example Usage")
    print("=" * 50)
    
    try:
        example_intent_agent()
        example_new_appointment_agent()
        example_escalation_handoff_agent()
        example_summary_agent()
        example_opportunity_scoring_agent()
        example_call_summarizer_agent()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
