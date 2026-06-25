import logging
from typing import Optional
from llm.schemas import AgentResponse, IntentType
from capabilities.browser.browser_controller import BrowserController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Executor:
    def __init__(self):
        self.browser = BrowserController()
        logger.info("Executor initialized successfully")

    def execute(self, response: AgentResponse) -> bool:
        try:
            logger.info(f"Executing response: Intent={response.intent}, Target={response.target}, Action={response.action}")
            
            if response.intent == IntentType.OPEN_WEBSITE:
                return self._execute_open_website(response)
            
            elif response.intent == IntentType.BROWSER_SEARCH:
                return self._execute_browser_search(response)
            
            elif response.intent == IntentType.WORD_ACTION:
                return self._execute_word_action(response)
            
            elif response.intent == IntentType.EXCEL_ACTION:
                return self._execute_excel_action(response)
            
            elif response.intent == IntentType.PAINT_ACTION:
                return self._execute_paint_action(response)
            
            else:
                logger.warning(f"Unknown intent type: {response.intent}")
                return False
                
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return False

    def _execute_open_website(self, response: AgentResponse) -> bool:
        try:
            if not response.url:
                logger.error("No URL provided for open_website intent")
                return False
            
            logger.info(f"Opening website: {response.url}")
            result = self.browser.open_url(response.url)
            
            if result:
                logger.info(f"Successfully opened {response.url}")
            else:
                logger.error(f"Failed to open {response.url}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing open_website: {e}")
            return False

    def _execute_browser_search(self, response: AgentResponse) -> bool:
        try:
            if not response.target:
                logger.error("No search query provided for browser_search intent")
                return False
            
            logger.info(f"Searching Google for: {response.target}")
            result = self.browser.search_google(response.target)
            
            if result:
                logger.info(f"Successfully searched for {response.target}")
            else:
                logger.error(f"Failed to search for {response.target}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing browser_search: {e}")
            return False

    def _execute_word_action(self, response: AgentResponse) -> bool:
        logger.info(f"Word action requested: {response.action} on {response.target}")
        logger.warning("Word actions not yet implemented")
        return False

    def _execute_excel_action(self, response: AgentResponse) -> bool:
        logger.info(f"Excel action requested: {response.action} on {response.target}")
        logger.warning("Excel actions not yet implemented")
        return False

    def _execute_paint_action(self, response: AgentResponse) -> bool:
        logger.info(f"Paint action requested: {response.action} on {response.target}")
        logger.warning("Paint actions not yet implemented")
        return False


if __name__ == "__main__":
    from llm.schemas import AgentResponse, IntentType
    
    print("Testing Executor")
    print("=" * 60)
    
    executor = Executor()
    
    test_responses = [
        AgentResponse(
            intent=IntentType.OPEN_WEBSITE,
            target="youtube",
            action="open",
            url="https://www.youtube.com",
            confidence=0.95
        ),
        AgentResponse(
            intent=IntentType.OPEN_WEBSITE,
            target="github",
            action="open",
            url="https://github.com",
            confidence=0.95
        ),
        AgentResponse(
            intent=IntentType.BROWSER_SEARCH,
            target="AI jobs",
            action="search",
            url="",
            confidence=0.95
        ),
        AgentResponse(
            intent=IntentType.BROWSER_SEARCH,
            target="Python tutorials",
            action="search",
            url="",
            confidence=0.90
        ),
        AgentResponse(
            intent=IntentType.WORD_ACTION,
            target="document",
            action="insert_blank_page",
            url="",
            confidence=0.85
        ),
        AgentResponse(
            intent=IntentType.UNKNOWN,
            target="",
            action="",
            url="",
            confidence=0.0
        )
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"Test {i}:")
        print(f"  Intent: {response.intent}")
        print(f"  Target: {response.target}")
        print(f"  Action: {response.action}")
        if response.url:
            print(f"  URL: {response.url}")
        
        result = executor.execute(response)
        status = "SUCCESS" if result else "FAILED"
        print(f"  Result: {status}")
        print("-" * 40)