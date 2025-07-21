# logic/action_handler.py

from typing import List, Tuple, Dict, Any

class ActionHandler:
    """
    Validates user-selected intervention paths against the current scenario steps.
    Applies immediate feedback logic (correct vs. wrong) and returns:
      - result: 'correct' or 'wrong'
      - feedback: the corresponding log message
      - vitals_change: dict of vitals deltas defined in the scenario
    """
    def __init__(self, scenario: Dict[str, Any]):
        """
        :param scenario: loaded JSON dict for a scenario, which must include:
            - 'steps': list of step dicts with keys:
                'id', 'prompt', 'options', 'correct_answer',
                'on_correct': { 'log', 'vitals_change'... },
                'on_wrong': { 'log', 'vitals_change'... }
        """
        self.steps = scenario.get("steps", [])
        self.current_step = 0

    def validate(self, selected_option: str) -> Tuple[str, str, Dict[str, int]]:
        """
        Validate the user's choice for the current step.

        :param selected_option: one of the strings in step['options']
        :returns: (result, feedback_log, vitals_change)
        """
        if self.current_step >= len(self.steps):
            raise IndexError("No more steps in scenario.")

        step = self.steps[self.current_step]
        correct = step["correct_answer"]

        if selected_option == correct:
            outcome = step.get("on_correct", {})
            result = "correct"
        else:
            outcome = step.get("on_wrong", {})
            result = "wrong"

        # Advance to next step
        self.current_step += 1

        feedback = outcome.get("log", "")
        vitals_change = outcome.get("vitals_change", {})

        return result, feedback, vitals_change

    def has_more_steps(self) -> bool:
        """Return True if there are more interaction steps remaining."""
        return self.current_step < len(self.steps)

    def reset(self):
        """Reset handler to the beginning of the scenario."""
        self.current_step = 0
