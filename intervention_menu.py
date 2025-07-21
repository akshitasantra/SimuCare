# intervention_menu.py

import tkinter as tk
from tkinter import ttk
from modal import SelectionModal
from utils.logger import ActionLogger

class InterventionMenu(ttk.Frame):
    """
    A frame with:
     - a button to open a modal of current step options
     - a label showing the selected option
     - a confirm button that fires callback(selected_option)
    """

    def __init__(self, master, logger: ActionLogger, callback=None):
        super().__init__(master, style='TFrame')
        self.logger = logger
        self.callback = callback  # called with [selected_option]
        self.options = []         # current list of string options
        self.selected_option = None

        # Choose Button
        self.choose_btn = ttk.Button(self, text="Choose Intervention", command=self.open_modal, state='disabled')
        self.choose_btn.pack(side='left', padx=(0,10))

        # Selection Label
        self.selection_label = ttk.Label(self, text="No intervention selected.", style='TLabel')
        self.selection_label.pack(side='left', fill='x', expand=True)

        # Confirm Button
        self.confirm_btn = ttk.Button(self, text="Confirm", state='disabled', command=self.confirm_selection)
        self.confirm_btn.pack(side='right')

    def configure_options(self, options):
        """
        Load a new set of options for the next step.
        :param options: list of strings
        """
        self.options = options
        self.selected_option = None
        self.selection_label.config(text="No intervention selected.")
        self.confirm_btn.config(state='disabled')
        self.choose_btn.config(state='normal')

    def open_modal(self):
        """
        Build a one-level tree from self.options and launch the SelectionModal.
        """
        # Build a simple tree: {opt: {}} for each option
        tree = {opt: {} for opt in self.options}
        SelectionModal(self, tree, title="Select Intervention", callback=lambda path: self.on_selected(path[0]))

    def on_selected(self, option):
        """
        Callback from modal with the chosen option (string).
        """
        self.selected_option = option
        self.selection_label.config(text=option)
        self.confirm_btn.config(state='normal')

    def confirm_selection(self):
        """
        Fires the external callback with [selected_option]; logs the attempt.
        """
        if not self.selected_option:
            return
        # Log attempt
        self.logger.log([self.selected_option], 'Attempted')
        # Fire external handler
        if self.callback:
            self.callback([self.selected_option])
        # Disable until next step
        self.choose_btn.config(state='disabled')
        self.confirm_btn.config(state='disabled')
        self.selection_label.config(text="No intervention selected.")
        self.selected_option = None

# Example standalone test
if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background='#2E3440')
    style.configure('TLabel', background='#2E3440', foreground='#D8DEE9', font=('Segoe UI', 12))
    style.configure('TButton', font=('Segoe UI', 12))

    logger = ActionLogger(root)
    logger.pack(side='bottom', fill='x')

    def external_callback(path):
        logger.log(path, 'Confirmed')

    menu = InterventionMenu(root, logger, callback=external_callback)
    menu.pack(padx=20, pady=20)

    # Demo: set some options
    menu.configure_options(["Administer Epinephrine", "Administer O2", "Insert OPA"])

    root.mainloop()
