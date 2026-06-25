import logging
import webbrowser
from typing import Optional
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self):
        self.registered_browsers = webbrowser._tryorder if hasattr(webbrowser, '_tryorder') else []
        logger.info(f"BrowserController initialized. Available browsers: {len(self.registered_browsers) if self.registered_browsers else 'default'}")
    
    def open_url(self, url: str) -> bool:
        try:
            if not url:
                logger.error("Empty URL provided")
                return False
            
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            
            logger.info(f"Opening URL: {url}")
            webbrowser.open(url)
            logger.info(f"Successfully opened: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open URL {url}: {e}")
            return False
    
    def search_google(self, query: str) -> bool:
        try:
            if not query or not query.strip():
                logger.error("Empty search query provided")
                return False
            
            encoded_query = quote(query.strip())
            url = f"https://www.google.com/search?q={encoded_query}"
            logger.info(f"Searching Google: {query}")
            webbrowser.open(url)
            logger.info(f"Successfully opened search for: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to search Google for {query}: {e}")
            return False


if __name__ == "__main__":
    controller = BrowserController()
    
    print("Testing BrowserController")
    print("=" * 60)
    
    test_cases = [
        ("Opening YouTube", controller.open_url, "https://www.youtube.com"),
        ("Opening GitHub", controller.open_url, "https://github.com"),
        ("Searching Google for AI jobs", controller.search_google, "AI jobs"),
        ("Opening with https", controller.open_url, "https://www.google.com"),
        ("Opening without protocol", controller.open_url, "www.stackoverflow.com"),
        ("Empty URL", controller.open_url, ""),
        ("Empty query", controller.search_google, "")
    ]
    
    for description, method, arg in test_cases:
        result = method(arg)
        status = "SUCCESS" if result else "FAILED"
        print(f"{description}: {status}")