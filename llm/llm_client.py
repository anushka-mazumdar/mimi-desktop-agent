import os
import json
import logging
from typing import Optional, Dict, Any
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
        
        self.transform_prompts = {
            "rewrite": "Rewrite the following text to make it better. Improve clarity, flow, and engagement. Keep the same general meaning but make it more polished.\n\nText: {text}\n\nImproved version:",
            "rewrite_professional": "Rewrite the following text to sound more professional and formal. Use appropriate business language and tone.\n\nText: {text}\n\nProfessional version:",
            "rewrite_casual": "Rewrite the following text to sound more casual and conversational. Make it friendly and approachable.\n\nText: {text}\n\nCasual version:",
            "summarize": "Summarize the following text concisely. Capture only the most important key points. Keep it brief.\n\nText: {text}\n\nSummary:",
            "translate": "Translate the following text to {language}. Provide only the translation, no additional text.\n\nText: {text}\n\nTranslation:",
            "fix_grammar": "Fix the grammar and spelling in the following text. Correct any errors while preserving the original meaning and style.\n\nText: {text}\n\nCorrected version:",
            "expand": "Expand and elaborate on the following text. Add more detail, examples, and depth. Make it more comprehensive.\n\nText: {text}\n\nExpanded version:",
            "shorten": "Shorten the following text concisely. Remove unnecessary words, repetition, and fluff while preserving key meaning.\n\nText: {text}\n\nShortened version:",
            "bullets": "Convert the following text into bullet points. Use clear, concise points. Format as a bulleted list.\n\nText: {text}\n\nBullet points:",
            "paragraph": "Convert the following text into a well-structured paragraph. Ensure smooth flow and logical organization.\n\nText: {text}\n\nParagraph:"
        }
        
        logger.info("LLMClient initialized successfully")

    def analyze_command(self, command: str, session_context: Optional[str] = None) -> AgentResponse:
        try:
            logger.info(f"Analyzing command: {command}")
            
            if session_context:
                logger.info("Session context provided")
                full_prompt = f"{session_context}\n\nUser: {command}"
                logger.info(f"Enhanced prompt with context")
            else:
                full_prompt = command
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
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

    def transform_text(self, text: str, action: str, parameters: Dict[str, Any] = None) -> Optional[str]:
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for transformation")
                return None
            
            if parameters is None:
                parameters = {}
            
            logger.info(f"Transforming text with action: {action}")
            
            mapped_action = self._map_action(action, parameters)
            
            if mapped_action not in self.transform_prompts:
                logger.error(f"Unsupported transformation action: {action}")
                return None
            
            prompt_template = self.transform_prompts[mapped_action]
            
            if mapped_action == "translate":
                language = parameters.get("language", "English")
                prompt = prompt_template.format(text=text, language=language)
            else:
                prompt = prompt_template.format(text=text)
            
            logger.info(f"Sending transformation request to LLM")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048,
                top_p=0.95
            )
            
            transformed_text = response.choices[0].message.content.strip()
            logger.info(f"Transformation successful. Result length: {len(transformed_text)}")
            
            return transformed_text
            
        except Exception as e:
            logger.error(f"Text transformation failed: {e}")
            return None

    def _map_action(self, action: str, parameters: Dict[str, Any]) -> str:
        if action == "rewrite":
            tone = parameters.get("tone", "better")
            if tone == "professional":
                return "rewrite_professional"
            elif tone == "casual":
                return "rewrite_casual"
            else:
                return "rewrite"
        
        return action

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
            
        print("\n" + "=" * 60)
        print("Testing Text Transformation")
        print("=" * 60)
        
        test_text = "This is a test document. It needs to be improved. The grammar is not great and it could be more professional."
        
        test_actions = [
            ("rewrite", {}),
            ("rewrite", {"tone": "professional"}),
            ("summarize", {}),
            ("fix_grammar", {}),
            ("expand", {}),
            ("shorten", {}),
            ("bullets", {}),
            ("paragraph", {})
        ]
        
        for action, params in test_actions:
            print(f"\nAction: {action} (params: {params})")
            result = client.transform_text(test_text, action, params)
            if result:
                print(f"Result: {result[:200]}...")
            else:
                print("Result: FAILED")
            print("-" * 40)
            
        print("\n" + "=" * 60)
        print("Testing Session Context")
        print("=" * 60)
        
        context = """Session Context:
  - Current Application: Word
  - Current Document: Report.docx
  - Current Task: Editing Document
  - Last Action: insert_text
  - Last Result: Success
  - Last Activity: 02:30 PM"""
        
        print(f"With context:\n{context}")
        command = "Insert a blank page"
        result = client.analyze_command(command, session_context=context)
        print(f"\nParsed AgentResponse:")
        print(f"  Intent: {result.intent}")
        print(f"  Application: {result.application}")
        print(f"  Target: {result.target}")
        print(f"  Action: {result.action}")
        print(f"  Confidence: {result.confidence}")
            
    except Exception as e:
        print(f"Test failed: {e}")