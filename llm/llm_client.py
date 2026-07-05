import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from config.prompts import get_system_prompt
from llm.schemas import AgentResponse, IntentType

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY is required")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        self.system_prompt = get_system_prompt()
        logger.info("LLMClient initialized successfully")

    def analyze_command(self, command: str) -> AgentResponse:
        try:
            logger.info(f"Analyzing command: {command}")
            
            full_prompt = f"{self.system_prompt}\n\nUser: {command}\nMimi:"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": command}
                ],
                temperature=0.1,
                max_tokens=256,
                top_p=0.95
            )
            
            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Raw LLM response: {raw_response}")
            
            cleaned_response = self._clean_json_response(raw_response)
            parsed_response = json.loads(cleaned_response)
            
            return self._parse_to_agent_response(parsed_response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._error_response()
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._error_response()

    def _clean_json_response(self, raw_response: str) -> str:
        cleaned = raw_response.strip()
        
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        return cleaned.strip()

    def _parse_to_agent_response(self, parsed_data: dict) -> AgentResponse:
        try:
            intent = IntentType(parsed_data.get("intent", "unknown"))
            application = parsed_data.get("application", "system")
            target = parsed_data.get("target", "")
            action = parsed_data.get("action", "")
            parameters = parsed_data.get("parameters", {})
            url = parsed_data.get("url", "")
            confidence = float(parsed_data.get("confidence", 0.0))
            
            if not isinstance(parameters, dict):
                parameters = {}
            
            if intent == IntentType.OPEN_WEBSITE and url:
                logger.info(f"Website URL detected: {url}")
            
            logger.info(f"Application: {application}")
            logger.info(f"Intent: {intent}")
            logger.info(f"Action: {action}")
            logger.info(f"Target: {target}")
            if parameters:
                logger.info(f"Parameters: {json.dumps(parameters, indent=2)}")
            if url:
                logger.info(f"URL: {url}")
            logger.info(f"Confidence: {confidence}")
            
            return AgentResponse(
                intent=intent,
                application=application,
                target=target,
                action=action,
                parameters=parameters,
                url=url,
                confidence=confidence
            )
        except ValueError as e:
            logger.error(f"Intent type error: {e}")
            return self._error_response()
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return self._error_response()

    def _error_response(self) -> AgentResponse:
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
        "Add a blank page in Word",
        "Center the heading on the first page",
        "Draw a blue circle in Paint",
        "Calculate the sum of selected cells in Excel",
        "Rewrite the selected paragraph professionally",
        "Some random command that doesnt make sense"
    ]

    try:
        client = LLMClient()
        
        for command in test_commands:
            print("=" * 60)
            print(f"Command: {command}")
            result = client.analyze_command(command)
            
            print(f"\nParsed AgentResponse:")
            print(f"  Intent: {result.intent}")
            print(f"  Application: {result.application}")
            print(f"  Target: {result.target}")
            print(f"  Action: {result.action}")
            if result.parameters:
                print(f"  Parameters: {json.dumps(result.parameters, indent=2)}")
            if result.url:
                print(f"  URL: {result.url}")
            print(f"  Confidence: {result.confidence}")
            print("=" * 60)
            
    except Exception as e:
        print(f"Test failed: {e}")