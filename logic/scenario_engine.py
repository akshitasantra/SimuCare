from typing import Dict, Any, List
import time

class ScenarioEngine:
    """
    Scenario logic for the *new* JSON format:
      {
        "title": "...",
        "description": "...",      # first prompt text
        "required_paths": [        # list of dicts
            {"path": [...], "prompt": "..."},
            ...
        ],
        "harmful_paths": [ [...], ... ]
      }
    """
    def __init__(self, scenario: Dict[str, Any]):
        self.title = scenario.get("title", "")
        self.description = scenario.get("description", "")
        self.required_paths: List[Dict[str, Any]] = scenario.get("required_paths", [])
        self.harmful_paths: List[List[str]] = scenario.get("harmful_paths", [])

        self.start_time: float | None = None
        self.completed: List[List[str]] = []          # paths the user successfully chose
        self.harmful_selected: List[List[str]] = []   # harmful paths the user clicked

    def start(self):
        self.start_time = time.time()

    def elapsed(self) -> float:
        return time.time() - self.start_time if self.start_time else 0.0

    def process_action(self, path: List[str]) -> Dict[str, Any]:
        """
        Called whenever the user clicks an intervention path.
        Returns a dict with the outcome and any follow-up prompt.
        """
        # harmful check first
        if path in self.harmful_paths:
            if path not in self.harmful_selected:
                self.harmful_selected.append(path)
            return {"result": "harmful", "prompt": None}

        # required check
        for rp in self.required_paths:
            if path == rp["path"] and path not in self.completed:
                self.completed.append(path)
                return {"result": "required", "prompt": rp.get("prompt", "")}

        return {"result": "unknown", "prompt": None}

    def is_completed(self) -> bool:
        """True if all required paths have been selected (order doesn’t matter)."""
        return len(self.completed) == len(self.required_paths)

    def scenario_failed(self) -> bool:
        """True if any harmful path has been selected."""
        return len(self.harmful_selected) > 0

    def reset(self):
        self.start_time = None
        self.completed.clear()
        self.harmful_selected.clear()
