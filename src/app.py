import tkinter as tk
from tkinter import ttk
from analyzer import NeuroFenceAnalyzer

class NeuroFenceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroFence - LLM Security & Forensics")
        self.root.geometry("600x400")
        
        # Simple Desktop UI Layout
        self.label = ttk.Label(root, text="NeuroFence AI Security Tool", font=("Arial", 16))
        self.label.pack(pady=20)
        
        self.btn = ttk.Button(root, text="Run Activation Scan", command=self.run_scan)
        self.btn.pack(pady=10)
        
    def run_scan(self):
        analyzer = NeuroFenceAnalyzer()
        print("Scan triggered via Desktop UI.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeuroFenceApp(root)
    root.mainloop()