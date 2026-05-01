from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAdapter(ABC):
    """
    Standard interface for all Open Source Kernel Adapters.
    """
    @abstractmethod
    def execute(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the physical action.
        """
        pass

    @abstractmethod
    def get_supported_actions(self) -> list[str]:
        """
        Returns a list of Schema.org action types this adapter handles.
        """
        pass
