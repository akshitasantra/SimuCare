# logic/scenario_engine.py

import time
from typing import Dict, Any, List

class ScenarioEngine:
    """
    Manages scenario progression:
     - Loads timeline of vitals changes
     - Exposes current vitals time and steps
     - (Optional) Advances scenario state automatically over real time
    """

    def __init__(self, scenario: Dict[str, Any]):
        """
        :param scenario: JSON-loaded dict containing:
            - 'timeline': list of {time, vitals}
            - 'steps': list of interaction steps
        """
        self.title = scenario.get("title", "")
        self.domains = scenario.get("domains", [])
        self.timeline = scenario.get("timeline", [])
        self.steps = scenario.get("steps", [])
        self.start_time = None

    def start(self):
        """Begin the scenario clock."""
        self.start_time = time.time()

    def elapsed(self) -> float:
        """
        Seconds since scenario start.
        Returns 0 if not started.
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def get_current_timeline_index(self) -> int:
        """
        Find the last timeline entry with time <= elapsed.
        """
        t = self.elapsed()
        idx = 0
        for i, pt in enumerate(self.timeline):
            if pt["time"] <= t:
                idx = i
            else:
                break
        return idx

    def get_current_vitals(self) -> Dict[str, Any]:
        """
        Return the vitals dict for the current timeline point.
        (Exact keypoint, interpolation is handled by VitalsSimulator.)
        """
        idx = self.get_current_timeline_index()
        return self.timeline[idx].get("vitals", {})

    def get_current_step(self) -> Dict[str, Any]:
        """
        Return the next interaction step dict, or None if done.
        """
        for step in self.steps:
            # steps are not tied to timeline times here; handled externally
            if not step.get("_completed", False):
                return step
        return None

    def mark_step_completed(self, step_id: str):
        """
        Mark the given step as completed, so get_current_step() skips it.
        """
        for step in self.steps:
            if step["id"] == step_id:
                step["_completed"] = True
                break

    def reset(self):
        """Reset scenario to initial state."""
        self.start_time = None
        for step in self.steps:
            if "_completed" in step:
                del step["_completed"]
