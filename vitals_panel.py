import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dashboard_palette import PALETTE

class VitalsPanel(ttk.Frame):
    def __init__(self, master, width=5, height=3, dpi=100):
        super().__init__(master, style='TFrame')
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=PALETTE['bg'])
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(PALETTE['bg'])
        self.ax.tick_params(colors=PALETTE['fg'])
        self.ax.spines['bottom'].set_color(PALETTE['fg'])
        self.ax.spines['top'].set_color(PALETTE['fg'])
        self.ax.spines['left'].set_color(PALETTE['fg'])
        self.ax.spines['right'].set_color(PALETTE['fg'])
        self.ax.yaxis.label.set_color(PALETTE['fg'])
        self.ax.xaxis.label.set_color(PALETTE['fg'])
        self.ax.title.set_color(PALETTE['accent'])

        # Initialize empty data
        self.times = []
        self.hr_data = []
        self.spo2_data = []

        # Setup lines
        self.hr_line, = self.ax.plot([], [], label='HR (bpm)', color=PALETTE['accent'])
        self.spo2_line, = self.ax.plot([], [], label='SpO₂ (%)', color=PALETTE['highlight'])

        self.ax.legend(loc='upper right', facecolor=PALETTE['bg'], labelcolor=PALETTE['fg'])
        self.ax.set_xlabel('Time (s)', color=PALETTE['fg'])
        self.ax.set_ylabel('Value', color=PALETTE['fg'])
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Internal timer
        self._start_time = 0
        self._timer_id = None

    def start(self, interval=1000):
        self._timer_id = self.after(interval, self._update_plot)

    def stop(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)

    def update_vitals(self, current_time, hr, spo2):
        # Append new data
        self.times.append(current_time)
        self.hr_data.append(hr)
        self.spo2_data.append(spo2)
        # Limit history length
        max_len = 60
        self.times = self.times[-max_len:]
        self.hr_data = self.hr_data[-max_len:]
        self.spo2_data = self.spo2_data[-max_len:]

    def _update_plot(self):
        # Refresh line data
        self.hr_line.set_data(self.times, self.hr_data)
        self.spo2_line.set_data(self.times, self.spo2_data)

        # Adjust axes
        if self.times:
            self.ax.set_xlim(self.times[0], self.times[-1])
        self.ax.set_ylim(0, max(max(self.hr_data or [100]), max(self.spo2_data or [100])) + 10)

        self.canvas.draw()
        # Schedule next update
        self._timer_id = self.after(1000, self._update_plot)

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background=PALETTE['bg'])

    panel = VitalsPanel(root)
    panel.pack(fill='both', expand=True)
    # Simulate data
    import random, time
    start = time.time()
    def simulate():
        t = int(time.time() - start)
        hr = random.randint(60, 140)
        spo2 = random.randint(85, 99)
        panel.update_vitals(t, hr, spo2)
        root.after(1000, simulate)
    simulate()
    panel.start()
    root.mainloop()
