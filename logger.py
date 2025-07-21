import tkinter as tk
from tkinter import ttk
import datetime

# Color palette
PALETTE = {
    'bg': '#2E3440',
    'fg': '#D8DEE9',
    'accent': '#88C0D0'
}

class ActionLogger(ttk.Frame):
    def __init__(self, master, height=10):
        super().__init__(master, style='TFrame')
        self.configure(height=height)

        # Create a scrollbar and text widget
        self.scrollbar = ttk.Scrollbar(self, orient='vertical')
        self.text = tk.Text(
            self,
            wrap='none',
            yscrollcommand=self.scrollbar.set,
            bg=PALETTE['bg'],
            fg=PALETTE['fg'],
            insertbackground=PALETTE['fg'],
            relief='flat',
            font=('Segoe UI', 12)
        )
        self.scrollbar.config(command=self.text.yview)

        # Layout
        self.text.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        # Disable direct editing
        self.text.configure(state='disabled')

    def log(self, path, result):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Path: {path} → {result}\n"
        # Enable, insert, disable to keep read-only
        self.text.configure(state='normal')
        self.text.insert('end', message)
        self.text.see('end')
        self.text.configure(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background=PALETTE['bg'])

    logger = ActionLogger(root)
    logger.pack(fill='both', expand=True)

    # Test logs
    logger.log(['Meds','Epinephrine','0.3mg_IM'], 'Correct')
    logger.log(['Breathing','Administer_O2','15L_NRB'], 'Wrong')

    root.mainloop()
