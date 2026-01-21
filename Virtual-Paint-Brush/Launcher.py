import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import os
import sys

class AIPainterLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Painter | Premium Edition")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # --- THEME COLORS ---
        self.bg_color = "#1e1e1e"      # Dark Grey Background
        self.accent_color = "#007acc"  # Blue Accent
        self.text_color = "#ffffff"    # White Text
        self.btn_color = "#333333"     # Darker Button
        
        self.root.configure(bg=self.bg_color)
        
        # --- STYLES ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure Button Style
        self.style.configure('TButton', 
                             font=('Segoe UI', 12), 
                             borderwidth=0, 
                             background=self.btn_color, 
                             foreground=self.text_color,
                             padding=10)
        self.style.map('TButton', 
                       background=[('active', self.accent_color)], 
                       foreground=[('active', 'white')])

        # --- UI ELEMENTS ---
        self.create_widgets()

    def create_widgets(self):
        # 1. Header Section
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(pady=40)
        
        title_label = tk.Label(header_frame, 
                               text="VIRTUAL PAINT BRUSH", 
                               font=("Segoe UI", 24, "bold"), 
                               bg=self.bg_color, 
                               fg="white")
        title_label.pack()

        subtitle_label = tk.Label(header_frame, 
                                  text="Gesture Controlled Digital Canvas", 
                                  font=("Segoe UI", 12), 
                                  bg=self.bg_color, 
                                  fg="#aaaaaa")
        subtitle_label.pack(pady=5)

        # 2. Buttons Section
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=20)

        # Start Button
        self.btn_start = ttk.Button(btn_frame, text="LAUNCH PAINTER", command=self.run_painter, width=25)
        self.btn_start.pack(pady=10)

        # Instructions Button
        self.btn_help = ttk.Button(btn_frame, text="CONTROLS / HELP", command=self.show_help, width=25)
        self.btn_help.pack(pady=10)
        
        # Exit Button
        self.btn_exit = ttk.Button(btn_frame, text="EXIT", command=self.root.quit, width=25)
        self.btn_exit.pack(pady=10)

        # Footer
        footer_label = tk.Label(self.root, text="v2.2 | Powered by OpenCV & MediaPipe", 
                                font=("Segoe UI", 8), bg=self.bg_color, fg="#555555")
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def run_painter(self):
        """Runs the AIPV4_2.py script as a subprocess"""
        try:
            # Check if file exists
            if not os.path.exists("AIPV4_2.py"):
                messagebox.showerror("Error", "Could not find 'APV2.2.py'.\nMake sure it is in the same folder as this launcher.")
                return
            
            # Minimize Launcher
            self.root.iconify() 
            
            # Run the script
            # We use sys.executable to ensure we use the same python interpreter
            subprocess.run([sys.executable, "AIPV4_2.py"])
            
            # Restore Launcher after painter closes
            self.root.deiconify() 
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application:\n{e}")
            self.root.deiconify()

    def show_help(self):
        help_text = (
            "CONTROLS:\n\n"
            "1. DRAWING MODE:\n"
            "   - Raise Index Finger ONLY.\n"
            "   - Move hand to draw.\n\n"
            "2. SELECTION MODE:\n"
            "   - Raise Index + Middle Fingers.\n"
            "   - Move hand to select colors/tools from the top menu.\n\n"
            "3. CLEAR CANVAS:\n"
            "   - Press C to clear the canvas.\n\n"
            "4. SAVE IMAGE:\n"
            "   - Press S to save your artwork as 'Art_***.jpg'.\n\n"
            "5. EXIT:\n"
            "   - Press 'q' on your keyboard while in the camera window."
        )
        messagebox.showinfo("How to Use", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = AIPainterLauncher(root)
    root.mainloop()