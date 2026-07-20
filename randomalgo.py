import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Callable


@dataclass
class SortStats:
    """Sort statistics container"""
    comparisons: int
    time_ms: float
    swaps: int = 0


class QuickSortAnimator:
    """Quicksort implementation with instrumentation for animation"""
    
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.steps = []  # For animation
        self.paused = False
    
    def reset(self):
        self.comparisons = 0
        self.swaps = 0
        self.steps = []
    
    def partition(self, arr: List[int], low: int, high: int, use_random: bool = False) -> int:
        """Partition with optional randomization"""
        if use_random and low < high:
            rand_idx = random.randint(low, high)
            arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
            self.swaps += 1
            self.steps.append(('swap', rand_idx, high))
        
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            self.comparisons += 1
            self.steps.append(('compare', j, high))
            
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                self.swaps += 1
                self.steps.append(('swap', i, j))
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.swaps += 1
        self.steps.append(('swap', i + 1, high))
        
        return i + 1
    
    def sort_deterministic(self, arr: List[int], low: int = 0, high: int = None):
        """Deterministic quicksort"""
        if high is None:
            high = len(arr) - 1
        
        if low < high:
            pi = self.partition(arr, low, high, use_random=False)
            self.sort_deterministic(arr, low, pi - 1)
            self.sort_deterministic(arr, pi + 1, high)
    
    def sort_randomized(self, arr: List[int], low: int = 0, high: int = None):
        """Randomized quicksort"""
        if high is None:
            high = len(arr) - 1
        
        if low < high:
            pi = self.partition(arr, low, high, use_random=True)
            self.sort_randomized(arr, low, pi - 1)
            self.sort_randomized(arr, pi + 1, high)


class QuickSortGUI:
    """Custom tkinter quicksort visualizer"""
    
    # Design tokens: performance/analytics aesthetic
    COLORS = {
        'dark_bg': '#0d1117',        # GitHub dark
        'light_bg': '#f6f8fa',       # GitHub light
        'primary': '#1f6feb',        # GitHub blue
        'secondary': '#238636',      # GitHub green
        'accent': '#da3633',         # GitHub red (pivot/unsorted)
        'accent_orange': '#fb8500',  # Orange (comparisons)
        'accent_cyan': '#58a6ff',    # Cyan (sorted)
        'text_primary': '#0d1117',
        'text_secondary': '#6e7681',
        'border': '#d0d7de',
        'bar_default': '#1f6feb',
        'bar_compare': '#fb8500',
        'bar_swap': '#da3633',
        'bar_sorted': '#58a6ff',
    }
    
    FONTS = {
        'title': ('Consolas', 20, 'bold'),
        'heading': ('Consolas', 12, 'bold'),
        'subhead': ('Consolas', 10, 'bold'),
        'body': ('Consolas', 9),
        'mono': ('Courier New', 9),
        'stats': ('Courier New', 10, 'bold'),
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title('QuickSort Visualizer')
        self.root.geometry('1300x820')
        self.root.configure(bg=self.COLORS['light_bg'])
        
        self.animator = QuickSortAnimator()
        self.data = []
        self.sorted_indices = set()
        self.current_step = 0
        self.sorting = False
        self.animation_speed = 100  # ms per step
        
        self.build_ui()
        self.generate_data()
    
    def build_ui(self):
        """Build main interface"""
        self.build_header()
        
        main = tk.Frame(self.root, bg=self.COLORS['light_bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Left: Controls
        left = tk.Frame(main, bg=self.COLORS['light_bg'], width=260)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left.pack_propagate(False)
        
        self.build_controls(left)
        
        # Right: Visualization + Stats
        right = tk.Frame(main, bg=self.COLORS['light_bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.build_viz(right)
    
    def build_header(self):
        """Build top header"""
        header = tk.Frame(self.root, bg=self.COLORS['dark_bg'], height=75)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        hframe = tk.Frame(header, bg=self.COLORS['dark_bg'])
        hframe.pack(pady=12, padx=12)
        
        tk.Label(
            hframe,
            text='⚡ QuickSort Visualizer',
            font=self.FONTS['title'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['accent_cyan']
        ).pack(anchor='w')
        
        tk.Label(
            hframe,
            text='Compare Deterministic vs Randomized QuickSort in real-time',
            font=self.FONTS['body'],
            bg=self.COLORS['dark_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(anchor='w')
    
    def build_controls(self, parent):
        """Build left control panel"""
        # Data size
        size_frame = tk.LabelFrame(
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
        size_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            size_frame,
            text='Array Size:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 4))
        
        self.size_var = tk.IntVar(value=100)
        tk.Scale(
            size_frame,
            from_=20,
            to=300,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=self.COLORS['primary'],
            command=lambda _: self.generate_data() if not self.sorting else None
        ).pack(fill=tk.X, pady=(0, 12))
        
        # Input type
        tk.Label(
            size_frame,
            text='Input Type:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 6))
        
        self.input_type_var = tk.StringVar(value='random')
        
        for input_type, label in [('random', 'Random'), ('sorted', 'Sorted'), 
                                   ('reverse', 'Reverse'), ('nearly', 'Nearly Sorted')]:
            tk.Radiobutton(
                size_frame,
                text=label,
                variable=self.input_type_var,
                value=input_type,
                font=self.FONTS['body'],
                bg=self.COLORS['light_bg'],
                fg=self.COLORS['text_primary'],
                selectcolor=self.COLORS['primary'],
                activebackground=self.COLORS['light_bg'],
                command=lambda: self.generate_data() if not self.sorting else None
            ).pack(anchor='w', pady=2)
        
        # Animation speed
        tk.Label(
            size_frame,
            text='Speed:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(anchor='w', pady=(12, 4))
        
        self.speed_var = tk.IntVar(value=50)
        tk.Scale(
            size_frame,
            from_=1,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=self.COLORS['accent_orange']
        ).pack(fill=tk.X, pady=(0, 12))
        
        # Action buttons
        btn_frame = tk.Frame(size_frame, bg=self.COLORS['light_bg'])
        btn_frame.pack(fill=tk.X)
        
        self.dqs_btn = tk.Button(
            btn_frame,
            text='▶ DQS',
            font=self.FONTS['heading'],
            bg=self.COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor='hand2',
            command=self.sort_deterministic
        )
        self.dqs_btn.pack(side=tk.LEFT, padx=(0, 6))
        
        self.rqs_btn = tk.Button(
            btn_frame,
            text='▶ RQS',
            font=self.FONTS['heading'],
            bg=self.COLORS['secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            pady=8,
            cursor='hand2',
            command=self.sort_randomized
        )
        self.rqs_btn.pack(side=tk.LEFT)
        
        tk.Button(
            size_frame,
            text='🔄 Reset',
            font=self.FONTS['body'],
            bg=self.COLORS['text_secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor='hand2',
            command=self.reset_view
        ).pack(fill=tk.X, pady=(12, 0))
        
        # Statistics
        stats_frame = tk.LabelFrame(
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
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            stats_frame,
            text='DQS (Deterministic)',
            font=self.FONTS['subhead'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['primary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.dqs_comps_label = tk.Label(
            stats_frame,
            text='Comparisons: —',
            font=self.FONTS['mono'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        )
        self.dqs_comps_label.pack(anchor='w', pady=2)
        
        self.dqs_time_label = tk.Label(
            stats_frame,
            text='Time: — ms',
            font=self.FONTS['mono'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        )
        self.dqs_time_label.pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            stats_frame,
            text='RQS (Randomized)',
            font=self.FONTS['subhead'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['secondary']
        ).pack(anchor='w', pady=(0, 8))
        
        self.rqs_comps_label = tk.Label(
            stats_frame,
            text='Comparisons: —',
            font=self.FONTS['mono'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        )
        self.rqs_comps_label.pack(anchor='w', pady=2)
        
        self.rqs_time_label = tk.Label(
            stats_frame,
            text='Time: — ms',
            font=self.FONTS['mono'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        )
        self.rqs_time_label.pack(anchor='w', pady=(0, 10))
        
        # Status
        self.status_label = tk.Label(
            stats_frame,
            text='Ready',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_secondary'],
            wraplength=220
        )
        self.status_label.pack(anchor='w', pady=(10, 0))
    
    def build_viz(self, parent):
        """Build visualization area"""
        viz_frame = tk.LabelFrame(
            parent,
            text='Sorting Visualization',
            font=self.FONTS['heading'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1,
            padx=10,
            pady=10
        )
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(
            viz_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            height=300
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', lambda e: self.draw_bars())
        
        # Progress
        progress_frame = tk.Frame(viz_frame, bg=self.COLORS['light_bg'])
        progress_frame.pack(fill=tk.X, pady=(12, 0))
        
        tk.Label(
            progress_frame,
            text='Progress:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT)
        
        self.progress_label = tk.Label(
            progress_frame,
            text='0%',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['primary']
        )
        self.progress_label.pack(side=tk.LEFT, padx=(8, 0))
    
    def generate_data(self):
        """Generate array based on input type"""
        n = self.size_var.get()
        input_type = self.input_type_var.get()
        
        if input_type == 'random':
            self.data = [random.randint(1, 1000) for _ in range(n)]
        elif input_type == 'sorted':
            self.data = list(range(1, n + 1))
        elif input_type == 'reverse':
            self.data = list(range(n, 0, -1))
        else:  # nearly sorted
            self.data = list(range(1, n + 1))
            for _ in range(n // 20):
                i, j = random.randint(0, n-1), random.randint(0, n-1)
                self.data[i], self.data[j] = self.data[j], self.data[i]
        
        self.sorted_indices = set()
        self.current_step = 0
        self.draw_bars()
        self.reset_stats()
    
    def reset_view(self):
        """Reset to original data"""
        self.sorted_indices = set()
        self.current_step = 0
        self.draw_bars()
        self.reset_stats()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.dqs_comps_label.config(text='Comparisons: —')
        self.dqs_time_label.config(text='Time: — ms')
        self.rqs_comps_label.config(text='Comparisons: —')
        self.rqs_time_label.config(text='Time: — ms')
        self.status_label.config(text='Ready', fg=self.COLORS['text_secondary'])
        self.progress_label.config(text='0%')
    
    def sort_deterministic(self):
        """Start deterministic quicksort"""
        if self.sorting:
            return
        
        self.sorting = True
        self.dqs_btn.config(state=tk.DISABLED)
        self.rqs_btn.config(state=tk.DISABLED)
        self.status_label.config(text='Sorting (DQS)...', fg=self.COLORS['primary'])
        
        thread = threading.Thread(
            target=self._sort_worker,
            args=(False,),
            daemon=True
        )
        thread.start()
    
    def sort_randomized(self):
        """Start randomized quicksort"""
        if self.sorting:
            return
        
        self.sorting = True
        self.dqs_btn.config(state=tk.DISABLED)
        self.rqs_btn.config(state=tk.DISABLED)
        self.status_label.config(text='Sorting (RQS)...', fg=self.COLORS['secondary'])
        
        thread = threading.Thread(
            target=self._sort_worker,
            args=(True,),
            daemon=True
        )
        thread.start()
    
    def _sort_worker(self, use_random: bool):
        """Background sort with animation"""
        self.animator.reset()
        arr = self.data[:]
        
        start = time.perf_counter()
        
        if use_random:
            self.animator.sort_randomized(arr, 0, len(arr) - 1)
            label_comps = self.rqs_comps_label
            label_time = self.rqs_time_label
        else:
            self.animator.sort_deterministic(arr, 0, len(arr) - 1)
            label_comps = self.dqs_comps_label
            label_time = self.dqs_time_label
        
        elapsed = (time.perf_counter() - start) * 1000
        
        # Update UI
        self.root.after(0, lambda: self._animate_sort(arr, use_random))
        self.root.after(0, lambda: label_comps.config(text=f'Comparisons: {self.animator.comparisons}'))
        self.root.after(0, lambda: label_time.config(text=f'Time: {elapsed:.2f} ms'))
    
    def _animate_sort(self, sorted_arr, use_random: bool):
        """Animate sort steps"""
        self.data = sorted_arr
        self.sorted_indices = set(range(len(self.data)))
        self.draw_bars()
        self.sorting = False
        self.dqs_btn.config(state=tk.NORMAL)
        self.rqs_btn.config(state=tk.NORMAL)
        
        algo_name = 'RQS' if use_random else 'DQS'
        self.status_label.config(
            text=f'✓ {algo_name} Complete',
            fg=self.COLORS['accent_cyan']
        )
        self.progress_label.config(text='100%')
    
    def draw_bars(self):
        """Draw array bars"""
        self.canvas.delete('all')
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1 or not self.data:
            return
        
        n = len(self.data)
        bar_w = w / n
        max_val = max(self.data)
        
        for i, val in enumerate(self.data):
            x0 = i * bar_w
            y0 = h - (val / max_val * h * 0.9)
            x1 = x0 + bar_w - 1
            y1 = h
            
            # Color coding
            if i in self.sorted_indices:
                color = self.COLORS['bar_sorted']
            else:
                color = self.COLORS['bar_default']
            
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=color,
                outline=color,
                width=0
            )


if __name__ == '__main__':
    root = tk.Tk()
    app = QuickSortGUI(root)
    root.mainloop()