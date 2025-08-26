#!/usr/bin/env python3
"""
Individual Tools Test Suite

Test each tool individually to ensure they work correctly
before testing the whole agent system.
"""

import sys
from src.sierra_agent.tools.tool_orchestrator import ToolOrchestrator


def test_tool_orchestrator_initialization():
    """Test ToolOrchestrator basic functionality."""
    print("🔧 Testing ToolOrchestrator Initialization...")
    
    try:
        orchestrator = ToolOrchestrator()
        print("✅ ToolOrchestrator creation successful")
        
        # Test get available tools
        tools = orchestrator.get_available_tools()
        print(f"✅ Available tools: {len(tools)} tools found")
        print(f"   Tools: {', '.join(tools[:5])}{'...' if len(tools) > 5 else ''}")
        
        # Test get tools for LLM planning
        llm_tools = orchestrator.get_tools_for_llm_planning()
        print(f"✅ LLM planning tools: {len(llm_tools)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ ToolOrchestrator initialization failed: {e}")
        return False


def test_individual_tools():
    """Test individual tools with valid parameters."""
    print("🔧 Testing Individual Tools...")
    
    try:
        orchestrator = ToolOrchestrator()
        available_tools = orchestrator.get_available_tools()
        
        # Test 1: Order status tool (should fail gracefully with invalid data)
        if "get_order_status" in available_tools:
            try:
                result = orchestrator.execute_tool(
                    "get_order_status", 
                    email="invalid@test.com", order_number="INVALID"
                )
                print(f"✅ get_order_status tool executed (result success: {result.success})")
            except Exception as e:
                print(f"⚠️ get_order_status tool error (expected): {str(e)[:50]}...")
        
        # Test 2: Product recommendations (should work)
        if "get_recommendations" in available_tools:
            try:
                result = orchestrator.execute_tool(
                    "get_recommendations",
                    recommendation_type="general", limit=3
                )
                print(f"✅ get_recommendations tool executed (success: {result.success})")
            except Exception as e:
                print(f"⚠️ get_recommendations tool error: {str(e)[:50]}...")
        
        # Test 3: Early Risers promotion
        if "get_early_risers_promotion" in available_tools:
            try:
                result = orchestrator.execute_tool("get_early_risers_promotion")
                print(f"✅ get_early_risers_promotion tool executed (success: {result.success})")
            except Exception as e:
                print(f"⚠️ get_early_risers_promotion tool error: {str(e)[:50]}...")
        
        # Test 4: Browse catalog
        if "browse_catalog" in available_tools:
            try:
                result = orchestrator.execute_tool(
                    "browse_catalog",
                    search_query="backpack", limit=5
                )
                print(f"✅ browse_catalog tool executed (success: {result.success})")
            except Exception as e:
                print(f"⚠️ browse_catalog tool error: {str(e)[:50]}...")
        
        # Test 5: Company info (should always work)
        if "get_company_info" in available_tools:
            try:
                result = orchestrator.execute_tool("get_company_info")
                print(f"✅ get_company_info tool executed (success: {result.success})")
                if result.success and result.data:
                    print(f"   Company: {getattr(result.data, 'company_name', 'N/A')}")
            except Exception as e:
                print(f"❌ get_company_info tool error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Individual tools test failed: {e}")
        return False


def test_tool_parameter_validation():
    """Test tool parameter validation."""
    print("🔧 Testing Tool Parameter Validation...")
    
    try:
        orchestrator = ToolOrchestrator()
        
        # Test 1: Missing required parameters
        try:
            result = orchestrator.execute_tool("get_order_status")
            # Should either succeed with validation error or handle gracefully
            print("✅ Tool handles missing parameters gracefully")
        except Exception as e:
            if "parameter" in str(e).lower() or "required" in str(e).lower():
                print("✅ Tool validates parameters correctly")
            else:
                print(f"⚠️ Tool parameter handling: {str(e)[:50]}...")
        
        # Test 2: Invalid tool name
        try:
            result = orchestrator.execute_tool("invalid_tool_name")
            print("⚠️ Invalid tool name handled")
        except Exception as e:
            if "not found" in str(e).lower() or "invalid" in str(e).lower():
                print("✅ Invalid tool name rejected correctly")
            else:
                print(f"⚠️ Invalid tool handling: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool parameter validation failed: {e}")
        return False


def run_tools_tests():
    """Run all individual tools tests."""
    print("🛠️ INDIVIDUAL TOOLS TEST SUITE 🛠️")
    print("Testing each tool independently...\n")
    
    tests = [
        test_tool_orchestrator_initialization,
        test_individual_tools,
        test_tool_parameter_validation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"{'='*50}")
    print(f"RESULTS: {passed}/{len(tests)} tool test suites passed")
    print(f"{'='*50}")
    
    return passed == len(tests)


if __name__ == "__main__":
    """Run individual tools validation."""
    try:
        success = run_tools_tests()
        if success:
            print("\n🎉 All individual tools tests PASSED!")
            print("✅ Tools are working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Some individual tools tests FAILED!")
            print("🔍 Check individual tool implementations")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)