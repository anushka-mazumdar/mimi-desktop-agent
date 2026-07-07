import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApplicationType(str, Enum):
    NONE = "none"
    BROWSER = "browser"
    WORD = "word"
    EXCEL = "excel"
    PAINT = "paint"
    POWERPOINT = "powerpoint"
    SYSTEM = "system"


@dataclass
class SessionContext:
    current_application: ApplicationType = ApplicationType.NONE
    current_document: str = ""
    current_task: str = ""
    last_action: str = ""
    last_target: str = ""
    last_parameters: Dict[str, Any] = field(default_factory=dict)
    last_success: Optional[bool] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


class SessionContextManager:
    def __init__(self, inactivity_timeout_minutes: int = 15):
        self.context = SessionContext()
        self.inactivity_timeout_seconds = inactivity_timeout_minutes * 60
        self._active = True
        logger.info(f"SessionContextManager initialized with {inactivity_timeout_minutes} minute timeout")

    def update(self, application: Optional[str] = None, document: Optional[str] = None,
               task: Optional[str] = None, action: Optional[str] = None,
               target: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None,
               success: Optional[bool] = None) -> None:
        """Update the session context with new information."""
        try:
            if application is not None:
                self.context.current_application = self._normalize_application(application)
                logger.info(f"Updated application: {self.context.current_application}")
            
            if document is not None:
                self.context.current_document = document
                logger.info(f"Updated document: {document}")
            
            if task is not None:
                self.context.current_task = task
                logger.info(f"Updated task: {task}")
            
            if action is not None:
                self.context.last_action = action
                logger.info(f"Updated last action: {action}")
            
            if target is not None:
                self.context.last_target = target
                logger.info(f"Updated last target: {target}")
            
            if parameters is not None:
                self.context.last_parameters = parameters
                logger.info(f"Updated last parameters: {parameters}")
            
            if success is not None:
                self.context.last_success = success
                logger.info(f"Updated last success: {success}")
            
            self.context.last_updated = datetime.now()
            self._active = True
            
        except Exception as e:
            logger.error(f"Failed to update session context: {e}")

    def clear(self) -> None:
        """Clear the entire session context."""
        self.context = SessionContext()
        self._active = True
        logger.info("Session context cleared")

    def get_context(self) -> SessionContext:
        """Return the current session context."""
        self._check_inactivity()
        return self.context

    def has_active_application(self) -> bool:
        """Check if there is an active application in context."""
        self._check_inactivity()
        return self.context.current_application != ApplicationType.NONE

    def to_prompt(self) -> str:
        """
        Return a concise text summary for prepending to the LLM prompt.
        """
        self._check_inactivity()
        
        if not self.has_active_application():
            return ""
        
        parts = []
        
        if self.context.current_application != ApplicationType.NONE:
            app_name = self.context.current_application.value.capitalize()
            parts.append(f"Current Application: {app_name}")
        
        if self.context.current_document:
            parts.append(f"Current Document: {self.context.current_document}")
        
        if self.context.current_task:
            parts.append(f"Current Task: {self.context.current_task}")
        
        if self.context.last_action:
            parts.append(f"Last Action: {self.context.last_action}")
        
        if self.context.last_target:
            parts.append(f"Last Target: {self.context.last_target}")
        
        if self.context.last_success is not None:
            result = "Success" if self.context.last_success else "Failed"
            parts.append(f"Last Result: {result}")
        
        if self.context.last_updated:
            time_str = self.context.last_updated.strftime("%I:%M %p")
            parts.append(f"Last Activity: {time_str}")
        
        if not parts:
            return ""
        
        context_text = "Session Context:\n" + "\n".join(f"  - {p}" for p in parts)
        return context_text

    def _normalize_application(self, app: str) -> ApplicationType:
        """Normalize application string to ApplicationType enum."""
        app_lower = app.lower().strip()
        
        mapping = {
            "browser": ApplicationType.BROWSER,
            "word": ApplicationType.WORD,
            "excel": ApplicationType.EXCEL,
            "paint": ApplicationType.PAINT,
            "powerpoint": ApplicationType.POWERPOINT,
            "system": ApplicationType.SYSTEM
        }
        
        return mapping.get(app_lower, ApplicationType.SYSTEM)

    def _check_inactivity(self) -> None:
        """Check if context has expired due to inactivity."""
        if self._active and self.context.last_updated:
            elapsed = (datetime.now() - self.context.last_updated).total_seconds()
            if elapsed > self.inactivity_timeout_seconds:
                self._active = False
                logger.info(f"Session context expired after {elapsed:.0f} seconds of inactivity")
                self.clear()
                logger.info("Session context cleared due to inactivity")

    def set_inactivity_timeout(self, minutes: int) -> None:
        """Set the inactivity timeout in minutes."""
        self.inactivity_timeout_seconds = minutes * 60
        logger.info(f"Inactivity timeout set to {minutes} minutes")


if __name__ == "__main__":
    print("Testing SessionContextManager")
    print("=" * 60)
    
    session = SessionContextManager(inactivity_timeout_minutes=1)
    
    print("Test 1: Initial context (should be empty)")
    print(f"Context: {session.get_context()}")
    print(f"To prompt: {session.to_prompt()}")
    print(f"Has active application: {session.has_active_application()}")
    print("-" * 40)
    
    print("Test 2: Update context")
    session.update(
        application="word",
        document="Test Document.docx",
        task="Editing text",
        action="insert_text",
        target="selection",
        parameters={"text": "Hello World"},
        success=True
    )
    
    print(f"Context: {session.get_context()}")
    print(f"To prompt:\n{session.to_prompt()}")
    print(f"Has active application: {session.has_active_application()}")
    print("-" * 40)
    
    print("Test 3: Update with partial data")
    session.update(
        action="bold_selection",
        target="selection",
        success=True
    )
    
    print(f"Context: {session.get_context()}")
    print(f"To prompt:\n{session.to_prompt()}")
    print("-" * 40)
    
    print("Test 4: Clear context")
    session.clear()
    print(f"After clear - Has active application: {session.has_active_application()}")
    print(f"To prompt: {session.to_prompt()}")
    print("-" * 40)
    
    print("Test 5: Inactivity timeout (waiting 2 seconds for 1 second timeout)")
    session.update(application="word", action="create_document", success=True)
    print(f"Initial context active: {session.has_active_application()}")
    
    import time
    time.sleep(2.5)
    
    print(f"After timeout - Has active application: {session.has_active_application()}")
    print(f"To prompt: {session.to_prompt()}")
    print("-" * 40)
    
    print("Test 6: Multiple applications")
    session.update(application="browser", action="open_website", target="youtube", success=True)
    print(f"To prompt:\n{session.to_prompt()}")
    
    session.update(application="word", action="create_document", target="document", success=True)
    print(f"To prompt after switching to word:\n{session.to_prompt()}")
    print("-" * 40)
    
    print("Test 7: Context with all fields")
    session.update(
        application="word",
        document="Report.docx",
        task="Writing report",
        action="insert_text",
        target="document",
        parameters={"text": "This is the report content", "style": "formal"},
        success=True
    )
    print(f"To prompt:\n{session.to_prompt()}")
    
    print("\nTest completed successfully!")