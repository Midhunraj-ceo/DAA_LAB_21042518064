import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches

def matrix_chain_order(dims):
    """
    Matrix Chain Multiplication using DP
    dims: list of dimensions, matrix i has dims[i-1] x dims[i]
    Time: O(n^3), Space: O(n^2)
    """
    n = len(dims) - 1
    # m[i][j] = minimum multiplications for matrices i..j
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]

    # l is the chain length
    for l in range(2, n + 1):
        for i in range(1, n - l + 2):
            j = i + l - 1
            m[i][j] = float('inf')
            for k in range(i, j):
                cost = m[i][k] + m[k+1][j] + dims[i-1] * dims[k] * dims[j]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
    return m, s

def print_optimal_parens(s, i, j):
    """Recursively construct optimal parenthesization"""
    if i == j:
        return f'A{i}'
    k = s[i][j]
    left = print_optimal_parens(s, i, k)
    right = print_optimal_parens(s, k + 1, j)
    return f'({left} × {right})'

def calculate_multiplications(dims, parens_str):
    """Calculate total scalar multiplications from parenthesization"""
    # Simple recursive calculation
    n = len(dims) - 1
    m, _ = matrix_chain_order(dims)
    return m[1][n]


class MatrixChainVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Matrix Chain Multiplication - DP Optimizer")
        self.root.geometry("1600x1000")
        self.root.configure(bg="#f0f0f0")
        
        # Data
        self.dims = []
        self.m = []
        self.s = []
        self.optimal_parens = ""
        self.min_cost = 0
        
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
        
        ttk.Label(input_frame, text="Matrix Dimensions (comma-separated):", 
                 font=('Helvetica', 10, 'bold')).pack(side="left", padx=5)
        self.dims_input = ttk.Entry(input_frame, width=80)
        self.dims_input.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(input_frame, text="Set Dimensions", 
                  command=self.set_dimensions).pack(side="left", padx=5)
        
        # Algorithm buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Run Algorithm", 
                  command=self.run_algorithm).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", 
                  command=self.reset_view).pack(side="left", padx=5)
        
        # Example buttons
        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=10)
        
        example_frame = ttk.Frame(control_frame)
        example_frame.pack(fill="x", pady=5)
        
        ttk.Label(example_frame, text="Load Example:", 
                 font=('Helvetica', 10, 'bold')).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 1 (4 matrices)", 
                  command=self.load_example_1).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 2 (5 matrices)", 
                  command=self.load_example_2).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 3 (6 matrices)", 
                  command=self.load_example_3).pack(side="left", padx=5)
        
        # Main content
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - DP Table
        left_frame = ttk.LabelFrame(content_frame, text="DP Cost Table m[i][j]", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.table_canvas_frame = ttk.Frame(left_frame)
        self.table_canvas_frame.pack(fill="both", expand=True)
        
        # Right side - Tabs
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", padx=(5, 0), expand=True)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Results tab
        results_tab = ttk.Frame(self.notebook)
        self.notebook.add(results_tab, text="Results")
        self.create_results_tab(results_tab)
        
        # Matrices tab
        matrices_tab = ttk.Frame(self.notebook)
        self.notebook.add(matrices_tab, text="Matrices")
        self.create_matrices_tab(matrices_tab)
        
        # Split table tab
        split_tab = ttk.Frame(self.notebook)
        self.notebook.add(split_tab, text="Split Points")
        self.create_split_tab(split_tab)
        
        # Algorithm info tab
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="Algorithm Info")
        self.create_info_tab(info_tab)
        
    def create_results_tab(self, parent):
        """Create results tab"""
        self.results_text = scrolledtext.ScrolledText(parent, font=('Courier', 10), 
                                                      height=30, width=50)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_text.tag_config("header", foreground="#1f77b4", font=('Courier', 11, 'bold'))
        self.results_text.tag_config("matrices", foreground="#2ca02c")
        self.results_text.tag_config("cost", foreground="#d62728", font=('Courier', 11, 'bold'))
        self.results_text.tag_config("parens", foreground="#ff7f0e", font=('Courier', 10, 'bold'))
        
    def create_matrices_tab(self, parent):
        """Create matrices tab"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="both", expand=True)
        
        self.matrices_canvas_frame = ttk.Frame(frame)
        self.matrices_canvas_frame.pack(fill="both", expand=True)
        
    def create_split_tab(self, parent):
        """Create split points tab"""
        self.split_text = scrolledtext.ScrolledText(parent, font=('Courier', 9), 
                                                    height=30, width=50)
        self.split_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.split_text.tag_config("header", foreground="#1f77b4", font=('Courier', 11, 'bold'))
        self.split_text.tag_config("split", foreground="#2ca02c", font=('Courier', 10, 'bold'))
        self.split_text.tag_config("range", foreground="#ff7f0e")
        
    def create_info_tab(self, parent):
        """Create algorithm info tab"""
        info_text = scrolledtext.ScrolledText(parent, font=('Courier', 9), height=30)
        info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_text.insert("end", "MATRIX CHAIN MULTIPLICATION\n", "header")
        info_text.insert("end", "=" * 55 + "\n\n")
        
        info_text.insert("end", "Problem Statement:\n", "header")
        info_text.insert("end", "Given a sequence of matrices to be multiplied,\n")
        info_text.insert("end", "find the optimal parenthesization that minimizes\n")
        info_text.insert("end", "the number of scalar multiplications.\n\n")
        
        info_text.insert("end", "Key Insight:\n", "header")
        info_text.insert("end", "Matrix multiplication is associative: (A×B)×C = A×(B×C)\n")
        info_text.insert("end", "but different parenthesizations have different costs!\n\n")
        
        info_text.insert("end", "Example:\n", "header")
        info_text.insert("end", "A (10×30) × B (30×5) × C (5×60)\n\n")
        info_text.insert("end", "(A×B)×C = 10×30×5 + 10×5×60 = 1500 + 3000 = 4500\n")
        info_text.insert("end", "A×(B×C) = 30×5×60 + 10×30×60 = 9000 + 18000 = 27000\n\n")
        
        info_text.insert("end", "Time Complexity: O(n³)\n")
        info_text.insert("end", "Space Complexity: O(n²)\n\n")
        
        info_text.insert("end", "DP Formula:\n", "header")
        info_text.insert("end", "m[i][j] = min cost to multiply matrices i through j\n\n")
        info_text.insert("end", "m[i][j] = 0, if i = j\n")
        info_text.insert("end", "m[i][j] = min(m[i][k] + m[k+1][j] +\n")
        info_text.insert("end", "              dims[i-1]×dims[k]×dims[j])\n")
        info_text.insert("end", "           for all i ≤ k < j\n\n")
        
        info_text.insert("end", "Table Interpretation:\n", "header")
        info_text.insert("end", "• m[i][j] stores minimum multiplications\n")
        info_text.insert("end", "• s[i][j] stores optimal split point k\n")
        info_text.insert("end", "• Diagonal contains 0 (single matrices)\n")
        info_text.insert("end", "• Lower triangle is unused\n")
        
        info_text.config(state="disabled")
        
    def set_dimensions(self):
        """Parse dimensions from input field"""
        try:
            dims_str = self.dims_input.get().strip()
            if dims_str.startswith('[') and dims_str.endswith(']'):
                dims_str = dims_str[1:-1]
            self.dims = [int(x.strip()) for x in dims_str.split(',')]
            if len(self.dims) < 2:
                messagebox.showerror("Error", "Need at least 2 dimensions!")
                return
            self.reset_view()
            messagebox.showinfo("Success", f"Loaded {len(self.dims)-1} matrices")
        except ValueError:
            messagebox.showerror("Error", "Invalid format! Use: 10,30,5,60,10")
            
    def load_example_1(self):
        """Load example 1 (4 matrices)"""
        self.dims = [10, 30, 5, 60, 10]
        self.dims_input.delete(0, "end")
        self.dims_input.insert(0, str(self.dims)[1:-1])
        self.reset_view()
        
    def load_example_2(self):
        """Load example 2 (5 matrices)"""
        self.dims = [5, 10, 3, 12, 5, 50, 6]
        self.dims_input.delete(0, "end")
        self.dims_input.insert(0, str(self.dims)[1:-1])
        self.reset_view()
        
    def load_example_3(self):
        """Load example 3 (6 matrices)"""
        self.dims = [30, 35, 15, 5, 10, 20, 25]
        self.dims_input.delete(0, "end")
        self.dims_input.insert(0, str(self.dims)[1:-1])
        self.reset_view()
        
    def reset_view(self):
        """Reset all displays"""
        self.m = []
        self.s = []
        self.optimal_parens = ""
        self.min_cost = 0
        self.clear_results()
        self.visualize_matrices()
        
    def clear_results(self):
        """Clear result displays"""
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.config(state="disabled")
        
        self.split_text.config(state="normal")
        self.split_text.delete("1.0", "end")
        self.split_text.config(state="disabled")
        
    def run_algorithm(self):
        """Run matrix chain multiplication algorithm"""
        if not self.dims:
            messagebox.showwarning("Warning", "Please load dimensions first!")
            return
            
        self.m, self.s = matrix_chain_order(self.dims)
        n = len(self.dims) - 1
        self.min_cost = self.m[1][n]
        self.optimal_parens = print_optimal_parens(self.s, 1, n)
        
        self.display_results()
        self.display_split_points()
        self.visualize_dp_table()
        self.visualize_matrices()
        
    def display_results(self):
        """Display algorithm results"""
        text = self.results_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "MATRIX CHAIN MULTIPLICATION RESULTS\n", "header")
        text.insert("end", "=" * 50 + "\n\n")
        
        text.insert("end", "Matrices:\n", "header")
        for i in range(len(self.dims) - 1):
            text.insert("end", f"  A{i+1}: {self.dims[i]} × {self.dims[i+1]}\n", "matrices")
        
        text.insert("end", f"\nMinimum Scalar Multiplications:\n", "header")
        text.insert("end", f"  {self.min_cost}\n", "cost")
        
        text.insert("end", f"\nOptimal Parenthesization:\n", "header")
        text.insert("end", f"  {self.optimal_parens}\n", "parens")
        
        # Calculate actual multiplications
        text.insert("end", f"\nBreakdown:\n", "header")
        text.insert("end", self.breakdown_multiplications())
        
        text.config(state="disabled")
        
    def breakdown_multiplications(self):
        """Breakdown the multiplication steps"""
        n = len(self.dims) - 1
        breakdown = ""
        
        def trace_multiplications(i, j, indent="  "):
            nonlocal breakdown
            if i == j:
                breakdown += f"{indent}Matrix A{i} (no multiplication needed)\n"
            else:
                k = self.s[i][j]
                left_cost = self.m[i][k]
                right_cost = self.m[k+1][j]
                result_cost = self.dims[i-1] * self.dims[k] * self.dims[j]
                
                breakdown += f"{indent}Multiply A{i}..{k} with A{k+1}..{j}\n"
                breakdown += f"{indent}  Left cost: {left_cost}\n"
                breakdown += f"{indent}  Right cost: {right_cost}\n"
                breakdown += f"{indent}  Merge cost: {self.dims[i-1]}×{self.dims[k]}×{self.dims[j]} = {result_cost}\n"
                
                if left_cost > 0:
                    trace_multiplications(i, k, indent + "    ")
                if right_cost > 0:
                    trace_multiplications(k+1, j, indent + "    ")
        
        trace_multiplications(1, n)
        return breakdown
        
    def display_split_points(self):
        """Display optimal split points"""
        text = self.split_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "OPTIMAL SPLIT POINTS (s[i][j])\n", "header")
        text.insert("end", "=" * 50 + "\n\n")
        
        n = len(self.dims) - 1
        
        text.insert("end", "Split Point Matrix:\n", "header")
        text.insert("end", f"{'':>5}", "")
        for j in range(1, n + 1):
            text.insert("end", f"A{j:>5}", "")
        text.insert("end", "\n")
        text.insert("end", "-" * (6 + 6 * n) + "\n")
        
        for i in range(1, n + 1):
            text.insert("end", f"A{i:<4}", "")
            for j in range(1, n + 1):
                if j < i:
                    text.insert("end", f"{'---':>5}", "")
                elif i == j:
                    text.insert("end", f"{'---':>5}", "")
                else:
                    text.insert("end", f"{self.s[i][j]:>5}", "split")
            text.insert("end", "\n")
        
        text.insert("end", "\nInterpretation:\n", "header")
        
        def interpret_splits(i, j, indent=""):
            nonlocal text
            if i == j:
                text.insert("end", f"{indent}A{i}\n", "range")
            else:
                k = self.s[i][j]
                text.insert("end", f"{indent}A{i}..{j}: split at k={k}\n", "split")
                text.insert("end", f"{indent}  Left:  ", "")
                if k == i:
                    text.insert("end", f"A{i}\n", "range")
                else:
                    text.insert("end", f"A{i}..{k} (cost: {self.m[i][k]})\n", "range")
                text.insert("end", f"{indent}  Right: ", "")
                if k + 1 == j:
                    text.insert("end", f"A{j}\n", "range")
                else:
                    text.insert("end", f"A{k+1}..{j} (cost: {self.m[k+1][j]})\n", "range")
                text.insert("end", f"{indent}  Merge cost: {self.dims[i-1]}×{self.dims[k]}×{self.dims[j]} = {self.dims[i-1]*self.dims[k]*self.dims[j]}\n\n")
        
        interpret_splits(1, len(self.dims) - 1)
        
        text.config(state="disabled")
        
    def visualize_dp_table(self):
        """Visualize DP table as heatmap"""
        # Clear previous canvas
        for widget in self.table_canvas_frame.winfo_children():
            widget.destroy()
            
        if not self.m:
            return
            
        n = len(self.dims) - 1
        
        # Create figure
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data for heatmap (only upper triangle)
        heatmap_data = []
        for i in range(1, n + 1):
            row = []
            for j in range(1, n + 1):
                if j < i:
                    row.append(0)
                else:
                    row.append(self.m[i][j])
            heatmap_data.append(row)
        
        # Create heatmap
        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Cost (scalar multiplications)', rotation=270, labelpad=20)
        
        # Set ticks and labels
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels([f'A{j}' for j in range(1, n + 1)])
        ax.set_yticklabels([f'A{i}' for i in range(1, n + 1)])
        
        # Add text annotations
        for i in range(n):
            for j in range(n):
                if j >= i:
                    text = ax.text(j, i, f'{int(heatmap_data[i][j])}',
                                 ha="center", va="center", color="black", fontsize=10, fontweight='bold')
        
        ax.set_title("DP Cost Table (m[i][j])", fontsize=12, fontweight='bold')
        ax.set_xlabel("Matrix j", fontsize=10, fontweight='bold')
        ax.set_ylabel("Matrix i", fontsize=10, fontweight='bold')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.table_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def visualize_matrices(self):
        """Visualize matrices and their dimensions"""
        # Clear previous canvas
        for widget in self.matrices_canvas_frame.winfo_children():
            widget.destroy()
            
        if not self.dims:
            return
            
        n = len(self.dims) - 1
        
        # Create figure
        fig = Figure(figsize=(12, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Draw matrices as rectangles with dimensions
        for i in range(n):
            x = i * 2.5
            rows, cols = self.dims[i], self.dims[i+1]
            
            # Normalize for visualization
            height = min(rows / 100, 1.5)
            width = min(cols / 100, 1.5)
            
            # Draw rectangle
            rect = patches.Rectangle((x, 0), width, height, 
                                     linewidth=2, edgecolor='#1f77b4', 
                                     facecolor='#1f77b4', alpha=0.6)
            ax.add_patch(rect)
            
            # Add label
            ax.text(x + width/2, height/2, f'A{i+1}',
                   ha='center', va='center', fontsize=12, fontweight='bold', color='white')
            
            # Add dimension text
            ax.text(x + width/2, -0.3, f'{rows}×{cols}',
                   ha='center', va='top', fontsize=10)
        
        ax.set_xlim(-0.5, n * 2.5)
        ax.set_ylim(-0.8, 2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("Matrix Dimensions Visualization", fontsize=12, fontweight='bold')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.matrices_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixChainVisualizer(root)
    root.mainloop()