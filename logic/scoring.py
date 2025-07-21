# logic/scoring.py

import time
from typing import List, Dict, Any

class Scoring:
    """
    Tracks user performance across scenario steps, including correctness and response times.
    After the scenario, can compute summary statistics.
    """

    def __init__(self, total_steps: int):
        """
        :param total_steps: total number of decision steps in the scenario
        """
        self.total_steps = total_steps
        self.records: List[Dict[str, Any]] = []  # each record: {step_id, correct, time_taken}

        # Internal state for timing
        self._step_start: float = None
        self._current_step_id: Any = None

    def start_step(self, step_id: Any):
        """
        Call when a new step is presented to the user.
        :param step_id: unique identifier of the step (e.g. 'epi_admin')
        """
        self._step_start = time.time()
        self._current_step_id = step_id

    def end_step(self, correct: bool):
        """
        Call immediately after the user confirms their choice.
        Records correctness and time taken.
        :param correct: True if the user chose the correct answer
        """
        if self._step_start is None or self._current_step_id is None:
            raise RuntimeError("start_step() must be called before end_step().")

        elapsed = time.time() - self._step_start
        self.records.append({
            "step_id": self._current_step_id,
            "correct": correct,
            "time_taken": elapsed
        })

        # Reset for next step
        self._step_start = None
        self._current_step_id = None

    def summary(self) -> Dict[str, Any]:
        """
        Returns a summary of performance:
          - total_steps
          - answered_steps
          - correct_count
          - incorrect_count
          - accuracy (0.0–1.0)
          - average_time (secs)
          - per-step breakdown
        """
        answered = len(self.records)
        correct = sum(1 for r in self.records if r["correct"])
        incorrect = answered - correct
        accuracy = correct / self.total_steps if self.total_steps else 0.0
        avg_time = sum(r["time_taken"] for r in self.records) / answered if answered else 0.0

        return {
            "total_steps": self.total_steps,
            "answered_steps": answered,
            "correct_count": correct,
            "incorrect_count": incorrect,
            "accuracy": accuracy,
            "average_time_sec": avg_time,
            "records": self.records.copy()
        }
