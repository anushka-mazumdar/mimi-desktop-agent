# agent/mimi.py
import logging
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
            logger.info(f"Command received: {command}")
            
            if not command or not command.strip():
                logger.warning("Empty command received")
                response = self._error_response("empty_command")
                return {
                    "response": response,
                    "execution_success": False
                }
            
            logger.info("Sending to LLMClient...")
            agent_response = self.llm_client.analyze_command(command)
            logger.info(f"LLM response received: Intent={agent_response.intent}, Target={agent_response.target}, Action={agent_response.action}")
            
            if agent_response.intent == IntentType.UNKNOWN:
                logger.warning("Unknown intent detected, skipping execution")
                return {
                    "response": agent_response,
                    "execution_success": False
                }
            
            logger.info("Sending to Executor...")
            execution_success = self.executor.execute(agent_response)
            
            if execution_success:
                logger.info("Execution successful")
            else:
                logger.warning("Execution failed")
            
            logger.info("Final result returned")
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
            target="",
            action="error",
            url="",
            confidence=0.0
            )


if __name__ == "__main__":
    test_commands = [
        "Open YouTube",
        "Open GitHub",
        "Search Google for AI jobs",
        "Open LinkedIn",
        "Add a blank page in Word",
        "Some random command that doesnt make sense"
    ]

    print("MimiAgent Test")
    print("=" * 60)

    agent = MimiAgent()

    for command in test_commands:
        print(f"\nCommand: {command}")
        result = agent.process_command(command)
        
        response = result["response"]
        execution_success = result["execution_success"]
        
        print(f"Intent: {response.intent}")
        print(f"Target: {response.target}")
        print(f"Action: {response.action}")
        if response.url:
            print(f"URL: {response.url}")
        print(f"Confidence: {response.confidence}")
        print(f"Execution Success: {execution_success}")
        print("-" * 40)