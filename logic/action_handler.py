from typing import List, Tuple, Dict, Any

class ActionHandler:
    """
    Validates user-selected intervention paths against the current scenario steps.
    Uses expected_path from scenario JSON to determine correctness.
    """

    def __init__(self, scenario: Dict[str, Any]):
        self.steps = scenario.get("steps", [])
        self.current_step = 0

    def validate(self, selected_path: List[str]) -> Tuple[str, str, Dict[str, int]]:
        """
        Validate the user's choice for the current step.

        :param selected_path: full path list from TREE, e.g. ["Meds","Epinephrine","0.3mg_IM"]
        :returns: (result, feedback_log)
        """
        if self.current_step >= len(self.steps):
            raise IndexError("No more steps in scenario.")

        step = self.steps[self.current_step]
        expected = step["expected_path"]

        if selected_path == expected:
            outcome = step.get("on_correct", {})
            result = "correct"
        else:
            outcome = step.get("on_wrong", {})
            result = "wrong"

        self.current_step += 1
        feedback = outcome.get("log", "")

        return result, feedback

    def has_more_steps(self) -> bool:
        """Return True if there are more interaction steps remaining."""
        return self.current_step < len(self.steps)

    def reset(self):
        """Reset handler to the beginning of the scenario."""
        self.current_step = 0
