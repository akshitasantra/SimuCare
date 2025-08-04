import customtkinter as ctk
from dashboard_palette import PALETTE
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class VitalsPanel(ctk.CTkFrame):
    def __init__(self, master, width=6, height=3, dpi=100):
        super().__init__(master, fg_color=PALETTE['bg'], corner_radius=0)

        # --- create matplotlib figure & axes ---
        self.figure = Figure(figsize=(width, height), dpi=dpi, facecolor=PALETTE['bg'])
        self.ax = self.figure.add_subplot(111)

        # embed canvas in Tk frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        widget = self.canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    def show_ecg_snapshot(self, rhythm: str = "sinus_tachycardia", hr: int = 120, spo2: int = 98,
                          duration: float = 10.0, fs: int = 250):
        """Render synthetic ECG strip + vital readouts."""

        # clear axes
        self.ax.clear()
        self.ax.set_facecolor(PALETTE['bg'])
        for spine in self.ax.spines.values():
            spine.set_color(PALETTE['fg'])
        self.ax.set_xlim(0, duration)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.set_title("12‑lead Snapshot", color=PALETTE['accent'])
        self.ax.set_xlabel("Time (s)", color=PALETTE['fg'])
        self.ax.set_ylabel("mV", color=PALETTE['fg'])

        # --- waveform generation ---
        t = np.linspace(0, duration, int(duration * fs))
        ecg = np.zeros_like(t)

        if rhythm in ("sinus_tachycardia", "svt"):
            rr_interval = 60.0 / max(hr, 30)  # prevent divide by 0
            qrs_width = 0.12 if rhythm == "sinus_tachycardia" else 0.06

            def one_beat(time_axis):
                beat = np.exp(-((time_axis - 0.1) ** 2) / (qrs_width ** 2)) * 1.2
                beat += np.exp(-((time_axis - 0.2) ** 2) / 0.01) * 0.25
                return beat

            for n in range(int(duration / rr_interval)):
                start = int(n * rr_interval * fs)
                end = start + int(0.6 * fs)
                if end < len(t):
                    beat_t = np.linspace(0, 0.6, end - start)
                    ecg[start:end] += one_beat(beat_t)

        elif rhythm == "vfib":
            ecg = 0.5 * np.random.randn(len(t))

        elif rhythm == "asystole":
            ecg = np.zeros_like(t)

        # plot waveform
        self.ax.plot(t, ecg, color=PALETTE['accent'], linewidth=1.2)

        # --- vital readouts ---
        label_text = f"HR: {hr} bpm     SpO₂: {spo2}%"
        self.ax.text(1.5, -1.2, label_text,
                     ha='center', va='center',
                     transform=self.ax.transData,
                     fontsize=14, color=PALETTE['fg'], weight='bold')

        self.canvas.draw()
