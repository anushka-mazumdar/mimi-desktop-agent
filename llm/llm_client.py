import os
import json
import logging
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from config.settings import Settings
from config.prompts import get_system_prompt
from llm.schemas import AgentResponse, IntentType

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.settings = Settings()
        
        if self.settings.llm_provider == "nvidia":
            self.api_key = self.settings.nvidia_api_key
            self.base_url = self.settings.nvidia_base_url
            self.model = self.settings.model_name
        else:
            logger.warning(f"Unsupported provider: {self.settings.llm_provider}, defaulting to NVIDIA")
            self.api_key = self.settings.nvidia_api_key
            self.base_url = self.settings.nvidia_base_url
            self.model = self.settings.model_name
        
        if not self.api_key:
            logger.error("API key not found")
            raise ValueError("API key is required")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
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
            "paragraph": "Convert the following text into a well-structured paragraph. Ensure smooth flow and logical organization.\n\nText: {text}\n\nParagraph:",
            "explain_formula": "Explain the following Excel formula in simple terms. Describe what it calculates and how it works.\n\nFormula: {text}\n\nExplanation:",
            "summarize_table": "Summarize the following spreadsheet data. Identify key totals, trends, and notable patterns. Keep it brief.\n\nData:\n{text}\n\nSummary:",
            "generate_sample_data": "Generate realistic sample spreadsheet data based on the following description. Return ONLY the data as rows, one row per line, with comma-separated values, no headers explanation and no additional commentary.\n\nDescription: {text}\n\nData:"
        }
        
        logger.info(f"LLMClient initialized with provider: {self.settings.llm_provider}")
        logger.info(f"Model: {self.model}")
        logger.info(f"Base URL: {self.base_url}")

    def analyze_command(self, command: str, session_context: Optional[str] = None) -> AgentResponse:
        try:
            logger.info(f"Analyzing command: {command}")
            
            if session_context:
                logger.info("Session context provided")
                full_prompt = f"{session_context}\n\nUser: {command}"
                logger.info("Enhanced prompt with context")
            else:
                full_prompt = command
            
            logger.info("API Request Started")
            start_time = time.time()
            
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
            
            elapsed_time = time.time() - start_time
            logger.info(f"API Response Received in {elapsed_time:.2f}s")
            
            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Raw LLM response: {raw_response[:200]}...")
            
            cleaned_response = self._clean_json_response(raw_response)
            parsed_response = json.loads(cleaned_response)
            logger.info("JSON Parsed Successfully")
            
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
            
            logger.info("Sending transformation request to LLM")
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048,
                top_p=0.95
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Transformation completed in {elapsed_time:.2f}s")
            
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
    print("Testing LLMClient with NVIDIA Build API")
    print("=" * 60)
    
    try:
        client = LLMClient()
        
        print(f"\nProvider: {client.settings.llm_provider}")
        print(f"Model: {client.model}")
        print(f"Base URL: {client.base_url}")
        
        test_commands = [
            "Open YouTube",
            "Add a blank page in Word",
            "Center the selected text",
            "Rewrite this professionally"
        ]
        
        print("\n" + "=" * 60)
        print("Testing Command Analysis")
        print("=" * 60)
        
        for command in test_commands:
            print(f"\nCommand: {command}")
            start_time = time.time()
            result = client.analyze_command(command)
            elapsed = time.time() - start_time
            
            print(f"Parsed AgentResponse ({elapsed:.2f}s):")
            print(f"  Application: {result.application}")
            print(f"  Intent: {result.intent}")
            print(f"  Target: {result.target}")
            print(f"  Action: {result.action}")
            if result.parameters:
                print(f"  Parameters: {json.dumps(result.parameters, indent=2)}")
            print(f"  Confidence: {result.confidence}")
            print("-" * 40)
        
        print("\n" + "=" * 60)
        print("Testing Text Transformation")
        print("=" * 60)
        
        test_text = "This is a test document. It needs to be improved. The grammar is not great and it could be more professional."
        
        test_actions = [
            ("rewrite", {}),
            ("rewrite", {"tone": "professional"}),
            ("summarize", {}),
            ("fix_grammar", {})
        ]
        
        for action, params in test_actions:
            print(f"\nAction: {action} (params: {params})")
            start_time = time.time()
            result = client.transform_text(test_text, action, params)
            elapsed = time.time() - start_time
            
            if result:
                print(f"Result ({elapsed:.2f}s): {result[:150]}...")
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
  - Last Result: Success"""
        
        command = "Insert a blank page"
        print(f"Command: {command}")
        print(f"With context:\n{context}")
        
        start_time = time.time()
        result = client.analyze_command(command, session_context=context)
        elapsed = time.time() - start_time
        
        print(f"\nParsed AgentResponse ({elapsed:.2f}s):")
        print(f"  Application: {result.application}")
        print(f"  Intent: {result.intent}")
        print(f"  Action: {result.action}")
        print(f"  Confidence: {result.confidence}")
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()