import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    def __init__(self):
        self._load_llm_settings()
        self._load_app_settings()
        self._load_ui_settings()
        self._load_word_settings()
        self._load_browser_settings()
        self._load_session_settings()
        self._load_logging_settings()
        self._validate_settings()
        self._log_settings()

    def _load_llm_settings(self) -> None:
        self.llm_provider = os.getenv("LLM_PROVIDER", "nvidia")
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY", "")
        self.nvidia_base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        self.model_name = os.getenv("MODEL_NAME", "nvidia/nemotron-3-ultra-550b-a55b")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")

    def _load_app_settings(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Mimi")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.voice_enabled = os.getenv("VOICE_ENABLED", "False").lower() == "true"
        self.vision_enabled = os.getenv("VISION_ENABLED", "False").lower() == "true"
        self.memory_enabled = os.getenv("MEMORY_ENABLED", "False").lower() == "true"

    def _load_ui_settings(self) -> None:
        self.theme = os.getenv("UI_THEME", "dark")
        self.corner_radius = int(os.getenv("UI_CORNER_RADIUS", "15"))
        self.window_width = int(os.getenv("UI_WINDOW_WIDTH", "120"))
        self.window_height = int(os.getenv("UI_WINDOW_HEIGHT", "50"))
        self.position_x = int(os.getenv("UI_POSITION_X", "-130"))
        self.position_y = int(os.getenv("UI_POSITION_Y", "-80"))

    def _load_word_settings(self) -> None:
        self.word_visible = os.getenv("WORD_VISIBLE", "True").lower() == "true"
        self.word_auto_save = os.getenv("WORD_AUTO_SAVE", "False").lower() == "true"
        self.word_save_interval = int(os.getenv("WORD_SAVE_INTERVAL", "300"))

    def _load_browser_settings(self) -> None:
        self.browser_default = os.getenv("BROWSER_DEFAULT", "default")
        self.browser_open_in_new_tab = os.getenv("BROWSER_OPEN_IN_NEW_TAB", "True").lower() == "true"

    def _load_session_settings(self) -> None:
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "15"))

    def _load_logging_settings(self) -> None:
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/mimi.log")

    def _validate_settings(self) -> None:
        if self.llm_provider == "nvidia":
            if not self.nvidia_api_key:
                logger.error("NVIDIA_API_KEY not found in environment variables")
                raise ValueError("NVIDIA_API_KEY is required when using NVIDIA provider")
        elif self.llm_provider == "groq":
            if not self.groq_api_key:
                logger.error("GROQ_API_KEY not found in environment variables")
                raise ValueError("GROQ_API_KEY is required when using Groq provider")
        else:
            logger.warning(f"Unknown LLM provider: {self.llm_provider}, defaulting to NVIDIA")
            self.llm_provider = "nvidia"
            if not self.nvidia_api_key:
                raise ValueError("NVIDIA_API_KEY is required")

    def _log_settings(self) -> None:
        logger.info(f"LLM Provider: {self.llm_provider}")
        logger.info(f"Model: {self.model_name}")
        logger.info(f"Base URL: {self.nvidia_base_url}")
        logger.info(f"API Key Loaded: {'Yes' if (self.nvidia_api_key if self.llm_provider == 'nvidia' else self.groq_api_key) else 'No'}")
        logger.info(f"App Name: {self.app_name}")
        logger.info(f"Debug Mode: {self.debug}")
        logger.info(f"Session Timeout: {self.session_timeout_minutes} minutes")

    def get_api_key(self) -> Optional[str]:
        if self.llm_provider == "nvidia":
            return self.nvidia_api_key
        elif self.llm_provider == "groq":
            return self.groq_api_key
        return None

    def get_base_url(self) -> str:
        if self.llm_provider == "nvidia":
            return self.nvidia_base_url
        elif self.llm_provider == "groq":
            return "https://api.groq.com/openai/v1"
        return self.nvidia_base_url

    def get_model_name(self) -> str:
        return self.model_name


if __name__ == "__main__":
    print("Testing Settings")
    print("=" * 60)
    
    try:
        settings = Settings()
        
        print("\nLLM Settings:")
        print(f"  Provider: {settings.llm_provider}")
        print(f"  Model: {settings.model_name}")
        print(f"  Base URL: {settings.nvidia_base_url}")
        print(f"  API Key: {'Loaded' if settings.get_api_key() else 'Missing'}")
        
        print("\nApplication Settings:")
        print(f"  App Name: {settings.app_name}")
        print(f"  Debug: {settings.debug}")
        print(f"  Voice Enabled: {settings.voice_enabled}")
        print(f"  Vision Enabled: {settings.vision_enabled}")
        print(f"  Memory Enabled: {settings.memory_enabled}")
        
        print("\nUI Settings:")
        print(f"  Theme: {settings.theme}")
        print(f"  Corner Radius: {settings.corner_radius}")
        print(f"  Window Size: {settings.window_width}x{settings.window_height}")
        
        print("\nWord Settings:")
        print(f"  Visible: {settings.word_visible}")
        print(f"  Auto Save: {settings.word_auto_save}")
        print(f"  Save Interval: {settings.word_save_interval}s")
        
        print("\nSession Settings:")
        print(f"  Timeout: {settings.session_timeout_minutes} minutes")
        
        print("\nSettings loaded successfully!")
        
    except Exception as e:
        print(f"Error loading settings: {e}")