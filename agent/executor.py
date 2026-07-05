import logging
from typing import Optional
from llm.schemas import AgentResponse, IntentType
from capabilities.browser.browser_controller import BrowserController
from capabilities.office.word_controller import WordController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Executor:
    def __init__(self):
        self.browser = None
        self.word = None
        logger.info("Executor initialized successfully")

    def execute(self, response: AgentResponse) -> bool:
        try:
            logger.info(f"Executing response: Application={response.application}, Intent={response.intent}, Action={response.action}")
            
            if response.application == "browser":
                return self._execute_browser(response)
            
            elif response.application == "word":
                return self._execute_word(response)
            
            else:
                logger.warning(f"Application not supported: {response.application}")
                return False
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return False

    def _get_browser(self) -> BrowserController:
        if self.browser is None:
            logger.info("Initializing BrowserController")
            self.browser = BrowserController()
        return self.browser

    def _get_word(self) -> WordController:
        if self.word is None:
            logger.info("Initializing WordController")
            self.word = WordController()
        return self.word

    def _execute_browser(self, response: AgentResponse) -> bool:
        try:
            logger.info(f"Browser action: {response.action}, Target: {response.target}")
            browser = self._get_browser()
            
            if response.intent == IntentType.OPEN_WEBSITE:
                if not response.url:
                    logger.error("No URL provided for open_website intent")
                    return False
                result = browser.open_url(response.url)
                logger.info(f"Browser execution result: {result}")
                return result
            
            elif response.intent == IntentType.BROWSER_SEARCH:
                if not response.target:
                    logger.error("No search query provided for browser_search intent")
                    return False
                result = browser.search_google(response.target)
                logger.info(f"Browser execution result: {result}")
                return result
            
            else:
                logger.warning(f"Unsupported browser intent: {response.intent}")
                return False
                
        except Exception as e:
            logger.error(f"Browser execution failed: {e}")
            return False

    def _execute_word(self, response: AgentResponse) -> bool:
        try:
            logger.info(f"Word action: {response.action}, Target: {response.target}")
            word = self._get_word()
            
            result = word.execute(
                action=response.action,
                target=response.target,
                parameters=response.parameters
            )
            
            logger.info(f"Word execution result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Word execution failed: {e}")
            return False


if __name__ == "__main__":
    from llm.schemas import AgentResponse, IntentType
    
    print("Testing Executor")
    print("=" * 60)
    
    executor = Executor()
    
    test_responses = [
        AgentResponse(
            intent=IntentType.OPEN_WEBSITE,
            application="browser",
            target="youtube",
            action="open",
            parameters={},
            url="https://www.youtube.com",
            confidence=0.95
        ),
        AgentResponse(
            intent=IntentType.BROWSER_SEARCH,
            application="browser",
            target="AI jobs",
            action="search",
            parameters={},
            url="",
            confidence=0.95
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            application="word",
            target="document",
            action="create_document",
            parameters={},
            url="",
            confidence=0.90
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            application="word",
            target="document",
            action="insert_blank_page",
            parameters={},
            url="",
            confidence=0.85
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            application="word",
            target="document",
            action="align_center",
            parameters={},
            url="",
            confidence=0.85
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            application="word",
            target="selection",
            action="rewrite_selection",
            parameters={"tone": "professional"},
            url="",
            confidence=0.80
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            application="word",
            target="selection",
            action="summarize_selection",
            parameters={},
            url="",
            confidence=0.80
        ),
        AgentResponse(
            intent=IntentType.UNKNOWN,
            application="system",
            target="",
            action="",
            parameters={},
            url="",
            confidence=0.0
        )
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"Test {i}:")
        print(f"  Application: {response.application}")
        print(f"  Intent: {response.intent}")
        print(f"  Action: {response.action}")
        if response.target:
            print(f"  Target: {response.target}")
        if response.url:
            print(f"  URL: {response.url}")
        
        result = executor.execute(response)
        status = "SUCCESS" if result else "FAILED"
        print(f"  Result: {status}")
        print("-" * 40)