import time
from typing import Dict, Any

class ScenarioEngine:
    """
    Manages scenario progression:
     - Tracks elapsed time
     - Provides current timeline vitals
     - Tracks completion of scenario steps
    """

    def __init__(self, scenario: Dict[str, Any]):
        self.title = scenario.get("title", "")
        self.domains = scenario.get("domains", [])
        self.timeline = scenario.get("timeline", [])
        self.steps = scenario.get("steps", [])
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def get_current_timeline_index(self) -> int:
        t = self.elapsed()
        idx = 0
        for i, pt in enumerate(self.timeline):
            if pt["time"] <= t:
                idx = i
            else:
                break
        return idx

    def get_current_vitals(self) -> Dict[str, Any]:
        idx = self.get_current_timeline_index()
        return self.timeline[idx].get("vitals", {})

    def get_current_step(self) -> Dict[str, Any]:
        for step in self.steps:
            if not step.get("_completed", False):
                return step
        return None

    def mark_step_completed(self, step_id: str):
        for step in self.steps:
            if step["id"] == step_id:
                step["_completed"] = True
                break

    def reset(self):
        self.start_time = None
        for step in self.steps:
            step.pop("_completed", None)

    def apply_vitals_change(self, vitals_change: Dict[str, int]):
        """Apply additive changes to the latest vitals point in the timeline."""
        if not self.timeline:
            return

        # modify the last timeline point (or current index)
        idx = self.get_current_timeline_index()
        vitals = self.timeline[idx]['vitals']

        for k, delta in vitals_change.items():
            if k in vitals and vitals[k] is not None:
                vitals[k] += delta
