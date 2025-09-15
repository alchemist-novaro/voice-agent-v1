#!/usr/bin/env python3
"""
Launcher script for the Simple Conversation UI.
"""

import os
import sys
from dotenv import load_dotenv
from simple_conversation_ui import create_simple_interface

# Load environment variables from .env file
load_dotenv()

GRADIO_SERVER_PORT = int(os.getenv("GRADIO_SERVER_PORT", 7860))

def main():
    """Main function to launch the simple UI."""
    print("🚀 Starting Simple Conversation UI...")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("\nTo set your OpenAI API key, create a .env file with:")
        print("OPENAI_API_KEY=your-api-key-here")
        print("\nOr set the environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("✅ OpenAI API key found")
    print("🌐 Launching simple conversation interface...")
    print("\nThe interface will be available at:")
    print(f"   Local: http://localhost:{GRADIO_SERVER_PORT}")
    print(f"   Network: http://0.0.0.0:{GRADIO_SERVER_PORT}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Create and launch the interface
        interface = create_simple_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=GRADIO_SERVER_PORT,
            share=True,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
