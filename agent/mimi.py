import logging
import json
from typing import Dict, Any
from llm.llm_client import LLMClient
from llm.schemas import AgentResponse, IntentType
from agent.executor import Executor
from agent.session_context import SessionContextManager, ApplicationType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MimiAgent:
    def __init__(self):
        self.llm_client = LLMClient()
        self.executor = Executor(llm_client=self.llm_client)
        self.session_context = SessionContextManager(inactivity_timeout_minutes=15)
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
            
            session_prompt = self.session_context.to_prompt()
            if session_prompt:
                logger.info("Session context available, including in analysis")
            
            logger.info("LLM Analysis Started")
            agent_response = self.llm_client.analyze_command(command, session_context=session_prompt if session_prompt else None)
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
                self._update_session_context(agent_response, success=True)
            else:
                logger.warning("Execution Failed")
                self._update_session_context(agent_response, success=False)
            
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

    def _update_session_context(self, response: AgentResponse, success: bool) -> None:
        try:
            if not success:
                logger.info("Execution failed, not updating session context")
                return
            
            application = self._normalize_application(response.application)
            
            target = response.target if response.target else None
            
            self.session_context.update(
                application=application if application != "none" else None,
                document=target if application == "word" else None,
                task=f"{response.action} on {response.target}" if response.target else response.action,
                action=response.action,
                target=target,
                parameters=response.parameters if response.parameters else None,
                success=success
            )
            
            logger.info(f"Session context updated: Application={application}, Action={response.action}")
            
        except Exception as e:
            logger.error(f"Failed to update session context: {e}")

    def _normalize_application(self, app: str) -> str:
        app_lower = app.lower().strip()
        
        valid_apps = ["browser", "word", "excel", "paint", "powerpoint", "system", "none"]
        
        if app_lower in valid_apps:
            return app_lower
        
        if "word" in app_lower:
            return "word"
        elif "excel" in app_lower:
            return "excel"
        elif "paint" in app_lower:
            return "paint"
        elif "browser" in app_lower:
            return "browser"
        elif "powerpoint" in app_lower:
            return "powerpoint"
        
        return "system"

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
        "Open GitHub",
        "Search Google for AI jobs",
        "Open word",
        "Create a new document",
        "Insert a blank page",
        "Center this",
        "Rewrite this professionally",
        "Summarize this"
    ]

    print("MimiAgent Test with Session Context")
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
        
        print("\nCurrent Session Context:")
        print(agent.session_context.to_prompt())
        print("-" * 40)