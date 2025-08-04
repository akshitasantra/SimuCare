import customtkinter as ctk
import json, time

from dashboard_palette import PALETTE
from vitals_panel import VitalsPanel
from logger import ActionLogger
from modal import SelectionModal
from logic.intervention_tree import TREE
from logic.vitals_simulator import VitalsSimulator
from logic.action_handler import ActionHandler
from logic.scoring import Scoring
from logic.scenario_engine import ScenarioEngine


# Initialize the customtkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class Dashboard(ctk.CTkFrame):
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self, master, scenario_file, update_interval=1000):
        super().__init__(master)
        self.master = master
        self.update_interval = update_interval
        self.time_remaining = 900  # seconds

        # Load scenario
        with open(scenario_file) as f:
            self.scenario = json.load(f)

        # Scenario engine + handlers
        self.engine = ScenarioEngine(self.scenario)
        self.engine.start()
        self.vitals_sim = VitalsSimulator(self.scenario['timeline'])
        self.action_handler = ActionHandler(self.scenario)
        self.scoring = Scoring(total_steps=len(self.scenario.get('steps', [])))
        if self.scenario.get('steps'):
            self.scoring.start_step(self.scenario['steps'][0]['id'])

        self.start_time = time.time()

        self._configure_master()
        self._build_ui()
        self._start_timer()


    def _configure_master(self):
        # Window setup
        self.master.title("SimuCare")
        self.master.geometry(f"{self.MIN_WIDTH}x{self.MIN_HEIGHT}")
        self.master.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Put Dashboard in a single expanding cell
        self.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # - rows 0 (title) and 1 (timer) should be fixed height (weight=0)
        # - row 2 (vitals) gets most of the extra space
        # - row 3 (categories) small, row 4 (log) gets some

        for r in range(5):
            weight = 0

        if r == 2:
            weight = 5
        elif r == 4:
            weight = 2
        self.grid_rowconfigure(r, weight=weight)
        # Two columns both expand equally
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _build_ui(self):
        # Title row
        self.title_label = ctk.CTkLabel(
            self,
            text=self.scenario['title'],
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=PALETTE['accent']
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 5), sticky="n")

        # Timer
        self.timer_label = ctk.CTkLabel(
            self,
            text=self._format_time(self.time_remaining),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="n")

        # Vitals panel
        vitals_frame = ctk.CTkFrame(self, fg_color=PALETTE['bg'])
        vitals_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        vitals_frame.grid_rowconfigure(0, weight=1)
        vitals_frame.grid_columnconfigure(0, weight=1)

        self.vitals_panel = VitalsPanel(vitals_frame, width=7, height=4)
        self.vitals_panel.grid(row=0, column=0, sticky="nsew")

        # Prompt + Intervention categories
        cat_frame = ctk.CTkFrame(self, fg_color=PALETTE['bg'])
        cat_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10,5), sticky="ew")

        # Step-specific prompt
        self.step_prompt_label = ctk.CTkLabel(
            cat_frame,
            text="",  # will be filled by _update_step_prompt
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=PALETTE['fg'],
            wraplength=600,
            justify="center"
        )
        self.step_prompt_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Now dynamically create category buttons from TREE
        categories = list(TREE.keys())
        num_cols = 3
        for i, name in enumerate(categories):
            r, c = divmod(i, num_cols)
            btn = ctk.CTkButton(
                cat_frame,
                text=name,
                command=lambda n=name: self._open_modal_for_category(n)
            )
            btn.grid(row=r+1, column=c, padx=5, pady=5, sticky="ew")
            cat_frame.grid_columnconfigure(c, weight=1)

        # Action log
        log_frame = ctk.CTkFrame(self, fg_color=PALETTE['bg'])
        log_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.logger = ActionLogger(log_frame)
        self.logger.grid(row=0, column=0, sticky="nsew")

        # Initialize step prompt
        self._update_step_prompt()

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

    def _update_vitals(self):
        t = int(self.engine.elapsed())
        hr, spo2, *_ = self.vitals_sim.get_vitals(t)
        self.vitals_panel.update_vitals(t, hr, spo2)
        self.after(self.update_interval, self._update_vitals)

    def _update_step_prompt(self):
        """Update the label with the current step's prompt text."""
        step = self.engine.get_current_step()
        if step:
            self.step_prompt_label.configure(text=step.get("prompt", ""))
        else:
            self.step_prompt_label.configure(text="Scenario complete!")

    def _on_intervention(self, path):
        step = self.engine.get_current_step()
        if not step:
            return

        result, feedback, vitals_change = self.action_handler.validate(path)
        self.logger.log(path, f"{result.capitalize()}: {feedback}")
        self.engine.apply_vitals_change(vitals_change)
        current_step = self.action_handler.current_step - 1  # Since current_step advanced in validate()
        step = self.action_handler.steps[current_step]
        self.engine.mark_step_completed(step['id'])

        # Special case: show snapshot only if EKG chosen
        if "EKG" in path:
            step = self.engine.get_current_step()
            rhythm = step.get("rhythm", "sinus_tachycardia")

            t = int(self.engine.elapsed())
            hr, spo2, *_ = self.vitals_sim.get_vitals(t)

            self.vitals_panel.show_ecg_snapshot(rhythm=rhythm, hr=hr, spo2=spo2)
            self.logger.log(path,
                            f"12‑lead taken → rhythm: {rhythm.replace('_', ' ').title()} | HR {hr} | SpO₂ {spo2}%")

        # Scoring
        self.scoring.end_step(result == 'correct')
        if self.action_handler.has_more_steps():
            next_step = self.scenario['steps'][self.action_handler.current_step]['id']
            self.scoring.start_step(next_step)

        # Mark step done
        self.engine.mark_step_completed(step['id'])

        # Update prompt for next step
        self._update_step_prompt()

        # If scenario over
        if not self.engine.get_current_step():
            self.logger.log([], 'Scenario Complete')
            summary = self.scoring.summary()
            self.logger.log([], f"Accuracy: {summary['accuracy'] * 100:.1f}%")
            self.logger.log([], f"Avg. response: {summary['average_time_sec']:.1f}s")

    def refresh_snapshot(self):
        """Draw the current vitals buffer once (no looping)."""
        self.hr_line.set_data(self.times, self.hr_data)
        self.spo2_line.set_data(self.times, self.spo2_data)

        if self.times:
            self.ax.set_xlim(self.times[0] - 1, self.times[0] + 1)  # just a tight window
        upper = max(max(self.hr_data or [100]), max(self.spo2_data or [100])) + 10
        self.ax.set_ylim(50, upper)

        self.canvas.draw()

    def run(self):
        self.start_time = time.time()
        self.pack(fill='both', expand=True)

if __name__ == "__main__":
    app = ctk.CTk()
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    dash = Dashboard(app, scenario_file='scenarios/sample.json')
    dash.run()
    app.mainloop()
