import tkinter as tk
from tkinter import ttk, messagebox
import threading
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SolverMetrics:
    """Track solver performance"""
    solutions_found: int = 0
    backtracks: int = 0
    is_solving: bool = False


class NQueensSolver:
    """N-Queens solver with backtracking instrumentation"""
    
    def __init__(self):
        self.metrics = SolverMetrics()
    
    def is_safe(self, board: List[int], row: int, col: int) -> bool:
        """Check if placing queen at (row, col) is safe"""
        for prev_row in range(row):
            placed = board[prev_row]
            if placed == col:  # Same column
                return False
            if abs(prev_row - row) == abs(placed - col):  # Diagonal
                return False
        return True
    
    def solve(self, n: int, progress_callback=None) -> Tuple[List[List[int]], int]:
        """Solve N-Queens and return solutions with backtrack count"""
        self.metrics = SolverMetrics(is_solving=True)
        board = [-1] * n
        solutions = []
        
        def backtrack(row):
            if not self.metrics.is_solving:
                return
            
            if row == n:
                solutions.append(board[:])
                self.metrics.solutions_found = len(solutions)
                if progress_callback:
                    progress_callback()
                return
            
            for col in range(n):
                if self.is_safe(board, row, col):
                    board[row] = col
                    backtrack(row + 1)
                    board[row] = -1
                    self.metrics.backtracks += 1
        
        backtrack(0)
        self.metrics.is_solving = False
        return solutions, self.metrics.backtracks


class NQueensGUI:
    """Modern tkinter GUI for N-Queens solver"""
    
    # Design tokens
    COLORS = {
        'dark_bg': '#1a1a1a',
        'light_bg': '#f5f5f5',
        'primary': '#e74c3c',      # Deep red for queens
        'secondary': '#34495e',     # Steel blue accents
        'board_dark': '#2c3e50',   # Chess dark square
        'board_light': '#ecf0f1',  # Chess light square
        'accent': '#f39c12',        # Gold for highlights
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'border': '#bdc3c7',
    }
    
    FONTS = {
        'title': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'mono': ('Courier New', 9),
        'stats': ('Courier New', 11, 'bold'),
    }
    
    CELL_SIZE = 50
    PADDING = 12
    
    def __init__(self, root):
        self.root = root
        self.root.title('N-Queens Solver')
        self.root.geometry('900x800')
        self.root.configure(bg=self.COLORS['light_bg'])
        
        self.solver = NQueensSolver()
        self.solutions: List[List[int]] = []
        self.current_solution_idx = 0
        self.solving_thread = None
        
        self.setup_styles()
        self.build_ui()
    
    def setup_styles(self):
        """Configure ttk styles for consistency"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom button style
        style.configure('Primary.TButton',
                       font=self.FONTS['body'],
                       padding=8)
        
        style.configure('Secondary.TButton',
                       font=self.FONTS['body'],
                       padding=6)
    
    def build_ui(self):
        """Build main interface"""
        # Header
        self.build_header()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.COLORS['light_bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.PADDING, pady=self.PADDING)
        
        # Left panel: Controls
        left_panel = tk.Frame(main_frame, bg=self.COLORS['light_bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, self.PADDING))
        self.build_controls(left_panel)
        
        # Right panel: Board + Navigation
        right_panel = tk.Frame(main_frame, bg=self.COLORS['light_bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.build_board_area(right_panel)
    
    def build_header(self):
        """Build top header section"""
        header = tk.Frame(self.root, bg=self.COLORS['board_dark'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text='♛ N-Queens Solver',
            font=self.FONTS['title'],
            bg=self.COLORS['board_dark'],
            fg=self.COLORS['accent']
        )
        title.pack(pady=12)
    
    def build_controls(self, parent):
        """Build left control panel"""
        # N value selector
        n_frame = tk.LabelFrame(
            parent,
            text='Board Size',
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            font=self.FONTS['heading'],
            relief=tk.FLAT,
            borderwidth=1
        )
        n_frame.pack(fill=tk.X, pady=(0, self.PADDING))
        
        tk.Label(n_frame, text='N =', font=self.FONTS['body'],
                bg=self.COLORS['light_bg'], fg=self.COLORS['text_primary']).pack(pady=8)
        
        self.n_var = tk.IntVar(value=4)
        n_spinbox = tk.Spinbox(
            n_frame,
            from_=4,
            to=12,
            textvariable=self.n_var,
            font=self.FONTS['body'],
            width=8,
            bg=self.COLORS['board_light'],
            fg=self.COLORS['text_primary'],
            relief=tk.FLAT,
            borderwidth=1
        )
        n_spinbox.pack(pady=8)
        
        # Solve button
        self.solve_btn = tk.Button(
            n_frame,
            text='▶ Solve',
            font=self.FONTS['heading'],
            bg=self.COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.on_solve_clicked
        )
        self.solve_btn.pack(pady=12)
        
        # Cancel button (hidden initially)
        self.cancel_btn = tk.Button(
            n_frame,
            text='⏸ Stop',
            font=self.FONTS['heading'],
            bg=self.COLORS['secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.on_cancel_clicked
        )
        
        # Metrics display
        metrics_frame = tk.LabelFrame(
            parent,
            text='Results',
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            font=self.FONTS['heading'],
            relief=tk.FLAT,
            borderwidth=1
        )
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=(0, self.PADDING))
        
        # Solutions found
        self.solutions_label = tk.Label(
            metrics_frame,
            text='Solutions: 0',
            font=self.FONTS['stats'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['primary']
        )
        self.solutions_label.pack(pady=8, padx=8, anchor='w')
        
        # Backtracks
        self.backtracks_label = tk.Label(
            metrics_frame,
            text='Backtracks: 0',
            font=self.FONTS['stats'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['secondary']
        )
        self.backtracks_label.pack(pady=8, padx=8, anchor='w')
        
        # Status
        self.status_label = tk.Label(
            metrics_frame,
            text='Ready',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_secondary'],
            wraplength=140
        )
        self.status_label.pack(pady=12, padx=8, anchor='w')
    
    def build_board_area(self, parent):
        """Build chess board and navigation"""
        # Board
        self.canvas = tk.Canvas(
            parent,
            bg=self.COLORS['board_light'],
            highlightthickness=0,
            cursor='cross'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, self.PADDING))
        self.canvas.bind('<Configure>', lambda e: self.draw_board())
        
        # Navigation bar
        nav_frame = tk.Frame(parent, bg=self.COLORS['light_bg'])
        nav_frame.pack(fill=tk.X)
        
        tk.Label(
            nav_frame,
            text='Solution:',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary']
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.prev_btn = tk.Button(
            nav_frame,
            text='◀ Prev',
            font=self.FONTS['body'],
            bg=self.COLORS['secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            cursor='hand2',
            command=self.prev_solution,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=4)
        
        self.solution_label = tk.Label(
            nav_frame,
            text='0 / 0',
            font=self.FONTS['body'],
            bg=self.COLORS['light_bg'],
            fg=self.COLORS['text_primary'],
            width=10
        )
        self.solution_label.pack(side=tk.LEFT, padx=8)
        
        self.next_btn = tk.Button(
            nav_frame,
            text='Next ▶',
            font=self.FONTS['body'],
            bg=self.COLORS['secondary'],
            fg='white',
            relief=tk.FLAT,
            padx=12,
            cursor='hand2',
            command=self.next_solution,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=4)
    
    def draw_board(self):
        """Render the chess board and queens"""
        self.canvas.delete('all')
        
        if not self.solutions:
            return
        
        solution = self.solutions[self.current_solution_idx]
        n = len(solution)
        
        # Calculate board dimensions to fit canvas
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        # Dynamic cell size
        cell_size = min(canvas_w // (n + 1), canvas_h // (n + 1), 80)
        board_w = n * cell_size
        board_h = n * cell_size
        
        # Center board
        offset_x = (canvas_w - board_w) // 2
        offset_y = (canvas_h - board_h) // 2
        
        # Draw board
        for row in range(n):
            for col in range(n):
                x0 = offset_x + col * cell_size
                y0 = offset_y + row * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                
                # Checkerboard pattern
                is_dark = (row + col) % 2 == 0
                bg_color = self.COLORS['board_dark'] if is_dark else self.COLORS['board_light']
                
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=bg_color,
                    outline=self.COLORS['border'],
                    width=1
                )
                
                # Draw queen if placed in this cell
                if solution[row] == col:
                    self.draw_queen(x0, y0, x1, y1, cell_size)
    
    def draw_queen(self, x0, y0, x1, y1, size):
        """Draw a stylized queen on the board"""
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        
        # Queen symbol
        radius = size // 3
        
        # Outer circle (crown)
        self.canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            fill=self.COLORS['primary'],
            outline=self.COLORS['accent'],
            width=2
        )
        
        # Inner circle (jewel)
        inner_r = radius // 2
        self.canvas.create_oval(
            cx - inner_r, cy - inner_r,
            cx + inner_r, cy + inner_r,
            fill=self.COLORS['accent'],
            outline=self.COLORS['primary'],
            width=1
        )
    
    def on_solve_clicked(self):
        """Handle solve button click"""
        n = self.n_var.get()
        
        # Validate
        if n < 4 or n > 12:
            messagebox.showerror('Invalid', 'N must be between 4 and 12')
            return
        
        # UI state: solving
        self.solve_btn.pack_forget()
        self.cancel_btn.pack(pady=12)
        self.n_var.set(n)
        
        # Disable controls
        for widget in [self.prev_btn, self.next_btn]:
            widget.config(state=tk.DISABLED)
        
        self.status_label.config(text='Solving...', fg=self.COLORS['primary'])
        self.solutions_label.config(text='Solutions: 0')
        self.backtracks_label.config(text='Backtracks: 0')
        
        # Solve in background thread
        self.solving_thread = threading.Thread(
            target=self._solve_worker,
            args=(n,),
            daemon=True
        )
        self.solving_thread.start()
    
    def _solve_worker(self, n):
        """Worker thread for solving"""
        try:
            self.solutions, backtracks = self.solver.solve(
                n,
                progress_callback=self.update_metrics
            )
            
            self.root.after(0, self._on_solve_complete, backtracks)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror('Error', str(e)))
    
    def update_metrics(self):
        """Update metrics display (called from solver)"""
        self.root.after(0, self._update_metrics_display)
    
    def _update_metrics_display(self):
        """Update displayed metrics"""
        self.solutions_label.config(
            text=f'Solutions: {self.solver.metrics.solutions_found}'
        )
    
    def _on_solve_complete(self, backtracks):
        """Called when solving completes"""
        self.current_solution_idx = 0
        
        # Update UI
        self.cancel_btn.pack_forget()
        self.solve_btn.pack(pady=12)
        
        count = len(self.solutions)
        self.solutions_label.config(text=f'Solutions: {count}')
        self.backtracks_label.config(text=f'Backtracks: {backtracks}')
        
        if count > 0:
            self.status_label.config(
                text=f'✓ Found {count} solution{"s" if count != 1 else ""}',
                fg=self.COLORS['secondary']
            )
            
            # Enable navigation if multiple solutions
            if count > 1:
                self.next_btn.config(state=tk.NORMAL)
                self.prev_btn.config(state=tk.NORMAL if self.current_solution_idx > 0 else tk.DISABLED)
            
            self.solution_label.config(text=f'1 / {count}')
            self.draw_board()
        else:
            self.status_label.config(text='No solutions found', fg=self.COLORS['text_secondary'])
    
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        self.solver.metrics.is_solving = False
        self.cancel_btn.pack_forget()
        self.solve_btn.pack(pady=12)
        self.status_label.config(text='Cancelled', fg=self.COLORS['text_secondary'])
    
    def next_solution(self):
        """Navigate to next solution"""
        if self.current_solution_idx < len(self.solutions) - 1:
            self.current_solution_idx += 1
            self.update_navigation()
    
    def prev_solution(self):
        """Navigate to previous solution"""
        if self.current_solution_idx > 0:
            self.current_solution_idx -= 1
            self.update_navigation()
    
    def update_navigation(self):
        """Update navigation button states and display"""
        count = len(self.solutions)
        current = self.current_solution_idx + 1
        
        self.solution_label.config(text=f'{current} / {count}')
        self.prev_btn.config(state=tk.NORMAL if self.current_solution_idx > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_solution_idx < count - 1 else tk.DISABLED)
        
        self.draw_board()


if __name__ == '__main__':
    root = tk.Tk()
    app = NQueensGUI(root)
    root.mainloop()