import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

# --- Algorithm Implementations ---
comparison_count = 0  # Global counter

def min_max_dc(arr, low, high):
    """Divide and Conquer approach for finding min and max"""
    global comparison_count
    # Base case: single element
    if low == high:
        return arr[low], arr[low]
    # Base case: two elements
    if high == low + 1:
        comparison_count += 1
        if arr[low] < arr[high]:
            return arr[low], arr[high]
        return arr[high], arr[low]

    # Divide
    mid = (low + high) // 2
    lmin, lmax = min_max_dc(arr, low, mid)
    rmin, rmax = min_max_dc(arr, mid + 1, high)

    # Conquer: combine with 2 comparisons
    comparison_count += 1
    overall_min = lmin if lmin < rmin else rmin
    comparison_count += 1
    overall_max = lmax if lmax > rmax else rmax
    return overall_min, overall_max

def min_max_naive(arr):
    """Naive approach for finding min and max"""
    mn, mx = arr[0], arr[0]
    comps = 0
    for x in arr[1:]:
        comps += 1
        if x < mn: mn = x
        comps += 1
        if x > mx: mx = x
    return mn, mx, comps


class MinMaxVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Min-Max Find: Divide and Conquer vs Naive")
        self.root.geometry("1500x900")
        self.root.configure(bg="#f0f0f0")
        
        # Data
        self.array = []
        self.min_val = None
        self.max_val = None
        self.dc_comps = 0
        self.naive_comps = 0
        
        self.setup_styles()
        self.create_widgets()
        self.load_example_1()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Info.TLabel', font=('Courier', 10))
        
    def create_widgets(self):
        """Create main GUI widgets"""
        # Top control panel
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Input section
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Array Input:", font=('Helvetica', 10, 'bold')).pack(side="left", padx=5)
        self.array_input = ttk.Entry(input_frame, width=80)
        self.array_input.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Set Array", command=self.set_array).pack(side="left", padx=5)
        
        # Algorithm buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Run Divide & Conquer", 
                  command=self.run_dc).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Naive", 
                  command=self.run_naive).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Both", 
                  command=self.run_both).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", 
                  command=self.reset_view).pack(side="left", padx=5)
        
        # Example buttons
        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=10)
        
        example_frame = ttk.Frame(control_frame)
        example_frame.pack(fill="x", pady=5)
        
        ttk.Label(example_frame, text="Load Example:", font=('Helvetica', 10, 'bold')).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 1 (10 elements)", 
                  command=self.load_example_1).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 2 (20 elements)", 
                  command=self.load_example_2).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 3 (50 elements)", 
                  command=self.load_example_3).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Random (100 elements)", 
                  command=self.load_random).pack(side="left", padx=5)
        
        # Main content
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Visualization and Results
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Array visualization
        array_frame = ttk.LabelFrame(left_frame, text="Array Visualization", padding=5)
        array_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        self.array_canvas_frame = ttk.Frame(array_frame)
        self.array_canvas_frame.pack(fill="both", expand=True)
        
        # Results display
        results_frame = ttk.LabelFrame(left_frame, text="Results", padding=10)
        results_frame.pack(fill="x")
        
        self.results_text = scrolledtext.ScrolledText(results_frame, font=('Courier', 10), height=8)
        self.results_text.pack(fill="both", expand=True)
        
        self.results_text.tag_config("header", foreground="#1f77b4", font=('Courier', 11, 'bold'))
        self.results_text.tag_config("dc", foreground="#2ca02c", font=('Courier', 10, 'bold'))
        self.results_text.tag_config("naive", foreground="#ff7f0e", font=('Courier', 10, 'bold'))
        self.results_text.tag_config("minmax", foreground="#d62728", font=('Courier', 10, 'bold'))
        self.results_text.tag_config("formula", foreground="#d62728", font=('Courier', 10, 'bold'))
        
        # Right side - Tabs
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", padx=(5, 0), expand=True)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Performance tab
        perf_tab = ttk.Frame(self.notebook)
        self.notebook.add(perf_tab, text="Performance Analysis")
        self.create_performance_tab(perf_tab)
        
        # Comparison tab
        comp_tab = ttk.Frame(self.notebook)
        self.notebook.add(comp_tab, text="Algorithm Comparison")
        self.create_comparison_tab(comp_tab)
        
        # Algorithm info tab
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="Algorithm Info")
        self.create_info_tab(info_tab)
        
    def create_performance_tab(self, parent):
        """Create performance analysis tab"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Run Performance Analysis", 
                  command=self.run_performance_analysis).pack(side="left", padx=5)
        
        self.perf_canvas_frame = ttk.Frame(frame)
        self.perf_canvas_frame.pack(fill="both", expand=True)
        
    def create_comparison_tab(self, parent):
        """Create algorithm comparison tab"""
        self.comparison_text = scrolledtext.ScrolledText(parent, font=('Courier', 9), 
                                                         height=30, width=50)
        self.comparison_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.comparison_text.tag_config("header", foreground="#1f77b4", font=('Courier', 11, 'bold'))
        self.comparison_text.tag_config("dc", foreground="#2ca02c")
        self.comparison_text.tag_config("naive", foreground="#ff7f0e")
        self.comparison_text.tag_config("formula", foreground="#d62728", font=('Courier', 10, 'bold'))
        
    def create_info_tab(self, parent):
        """Create algorithm info tab"""
        info_text = scrolledtext.ScrolledText(parent, font=('Courier', 9), height=30)
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_text.insert("end", "MIN-MAX DIVIDE AND CONQUER\n", "header")
        info_text.insert("end", "=" * 50 + "\n\n")
        
        info_text.insert("end", "Algorithm Overview:\n", "header")
        info_text.insert("end", "Finds both minimum and maximum in an array using\n")
        info_text.insert("end", "divide and conquer approach with fewer comparisons.\n\n")
        
        info_text.insert("end", "Time Complexity:\n", "header")
        info_text.insert("end", "Divide & Conquer: O(n)\n", "dc")
        info_text.insert("end", "Comparisons: 3n/2 - 2\n", "formula")
        info_text.insert("end", "Naive: O(n)\n", "naive")
        info_text.insert("end", "Comparisons: 2n - 2\n\n")
        
        info_text.insert("end", "How It Works:\n", "header")
        info_text.insert("end", "1. Base case: 1 element → return (element, element)\n")
        info_text.insert("end", "2. Base case: 2 elements → 1 comparison\n")
        info_text.insert("end", "3. Recursive: Divide into two halves\n")
        info_text.insert("end", "4. Recursively find min/max in each half\n")
        info_text.insert("end", "5. Conquer: Combine using 2 comparisons\n\n")
        
        info_text.insert("end", "Key Insight:\n", "header")
        info_text.insert("end", "Instead of comparing each element with both min\n")
        info_text.insert("end", "and max, we find min/max in separate halves first,\n")
        info_text.insert("end", "then only compare the results.\n\n")
        
        info_text.insert("end", "Comparison Count Breakdown:\n", "header")
        info_text.insert("end", "For n elements:\n")
        info_text.insert("end", "  D&C: Approximately 3n/2 - 2 comparisons\n", "dc")
        info_text.insert("end", "  Naive: 2n - 2 comparisons\n\n", "naive")
        
        info_text.insert("end", "Savings:\n", "header")
        info_text.insert("end", "D&C saves ~n/2 comparisons vs Naive approach!\n", "formula")
        
        info_text.config(state="disabled")
        
    def set_array(self):
        """Parse array from input field"""
        try:
            array_str = self.array_input.get().strip()
            if array_str.startswith('[') and array_str.endswith(']'):
                array_str = array_str[1:-1]
            self.array = [int(x.strip()) for x in array_str.split(',')]
            if not self.array:
                messagebox.showerror("Error", "Array cannot be empty!")
                return
            self.reset_view()
            messagebox.showinfo("Success", f"Array loaded with {len(self.array)} elements")
        except ValueError:
            messagebox.showerror("Error", "Invalid array format! Use: 1,2,3,4,5")
            
    def load_example_1(self):
        """Load example 1"""
        self.array = [3, 1, 7, 4, 9, 2, 8, 5, 6, 0]
        self.array_input.delete(0, "end")
        self.array_input.insert(0, str(self.array)[1:-1])
        self.reset_view()
        
    def load_example_2(self):
        """Load example 2"""
        self.array = [random.randint(1, 100) for _ in range(20)]
        self.array_input.delete(0, "end")
        self.array_input.insert(0, str(self.array)[1:-1])
        self.reset_view()
        
    def load_example_3(self):
        """Load example 3"""
        self.array = [random.randint(1, 1000) for _ in range(50)]
        self.array_input.delete(0, "end")
        self.array_input.insert(0, str(self.array)[1:-1])
        self.reset_view()
        
    def load_random(self):
        """Load random array"""
        self.array = [random.randint(1, 1000) for _ in range(100)]
        self.array_input.delete(0, "end")
        self.array_input.insert(0, str(self.array)[1:-1])
        self.reset_view()
        
    def reset_view(self):
        """Reset all displays"""
        self.min_val = None
        self.max_val = None
        self.dc_comps = 0
        self.naive_comps = 0
        self.clear_results()
        self.visualize_array()
        
    def clear_results(self):
        """Clear result displays"""
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.config(state="disabled")
        
        self.comparison_text.config(state="normal")
        self.comparison_text.delete("1.0", "end")
        self.comparison_text.config(state="disabled")
        
    def run_dc(self):
        """Run divide and conquer algorithm"""
        if not self.array:
            messagebox.showwarning("Warning", "Please load an array first!")
            return
            
        global comparison_count
        comparison_count = 0
        self.min_val, self.max_val = min_max_dc(self.array, 0, len(self.array) - 1)
        self.dc_comps = comparison_count
        self.display_results()
        self.visualize_array(highlight="dc")
        
    def run_naive(self):
        """Run naive algorithm"""
        if not self.array:
            messagebox.showwarning("Warning", "Please load an array first!")
            return
            
        self.min_val, self.max_val, self.naive_comps = min_max_naive(self.array)
        self.display_results()
        self.visualize_array(highlight="naive")
        
    def run_both(self):
        """Run both algorithms"""
        if not self.array:
            messagebox.showwarning("Warning", "Please load an array first!")
            return
            
        global comparison_count
        
        # Run D&C
        comparison_count = 0
        min_dc, max_dc = min_max_dc(self.array, 0, len(self.array) - 1)
        self.dc_comps = comparison_count
        
        # Run Naive
        min_naive, max_naive, self.naive_comps = min_max_naive(self.array)
        
        self.min_val = min_dc
        self.max_val = max_dc
        
        self.display_results()
        self.display_comparison()
        self.visualize_array(highlight="both")
        
    def display_results(self):
        """Display results"""
        text = self.results_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", f"Array: {self.array}\n\n")
        text.insert("end", f"Minimum: ", "")
        text.insert("end", f"{self.min_val}\n", "minmax")
        text.insert("end", f"Maximum: ", "")
        text.insert("end", f"{self.max_val}\n\n", "minmax")
        
        if self.dc_comps > 0:
            text.insert("end", f"D&C Comparisons: ", "")
            text.insert("end", f"{self.dc_comps}\n", "dc")
            formula = 3 * len(self.array) // 2 - 2
            text.insert("end", f"Formula (3n/2-2): {formula}\n", "formula")
            
        if self.naive_comps > 0:
            text.insert("end", f"Naive Comparisons: ", "")
            text.insert("end", f"{self.naive_comps}\n", "naive")
            
        if self.dc_comps > 0 and self.naive_comps > 0:
            savings = self.naive_comps - self.dc_comps
            text.insert("end", f"\nSavings: ", "")
            text.insert("end", f"{savings} comparisons\n", "formula")
            
        text.config(state="disabled")
        
    def display_comparison(self):
        """Display algorithm comparison"""
        text = self.comparison_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "ALGORITHM COMPARISON\n", "header")
        text.insert("end", "=" * 50 + "\n\n")
        
        n = len(self.array)
        formula_value = 3 * n // 2 - 2
        
        text.insert("end", f"Array Size: {n}\n\n")
        
        text.insert("end", "Divide & Conquer:\n", "header")
        text.insert("end", f"  Comparisons: {self.dc_comps}\n", "dc")
        text.insert("end", f"  Formula (3n/2-2): {formula_value}\n", "dc")
        text.insert("end", f"  Accuracy: {'✓' if abs(self.dc_comps - formula_value) <= 2 else '✗'}\n\n")
        
        text.insert("end", "Naive Approach:\n", "header")
        text.insert("end", f"  Comparisons: {self.naive_comps}\n", "naive")
        text.insert("end", f"  Formula (2n-2): {2*n - 2}\n", "naive")
        text.insert("end", f"  Accuracy: ✓\n\n")
        
        text.insert("end", "Performance Metrics:\n", "header")
        text.insert("end", f"  Difference: {self.naive_comps - self.dc_comps}\n")
        text.insert("end", f"  Savings: {((self.naive_comps - self.dc_comps) / self.naive_comps * 100):.1f}%\n", "formula")
        text.insert("end", f"  Winner: ", "")
        
        if self.dc_comps < self.naive_comps:
            text.insert("end", "Divide & Conquer ✓\n", "dc")
        else:
            text.insert("end", "Tie\n")
            
        text.config(state="disabled")
        
    def visualize_array(self, highlight=None):
        """Visualize array with min/max highlighted"""
        # Clear previous canvas
        for widget in self.array_canvas_frame.winfo_children():
            widget.destroy()
            
        if not self.array:
            return
            
        # Create figure
        fig = Figure(figsize=(12, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Colors for bars
        colors = []
        for val in self.array:
            if val == self.min_val:
                colors.append("#2ca02c")  # Green for min
            elif val == self.max_val:
                colors.append("#d62728")  # Red for max
            else:
                colors.append("#1f77b4")  # Blue for others
        
        # Bar chart
        bars = ax.bar(range(len(self.array)), self.array, color=colors, edgecolor="black", linewidth=1.5)
        
        # Labels
        ax.set_xlabel("Index", fontsize=10, fontweight='bold')
        ax.set_ylabel("Value", fontsize=10, fontweight='bold')
        ax.set_title(f"Array Visualization (Size: {len(self.array)})", fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Legend
        min_patch = mpatches.Patch(color='#2ca02c', label=f'Min = {self.min_val}')
        max_patch = mpatches.Patch(color='#d62728', label=f'Max = {self.max_val}')
        other_patch = mpatches.Patch(color='#1f77b4', label='Other')
        ax.legend(handles=[min_patch, max_patch, other_patch], loc='upper right')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.array_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def run_performance_analysis(self):
        """Run performance analysis on various sizes"""
        # Clear previous canvas
        for widget in self.perf_canvas_frame.winfo_children():
            widget.destroy()
            
        sizes = [10, 50, 100, 500, 1000, 5000]
        dc_comps_list = []
        naive_comps_list = []
        formula_list = []
        
        for size in sizes:
            arr = [random.randint(1, 10000) for _ in range(size)]
            
            # D&C
            global comparison_count
            comparison_count = 0
            min_max_dc(arr, 0, len(arr) - 1)
            dc_comps_list.append(comparison_count)
            
            # Naive
            _, _, naive_comps = min_max_naive(arr)
            naive_comps_list.append(naive_comps)
            
            # Formula
            formula_list.append(3 * size // 2 - 2)
        
        # Create figure
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot lines
        ax.plot(sizes, dc_comps_list, marker='o', linewidth=2, markersize=8, 
               label='D&C Actual', color='#2ca02c')
        ax.plot(sizes, formula_list, marker='s', linewidth=2, markersize=8, 
               label='D&C Formula (3n/2-2)', color='#2ca02c', linestyle='--', alpha=0.7)
        ax.plot(sizes, naive_comps_list, marker='^', linewidth=2, markersize=8, 
               label='Naive (2n-2)', color='#ff7f0e')
        
        # Labels and title
        ax.set_xlabel("Array Size (n)", fontsize=10, fontweight='bold')
        ax.set_ylabel("Number of Comparisons", fontsize=10, fontweight='bold')
        ax.set_title("Performance Comparison: D&C vs Naive", fontsize=12, fontweight='bold')
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.perf_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Display analysis text
        analysis = "PERFORMANCE ANALYSIS RESULTS\n"
        analysis += "=" * 50 + "\n\n"
        analysis += f"{'Size':<10} {'D&C':<12} {'Formula':<12} {'Naive':<12}\n"
        analysis += "-" * 50 + "\n"
        
        for i, size in enumerate(sizes):
            analysis += f"{size:<10} {dc_comps_list[i]:<12} {formula_list[i]:<12} {naive_comps_list[i]:<12}\n"
            
        self.comparison_text.config(state="normal")
        self.comparison_text.delete("1.0", "end")
        self.comparison_text.insert("end", analysis)
        self.comparison_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = MinMaxVisualizer(root)
    root.mainloop()