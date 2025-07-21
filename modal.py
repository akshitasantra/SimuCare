import tkinter as tk
from tkinter import ttk

# Color palette for consistency
PALETTE = {
    'bg': '#2E3440',
    'fg': '#D8DEE9',
    'accent': '#88C0D0'
}

class SelectionModal(tk.Toplevel):
    def __init__(self, master, tree, title="Select Action", callback=None):
        super().__init__(master)
        self.tree = tree  # Nested dict: {level1: {level2: {level3: {}}}}
        self.callback = callback  # Called with list of selected path
        self.selected_path = []

        self._configure_window(title)
        self._show_level(self.tree)

    def _configure_window(self, title):
        self.title(title)
        self.configure(bg=PALETTE['bg'])
        self.resizable(False, False)
        self.grab_set()  # Modal behavior

        # Center on parent
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")

        # Container for buttons
        self.container = ttk.Frame(self, style='TFrame')
        self.container.pack(padx=20, pady=20)

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _show_level(self, level_dict, level=1):
        self._clear_container()
        ttk.Label(self.container, text=f"Step {level}: Choose an option", style='TLabel').pack(pady=(0,10))

        for key in level_dict.keys():
            btn = ttk.Button(
                self.container,
                text=key,
                style='TButton',
                command=lambda k=key: self._on_select(k, level_dict[k], level)
            )
            btn.pack(fill='x', pady=5)

    def _on_select(self, key, subtree, level):
        self.selected_path.append(key)
        if isinstance(subtree, dict) and subtree:
            # More levels
            self._show_level(subtree, level+1)
        else:
            # Final selection
            if self.callback:
                self.callback(self.selected_path)
            self.destroy()

# Example usage:
if __name__ == '__main__':
    def on_choice(path):
        print("Selected path:", path)

    sample_tree = {
        'Meds': {'Epinephrine': {'0.3mg_IM': {}, '0.15mg_IM': {}}, 'Naloxone': {'2mg_IN': {}}},
        'Airway': {'Insert OPA': {'Size_6': {}, 'Size_8': {}}},
        'Breathing': {'Administer_O2': {'15L_NRB': {}, '6L_NC': {}}}
    }

    root = tk.Tk()
    root.withdraw()
    modal = SelectionModal(root, sample_tree, callback=on_choice)
    root.mainloop()
