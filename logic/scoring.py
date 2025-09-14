from typing import List, Dict, Any
import time

class Scoring:
    """
    Scoring for the flat scenario format:
      • +1 for each required path completed
      • 0 accuracy if any harmful action chosen
      • Tracks timing and history
    """
    def __init__(self, total_required: int):
        self.total_required = total_required
        self.completed: List[List[str]] = []
        self.harmful: List[List[str]] = []
        self.records: List[Dict[str, Any]] = []
        self._start_times: Dict[str, float] = {}  # key: str(path) for timing

    def start_action(self, path: List[str]):
        self._start_times[str(path)] = time.time()

    def record_action(self, path: List[str], result: str):
        elapsed = time.time() - self._start_times.get(str(path), time.time())
        self.records.append({
            "path": path,
            "result": result,
            "time_taken": elapsed
        })
        if result == "required":
            if path not in self.completed:
                self.completed.append(path)
        elif result == "harmful":
            if path not in self.harmful:
                self.harmful.append(path)

    def summary(self) -> Dict[str, Any]:
        scenario_failed = bool(self.harmful)
        total_points = len(self.completed)
        total_possible = self.total_required
        accuracy = 0.0 if scenario_failed else (
            total_points / total_possible if total_possible else 0.0
        )
        return {
            "completed_paths": self.completed,
            "harmful_paths": self.harmful,
            "total_points": total_points,
            "total_possible": total_possible,  # NEW
            "accuracy": accuracy,
            "scenario_failed": scenario_failed,
            "records": self.records.copy()
        }

