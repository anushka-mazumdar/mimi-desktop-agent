import logging
import json
from typing import Dict, Any
from llm.llm_client import LLMClient
from llm.schemas import AgentResponse, IntentType
from agent.executor import Executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MimiAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.executor = Executor()
        logger.info("MimiAgent initialized successfully")

    def process_command(self, command: str) -> Dict[str, Any]:
        try:
            logger.info(f"Received Command: {command}")
            
            if not command or not command.strip():
                logger.warning("Empty command received")
                response = self._error_response("empty_command")
                return {
                    "response": response,
                    "execution_success": False
                }
            
            logger.info("LLM Analysis Started")
            agent_response = self.llm_client.analyze_command(command)
            logger.info("LLM Analysis Finished")
            
            logger.info(f"Application: {agent_response.application}")
            logger.info(f"Intent: {agent_response.intent}")
            logger.info(f"Action: {agent_response.action}")
            if agent_response.target:
                logger.info(f"Target: {agent_response.target}")
            if agent_response.parameters:
                logger.info(f"Parameters: {json.dumps(agent_response.parameters, indent=2)}")
            if agent_response.url:
                logger.info(f"URL: {agent_response.url}")
            logger.info(f"Confidence: {agent_response.confidence}")
            
            if agent_response.parameters.get("clarification_required", False):
                logger.info("Clarification required, returning to UI layer")
                return {
                    "response": agent_response,
                    "execution_success": False
                }
            
            if agent_response.intent == IntentType.UNKNOWN:
                logger.warning("Unknown intent detected, skipping execution")
                return {
                    "response": agent_response,
                    "execution_success": False
                }
            
            logger.info("Executor Started")
            execution_success = self.executor.execute(agent_response)
            logger.info("Executor Finished")
            
            if execution_success:
                logger.info("Execution Successful")
            else:
                logger.warning("Execution Failed")
            
            return {
                "response": agent_response,
                "execution_success": execution_success
            }
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            response = self._error_response(str(e))
            return {
                "response": response,
                "execution_success": False
            }

    def _error_response(self, error_message: str) -> AgentResponse:
        return AgentResponse(
            intent=IntentType.UNKNOWN,
            application="unknown",
            target="",
            action="error",
            parameters={},
            url="",
            confidence=0.0
        )


if __name__ == "__main__":
    test_commands = [
        "Open YouTube",
        "Search Google for AI jobs",
        "Open GitHub",
        "Insert a blank page",
        "Center the selected text",
        "Justify the whole document",
        "Rewrite the selected paragraph professionally",
        "Summarize the selected text",
        "Save the document",
        "Create a new document"
    ]

    print("MimiAgent Test")
    print("=" * 60)

    agent = MimiAgent()

    for command in test_commands:
        print(f"\nCommand: {command}")
        result = agent.process_command(command)
        
        response = result["response"]
        execution_success = result["execution_success"]
        
        print(f"Application: {response.application}")
        print(f"Intent: {response.intent}")
        print(f"Target: {response.target}")
        print(f"Action: {response.action}")
        if response.parameters:
            print(f"Parameters: {json.dumps(response.parameters, indent=2)}")
        if response.url:
            print(f"URL: {response.url}")
        print(f"Confidence: {response.confidence}")
        print(f"Execution Success: {execution_success}")
        print("-" * 40)