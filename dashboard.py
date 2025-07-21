import tkinter as tk
from tkinter import ttk
import json, time

from dashboard_palette import PALETTE  # define your palette as before
from vitals_panel import VitalsPanel
from utils.logger import ActionLogger
from logic.intervention_tree import TREE
from logic.vitals_simulator import VitalsSimulator
from logic.action_handler import ActionHandler
from intervention_menu import InterventionMenu
from logic.scoring import Scoring
from logic.scenario_engine import ScenarioEngine


class Dashboard(tk.Frame):
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self, master, scenario_file, update_interval=1000):
        try:
            master.tk.call('tk', 'scaling', 1.5)
        except tk.TclError:
            pass
        super().__init__(master, bg=PALETTE['bg'])
        self.master = master
        self.update_interval = update_interval
        self.time_remaining = 900  # seconds

        # Load scenario
        with open(scenario_file) as f:
            self.scenario = json.load(f)

        # Prepare engine and handlers
        self.engine = ScenarioEngine(self.scenario)
        self.engine.start()  # begin scenario clock
        self.vitals_sim = VitalsSimulator(self.scenario['timeline'])
        self.action_handler = ActionHandler(self.scenario)

        # Prepare scoring
        self.scoring = Scoring(total_steps=len(self.scenario.get('steps', [])))
        if self.scenario.get('steps'):
            first_id = self.scenario['steps'][0]['id']
            self.scoring.start_step(first_id)


        # Prepare handlers
        self.vitals_sim = VitalsSimulator(self.scenario['timeline'])
        self.action_handler = ActionHandler(self.scenario)

        # Prepare scoring
        self.scoring = Scoring(total_steps=len(self.scenario.get('steps', [])))
        # Start first step timer

        if self.scenario.get('steps'):
            first_id = self.scenario['steps'][0]['id']
            self.scoring.start_step(first_id)

        # Record start time for vitals simulation
        self.start_time = time.time()

        self._configure_master()
        self._build_ui()
        self._start_timer()
        self._start_vitals_loop()

    def _configure_master(self):
        self.master.title("SimuCare")
        self.master.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.master.configure(bg=PALETTE['bg'])
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(1, weight=0)
        self.master.rowconfigure(2, weight=1)
        self.master.rowconfigure(3, weight=0)

    def _build_ui(self):
        style = ttk.Style(self.master)
        style.theme_use('clam')
        default_font = ('Segoe UI', 14)
        title_font = ('Segoe UI', 28, 'bold')
        timer_font = ('Segoe UI', 22)

        style.configure('TFrame', background=PALETTE['bg'])
        style.configure('TLabel', background=PALETTE['bg'], foreground=PALETTE['fg'], font=default_font)
        style.configure('Title.TLabel', font=title_font, foreground=PALETTE['accent'])
        style.configure('Timer.TLabel', font=timer_font, foreground=PALETTE['highlight'])

        self.grid(sticky='nsew')
        # Title
        self.title_label = ttk.Label(self, text=self.scenario['title'], style='Title.TLabel')
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20,10), sticky='n')
        # Timer
        self.timer_label = ttk.Label(self, text=self._format_time(self.time_remaining), style='Timer.TLabel')
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=(0,15), sticky='n')
        # Vitals Panel
        self.vitals_panel = VitalsPanel(self)
        self.vitals_panel.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=30, pady=10)
        # Intervention Menu and Logger
        control_frame = ttk.Frame(self)
        control_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=20, pady=(10,20))
        control_frame.columnconfigure(0, weight=2)
        control_frame.columnconfigure(1, weight=1)

        self.logger = ActionLogger(control_frame)
        self.logger.grid(row=0, column=1, sticky='nsew', padx=(10,0))

        self.intervention_menu = InterventionMenu(control_frame, logger=self.logger, callback=self._on_intervention)
        self.intervention_menu.grid(row=0, column=0, sticky='ew')
        step = self.engine.get_current_step()
        if step:
            self.intervention_menu.configure_options(step['options'])
        else:
            self.intervention_menu.configure_options()

    def _format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"Time Remaining: {mins:02d}:{secs:02d}"

    def _start_timer(self):
        self._update_timer()

    def _update_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=self._format_time(self.time_remaining))
            self.after(self.update_interval, self._update_timer)
        else:
            self.timer_label.config(text="Time's up!", foreground=PALETTE['fg'])
            # scenario end logic

    def _start_vitals_loop(self):
        self._update_vitals()

    def _update_vitals(self):
        t = int(self.engine.elapsed())
        hr, spo2, bp, rr = self.vitals_sim.get_vitals(t)
        self.vitals_panel.update_vitals(t, hr, spo2)
        self.after(self.update_interval, self._update_vitals)

    def _on_intervention(self, path):
        step = self.engine.get_current_step()
        if not step:
            return

        chosen = path[-1]
        result, feedback, vitals_delta = self.action_handler.validate(chosen)
        self.logger.log(path, result.capitalize())

        # Scoring
        self.scoring.end_step(result == 'correct')
        if self.action_handler.has_more_steps():
            next_step = self.scenario['steps'][self.action_handler.current_step]['id']
            self.scoring.start_step(next_step)

        # Mark step done in engine
        self.engine.mark_step_completed(step['id'])

        # If scenario over
        if not self.engine.get_current_step():
            self.logger.log([], 'Scenario Complete')
            summary = self.scoring.summary()
            self.logger.log([], f"Accuracy: {summary['accuracy'] * 100:.1f}%")
            self.logger.log([], f"Avg. response: {summary['average_time_sec']:.1f}s")

    def run(self):
        self.start_time = time.time()
        self.pack(fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    dash = Dashboard(root, scenario_file='scenarios/sample.json')
    dash.run()
    root.mainloop()
