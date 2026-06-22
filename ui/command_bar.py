import customtkinter as ctk
from typing import Optional, Callable

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CommandBar(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        self.parent = parent
        self._submit_callback: Optional[Callable[[str], None]] = None

        self.title("")
        self.geometry("400x60")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.withdraw()

        self.configure(fg_color="#2b2b2b")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.input_field = ctk.CTkEntry(
            self,
            placeholder_text="Enter a task...",
            font=("Segoe UI", 14),
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#3a3a3a",
            fg_color="#1e1e1e",
            text_color="#ffffff"
        )
        self.input_field.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.input_field.bind("<Return>", self._handle_submit)
        self.input_field.bind("<Escape>", self._handle_escape)

        self.run_button = ctk.CTkButton(
            self,
            text="➜",
            font=("Segoe UI", 18),
            width=50,
            height=40,
            corner_radius=8,
            fg_color="#4a6fa5",
            hover_color="#5a7fb5",
            command=self._handle_submit
        )
        self.run_button.grid(row=0, column=1, padx=(0, 10), pady=10)

        self.bind("<Escape>", self._handle_escape)
        self.bind("<FocusOut>", self._handle_focus_out)

        self._initial_x = 0
        self._initial_y = 0

    def _handle_submit(self, event=None) -> None:
        text = self.input_field.get().strip()
        if not text:
            return

        if self._submit_callback:
            self._submit_callback(text)

        self.clear()
        self.hide_bar()

    def _handle_escape(self, event=None) -> None:
        self.clear()
        self.hide_bar()

    def _handle_focus_out(self, event=None) -> None:
        if event and event.widget == self:
            self.after(100, self._check_focus)

    def _check_focus(self) -> None:
        if not self.focus_get():
            self.hide_bar()

    def show_bar(self, x: int, y: int) -> None:
        self._initial_x = x
        self._initial_y = y

        self.geometry(f"400x60+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()
        self.after(50, self.focus_input)

    def hide_bar(self) -> None:
        self.withdraw()

    def clear(self) -> None:
        self.input_field.delete(0, "end")

    def get_text(self) -> str:
        return self.input_field.get().strip()

    def focus_input(self) -> None:
        self.input_field.focus_set()
        self.input_field.select_range(0, "end")

    def on_submit(self, callback: Callable[[str], None]) -> None:
        self._submit_callback = callback


if __name__ == "__main__":
    def on_task_submitted(task: str) -> None:
        print(f"Submitted: {task}")

    root = ctk.CTk()
    root.title("Command Bar Test")
    root.geometry("500x400")
    root.configure(fg_color="#1a1a1a")

    command_bar = CommandBar(root)
    command_bar.on_submit(on_task_submitted)

    def show_command_bar():
        x = 50
        y = 100
        command_bar.show_bar(x, y)

    test_button = ctk.CTkButton(
        root,
        text="Show Command Bar",
        font=("Segoe UI", 16),
        height=50,
        width=200,
        corner_radius=10,
        command=show_command_bar
    )
    test_button.pack(expand=True)

    root.mainloop()