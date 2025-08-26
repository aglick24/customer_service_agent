#!/usr/bin/env python3
"""
Test specifically the greeting response to see if branding is working
"""

from src.sierra_agent.core.agent import SierraAgent

def test_greeting_branding():
    print("🏔️ Testing Greeting Branding...")
    
    agent = SierraAgent()
    session_id = agent.start_conversation()
    
    # Test multiple greeting variations
    greetings = ["hello", "hi", "hey there", "good morning"]
    
    for greeting in greetings:
        print(f"\n--- Testing: '{greeting}' ---")
        response = agent.process_user_input(greeting)
        
        print(f"Response length: {len(response)} chars")
        print(f"Response: {response[:200]}...")
        
        # Check for branding elements
        branding_elements = ["🏔️", "adventure", "outdoor", "trail", "sierra", "outfitters"]
        found_elements = [elem for elem in branding_elements if elem.lower() in response.lower()]
        
        print(f"Branding elements found: {found_elements}")
        
        if found_elements:
            print("✅ Has outdoor branding")
        else:
            print("❌ Missing outdoor branding")

if __name__ == "__main__":
    test_greeting_branding()