import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math
from dataclasses import dataclass
from typing import List, Tuple, Dict
from itertools import permutations


INF = float('inf')


@dataclass
class TSPSolution:
    """TSP solution container"""
    path: List[int]
    cost: float
    cities: List[str]


class TSPSolver:
    """Traveling Salesman Problem solver"""
    
    @staticmethod
    def reduce_matrix(mat):
        """Reduce matrix and return reduction cost"""
        import copy
        m = [row[:] for row in mat]
        n = len(m)
        cost = 0
        
        # Row reduction
        for i in range(n):
            row_min = min(m[i])
            if row_min and row_min != INF:
                cost += row_min
                m[i] = [x - row_min if x != INF else INF for x in m[i]]
        
        # Column reduction
        for j in range(n):
            col_min = min(m[i][j] for i in range(n))
            if col_min and col_min != INF:
                cost += col_min
                for i in range(n):
                    if m[i][j] != INF:
                        m[i][j] -= col_min
        
        return m, cost
    
    @staticmethod
    def brute_force(cost_matrix: List[List[float]], cities: List[str]) -> TSPSolution:
        """Brute force TSP solver"""
        n = len(cost_matrix)
        city_indices = list(range(1, n))
        
        best_cost = INF
        best_path = None
        
        for perm in permutations(city_indices):
            path = [0] + list(perm) + [0]
            c = sum(cost_matrix[path[i]][path[i+1]] for i in range(n))
            
            if c < best_cost:
                best_cost = c
                best_path = path
        
        return TSPSolution(best_path, best_cost, cities)


class TSPVisualizerGUI:
    """Custom tkinter TSP solver GUI"""
    
    # Design tokens: logistics/network aesthetic
    COLORS = {
        'dark_bg': '#0f1419',        # Deep navy
        'light_bg': '#f8f9fa',       # Clean white
        'primary': '#ff6b6b',         # Vibrant red (route highlight)
        'secondary': '#4ecdc4',       # Teal (nodes)
        'accent': '#ffe66d',          # Golden (best solution)
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'grid_line': '#e0e0e0',
        'edge_default': '#bdc3c7',
        'edge_tour': '#ff6b6b',
    }
    
    FONTS = {
        'title': ('Inter', 20, 'bold'),
        'heading': ('Inter', 12, 'bold'),
        'subhead': ('Inter', 10, 'bold'),
        'body': ('Inter', 10),
        'mono': ('Courier New', 9),
        'matrix_val': ('Courier New', 8),
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title('TSP Solver — Route Optimizer')
        self.root.geometry('1200x750')
        self.root.configure(bg=self.COLORS['light_bg'])
        
        self.solver = TSPSolver()
        self.solution: TSPSolution = None
        self.cost_matrix = None
        self.cities = []
        self.solving = False
        
        self.setup_styles()
        self.build_ui()
        self.load_example()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Primary.TButton',
                       font=self.FONTS['body'],
                       padding=8)
    
    def build_ui(self):
        """Build main layout"""
        # Header
        self.build_header()
        
        # Main content
        main = tk.Frame(self.root, bg=self.COLORS['light_bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Left panel: Cost matrix + controls
        left = tk.Frame(main, bg=self.COLORS['light_bg'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))
        
        self.build_matrix_panel(left)
        self.build_controls(left)
        
        # Right panel: Visualization
        right = tk.Frame(main, bg=self.COLORS['light_bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.build_viz_panel(right)
    
    def build_header(self):
        """Build top header"""
        header = tk.Frame(self.root, bg=self.COLORS['dark_bg'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.COLORS['dark_bg'])
        title_frame.pack(pady=12, padx=12)
        
        tk.Label(
            title_frame,
            text='🛣️  Traveling Salesman Problem',
            font=self.FONTS['title'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['primary']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text='Find the shortest route visiting all cities exactly once',
            font=self.FONTS['body'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(anchor='w')
    
    def build_matrix_panel(self, parent):
        """Build cost matrix display"""
        frame = tk.LabelFrame(
            parent,
            text='Cost Matrix',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=8,
            pady=8
        )
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Canvas for matrix
        self.matrix_canvas = tk.Canvas(
            frame,
            bg='white',
            highlightthickness=1,
            highlightbackground=self.COLORS['grid_line'],
            height=300,
            width=350
        )
        self.matrix_canvas.pack(fill=tk.BOTH, expand=True)
        self.matrix_canvas.bind('<Configure>', lambda e: self.draw_matrix())
    
    def build_controls(self, parent):
        """Build control panel"""
        frame = tk.LabelFrame(
            parent,
            text='Solver',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=8,
            pady=8
        )
        frame.pack(fill=tk.X)
        
        # City count
        count_frame = tk.Frame(frame, bg=self.COLORS['light_bg'])
        count_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            count_frame,
            text='Cities:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        self.city_count_var = tk.IntVar(value=5)
        tk.Spinbox(
            count_frame,
            from_=3,
            to=10,
            textvariable=self.city_count_var,
            font=self.FONTS['body'],
            width=5,
            bg='white',
            relief=tk.FLAT,
            borderwidth=1
        ).pack(side=tk.LEFT, padx=8)
        
        # Buttons
        btn_frame = tk.Frame(frame, bg=self.COLORS['light_bg'])
        btn_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.solve_btn = tk.Button(
            btn_frame,
            text='▶ Solve',
            font=self.FONTS['heading'],
            bg=self.COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor='hand2',
            command=self.on_solve
        )
        self.solve_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            btn_frame,
            text='🔄 Random',
            font=self.FONTS['body'],
            bg=self.COLORS['secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor='hand2',
            command=self.generate_random
        ).pack(side=tk.LEFT)
        
        # Results
        results_frame = tk.LabelFrame(
            frame,
            text='Solution',
            font=self.FONTS['subhead'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=8,
            pady=8
        )
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        
        # Cost display
        self.cost_label = tk.Label(
            results_frame,
            text='Total Cost: —',
            font=('Courier New', 12, 'bold'),
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['primary']
        )
        self.cost_label.pack(pady=8)
        
        # Path display
        path_frame = tk.Frame(results_frame, bg=self.COLORS['light_bg'])
        path_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        tk.Label(
            path_frame,
            text='Route:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(anchor='w')
        
        self.path_text = tk.Text(
            path_frame,
            font=self.FONTS['mono'],
            height=5,
            bg='white',
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            state=tk.DISABLED
        )
        self.path_text.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
    
    def build_viz_panel(self, parent):
        """Build visualization panel"""
        frame = tk.LabelFrame(
            parent,
            text='Route Visualization',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=8,
            pady=8
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        self.viz_canvas = tk.Canvas(
            frame,
            bg='white',
            highlightthickness=1,
            highlightbackground=self.COLORS['grid_line']
        )
        self.viz_canvas.pack(fill=tk.BOTH, expand=True)
        self.viz_canvas.bind('<Configure>', lambda e: self.draw_graph())
    
    def draw_matrix(self):
        """Render cost matrix as heatmap"""
        if not self.cost_matrix:
            return
        
        canvas = self.matrix_canvas
        canvas.delete('all')
        
        n = len(self.cost_matrix)
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w <= 1:
            return
        
        cell_w = (w - 60) / n
        cell_h = (h - 60) / n
        
        padding = 40
        
        # Draw row/column labels
        for i, city in enumerate(self.cities):
            # Column header
            x = padding + i * cell_w + cell_w / 2
            canvas.create_text(
                x, 15,
                text=city,
                font=self.FONTS['matrix_val'],
                fill=self.COLORS['text_primary']
            )
            
            # Row header
            y = padding + i * cell_h + cell_h / 2
            canvas.create_text(
                15, y,
                text=city,
                font=self.FONTS['matrix_val'],
                fill=self.COLORS['text_primary']
            )
        
        # Draw cells
        for i in range(n):
            for j in range(n):
                x0 = padding + j * cell_w
                y0 = padding + i * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h
                
                val = self.cost_matrix[i][j]
                
                # Color: diagonal (diagonal) and high costs get warm colors
                if i == j:
                    color = '#f0f0f0'
                elif val == INF:
                    color = '#333333'
                else:
                    # Heat gradient: cool (blue) for low, warm (red) for high
                    max_cost = max(v for row in self.cost_matrix for v in row if v != INF)
                    ratio = val / max_cost
                    # Interpolate from teal to red
                    r = int(78 + (255 - 78) * ratio)
                    g = int(205 - 205 * ratio)
                    b = int(196 - 196 * ratio)
                    color = f'#{r:02x}{g:02x}{b:02x}'
                
                canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=color,
                    outline=self.COLORS['grid_line'],
                    width=1
                )
                
                # Value text
                if val != INF:
                    text_color = 'white' if i == j else self.COLORS['text_primary']
                    canvas.create_text(
                        (x0 + x1) / 2, (y0 + y1) / 2,
                        text=str(int(val)),
                        font=self.FONTS['matrix_val'],
                        fill=text_color
                    )
    
    def draw_graph(self):
        """Render network graph visualization"""
        if not self.cities:
            return
        
        canvas = self.viz_canvas
        canvas.delete('all')
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if w <= 1:
            return
        
        n = len(self.cities)
        center_x = w / 2
        center_y = h / 2
        radius = min(w, h) / 3
        
        # Position cities on circle
        positions = {}
        for i, city in enumerate(self.cities):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[i] = (x, y)
        
        # Draw edges (non-solution)
        for i in range(n):
            for j in range(i + 1, n):
                x0, y0 = positions[i]
                x1, y1 = positions[j]
                
                canvas.create_line(
                    x0, y0, x1, y1,
                    fill=self.COLORS['edge_default'],
                    width=1,
                    dash=(2, 4)
                )
        
        # Draw tour edges (if solution exists)
        if self.solution:
            path = self.solution.path
            for k in range(len(path) - 1):
                i, j = path[k], path[k + 1]
                x0, y0 = positions[i]
                x1, y1 = positions[j]
                
                canvas.create_line(
                    x0, y0, x1, y1,
                    fill=self.COLORS['edge_tour'],
                    width=3
                )
        
        # Draw nodes
        node_radius = 20
        for i, city in enumerate(self.cities):
            x, y = positions[i]
            
            canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=self.COLORS['secondary'],
                outline=self.COLORS['text_primary'],
                width=2
            )
            
            canvas.create_text(
                x, y,
                text=city,
                font=self.FONTS['heading'],
                fill='white',
                anchor='center'
            )
    
    def load_example(self):
        """Load example 5-city problem"""
        self.cost_matrix = [
            [INF,  10,   8,   9,   7],
            [ 10, INF,  10,   5,   6],
            [  8,  10, INF,   8,   9],
            [  9,   5,   8, INF,   6],
            [  7,   6,   9,   6, INF]
        ]
        self.cities = ['A', 'B', 'C', 'D', 'E']
        self.city_count_var.set(5)
        self.draw_matrix()
        self.draw_graph()
    
    def generate_random(self):
        """Generate random TSP instance"""
        import random
        
        n = self.city_count_var.get()
        self.cities = [chr(65 + i) for i in range(n)]
        
        # Random symmetric cost matrix
        self.cost_matrix = [[INF if i == j else random.randint(5, 20) for j in range(n)] for i in range(n)]
        
        # Make symmetric
        for i in range(n):
            for j in range(i + 1, n):
                val = self.cost_matrix[i][j]
                self.cost_matrix[j][i] = val
        
        self.solution = None
        self.cost_label.config(text='Total Cost: —')
        self.path_text.config(state=tk.NORMAL)
        self.path_text.delete('1.0', tk.END)
        self.path_text.config(state=tk.DISABLED)
        
        self.draw_matrix()
        self.draw_graph()
    
    def on_solve(self):
        """Solve TSP"""
        if not self.cost_matrix:
            messagebox.showwarning('No data', 'Load or generate a TSP instance first')
            return
        
        self.solve_btn.config(state=tk.DISABLED)
        self.solving = True
        
        thread = threading.Thread(target=self._solve_worker, daemon=True)
        thread.start()
    
    def _solve_worker(self):
        """Background solver"""
        try:
            self.solution = self.solver.brute_force(self.cost_matrix, self.cities)
            self.root.after(0, self._update_solution)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror('Error', str(e)))
        finally:
            self.solving = False
            self.root.after(0, lambda: self.solve_btn.config(state=tk.NORMAL))
    
    def _update_solution(self):
        """Update UI with solution"""
        if not self.solution:
            return
        
        # Update cost
        self.cost_label.config(
            text=f'Total Cost: {self.solution.cost:.0f}',
            fg=self.COLORS['accent']
        )
        
        # Update path
        path_str = ' → '.join(self.solution.cities[i] for i in self.solution.path)
        
        self.path_text.config(state=tk.NORMAL)
        self.path_text.delete('1.0', tk.END)
        self.path_text.insert('1.0', path_str)
        self.path_text.config(state=tk.DISABLED)
        
        # Redraw graph
        self.draw_graph()


if __name__ == '__main__':
    root = tk.Tk()
    app = TSPVisualizerGUI(root)
    root.mainloop()