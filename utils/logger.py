# utils/logger.py

import tkinter as tk
from datetime import datetime

class ActionLogger(tk.Frame):
    """
    A logging widget that displays timestamped action entries.
    Usage:
        logger = ActionLogger(parent)
        logger.log(['Meds', 'Epinephrine', '0.3mg_IM'], 'Correct')
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Text widget (read-only) with vertical scrollbar
        self.text = tk.Text(self, wrap='word', state='disabled', height=10, bg='#2E3440', fg='#D8DEE9')
        scrollbar = tk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Configure grid to expand
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def log(self, path, result):
        """
        Append a new log entry.
        :param path: list of strings indicating the intervention path
        :param result: string indicating 'Correct' or 'Wrong' (or custom)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] Path: {path} → {result}\n"

        # Enable editing, insert, then disable
        self.text.configure(state='normal')
        self.text.insert('end', entry)
        self.text.see('end')  # auto-scroll to bottom
        self.text.configure(state='disabled')
