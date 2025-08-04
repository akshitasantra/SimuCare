import customtkinter as ctk
from dashboard_palette import PALETTE


class SelectionModal(ctk.CTkToplevel):
    def __init__(self, master, tree, title="Select Action", callback=None):
        super().__init__(master)
        self.tree = tree
        self.callback = callback
        self.selected_path = []

        self._configure_window(title)
        self._show_level(self.tree)

    def _configure_window(self, title):
        self.title(title)
        self.configure(fg_color=PALETTE['bg'])
        self.grab_set()  # modal behavior

        # min/max size
        self.minsize(350, 250)
        self.maxsize(600, 500)

        # Scrollable container instead of plain frame
        self.container = ctk.CTkScrollableFrame(
            self,
            fg_color=PALETTE['bg'],
            scrollbar_button_color=PALETTE['accent'],
            scrollbar_button_hover_color=PALETTE['fg'],
            corner_radius=0
        )
        self.container.pack(padx=20, pady=20, fill="both", expand=True)

    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _show_level(self, level_dict, level=1):
        self._clear_container()

        # Prompt label
        prompt = ctk.CTkLabel(
            self.container,
            text=f"Step {level}: Choose an option",
            text_color=PALETTE['fg'],
            font=ctk.CTkFont(size=18, weight="bold")
        )
        prompt.pack(pady=(0, 10))

        # Option buttons
        for key, subtree in level_dict.items():
            btn = ctk.CTkButton(
                self.container,
                text=key,
                fg_color=PALETTE['accent'],
                hover_color=PALETTE['fg'],
                text_color=PALETTE['bg'],
                font=ctk.CTkFont(size=16),
                command=lambda k=key, s=subtree: self._on_select(k, s, level)
            )
            btn.pack(fill="x", pady=6)

        # resize & center relative to master
        self.update_idletasks()
        w = min(self.winfo_reqwidth() + 40, 600)
        h = min(self.winfo_reqheight() + 40, 500)
        x = self.master.winfo_x() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_select(self, key, subtree, level):
        self.selected_path.append(key)
        if isinstance(subtree, dict) and subtree:
            self._show_level(subtree, level + 1)
        else:
            if self.callback:
                self.callback(self.selected_path)
            self.destroy()
