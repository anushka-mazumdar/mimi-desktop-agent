from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import json

class IntentType(str, Enum):
    OPEN_WEBSITE = "open_website"
    BROWSER_SEARCH = "browser_search"
    WORD_ACTION = "word_action"
    EXCEL_ACTION = "excel_action"
    PAINT_ACTION = "paint_action"
    UNKNOWN = "unknown"

class AgentResponse(BaseModel):
    intent: IntentType = Field(
        description="The identified intent of the user's request"
    )
    target: str = Field(
        description="The target object of the action (website name, search query, document context, etc.)"
    )
    action: str = Field(
        description="The specific action to perform"
    )
    url: str = Field(
        default="",
        description="A fully qualified URL used by browser-related actions. Empty string for non-browser actions."
    )
    confidence: float = Field(
        description="Confidence score for the intent classification (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {value}")
        return value

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if value and not value.startswith(("http://", "https://")):
            return f"https://{value}"
        return value

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResponse":
        return cls(**data)


if __name__ == "__main__":
    examples = [
        {
            "intent": "open_website",
            "target": "youtube",
            "action": "open",
            "url": "https://www.youtube.com",
            "confidence": 0.95
        },
        {
            "intent": "browser_search",
            "target": "AI jobs",
            "action": "search",
            "url": "",
            "confidence": 0.95
        },
        {
            "intent": "word_action",
            "target": "document",
            "action": "insert_blank_page",
            "url": "",
            "confidence": 0.90
        },
        {
            "intent": "excel_action",
            "target": "budget",
            "action": "create_template",
            "url": "",
            "confidence": 0.85
        },
        {
            "intent": "paint_action",
            "target": "canvas",
            "action": "draw_circle",
            "url": "",
            "confidence": 0.90
        },
        {
            "intent": "unknown",
            "target": "",
            "action": "",
            "url": "",
            "confidence": 0.0
        }
    ]

    for example in examples:
        response = AgentResponse.from_dict(example)
        print(f"Model: {response}")
        print(f"Dict: {response.to_dict()}")
        print(f"JSON: {response.to_json()}")
        print("-" * 50)