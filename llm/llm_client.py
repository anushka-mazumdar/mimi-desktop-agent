# llm/llm_client.py
import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from config.prompts import get_system_prompt
from llm.schemas import AgentResponse, IntentType
from config.settings import GROQ_API_KEY, MODEL_NAME, LLM_PROVIDER

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY is required")
        
        self.model_name = MODEL_NAME or "llama-3.3-70b-versatile"
        self.provider = LLM_PROVIDER or "groq"
        
        self.client = Groq(api_key=self.api_key)
        self.system_prompt = get_system_prompt()
        
        logger.info(f"LLMClient initialized successfully")
        logger.info(f"Provider: {self.provider}")
        logger.info(f"Model: {self.model_name}")

    def analyze_command(self, command: str) -> AgentResponse:
        try:
            logger.info(f"Analyzing command: {command}")
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": command}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
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
            target = parsed_data.get("target", "")
            action = parsed_data.get("action", "")
            url = parsed_data.get("url", "")
            confidence = float(parsed_data.get("confidence", 0.0))
            
            if intent == IntentType.OPEN_WEBSITE and url:
                logger.info(f"Website URL detected: {url}")
            
            return AgentResponse(
                intent=intent,
                target=target,
                action=action,
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
            target="",
            action="error",
            url="",
            confidence=0.0
        )


if __name__ == "__main__":
    test_commands = [
        "Open YouTube",
        "Search Google for AI jobs",
        "Add a blank page in Word",
        "Draw a circle in Paint",
        "Open GitHub"
    ]

    try:
        client = LLMClient()
        
        for command in test_commands:
            print("=" * 60)
            print(f"Command: {command}")
            result = client.analyze_command(command)
            print(f"Parsed AgentResponse: {result}")
            print(f"Intent: {result.intent}")
            print(f"Target: {result.target}")
            print(f"Action: {result.action}")
            if result.url:
                print(f"URL: {result.url}")
            print(f"Confidence: {result.confidence}")
            print("=" * 60)
            
    except Exception as e:
        print(f"Test failed: {e}")