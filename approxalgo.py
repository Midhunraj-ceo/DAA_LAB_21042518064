import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PackingResult:
    """Result container for packing algorithm"""
    bins: List[List[float]]
    num_bins: int
    efficiency: float


class BinPackingSolver:
    """Bin packing algorithms"""
    
    @staticmethod
    def first_fit(items: List[float], capacity: float = 1.0) -> PackingResult:
        """First Fit algorithm"""
        bins = []
        bin_contents = []
        
        for item in items:
            placed = False
            for i, space in enumerate(bins):
                if space >= item:
                    bins[i] -= item
                    bin_contents[i].append(item)
                    placed = True
                    break
            
            if not placed:
                bins.append(capacity - item)
                bin_contents.append([item])
        
        total_used = sum(items)
        efficiency = (total_used / (len(bin_contents) * capacity)) * 100 if bin_contents else 0
        
        return PackingResult(bin_contents, len(bin_contents), efficiency)
    
    @staticmethod
    def first_fit_decreasing(items: List[float], capacity: float = 1.0) -> PackingResult:
        """First Fit Decreasing algorithm"""
        sorted_items = sorted(items, reverse=True)
        bins = []
        bin_contents = []
        
        for item in sorted_items:
            placed = False
            for i, space in enumerate(bins):
                if space >= item:
                    bins[i] -= item
                    bin_contents[i].append(item)
                    placed = True
                    break
            
            if not placed:
                bins.append(capacity - item)
                bin_contents.append([item])
        
        total_used = sum(items)
        efficiency = (total_used / (len(bin_contents) * capacity)) * 100 if bin_contents else 0
        
        return PackingResult(bin_contents, len(bin_contents), efficiency)
    
    @staticmethod
    def best_fit_decreasing(items: List[float], capacity: float = 1.0) -> PackingResult:
        """Best Fit Decreasing algorithm"""
        sorted_items = sorted(items, reverse=True)
        bins = []
        bin_contents = []
        
        for item in sorted_items:
            best_idx = -1
            best_space = float('inf')
            
            for i, space in enumerate(bins):
                if space >= item and space - item < best_space:
                    best_space = space - item
                    best_idx = i
            
            if best_idx >= 0:
                bins[best_idx] -= item
                bin_contents[best_idx].append(item)
            else:
                bins.append(capacity - item)
                bin_contents.append([item])
        
        total_used = sum(items)
        efficiency = (total_used / (len(bin_contents) * capacity)) * 100 if bin_contents else 0
        
        return PackingResult(bin_contents, len(bin_contents), efficiency)


class BinPackingGUI:
    """Custom tkinter bin packing visualizer"""
    
    # Design tokens: warehouse/logistics aesthetic
    COLORS = {
        'dark_bg': '#1a1a2e',        # Deep navy
        'light_bg': '#f0f2f5',       # Clean light
        'primary': '#0f3460',        # Dark blue (bins)
        'secondary': '#16213e',      # Darker blue
        'accent': '#e94560',         # Vibrant red (highlight)
        'accent_green': '#00d4aa',   # Teal (efficiency)
        'text_primary': '#1a1a2e',
        'text_secondary': '#5a6c7d',
        'item_colors': [
            '#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3',
            '#f38181', '#aa96da', '#fcbad3', '#a8d8ea'
        ],
    }
    
    FONTS = {
        'title': ('Segoe UI', 22, 'bold'),
        'heading': ('Segoe UI', 13, 'bold'),
        'subhead': ('Segoe UI', 11, 'bold'),
        'body': ('Segoe UI', 10),
        'mono': ('Courier New', 9),
        'stats': ('Courier New', 11, 'bold'),
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title('Bin Packing Optimizer')
        self.root.geometry('1250x800')
        self.root.configure(bg=self.COLORS['light_bg'])
        
        self.solver = BinPackingSolver()
        self.items = [0.5, 0.7, 0.3, 0.9, 0.2, 0.6, 0.8, 0.4, 0.1, 0.5]
        self.capacity = 1.0
        self.results = {}
        self.selected_algo = tk.StringVar(value='FFD')
        self.solving = False
        
        self.setup_styles()
        self.build_ui()
        self.load_example()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Primary.TButton', font=self.FONTS['body'], padding=8)
    
    def build_ui(self):
        """Build main interface"""
        self.build_header()
        
        main = tk.Frame(self.root, bg=self.COLORS['light_bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Left: Controls & Stats (fixed width sidebar)
        left = tk.Frame(main, bg=self.COLORS['light_bg'], width=280)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left.pack_propagate(False)
        
        self.build_controls(left)
        self.build_stats(left)
        
        # Right: Visualization
        right = tk.Frame(main, bg=self.COLORS['light_bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.build_viz(right)
    
    def build_header(self):
        """Build top header"""
        header = tk.Frame(self.root, bg=self.COLORS['dark_bg'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        hframe = tk.Frame(header, bg=self.COLORS['dark_bg'])
        hframe.pack(pady=12, padx=12)
        
        tk.Label(
            hframe,
            text='📦 Bin Packing Optimizer',
            font=self.FONTS['title'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['accent_green']
        ).pack(anchor='w')
        
        tk.Label(
            hframe,
            text='Compare FF, FFD, and BFD algorithms to minimize bins used',
            font=self.FONTS['body'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(anchor='w')
    
    def build_controls(self, parent):
        """Build control panel"""
        frame = tk.LabelFrame(
            parent,
            text='Configuration',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.X, pady=(0, 12))
        
        # Item count
        tk.Label(
            frame,
            text='Items:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 4))
        
        count_frame = tk.Frame(frame, bg=self.COLORS['light_bg'])
        count_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.item_count_var = tk.IntVar(value=len(self.items))
        tk.Spinbox(
            count_frame,
            from_=5,
            to=50,
            textvariable=self.item_count_var,
            font=self.FONTS['body'],
            width=6,
            bg='white',
            relief=tk.FLAT,
            borderwidth=1
        ).pack(side=tk.LEFT)
        
        # Capacity
        tk.Label(
            frame,
            text='Capacity:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 4))
        
        self.capacity_var = tk.DoubleVar(value=1.0)
        tk.Scale(
            frame,
            from_=0.5,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.capacity_var,
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=self.COLORS['accent_green']
        ).pack(fill=tk.X, pady=(0, 12))
        
        # Algorithm selector
        tk.Label(
            frame,
            text='Algorithm:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 8))
        
        for algo, label in [('FF', 'First Fit'), ('FFD', 'FF Decreasing'), ('BFD', 'Best Fit Decreasing')]:
            tk.Radiobutton(
                frame,
                text=label,
                variable=self.selected_algo,
                value=algo,
                font=self.FONTS['body'],
                bg=self.COLORS['light_bg'],
                fg=self.COLORS['text_primary'],
                selectcolor=self.COLORS['accent_green'],
                activebackground=self.COLORS['light_bg'],
                command=self.update_viz
            ).pack(anchor='w', pady=2)
        
        # Buttons
        btn_frame = tk.Frame(frame, bg=self.COLORS['light_bg'])
        btn_frame.pack(fill=tk.X, pady=(12, 0))
        
        tk.Button(
            btn_frame,
            text='▶ Solve All',
            font=self.FONTS['heading'],
            bg=self.COLORS['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor='hand2',
            command=self.solve_all
        ).pack(side=tk.LEFT, padx=(0, 6))
        
        tk.Button(
            btn_frame,
            text='🔄 Random',
            font=self.FONTS['body'],
            bg=self.COLORS['accent_green'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor='hand2',
            command=self.generate_random
        ).pack(side=tk.LEFT)
    
    def build_stats(self, parent):
        """Build statistics display"""
        frame = tk.LabelFrame(
            parent,
            text='Results',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Lower bound
        tk.Label(
            frame,
            text='Lower Bound:',
            font=self.FONTS['subhead'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(anchor='w', pady=(0, 4))
        
        self.lower_bound_label = tk.Label(
            frame,
            text='—',
            font=self.FONTS['stats'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['accent']
        )
        self.lower_bound_label.pack(anchor='w', pady=(0, 12))
        
        # Algorithm stats
        for algo, label in [('FF', 'First Fit'), ('FFD', 'FF Decreasing'), ('BFD', 'Best Fit Decreasing')]:
            algo_frame = tk.Frame(frame, bg=self.COLORS['light_bg'])
            algo_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                algo_frame,
                text=label,
                font=self.FONTS['subhead'],
                bg=self.COLORS['light_bg'],
                fg=self.COLORS['text_primary']
            ).pack(anchor='w')
            
            stat_frame = tk.Frame(algo_frame, bg=self.COLORS['light_bg'])
            stat_frame.pack(fill=tk.X, pady=(4, 0))
            
            bins_label = tk.Label(
                stat_frame,
                text='Bins: —',
                font=self.FONTS['mono'],
                bg=self.COLORS['light_bg'],
                fg=self.COLORS['primary']
            )
            bins_label.pack(anchor='w', side=tk.LEFT, padx=(8, 0))
            
            eff_label = tk.Label(
                stat_frame,
                text='Eff: —%',
                font=self.FONTS['mono'],
                bg=self.COLORS['light_bg'],
                fg=self.COLORS['accent_green']
            )
            eff_label.pack(anchor='w', side=tk.LEFT, padx=12)
            
            setattr(self, f'{algo}_bins_label', bins_label)
            setattr(self, f'{algo}_eff_label', eff_label)
    
    def build_viz(self, parent):
        """Build visualization area"""
        frame = tk.LabelFrame(
            parent,
            text='Bin Packing Visualization',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(
            frame,
            bg='white',
            highlightthickness=1,
            highlightbackground=self.COLORS['text_secondary']
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda e: self.draw_bins())
    
    def load_example(self):
        """Load example items"""
        self.draw_bins()
        self.update_stats()
    
    def generate_random(self):
        """Generate random items"""
        n = self.item_count_var.get()
        self.items = [round(random.uniform(0.1, 0.9), 1) for _ in range(n)]
        self.results = {}
        self.draw_bins()
        self.update_stats()
    
    def solve_all(self):
        """Solve with all three algorithms"""
        capacity = self.capacity_var.get()
        
        def worker():
            self.results = {
                'FF': self.solver.first_fit(self.items, capacity),
                'FFD': self.solver.first_fit_decreasing(self.items, capacity),
                'BFD': self.solver.best_fit_decreasing(self.items, capacity),
            }
            self.root.after(0, self.update_stats)
            self.root.after(0, self.draw_bins)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def update_stats(self):
        """Update statistics display"""
        total = sum(self.items)
        lower_bound = -(-total // self.capacity_var.get())
        self.lower_bound_label.config(text=f'{int(lower_bound)}')
        
        for algo in ['FF', 'FFD', 'BFD']:
            if algo in self.results:
                result = self.results[algo]
                getattr(self, f'{algo}_bins_label').config(
                    text=f'Bins: {result.num_bins}'
                )
                getattr(self, f'{algo}_eff_label').config(
                    text=f'Eff: {result.efficiency:.1f}%'
                )
            else:
                getattr(self, f'{algo}_bins_label').config(text='Bins: —')
                getattr(self, f'{algo}_eff_label').config(text='Eff: —%')
    
    def draw_bins(self):
        """Draw bin visualization"""
        self.canvas.delete('all')
        
        algo = self.selected_algo.get()
        if algo not in self.results:
            return
        
        result = self.results[algo]
        bins_data = result.bins
        
        if not bins_data:
            return
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1:
            return
        
        # Layout: grid of bins
        max_cols = 4
        num_bins = len(bins_data)
        num_cols = min(max_cols, max(1, num_bins))
        num_rows = (num_bins + num_cols - 1) // num_cols
        
        bin_w = (w - 40) / num_cols
        bin_h = (h - 40) / num_rows
        
        padding = 20
        bin_spacing = 10
        
        for bin_idx, items_in_bin in enumerate(bins_data):
            row = bin_idx // num_cols
            col = bin_idx % num_cols
            
            bin_x = padding + col * (bin_w + bin_spacing)
            bin_y = padding + row * (bin_h + bin_spacing)
            
            # Bin container
            bin_height = bin_h - 20
            self.canvas.create_rectangle(
                bin_x, bin_y,
                bin_x + bin_w - bin_spacing, bin_y + bin_height,
                fill=self.COLORS['secondary'],
                outline=self.COLORS['primary'],
                width=2
            )
            
            # Bin label
            self.canvas.create_text(
                bin_x + 5, bin_y + 5,
                text=f'Bin {bin_idx + 1}',
                font=self.FONTS['subhead'],
                fill='white',
                anchor='nw'
            )
            
            # Items in bin (stacked from bottom)
            y_offset = bin_y + bin_height - 10
            used_space = 0
            
            for item_idx, item in enumerate(items_in_bin):
                item_height = item * (bin_height - 30)
                item_color = self.COLORS['item_colors'][item_idx % len(self.COLORS['item_colors'])]
                
                self.canvas.create_rectangle(
                    bin_x + 5, y_offset - item_height,
                    bin_x + bin_w - bin_spacing - 5, y_offset,
                    fill=item_color,
                    outline=self.COLORS['text_primary'],
                    width=1
                )
                
                # Item label
                if item_height > 15:
                    self.canvas.create_text(
                        bin_x + bin_w / 2 - bin_spacing / 2, y_offset - item_height / 2,
                        text=f'{item:.1f}',
                        font=self.FONTS['mono'],
                        fill=self.COLORS['text_primary'],
                        anchor='center'
                    )
                
                y_offset -= item_height
                used_space += item
            
            # Utilization bar at bottom
            util_pct = (used_space / self.capacity_var.get()) * 100
            util_text = f'{util_pct:.0f}%'
            
            self.canvas.create_text(
                bin_x + bin_w / 2 - bin_spacing / 2, bin_y + bin_height + 8,
                text=util_text,
                font=self.FONTS['body'],
                fill=self.COLORS['text_primary'],
                anchor='n'
            )
    
    def update_viz(self):
        """Update visualization when algorithm changes"""
        self.draw_bins()


if __name__ == '__main__':
    root = tk.Tk()
    app = BinPackingGUI(root)
    root.mainloop()