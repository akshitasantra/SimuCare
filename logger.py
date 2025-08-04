import datetime
import customtkinter as ctk
from dashboard_palette import PALETTE

class ActionLogger(ctk.CTkFrame):
    def __init__(self, master, width=400, height=200):
        super().__init__(master, fg_color=PALETTE['bg'], corner_radius=8,
                         border_width=1, border_color=PALETTE['accent'])
        # Configure sizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(width=width, height=height)

        # Create a themed textbox for logging (has its own scrollbar)
        self.textbox = ctk.CTkTextbox(
            self,
            width=width,
            height=height,
            corner_radius=4,
            border_width=0,
            fg_color=PALETTE['bg'],
            text_color=PALETTE['fg'],
            scrollbar_button_color=PALETTE['accent'],
            scrollbar_button_hover_color=PALETTE['fg'],
            font=("Helvetica", 18)
        )
        self.textbox.grid(row=0, column=0, padx=8, pady=8, sticky='nsew')
        self.textbox.configure(state='disabled')

    def log(self, path, result):
        """
        Append a timestamped entry to the read-only textbox.
        :param path: list of strings, the chosen intervention path
        :param result: string, e.g. 'Correct' or 'Wrong'
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {path} → {result}\n"
        # Enable, insert, then disable again
        self.textbox.configure(state='normal')
        self.textbox.insert('end', entry)
        self.textbox.see('end')
        self.textbox.configure(state='disabled')


if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = ctk.CTk()
    app.geometry("500x300")
    logger = ActionLogger(app)
    logger.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

    # Test entries
    logger.log(['Meds','Epinephrine','0.3mg_IM'], 'Correct')
    logger.log(['Breathing','Administer_O2','15L_NRB'], 'Wrong')

    app.mainloop()
