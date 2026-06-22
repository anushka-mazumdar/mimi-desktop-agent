import customtkinter as ctk
import tkinter as tk
from typing import Optional


class MimiWidget:
    """
    Main desktop widget class for the Mimi AI Assistant.
    
    This class creates a floating, always-on-top window that serves as
    the primary interface for user interaction with the agent system.
    
    Attributes:
        root (ctk.CTk): The main application window
        chat_display (ctk.CTkTextbox): Read-only chat history area
        input_box (ctk.CTkEntry): User input field
        send_button (ctk.CTkButton): Send message button
        status_label (ctk.CTkLabel): Status indicator
        header_label (ctk.CTkLabel): Widget title
        drag_data (dict): Stores drag start coordinates for window movement
        is_dragging (bool): Flag indicating if drag is in progress
    """
    
    # Color scheme - consistent dark theme
    COLORS = {
        "bg_dark": "#1a1a1a",
        "bg_medium": "#2b2b2b",
        "bg_input": "#3a3a3a",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "accent": "#4a9eff",
        "accent_hover": "#5aafff",
        "border": "#404040",
        "status_ready": "#4caf50",
        "status_busy": "#ff9800"
    }
    
    def __init__(self):
        """
        Initialize the Mimi widget.
        
        Sets up the CustomTkinter window, configures the appearance,
        and creates all UI components.
        """
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Mimi")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        
        # Remove default title bar for custom header
        self.root.overrideredirect(True)
        
        # Initialize drag tracking
        self.drag_data = {"x": 0, "y": 0}
        self.is_dragging = False
        
        # Position window in bottom-right corner
        self._position_window_bottom_right()
        
        # Build the UI
        self._build_ui()
        
        # Bind events for window dragging
        self._bind_drag_events()
        
        # Bind keyboard shortcuts
        self.root.bind("<Return>", self._on_enter_pressed)
    
    def _position_window_bottom_right(self) -> None:
        """
        Position the window near the bottom-right corner of the screen.
        
        Places the window with a 50px margin from the right and bottom edges.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position with margin
        window_width = 400
        window_height = 600
        x_pos = screen_width - window_width - 50
        y_pos = screen_height - window_height - 50
        
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    
    def _build_ui(self) -> None:
        """
        Build the complete UI hierarchy.
        
        Creates the main container, header, chat display, input area,
        and status components in a structured layout.
        """
        # Main container with rounded corners
        self.main_container = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color=self.COLORS["bg_dark"],
            border_width=2,
            border_color=self.COLORS["border"]
        )
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Build each section
        self._build_header()
        self._build_chat_display()
        self._build_input_area()
        self._build_status_bar()
    
    def _build_header(self) -> None:
        """
        Create the draggable header section.
        
        Includes the Mimi title and provides drag functionality
        through mouse events on the header frame.
        """
        self.header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=self.COLORS["bg_medium"],
            corner_radius=10,
            height=50
        )
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)
        
        # Title label
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="✨ Mimi",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.COLORS["text_primary"]
        )
        self.header_label.pack(side="left", padx=15, pady=10)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.header_frame,
            text="✕",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=30,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#ff4444",
            text_color=self.COLORS["text_secondary"],
            command=self.root.destroy
        )
        self.close_button.pack(side="right", padx=10, pady=10)
        
        # Bind drag events to header
        for widget in [self.header_frame, self.header_label]:
            widget.bind("<Button-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)
            widget.bind("<ButtonRelease-1>", self._on_drag_end)
    
    def _build_chat_display(self) -> None:
        """
        Create the chat history display area.
        
        A read-only text box that shows conversation history
        with a modern, clean appearance.
        """
        self.chat_container = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            corner_radius=10
        )
        self.chat_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.chat_display = ctk.CTkTextbox(
            self.chat_container,
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS["text_primary"],
            fg_color=self.COLORS["bg_dark"],
            border_width=1,
            border_color=self.COLORS["border"],
            corner_radius=10,
            wrap="word",
            state="disabled"  # Read-only
        )
        self.chat_display.pack(fill="both", expand=True)
        
        # Add placeholder message
        self.add_message("Welcome to Mimi! 🎯\nI'm ready to assist you.")
    
    def _build_input_area(self) -> None:
        """
        Create the input area with text field and send button.
        
        Includes a multi-line capable input field and a send button
        that triggers message processing.
        """
        self.input_container = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            corner_radius=10
        )
        self.input_container.pack(fill="x", padx=10, pady=(5, 10))
        
        # Configure grid for input layout
        self.input_container.grid_columnconfigure(0, weight=1)
        self.input_container.grid_columnconfigure(1, weight=0)
        
        # Input text box
        self.input_box = ctk.CTkEntry(
            self.input_container,
            font=ctk.CTkFont(size=13),
            placeholder_text="Type your message...",
            height=40,
            corner_radius=10,
            border_width=1,
            border_color=self.COLORS["border"],
            fg_color=self.COLORS["bg_input"],
            text_color=self.COLORS["text_primary"]
        )
        self.input_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_box.bind("<FocusIn>", self._on_input_focus)
        self.input_box.bind("<FocusOut>", self._on_input_blur)
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.input_container,
            text="Send",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=80,
            corner_radius=10,
            fg_color=self.COLORS["accent"],
            hover_color=self.COLORS["accent_hover"],
            text_color=self.COLORS["text_primary"],
            command=self._on_send_click
        )
        self.send_button.grid(row=0, column=1, sticky="ew")
    
    def _build_status_bar(self) -> None:
        """
        Create the status bar at the bottom of the widget.
        
        Shows the current status of the assistant (Ready, Busy, etc.)
        with a colored indicator dot.
        """
        self.status_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=30
        )
        self.status_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        # Status label with indicator
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● Ready",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS["status_ready"]
        )
        self.status_label.pack(side="left")
        
        # Version info
        self.version_label = ctk.CTkLabel(
            self.status_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS["text_secondary"]
        )
        self.version_label.pack(side="right")
    
    def _bind_drag_events(self) -> None:
        """
        Bind mouse events to the entire window for drag functionality.
        
        Allows dragging from any point on the widget.
        """
        self.root.bind("<Button-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)
        self.root.bind("<ButtonRelease-1>", self._on_drag_end)
    
    def _on_drag_start(self, event) -> None:
        """
        Handle drag start event.
        
        Records the starting position for the drag operation.
        
        Args:
            event: The mouse event object
        """
        self.is_dragging = True
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()
    
    def _on_drag_motion(self, event) -> None:
        """
        Handle drag motion event.
        
        Updates the window position during a drag operation.
        
        Args:
            event: The mouse event object
        """
        if self.is_dragging:
            x = event.x_root - self.drag_data["x"]
            y = event.y_root - self.drag_data["y"]
            self.root.geometry(f"+{x}+{y}")
    
    def _on_drag_end(self, event) -> None:
        """
        Handle drag end event.
        
        Resets the dragging flag when the mouse button is released.
        
        Args:
            event: The mouse event object
        """
        self.is_dragging = False
    
    def _on_send_click(self) -> None:
        """
        Handle send button click event.
        
        Reads the input text, adds it to the chat display,
        and clears the input field for the next message.
        """
        message = self.input_box.get().strip()
        if message:
            self.add_message(f"You: {message}")
            self.input_box.delete(0, tk.END)
            # Future: Here we'll process the message with the agent
    
    def _on_enter_pressed(self, event) -> None:
        """
        Handle Enter key press event.
        
        Triggers the same action as clicking the send button.
        
        Args:
            event: The keyboard event object
        """
        self._on_send_click()
    
    def _on_input_focus(self, event) -> None:
        """
        Handle input field focus event.
        
        Highlights the input field when it receives focus.
        
        Args:
            event: The focus event object
        """
        self.input_box.configure(border_color=self.COLORS["accent"])
    
    def _on_input_blur(self, event) -> None:
        """
        Handle input field blur event.
        
        Removes the highlight when the input field loses focus.
        
        Args:
            event: The focus event object
        """
        self.input_box.configure(border_color=self.COLORS["border"])
    
    def add_message(self, message: str) -> None:
        """
        Add a message to the chat display.
        
        This method is the primary way to display messages in the chat area.
        
        Args:
            message (str): The message text to display
        
        Example:
            >>> widget.add_message("Hello, how can I help?")
        
        Note:
            Messages are automatically appended with a newline.
            The display remains scrollable and read-only.
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
    
    def set_status(self, status: str) -> None:
        """
        Update the status label with a new status message.
        
        Provides visual feedback about the assistant's current state.
        
        Args:
            status (str): Status text to display
        
        Example:
            >>> widget.set_status("Processing...")
            >>> widget.set_status("Ready")
        
        Note:
            Status color automatically changes based on common status values:
            - "Ready": Green
            - "Busy", "Processing", "Thinking": Orange
            - "Error": Red
        """
        status_text = f"● {status}"
        
        # Color coding based on status
        status_lower = status.lower()
        if status_lower in ["ready", "idle", "done"]:
            color = self.COLORS["status_ready"]
        elif status_lower in ["busy", "processing", "thinking", "working"]:
            color = self.COLORS["status_busy"]
        elif status_lower in ["error", "failed", "error"]:
            color = "#ff4444"
        else:
            color = self.COLORS["text_secondary"]
        
        self.status_label.configure(text=status_text, text_color=color)
    
    def run(self) -> None:
        """
        Start the main application event loop.
        
        This method should be called after initialization to display
        the widget and begin processing user events.
        
        Example:
            >>> if __name__ == "__main__":
            ...     widget = MimiWidget()
            ...     widget.run()
        
        Note:
            This method blocks execution until the window is closed.
        """
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()
    
    def destroy(self) -> None:
        """
        Clean up and destroy the widget.
        
        Properly closes the window and releases resources.
        """
        self.root.destroy()


# ----------------------------
# Standalone Testing
# ----------------------------

if __name__ == "__main__":
    """
    Standalone test entry point.
    
    Creates and displays the Mimi widget for independent testing
    without requiring the full agent system.
    """
    try:
        # Create and run the widget
        mimi = MimiWidget()
        mimi.run()
    except KeyboardInterrupt:
        print("\nMimi closed by user.")
    except Exception as e:
        print(f"Error running Mimi: {e}")
        raise