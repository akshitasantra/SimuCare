import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dashboard_palette import PALETTE
from matplotlib import pyplot as plt

class VitalsPanel(ttk.Frame):
    def __init__(self, master, width=6, height=4, dpi=100):
        super().__init__(master, style='TFrame')
        self.times = []
        self.hr_data = []
        self.spo2_data = []
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=PALETTE['bg'])
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)


        self.ax.set_facecolor(PALETTE['bg'])
        self.ax.tick_params(colors=PALETTE['fg'], labelsize=12)
        self.ax.xaxis.label.set_size(14)
        self.ax.yaxis.label.set_size(14)
        self.ax.title.set_fontsize(16)

        for spine in self.ax.spines.values():
            spine.set_color(PALETTE['fg'])

        self.ax.yaxis.label.set_color(PALETTE['fg'])
        self.ax.xaxis.label.set_color(PALETTE['fg'])
        self.ax.title.set_color(PALETTE['accent'])

        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Value')

        self.hr_line, = self.ax.plot([], [], label='HR (bpm)', color=PALETTE['accent'], linewidth=2)
        self.spo2_line, = self.ax.plot([], [], label='SpO₂ (%)', color=PALETTE['highlight'],
                                       linewidth=2)

        self.ax.legend(loc='upper right', facecolor=PALETTE['bg'], labelcolor=PALETTE['fg'],
                       fontsize=12)

        # Grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()

        widget = self.canvas.get_tk_widget()
        widget.grid(row=0, column=0, sticky='nsew')  # Use only grid

        self._timer_id = None


    def start(self, interval=1000):
        self._timer_id = self.after(interval, self._update_plot)

    def stop(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)

    def update_vitals(self, current_time, hr, spo2):
        self.times.append(current_time)
        self.hr_data.append(hr)
        self.spo2_data.append(spo2)

        max_len = 60
        self.times = self.times[-max_len:]
        self.hr_data = self.hr_data[-max_len:]
        self.spo2_data = self.spo2_data[-max_len:]

    def _update_plot(self):
        self.hr_line.set_data(self.times, self.hr_data)
        self.spo2_line.set_data(self.times, self.spo2_data)

        if self.times:
            self.ax.set_xlim(self.times[0], self.times[-1])

        upper_bound = max(max(self.hr_data or [100]), max(self.spo2_data or [100])) + 10
        self.ax.set_ylim(50, upper_bound)

        self.canvas.draw()
        self._timer_id = self.after(1000, self._update_plot)

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background=PALETTE['bg'])

    panel = VitalsPanel(root)
    panel.grid(row=0, column=0, sticky='nsew')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

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
