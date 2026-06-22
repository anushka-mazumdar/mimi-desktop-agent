import customtkinter as ctk
from typing import Optional
from .widget_state import WidgetStateManager, WidgetState
from .context_menu import MimiContextMenu
from .command_bar import CommandBar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MimiPet(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        self.parent = parent
        self.state_manager = WidgetStateManager()
        self._command_bar_visible = False
        self._input_mode = "keyboard"

        self.title("")
        self.geometry("120x50")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#2b2b2b")

        self._setup_ui()
        self._setup_position()
        self._setup_drag()
        self._setup_context_menu()
        self._setup_command_bar()
        self._setup_state_callback()

        self.bind("<Button-1>", self._on_left_click)
        self.bind("<Button-3>", self._on_right_click)

        self.protocol("WM_DELETE_WINDOW", self._on_exit)

    def _setup_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#2b2b2b",
            border_width=1,
            border_color="#3a3a3a"
        )
        self.container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.pet_label = ctk.CTkLabel(
            self.container,
            text="🐱 Mimi",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff"
        )
        self.pet_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

    def _setup_position(self) -> None:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 130
        y = screen_height - 80
        self.geometry(f"+{x}+{y}")

    def _setup_drag(self) -> None:
        self._drag_data = {"x": 0, "y": 0}
        self.bind("<ButtonPress-1>", self._drag_start)
        self.bind("<B1-Motion>", self._drag_motion)
        self.pet_label.bind("<ButtonPress-1>", self._drag_start)
        self.pet_label.bind("<B1-Motion>", self._drag_motion)

    def _drag_start(self, event) -> None:
        self._drag_data["x"] = event.x_root - self.winfo_x()
        self._drag_data["y"] = event.y_root - self.winfo_y()

    def _drag_motion(self, event) -> None:
        x = event.x_root - self._drag_data["x"]
        y = event.y_root - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")

    def _setup_context_menu(self) -> None:
        self.context_menu = MimiContextMenu(self)
        self.context_menu.set_keyboard_callback(self._on_keyboard_selected)
        self.context_menu.set_voice_callback(self._on_voice_selected)
        self.context_menu.set_settings_callback(self._on_settings_selected)
        self.context_menu.set_exit_callback(self._on_exit)

    def _setup_command_bar(self) -> None:
        self.command_bar = CommandBar(self.parent)
        self.command_bar.on_submit(self._on_task_submitted)

    def _setup_state_callback(self) -> None:
        self.state_manager.register_callback(self._on_state_changed)

    def _on_state_changed(self, state: WidgetState) -> None:
        print(f"State changed: {state.value.upper()}")

    def _on_left_click(self, event=None) -> None:
        if self._command_bar_visible:
            self._hide_command_bar()
        else:
            self._show_command_bar()

    def _on_right_click(self, event) -> None:
        self.context_menu.show(event.x_root, event.y_root)

    def _show_command_bar(self) -> None:
        pet_x = self.winfo_x()
        pet_y = self.winfo_y()
        bar_x = pet_x - 410
        bar_y = pet_y + 5
        self.command_bar.show_bar(bar_x, bar_y)
        self._command_bar_visible = True
        self.state_manager.set_state(WidgetState.INPUT_OPEN)

    def _hide_command_bar(self) -> None:
        self.command_bar.hide_bar()
        self._command_bar_visible = False
        if self.state_manager.get_state() != WidgetState.IDLE:
            self.state_manager.set_state(WidgetState.IDLE)

    def _on_task_submitted(self, task: str) -> None:
        print(f"Task received: {task}")
        self.state_manager.set_state(WidgetState.THINKING)
        self._command_bar_visible = False
        self.parent.after(1000, self._reset_to_idle)

    def _reset_to_idle(self) -> None:
        self.state_manager.set_state(WidgetState.IDLE)

    def _on_keyboard_selected(self) -> None:
        self._input_mode = "keyboard"
        print("Keyboard mode selected")

    def _on_voice_selected(self) -> None:
        self._input_mode = "voice"
        print("Voice mode selected")

    def _on_settings_selected(self) -> None:
        print("Settings clicked")

    def _on_exit(self) -> None:
        self.command_bar.hide_bar()
        self.parent.quit()
        self.parent.destroy()

    def show_pet(self) -> None:
        self.deiconify()
        self.lift()

    def hide_pet(self) -> None:
        self.withdraw()

    def run(self) -> None:
        self.show_pet()


if __name__ == "__main__":
    def on_state_change(state: WidgetState) -> None:
        pass

    root = ctk.CTk()
    root.title("Mimi Pet Test")
    root.geometry("300x200")
    root.withdraw()

    pet = MimiPet(root)

    def show_pet():
        pet.show_pet()
        root.withdraw()

    root.after(100, show_pet)
    root.mainloop()