import customtkinter as ctk
import json, time

from dashboard_palette import PALETTE
from logger import ActionLogger
from modal import SelectionModal
from logic.intervention_tree import TREE
from logic.action_handler import ActionHandler
from logic.scoring import Scoring
from logic.scenario_engine import ScenarioEngine


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class Dashboard(ctk.CTkFrame):
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self, master, scenario_file, update_interval=1000):
        super().__init__(master)
        self.master = master
        self.update_interval = update_interval
        self.time_remaining = 600  # seconds

        # ----- Load Scenario -----
        with open(scenario_file) as f:
            self.scenario = json.load(f)

        # Engine + scoring
        self.engine = ScenarioEngine(self.scenario)
        self.engine.start()
        self.scoring = Scoring(total_required=len(self.scenario.get("required_paths", [])))
        self.action_handler = ActionHandler(self.scenario)

        self.start_time = time.time()

        self._configure_master()
        self._build_ui()
        self._start_timer()

    def _configure_master(self):
        self.master.title("SimuCare")
        self.master.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.master.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        self.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Main rows: title, timer, cat_frame, log_frame
        for r in range(4):
            if r == 2:
                self.grid_rowconfigure(r, weight=0)  # cat_frame tight
            elif r == 3:
                self.grid_rowconfigure(r, weight=1)  # log_frame expands
            else:
                self.grid_rowconfigure(r, weight=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _build_ui(self):
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.scenario.get("title", "Scenario"),
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=PALETTE["accent"]
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 2), sticky="n")

        # Timer
        self.timer_label = ctk.CTkLabel(
            self,
            text=self._format_time(self.time_remaining),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="n")

        # Prompt + categories container
        cat_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"])
        cat_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 5), sticky="new")

        # Initial case description
        self.step_prompt_label = ctk.CTkLabel(
            cat_frame,
            text=self.scenario.get("description", ""),
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=PALETTE["bg"],
            wraplength=600,
            justify="center"
        )
        self.step_prompt_label.grid(row=0, column=0, columnspan=4, pady=(0, 8), sticky="n")

        # Category buttons
        categories = list(TREE.keys())
        num_cols = 4
        for i, name in enumerate(categories):
            r, c = divmod(i, num_cols)
            btn = ctk.CTkButton(
                cat_frame,
                text=name,
                command=lambda n=name: self._open_modal_for_category(n)
            )
            btn.grid(row=r + 1, column=c, padx=4, pady=4, sticky="ew")
            cat_frame.grid_columnconfigure(c, weight=1)

        # Ensure cat_frame rows don't stretch
        for r in range(len(categories) // num_cols + 2):
            cat_frame.grid_rowconfigure(r, weight=0)

        # Action log
        log_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg"])
        log_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 5), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.logger = ActionLogger(log_frame)
        self.logger.grid(row=0, column=0, sticky="nsew")

        # End Scenario button under the logger, same width
        self.end_button = ctk.CTkButton(
            self,
            text="End Scenario",
            fg_color=None,  # same color as the other CTkButtons
            command=self._end_scenario
        )
        self.end_button.grid(row=4, column=0, columnspan=2, padx=20, pady=(5, 10), sticky="ew")

        # Adjust main grid row weights so log_frame expands and button stays below
        self.grid_rowconfigure(3, weight=1)  # log_frame expands
        self.grid_rowconfigure(4, weight=0)  # button stays fixed

    def _open_modal_for_category(self, category):
        subtree = TREE.get(category, {})
        if subtree:
            SelectionModal(self, tree={category: subtree}, callback=self._on_intervention)
        else:
            self.logger.log([], f"No interventions for {category}")

    def _format_time(self, sec):
        m, s = divmod(sec, 60)
        return f"Time Remaining: {m:02d}:{s:02d}"

    def _start_timer(self):
        self._update_timer()

    def _update_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.configure(text=self._format_time(self.time_remaining))
            self.after(self.update_interval, self._update_timer)

    # ---------- New intervention handler ----------
    def _on_intervention(self, path):
        if self.time_remaining == 0:
            self.logger.log([], "Scenario has ended. No further actions allowed.")
            return

        self.scoring.start_action(path)
        result = self.engine.process_action(path)
        self.scoring.record_action(path, result["result"])

        # Update prompt with any follow-up info
        if result["result"] == "required":
            prompt = result.get("prompt") or "Action acknowledged."
            self.step_prompt_label.configure(text=prompt)
            self.logger.log(path, f"✅ {prompt}")
        elif result["result"] == "harmful":
            self.logger.log(path, "⚠️ Harmful action selected!")
        else:
            self.logger.log(path, "No effect.")

        # Scenario end check
        if self.engine.is_completed():
            summary = self.scoring.summary()
            if summary["scenario_failed"]:
                self.logger.log([], "⚠️ Scenario failed due to harmful actions.")
            else:
                self.logger.log([], "✅ Scenario complete!")
            self.logger.log([], f"Points: {summary['total_points']}")

    def _end_scenario(self):
        # Scenario failed if engine or scoring says harmful selected
        if self.engine.scenario_failed() or self.scoring.harmful:
            self.logger.log([], "⚠️ Scenario ended: harmful actions were selected.")
        else:
            self.logger.log([], "✅ Scenario ended by user.")

        summary = self.scoring.summary()
        self.logger.log([], f"Points: {summary['total_points']} / {summary['total_possible']}")

        # Stop the timer
        self.time_remaining = 0

    def run(self):
        self.start_time = time.time()
        self.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = ctk.CTk()
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    dash = Dashboard(app, scenario_file="scenarios/medical_sample.json")
    dash.run()
    app.mainloop()
