"""
Simple Conversation UI for AgentForce Framework
A streamlined interface for complete customer service conversations.
"""

import gradio as gr
import openai
import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConversationManager:
    """Manages the complete conversation workflow."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the conversation manager with OpenAI API key."""
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.conversation_history = []
        self.current_state = "greeting"
        self.appointment_data = {}
        
    def get_system_prompt(self, account_name: str, account_services: str) -> str:
        """Get the system prompt for the conversation workflow."""
        return f"""You are a digital assistant from {account_name} working on customer inquiries. 
You handle the complete customer service workflow including:

1. **Greeting & Service Confirmation**: Welcome customers and confirm their service request
2. **Service Area Check**: Verify if we provide services in their area
3. **Service Type Validation**: Confirm we provide the requested service
4. **Appointment Scheduling**: Show available times and schedule appointments
5. **Information Collection**: Gather necessary details (residential/commercial, dispatch fee approval, etc.)
6. **Appointment Confirmation**: Confirm all details and provide technician information
7. **Rescheduling**: Handle appointment changes
8. **Cancellation**: Process cancellations with retention offers
9. **Pricing Information**: Provide cost breakdowns when requested

**Company Services**: {account_services}

**Conversation Flow**:
- Always start with a friendly greeting and confirm the service request
- Check service area and service type compatibility
- Show available appointment times
- Collect required information (property type, dispatch fee approval, issue details)
- Confirm appointment with all details
- Handle follow-up requests (rescheduling, cancellation, pricing)

**Key Information to Collect**:
- Customer name
- Service area (ZIP code)
- Property type (residential/commercial)
- Dispatch fee approval ($75, waived if repair needed)
- Issue details (backup, property damage, etc.)
- Preferred appointment time
- Contact preferences

**Appointment Details Format**:
- **Date & Time**: [Selected time]
- **Technician**: [Name] (ID: [ID])
- **Contact**: [Phone number]
- **Estimated Time**: 45-60 min
- **Estimated Cost**: Starts at $75 (waived if repair is done)

**Pricing Breakdown**:
- **Basic Unclogging**: $75-150
- **Deep Cleaning**: $150-250
- **Pipe Replacement (if needed)**: $250+

Always be professional, helpful, and follow the conversation flow naturally. If you can't provide a service, offer alternatives or recommendations when appropriate."""

    def process_message(self, message: str, account_name: str = "LBA Services", 
                       account_services: str = "plumbing, drain cleaning, HVAC, electrical"):
        """Process a customer message and return the AI response."""
        if not message.strip():
            return "Please enter a message."
        
        try:
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.get_system_prompt(account_name, account_services)}
            ]
            
            # Add conversation history
            for entry in self.conversation_history[-10:]:  # Keep last 10 messages
                messages.append(entry)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAIstream = self.openai_client.chat.completions.create(
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )

            full_text = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.get("content"):
                    token = chunk.choices[0].delta["content"]
                    full_text += token
                    yield token
                    
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_conversation(self) -> str:
        """Clear the conversation history."""
        self.conversation_history = []
        self.current_state = "greeting"
        self.appointment_data = {}
        return "Conversation cleared! Starting fresh."
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation yet."
        
        summary = "**Conversation Summary:**\n\n"
        for i, entry in enumerate(self.conversation_history, 1):
            role = "Customer" if entry["role"] == "user" else "Assistant"
            summary += f"{i}. **{role}**: {entry['content']}\n\n"
        
        return summary


def create_simple_interface():
    """Create the simplified conversation interface."""
    
    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return gr.Interface(
            fn=lambda x: "Please set OPENAI_API_KEY in your .env file",
            inputs=gr.Textbox(label="Message"),
            outputs=gr.Textbox(label="Response"),
            title="Simple Conversation UI - OpenAI API Key Required",
            description="Please set the OPENAI_API_KEY in your .env file to use this interface."
        )
    
    # Initialize the conversation manager
    conversation_manager = ConversationManager(openai_api_key)
    
    # Create the interface
    with gr.Blocks(title="Simple Conversation UI", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 💬 Simple Customer Service Conversation")
        gr.Markdown("A streamlined interface for complete customer service conversations.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Account settings
                account_name = gr.Textbox(
                    value="LBA Services",
                    label="Company Name",
                    info="Name of your business"
                )
                
                account_services = gr.Textbox(
                    value="plumbing, drain cleaning, HVAC, electrical",
                    label="Services Offered",
                    info="Services your company provides"
                )
                
                # Conversation controls
                clear_button = gr.Button("Clear Conversation", variant="stop")
                summary_button = gr.Button("Show Summary", variant="secondary")
                
                # Quick start examples
                gr.Markdown("### 🚀 Quick Start Examples")
                example_buttons = [
                    gr.Button("Service Request", variant="secondary"),
                    gr.Button("Reschedule Appointment", variant="secondary"),
                    gr.Button("Cancel Appointment", variant="secondary"),
                    gr.Button("Pricing Question", variant="secondary")
                ]
                
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_label=True,
                    type="messages"
                )
                
                message_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Type your message here...",
                    lines=2
                )
                
                send_button = gr.Button("Send Message", variant="primary")
                
                # Response output
                response_output = gr.Textbox(
                    label="AI Response",
                    lines=3,
                    max_lines=8,
                    interactive=False
                )
        
        # Event handlers
        def chat_function(message, account_name, account_services):
            if not message.strip():
                return [], "", "Please enter a message."
            
            response = conversation_manager.process_message(message, account_name, account_services)
            
            # Update conversation history for display
            conversation_display = []
            for entry in conversation_manager.conversation_history:
                conversation_display.append({"role": entry["role"], "content": entry["content"]})
            
            return conversation_display, response, ""
        
        def clear_conversation():
            conversation_manager.clear_conversation()
            return [], "", "Conversation cleared! Starting fresh."
        
        def show_summary():
            return conversation_manager.get_conversation_summary()
        
        def example_click(example_text):
            return example_text
        
        # Connect events
        send_button.click(
            fn=chat_function,
            inputs=[message_input, account_name, account_services],
            outputs=[chatbot, response_output, message_input]
        )
        
        message_input.submit(
            fn=chat_function,
            inputs=[message_input, account_name, account_services],
            outputs=[chatbot, response_output, message_input]
        )
        
        clear_button.click(
            fn=clear_conversation,
            outputs=[chatbot, response_output, message_input]
        )
        
        summary_button.click(
            fn=show_summary,
            outputs=[response_output]
        )
        
        # Example button handlers
        example_buttons[0].click(
            fn=lambda: "Hi, I need help with a clogged drain. Can you help me schedule a service?",
            outputs=[message_input]
        )
        
        example_buttons[1].click(
            fn=lambda: "I need to reschedule my appointment for tomorrow.",
            outputs=[message_input]
        )
        
        example_buttons[2].click(
            fn=lambda: "I need to cancel my appointment.",
            outputs=[message_input]
        )
        
        example_buttons[3].click(
            fn=lambda: "What are your rates for drain cleaning?",
            outputs=[message_input]
        )
        
        # Instructions
        gr.Markdown("""
        ## How to Use
        
        1. **Configure Company**: Set your company name and services
        2. **Start Conversation**: Type a message or use the example buttons
        3. **Follow the Flow**: The AI will guide you through the complete customer service process
        4. **Manage Conversation**: Use Clear to start fresh or Summary to review
        
        ## Conversation Flow
        
        The AI handles the complete workflow:
        - ✅ Service confirmation and area check
        - ✅ Appointment scheduling and rescheduling
        - ✅ Information collection (property type, fees, etc.)
        - ✅ Appointment confirmation with details
        - ✅ Cancellation with retention offers
        - ✅ Pricing information and cost breakdowns
        
        ## Example Scenarios
        
        - **Service Request**: "I need help with a clogged drain"
        - **Rescheduling**: "I need to change my appointment time"
        - **Cancellation**: "I want to cancel my appointment"
        - **Pricing**: "What does drain cleaning cost?"
        """)
    
    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_simple_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
