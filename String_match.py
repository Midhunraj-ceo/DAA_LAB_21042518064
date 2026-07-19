import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import string
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class StringMatchingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("String Matching Algorithm Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Apply custom styles
        self.setup_styles()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Basic Search
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Basic Search")
        self.setup_basic_search_tab()
        
        # Tab 2: Performance Comparison
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Performance Comparison")
        self.setup_performance_tab()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Normal.TLabel', font=('Helvetica', 10))
        
    def setup_basic_search_tab(self):
        """Setup the basic search tab"""
        # Input frame
        input_frame = ttk.LabelFrame(self.tab1, text="Input", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Text input
        ttk.Label(input_frame, text="Text:", font=('Helvetica', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.text_input = scrolledtext.ScrolledText(input_frame, height=4, width=80, wrap=tk.WORD)
        self.text_input.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Pattern input
        ttk.Label(input_frame, text="Pattern:", font=('Helvetica', 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.pattern_input = ttk.Entry(input_frame, width=80)
        self.pattern_input.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Example data buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Button(button_frame, text="Load Example 1", 
                  command=self.load_example_1).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load Example 2", 
                  command=self.load_example_2).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_inputs).pack(side="left", padx=5)
        
        input_frame.columnconfigure(0, weight=1)
        
        # Algorithm buttons frame
        algo_frame = ttk.LabelFrame(self.tab1, text="Algorithms", padding=10)
        algo_frame.pack(fill="x", padx=10, pady=10)
        
        button_container = ttk.Frame(algo_frame)
        button_container.pack(fill="x")
        
        ttk.Button(button_container, text="Run Naive Search", 
                  command=self.run_naive_search).pack(side="left", padx=5)
        ttk.Button(button_container, text="Run KMP Search", 
                  command=self.run_kmp_search).pack(side="left", padx=5)
        ttk.Button(button_container, text="Run Rabin-Karp", 
                  command=self.run_rabin_karp).pack(side="left", padx=5)
        ttk.Button(button_container, text="Run All", 
                  command=self.run_all).pack(side="left", padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.tab1, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results text with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80, 
                                                      font=('Courier', 10), state="disabled")
        self.results_text.pack(fill="both", expand=True)
        
        # Configure text tags for coloring
        self.results_text.tag_config("header", foreground="#1f77b4", font=('Courier', 10, 'bold'))
        self.results_text.tag_config("matches", foreground="#2ca02c")
        self.results_text.tag_config("comparisons", foreground="#ff7f0e")
        self.results_text.tag_config("timing", foreground="#d62728")
        
    def setup_performance_tab(self):
        """Setup the performance comparison tab"""
        control_frame = ttk.LabelFrame(self.tab2, text="Performance Test Parameters", padding=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Text size
        ttk.Label(control_frame, text="Text Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.text_size_var = tk.IntVar(value=10000)
        text_size_spinbox = ttk.Spinbox(control_frame, from_=1000, to=100000, textvariable=self.text_size_var, width=15)
        text_size_spinbox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(control_frame, text="Run Performance Comparison", 
                  command=self.run_performance_comparison).grid(row=0, column=2, padx=10)
        
        # Canvas for plot
        self.canvas_frame = ttk.Frame(self.tab2)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def append_results(self, text, tag=""):
        """Append text to results display"""
        self.results_text.config(state="normal")
        self.results_text.insert("end", text, tag)
        self.results_text.see("end")
        self.results_text.config(state="disabled")
        
    def clear_results(self):
        """Clear results display"""
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.config(state="disabled")
        
    def load_example_1(self):
        """Load example 1"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", "AABAACAADAABAABA")
        self.pattern_input.delete(0, "end")
        self.pattern_input.insert(0, "AABA")
        
    def load_example_2(self):
        """Load example 2"""
        self.text_input.delete("1.0", "end")
        self.text_input.insert("1.0", "ABCCDDEFEFGGHIJKLMNOP" * 10)
        self.pattern_input.delete(0, "end")
        self.pattern_input.insert(0, "DEFG")
        
    def clear_inputs(self):
        """Clear all inputs"""
        self.text_input.delete("1.0", "end")
        self.pattern_input.delete(0, "end")
        self.clear_results()
        
    def validate_inputs(self):
        """Validate user inputs"""
        text = self.text_input.get("1.0", "end-1c").strip()
        pattern = self.pattern_input.get().strip()
        
        if not text:
            messagebox.showerror("Error", "Please enter text")
            return None, None
        if not pattern:
            messagebox.showerror("Error", "Please enter a pattern")
            return None, None
        if len(pattern) > len(text):
            messagebox.showerror("Error", "Pattern cannot be longer than text")
            return None, None
            
        return text, pattern
        
    def run_naive_search(self):
        """Run naive search algorithm"""
        text, pattern = self.validate_inputs()
        if text is None:
            return
            
        self.clear_results()
        self.append_results("Running Naive Search...\n\n", "header")
        
        start_time = time.time()
        matches, comparisons = naive_search(text, pattern)
        elapsed = time.time() - start_time
        
        self.display_results("Naive Search", text, pattern, matches, comparisons, elapsed)
        
    def run_kmp_search(self):
        """Run KMP search algorithm"""
        text, pattern = self.validate_inputs()
        if text is None:
            return
            
        self.clear_results()
        self.append_results("Running KMP Search...\n\n", "header")
        
        start_time = time.time()
        matches, comparisons = kmp_search(text, pattern)
        elapsed = time.time() - start_time
        
        self.display_results("KMP Search", text, pattern, matches, comparisons, elapsed)
        
    def run_rabin_karp(self):
        """Run Rabin-Karp search algorithm"""
        text, pattern = self.validate_inputs()
        if text is None:
            return
            
        self.clear_results()
        self.append_results("Running Rabin-Karp Search...\n\n", "header")
        
        start_time = time.time()
        matches, comparisons = rabin_karp(text, pattern)
        elapsed = time.time() - start_time
        
        self.display_results("Rabin-Karp Search", text, pattern, matches, comparisons, elapsed)
        
    def run_all(self):
        """Run all three algorithms"""
        text, pattern = self.validate_inputs()
        if text is None:
            return
            
        self.clear_results()
        self.append_results("Running All Algorithms...\n" + "="*70 + "\n\n", "header")
        
        algorithms = [
            ("Naive Search", naive_search),
            ("KMP Search", kmp_search),
            ("Rabin-Karp Search", rabin_karp)
        ]
        
        for algo_name, algo_func in algorithms:
            start_time = time.time()
            matches, comparisons = algo_func(text, pattern)
            elapsed = time.time() - start_time
            
            self.display_results(algo_name, text, pattern, matches, comparisons, elapsed)
            self.append_results("\n" + "-"*70 + "\n\n", "header")
            
    def display_results(self, algo_name, text, pattern, matches, comparisons, elapsed):
        """Display results for an algorithm"""
        self.append_results(f"{algo_name}:\n", "header")
        self.append_results(f"  Text: {text[:60]}{'...' if len(text) > 60 else ''}\n")
        self.append_results(f"  Pattern: {pattern}\n\n")
        self.append_results(f"  Matches found: ", "")
        self.append_results(f"{len(matches)}\n", "matches")
        self.append_results(f"  Positions: {matches if matches else 'None'}\n")
        self.append_results(f"  Character comparisons: ", "")
        self.append_results(f"{comparisons}\n", "comparisons")
        self.append_results(f"  Execution time: ", "")
        self.append_results(f"{elapsed*1000:.4f} ms\n", "timing")
        
    def run_performance_comparison(self):
        """Run performance comparison on various pattern sizes"""
        text_size = self.text_size_var.get()
        
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
            
        # Generate random text
        text_large = ''.join(random.choices('ABCD', k=text_size))
        patterns = ['AB', 'ABCD', 'ABCDAB', 'ABCDABCD']
        
        # Collect data
        naive_times = []
        kmp_times = []
        rk_times = []
        
        for p in patterns:
            # Naive
            start = time.time()
            naive_search(text_large, p)
            naive_times.append((time.time() - start) * 1000)
            
            # KMP
            start = time.time()
            kmp_search(text_large, p)
            kmp_times.append((time.time() - start) * 1000)
            
            # Rabin-Karp
            start = time.time()
            rabin_karp(text_large, p)
            rk_times.append((time.time() - start) * 1000)
        
        # Create plot
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        x = range(len(patterns))
        width = 0.25
        
        ax.bar([i - width for i in x], naive_times, width, label='Naive Search', color='#ff7f0e')
        ax.bar(x, kmp_times, width, label='KMP Search', color='#2ca02c')
        ax.bar([i + width for i in x], rk_times, width, label='Rabin-Karp', color='#1f77b4')
        
        ax.set_xlabel('Pattern', fontsize=10, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=10, fontweight='bold')
        ax.set_title(f'Performance Comparison (Text Size: {text_size})', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(patterns)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# Algorithm Implementations
def naive_search(text, pattern):
    n, m = len(text), len(pattern)
    matches, comparisons = [], 0
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            matches.append(i)
    return matches, comparisons


def compute_lps(pattern):
    m = len(pattern)
    lps = [0] * m
    length, i = 0, 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    lps = compute_lps(pattern)
    matches, comparisons = [], 0
    i = j = 0
    while i < n:
        comparisons += 1
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == m:
            matches.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches, comparisons


def rabin_karp(text, pattern, q=101):
    n, m = len(text), len(pattern)
    d = 256
    h = pow(d, m - 1, q)
    p_hash = t_hash = 0
    matches, comparisons = [], 0
    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % q
        t_hash = (d * t_hash + ord(text[i])) % q
    for s in range(n - m + 1):
        if p_hash == t_hash:
            for k in range(m):
                comparisons += 1
                if text[s + k] != pattern[k]:
                    break
            else:
                matches.append(s)
        if s < n - m:
            t_hash = (d * (t_hash - ord(text[s]) * h) + ord(text[s + m])) % q
            if t_hash < 0:
                t_hash += q
    return matches, comparisons


if __name__ == "__main__":
    root = tk.Tk()
    app = StringMatchingGUI(root)
    root.mainloop()