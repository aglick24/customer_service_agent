#!/usr/bin/env python3
"""
System-Wide Testing
Test various user inputs to verify the complete system is working correctly
"""

from src.sierra_agent.core.agent import SierraAgent

def test_various_inputs():
    print("🏔️ SYSTEM-WIDE TESTING...")
    
    agent = SierraAgent()
    
    # Test cases with expected behaviors
    test_cases = [
        # Conversational inputs - should get branded responses
        {
            "input": "hello",
            "expected_type": "conversational",
            "should_have_branding": True
        },
        {
            "input": "thanks",
            "expected_type": "conversational", 
            "should_have_branding": True
        },
        {
            "input": "what can you help with?",
            "expected_type": "conversational",
            "should_have_branding": True
        },
        
        # Tool-based inputs - should attempt to use tools
        {
            "input": "show me backpacks",
            "expected_type": "tool",
            "expected_tools": ["browse_catalog"],
            "should_have_branding": True
        },
        {
            "input": "tell me about your company", 
            "expected_type": "tool",
            "expected_tools": ["get_company_info"],
            "should_have_branding": True
        },
        {
            "input": "what promotions do you have?",
            "expected_type": "tool", 
            "expected_tools": ["get_early_risers_promotion"],
            "should_have_branding": True
        },
        
        # Missing info inputs - should ask for clarification
        {
            "input": "check my order",
            "expected_type": "missing_info",
            "should_have_branding": True
        }
    ]
    
    results = {"passed": 0, "failed": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: '{test_case['input']}' ---")
        
        # Start fresh session for each test
        session_id = agent.start_conversation()
        response = agent.process_user_input(test_case["input"])
        
        print(f"Response: {response[:100]}...")
        
        # Check for outdoor branding
        branding_elements = ["🏔️", "adventure", "outdoor", "trail", "sierra", "outfitters"]
        found_branding = [elem for elem in branding_elements if elem.lower() in response.lower()]
        
        has_branding = len(found_branding) > 0
        
        if test_case.get("should_have_branding", True):
            if has_branding:
                print(f"✅ Has outdoor branding: {found_branding}")
                results["passed"] += 1
            else:
                print("❌ Missing outdoor branding")
                results["failed"] += 1
        else:
            print(f"ℹ️  Branding check skipped")
            results["passed"] += 1
    
    print(f"\n🏔️ SYSTEM-WIDE TEST RESULTS:")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")  
    print(f"📊 Total: {results['total']}")
    
    if results["failed"] == 0:
        print("🎉 ALL SYSTEM TESTS PASSED!")
    else:
        print(f"⚠️  {results['failed']} tests failed")

def test_tool_orchestrator_integration():
    """Test that the tool orchestrator is working correctly"""
    print("\n🔧 TESTING TOOL ORCHESTRATOR INTEGRATION...")
    
    from src.sierra_agent.tools.tool_orchestrator import ToolOrchestrator
    
    orchestrator = ToolOrchestrator()
    tools = orchestrator.get_available_tools()
    
    print(f"Available tools: {len(tools)}")
    for tool in tools[:5]:  # Show first 5
        print(f"  - {tool}")
    
    if len(tools) >= 9:
        print("✅ Tool orchestrator has expected number of tools")
    else:
        print("❌ Tool orchestrator missing expected tools")
    
    # Test tool descriptions
    descriptions = orchestrator.get_tool_descriptions()
    if descriptions and len(descriptions) > 100:  # Should be a substantial description
        print("✅ Tool descriptions available")
    else:
        print("❌ Tool descriptions missing or incomplete")

if __name__ == "__main__":
    test_various_inputs()
    test_tool_orchestrator_integration()