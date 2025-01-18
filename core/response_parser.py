from typing import Dict, Any, Optional
import json
from abc import ABC, abstractmethod

class ResponseParseError(Exception):
    pass

class ResponseParser(ABC):
    @abstractmethod
    def parse(self, response: str) -> Dict[str, Any]:
        pass

class JSONResponseParser(ResponseParser):
    def parse(self, response: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(response)
            self._validate_response_structure(parsed)
            return parsed
        except json.JSONDecodeError as e:
            raise ResponseParseError(f"Invalid JSON response: {str(e)}")
        except KeyError as e:
            raise ResponseParseError(f"Missing required field: {str(e)}")

    def _validate_response_structure(self, parsed: Dict[str, Any]):
        required_fields = {
            "response": str,
            "actions": list,
            "required_information": list,
            "next_state": str,
            "confidence": (int, float)
        }

        for field, expected_type in required_fields.items():
            if field not in parsed:
                raise ResponseParseError(f"Missing required field: {field}")
            if not isinstance(parsed[field], expected_type):
                raise ResponseParseError(
                    f"Invalid type for {field}. Expected {expected_type}, got {type(parsed[field])}"
                )

class StructuredResponseParser(ResponseParser):
    def parse(self, response: str) -> Dict[str, Any]:
        lines = response.strip().split('\n')
        parsed = {}
        current_section = None

        for line in lines:
            if line.startswith('#'):
                current_section = line[1:].strip().lower()
                parsed[current_section] = []
            elif current_section and line.strip():
                parsed[current_section].append(line.strip())

        return self._process_sections(parsed)