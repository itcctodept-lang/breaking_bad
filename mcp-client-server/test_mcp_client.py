#!/usr/bin/env python3
"""
Comprehensive Tester for MCP Client

This script tests both MCP tools with various document scenarios.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from mcp_client import MCPClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClientTester:
    """Tester for MCP client tools."""
    
    def __init__(self):
        self.client = MCPClient()
        self.test_results = []
        
    def print_separator(self, title: str = ""):
        """Print a visual separator."""
        if title:
            print(f"\n{'='*80}")
            print(f"  {title}")
            print(f"{'='*80}\n")
        else:
            print(f"\n{'-'*80}\n")
    
    def print_result(self, test_name: str, result: Dict[str, Any], success: bool = True):
        """Print test result in a formatted way."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        print(f"Result: {json.dumps(result, indent=2)}")
        self.print_separator()
        
    async def test_recipient_suggestions(self):
        """Test get_recipient_suggestion tool with various documents."""
        self.print_separator("TESTING: get_recipient_suggestion")
        
        test_cases = [
            {
                "name": "Legal Document",
                "content": """
                We need to review the new employee benefits package to ensure compliance 
                with labor laws. The package includes health insurance, retirement plans, 
                and paid time off policies. Legal review is required before implementation.
                """,
                "expected_recipients": ["Legal", "HR"]
            },
            {
                "name": "Financial Report",
                "content": """
                Q4 financial results show a 15% increase in revenue compared to last quarter.
                Operating expenses have decreased by 8%, resulting in improved profit margins.
                Board approval is needed for the proposed budget allocation.
                """,
                "expected_recipients": ["Finance", "Executive"]
            },
            {
                "name": "Technical Update",
                "content": """
                The new API v2.0 will be deployed next week. All engineering teams should
                review the migration guide and update their services accordingly. Breaking
                changes are documented in the changelog.
                """,
                "expected_recipients": ["Engineering"]
            },
            {
                "name": "PR Announcement",
                "content": """
                We are excited to announce our new partnership with TechCorp. This collaboration
                will expand our market reach and bring innovative solutions to our customers.
                Press release scheduled for Monday morning.
                """,
                "expected_recipients": ["PR", "Executive"]
            },
            {
                "name": "Company-Wide Policy",
                "content": """
                Effective immediately, all employees are required to complete the annual
                cybersecurity training by the end of this month. This is a mandatory
                compliance requirement for all staff members.
                """,
                "expected_recipients": ["All Employees", "HR"]
            },
            {
                "name": "HR Policy Update",
                "content": """
                The remote work policy has been updated to allow up to 3 days per week
                of remote work for eligible positions. Managers should discuss arrangements
                with their team members.
                """,
                "expected_recipients": ["HR", "All Employees"]
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await self.client.get_recipient_suggestion(test_case["content"])
                
                success = (
                    "error" not in result or result["error"] is None
                ) and len(result.get("recipients", [])) > 0
                
                self.print_result(test_case["name"], result, success)
                self.test_results.append({
                    "test": test_case["name"],
                    "tool": "get_recipient_suggestion",
                    "success": success,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Test failed: {test_case['name']} - {e}")
                self.print_result(test_case["name"], {"error": str(e)}, False)
    
    async def test_document_improvement(self):
        """Test improve_document tool with various documents."""
        self.print_separator("TESTING: improve_document")
        
        test_cases = [
            {
                "name": "Grammar Issues",
                "content": """
                this document need to be more better and clear for everyone to understand 
                it good. we should make sure its professional and easy to read.
                """
            },
            {
                "name": "Unclear Structure",
                "content": """
                The meeting yesterday was about the project and we talked about deadlines
                and also budget stuff and some people said things about the timeline but
                we need to decide soon.
                """
            },
            {
                "name": "Informal Tone",
                "content": """
                Hey guys, so like we gotta finish this thing by Friday or whatever. 
                Make sure u check the docs and stuff. Thx!
                """
            },
            {
                "name": "Redundant Content",
                "content": """
                The report shows that the results indicate that the findings demonstrate
                that the data suggests that sales have increased. The increase in sales
                is shown by the data in the report.
                """
            },
            {
                "name": "Technical Jargon",
                "content": """
                We need to refactor the codebase to implement DRY principles and reduce
                technical debt by leveraging microservices architecture and containerization
                paradigms for optimal scalability.
                """
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await self.client.improve_document(test_case["content"])
                
                success = (
                    "error" not in result or result["error"] is None
                ) and result.get("improved_content") != test_case["content"]
                
                self.print_result(test_case["name"], result, success)
                self.test_results.append({
                    "test": test_case["name"],
                    "tool": "improve_document",
                    "success": success,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Test failed: {test_case['name']} - {e}")
                self.print_result(test_case["name"], {"error": str(e)}, False)
    
    async def test_list_tools(self):
        """Test listing available tools."""
        self.print_separator("TESTING: list_tools")
        
        try:
            tools = await self.client.list_tools()
            
            success = len(tools) == 2 and \
                     "get_recipient_suggestion" in tools and \
                     "improve_document" in tools
            
            self.print_result("List Tools", tools, success)
            self.test_results.append({
                "test": "List Tools",
                "tool": "list_tools",
                "success": success,
                "result": tools
            })
            
        except Exception as e:
            logger.error(f"Test failed: List Tools - {e}")
            self.print_result("List Tools", {"error": str(e)}, False)
    
    async def test_edge_cases(self):
        """Test edge cases and error handling."""
        self.print_separator("TESTING: Edge Cases")
        
        edge_cases = [
            {
                "name": "Empty Document",
                "tool": "get_recipient_suggestion",
                "content": ""
            },
            {
                "name": "Very Short Document",
                "tool": "improve_document",
                "content": "Hi."
            },
            {
                "name": "Very Long Document",
                "tool": "get_recipient_suggestion",
                "content": "This is a test. " * 500
            },
            {
                "name": "Special Characters",
                "tool": "improve_document",
                "content": "Test @#$% document with special chars & symbols!"
            }
        ]
        
        for test_case in edge_cases:
            try:
                if test_case["tool"] == "get_recipient_suggestion":
                    result = await self.client.get_recipient_suggestion(test_case["content"])
                else:
                    result = await self.client.improve_document(test_case["content"])
                
                # For edge cases, we just check that we get a response without crashing
                success = result is not None
                
                self.print_result(test_case["name"], result, success)
                self.test_results.append({
                    "test": test_case["name"],
                    "tool": test_case["tool"],
                    "success": success,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Test failed: {test_case['name']} - {e}")
                self.print_result(test_case["name"], {"error": str(e)}, False)
    
    def print_summary(self):
        """Print test summary."""
        self.print_separator("TEST SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']} ({result['tool']})")
        
        self.print_separator()
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("Starting MCP Client Tests...")
        
        async with self.client.connect():
            logger.info("MCP Client connected successfully")
            
            # Run all test suites
            await self.test_list_tools()
            await self.test_recipient_suggestions()
            await self.test_document_improvement()
            await self.test_edge_cases()
            
            # Print summary
            self.print_summary()


async def main():
    """Main test runner."""
    tester = MCPClientTester()
    
    try:
        await tester.run_all_tests()
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        raise


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                  MCP Client Test Suite                         ║
    ║                                                                ║
    ║  This will test both MCP tools with various scenarios:        ║
    ║  - get_recipient_suggestion (6 test cases)                    ║
    ║  - improve_document (5 test cases)                            ║
    ║  - Edge cases (4 test cases)                                  ║
    ║  - Tool listing (1 test case)                                 ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
