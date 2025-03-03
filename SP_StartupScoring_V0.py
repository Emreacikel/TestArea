import tkinter as tk
from tkinter import ttk

class FullScreenApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Full Screen Application with Tabs")
        
        # Create a full-screen window
        self.master.attributes("-fullscreen", True)
        
        # Create a tab control
        self.tab_control = ttk.Notebook(self.master)
        
        # Create 8 tabs
        for i in range(1, 9):
            tab = ttk.Frame(self.tab_control)
            if i == 1:
                tab_label = "General"  # Rename Tab 1 to "General"
            elif i == 2:
                tab_label = "Market"  # Rename Tab 2 to "Market"
            elif i == 3:
                tab_label = "Team"  # Rename Tab 3 to "Team"
            else:
                tab_label = f"Tab {i}"
            self.tab_control.add(tab, text=tab_label)
            label = tk.Label(tab, text=f"This is {tab_label}", font=("Arial", 24))
            label.pack(pady=20)
        
        self.tab_control.pack(expand=1, fill="both")

        # Bind the escape key to exit full screen
        self.master.bind("<Escape>", self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        # Toggle full screen mode
        self.master.attributes("-fullscreen", not self.master.attributes("-fullscreen"))

if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenApp(root)
    root.mainloop()