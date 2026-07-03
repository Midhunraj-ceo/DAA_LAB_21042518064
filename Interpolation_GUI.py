"""
Interpolation Search Visualizer
--------------------------------
A custom Tkinter GUI that animates interpolation search step-by-step,
compares it against binary search, and reports comparison counts / timing.

Run with:  python interpolation_search_gui.py
(Requires only the Python standard library - tkinter ships with CPython.)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time


# ----------------------------------------------------------------------
# Search algorithms (return list of "steps" for animation + final result)
# ----------------------------------------------------------------------

def interpolation_search_steps(arr, target):
    steps = []
    low, high = 0, len(arr) - 1
    comparisons = 0
    result = -1

    while low <= high and arr[low] <= target <= arr[high]:
        comparisons += 1
        if low == high:
            if arr[low] == target:
                result = low
                steps.append(dict(low=low, high=high, pos=low, found=True))
            else:
                steps.append(dict(low=low, high=high, pos=low, found=False))
            break

        pos = low + int(((target - arr[low]) * (high - low)) / (arr[high] - arr[low]))
        pos = max(low, min(high, pos))  # safety clamp

        if arr[pos] == target:
            result = pos
            steps.append(dict(low=low, high=high, pos=pos, found=True))
            break
        elif arr[pos] < target:
            steps.append(dict(low=low, high=high, pos=pos, found=False, move="right"))
            low = pos + 1
        else:
            steps.append(dict(low=low, high=high, pos=pos, found=False, move="left"))
            high = pos - 1

    return steps, result, comparisons


def binary_search_steps(arr, target):
    steps = []
    low, high = 0, len(arr) - 1
    comparisons = 0
    result = -1

    while low <= high:
        comparisons += 1
        mid = (low + high) // 2
        if arr[mid] == target:
            result = mid
            steps.append(dict(low=low, high=high, pos=mid, found=True))
            break
        elif arr[mid] < target:
            steps.append(dict(low=low, high=high, pos=mid, found=False, move="right"))
            low = mid + 1
        else:
            steps.append(dict(low=low, high=high, pos=mid, found=False, move="left"))
            high = mid - 1

    return steps, result, comparisons


# ----------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------

BG = "#1e1f29"
PANEL = "#282a3a"
FG = "#e8e8f0"
ACCENT = "#7c8cff"
GREEN = "#4caf50"
RED = "#ef5350"
YELLOW = "#ffca28"
BLUE = "#42a5f5"
GREY = "#4a4c5e"


class SearchVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interpolation Search Visualizer")
        self.geometry("1150x680")
        self.configure(bg=BG)
        self.minsize(950, 600)

        self.arr = []
        self.steps = []
        self.step_index = -1
        self.target = None
        self.result_idx = None
        self.comparisons = 0
        self.playing = False

        self._build_style()
        self._build_layout()
        self.generate_array()

    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=FG, font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", background=ACCENT)
        style.configure("TEntry", padding=4)
        style.configure("Horizontal.TScale", background=PANEL)

    def _build_layout(self):
        # Title
        title = ttk.Label(self, text="🔍 Interpolation Search Visualizer", style="Title.TLabel")
        title.pack(pady=(14, 6))

        # --- Controls panel ---
        controls = ttk.Frame(self, style="Panel.TFrame")
        controls.pack(fill="x", padx=16, pady=6)

        pad = dict(padx=6, pady=8)

        ttk.Label(controls, text="Array size:", style="Panel.TLabel").grid(row=0, column=0, **pad)
        self.size_var = tk.StringVar(value="20")
        ttk.Entry(controls, textvariable=self.size_var, width=6).grid(row=0, column=1, **pad)

        ttk.Label(controls, text="Max value:", style="Panel.TLabel").grid(row=0, column=2, **pad)
        self.maxval_var = tk.StringVar(value="200")
        ttk.Entry(controls, textvariable=self.maxval_var, width=8).grid(row=0, column=3, **pad)

        gen_btn = ttk.Button(controls, text="🎲 Generate Random Array", command=self.generate_array)
        gen_btn.grid(row=0, column=4, **pad)

        ttk.Label(controls, text="Or custom array (comma-separated, sorted):",
                  style="Panel.TLabel").grid(row=1, column=0, columnspan=2, **pad, sticky="w")
        self.custom_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.custom_var, width=50).grid(
            row=1, column=2, columnspan=3, **pad, sticky="we")
        ttk.Button(controls, text="Use Custom Array", command=self.use_custom_array).grid(
            row=1, column=5, **pad)

        ttk.Label(controls, text="Target value:", style="Panel.TLabel").grid(row=2, column=0, **pad)
        self.target_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.target_var, width=10).grid(row=2, column=1, **pad)

        ttk.Button(controls, text="🎯 Random Target (in array)",
                   command=self.random_target_in_array).grid(row=2, column=2, **pad)
        ttk.Button(controls, text="❓ Random Target (may miss)",
                   command=self.random_target_any).grid(row=2, column=3, **pad)

        run_btn = ttk.Button(controls, text="▶ Run Search", command=self.run_search)
        run_btn.grid(row=2, column=4, **pad)

        for i in range(6):
            controls.columnconfigure(i, weight=1)

        # --- Playback panel ---
        playback = ttk.Frame(self, style="Panel.TFrame")
        playback.pack(fill="x", padx=16, pady=(0, 6))

        ttk.Button(playback, text="⏮ Reset", command=self.reset_playback).pack(side="left", padx=6, pady=8)
        ttk.Button(playback, text="⏪ Prev Step", command=self.prev_step).pack(side="left", padx=6, pady=8)
        ttk.Button(playback, text="⏩ Next Step", command=self.next_step).pack(side="left", padx=6, pady=8)
        self.play_btn = ttk.Button(playback, text="▶ Auto Play", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=6, pady=8)

        ttk.Label(playback, text="Speed:", style="Panel.TLabel").pack(side="left", padx=(20, 4))
        self.speed_var = tk.DoubleVar(value=700)
        ttk.Scale(playback, from_=100, to=2000, orient="horizontal",
                  variable=self.speed_var, length=160).pack(side="left", padx=4)

        self.algo_choice = tk.StringVar(value="interpolation")
        ttk.Radiobutton(playback, text="Interpolation Search", value="interpolation",
                         variable=self.algo_choice, command=self.reset_playback).pack(side="left", padx=(24, 6))
        ttk.Radiobutton(playback, text="Binary Search", value="binary",
                         variable=self.algo_choice, command=self.reset_playback).pack(side="left", padx=6)

        # --- Canvas ---
        canvas_frame = ttk.Frame(self, style="Panel.TFrame")
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=6)
        self.canvas = tk.Canvas(canvas_frame, bg=PANEL, highlightthickness=0, height=340)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Legend ---
        legend = ttk.Frame(self, style="TFrame")
        legend.pack(fill="x", padx=16)
        for color, text in [(BLUE, "low"), (RED, "high"), (YELLOW, "interpolated pos"), (GREEN, "found")]:
            sw = tk.Canvas(legend, width=14, height=14, bg=BG, highlightthickness=0)
            sw.pack(side="left", padx=(0, 4), pady=4)
            sw.create_rectangle(1, 1, 13, 13, fill=color, outline=color)
            ttk.Label(legend, text=text).pack(side="left", padx=(0, 16))

        # --- Status / log ---
        bottom = ttk.Frame(self, style="Panel.TFrame")
        bottom.pack(fill="both", padx=16, pady=(6, 16), expand=False)

        self.status_var = tk.StringVar(value="Generate an array and pick a target to begin.")
        ttk.Label(bottom, textvariable=self.status_var, style="Panel.TLabel",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 2))

        log_frame = ttk.Frame(bottom, style="Panel.TFrame")
        log_frame.pack(fill="both", padx=10, pady=(0, 8), expand=True)
        self.log_text = tk.Text(log_frame, height=6, bg="#1a1b24", fg=FG, insertbackground=FG,
                                 font=("Consolas", 10), relief="flat")
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    # ------------------------------------------------------------------
    # Array / target generation
    # ------------------------------------------------------------------
    def generate_array(self):
        try:
            size = max(3, min(200, int(self.size_var.get())))
            maxval = max(size, int(self.maxval_var.get()))
        except ValueError:
            messagebox.showerror("Invalid input", "Array size and max value must be integers.")
            return
        self.arr = sorted(random.sample(range(maxval), size))
        self.custom_var.set("")
        self.random_target_in_array()
        self.reset_playback()
        self.draw_array()

    def use_custom_array(self):
        text = self.custom_var.get().strip()
        if not text:
            messagebox.showinfo("Empty", "Type comma-separated numbers first.")
            return
        try:
            values = [int(v.strip()) for v in text.split(",") if v.strip() != ""]
        except ValueError:
            messagebox.showerror("Invalid input", "Array must contain integers only.")
            return
        if len(values) < 2:
            messagebox.showerror("Invalid input", "Array needs at least 2 elements.")
            return
        if values != sorted(values):
            if not messagebox.askyesno("Not sorted", "Array isn't sorted. Sort it automatically?"):
                return
            values = sorted(values)
        self.arr = values
        self.size_var.set(str(len(values)))
        self.reset_playback()
        self.draw_array()

    def random_target_in_array(self):
        if not self.arr:
            return
        self.target_var.set(str(random.choice(self.arr)))
        self.reset_playback()

    def random_target_any(self):
        if not self.arr:
            return
        lo, hi = self.arr[0], self.arr[-1]
        self.target_var.set(str(random.randint(lo - 10, hi + 10)))
        self.reset_playback()

    # ------------------------------------------------------------------
    # Search execution
    # ------------------------------------------------------------------
    def run_search(self):
        if not self.arr:
            messagebox.showinfo("No array", "Generate or enter an array first.")
            return
        try:
            self.target = int(self.target_var.get())
        except (ValueError, TypeError):
            messagebox.showerror("Invalid target", "Target must be an integer.")
            return

        if self.algo_choice.get() == "interpolation":
            self.steps, self.result_idx, self.comparisons = interpolation_search_steps(self.arr, self.target)
            algo_name = "Interpolation Search"
        else:
            self.steps, self.result_idx, self.comparisons = binary_search_steps(self.arr, self.target)
            algo_name = "Binary Search"

        self.step_index = -1
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", f"Running {algo_name} for target = {self.target}\n")
        self.log_text.insert("end", "-" * 60 + "\n")
        self.status_var.set(f"{algo_name}: {len(self.steps)} step(s) ready. Use Next Step or Auto Play.")
        self.draw_array()
        self.next_step()

    def reset_playback(self):
        self.playing = False
        self.play_btn.configure(text="▶ Auto Play")
        self.steps = []
        self.step_index = -1
        self.result_idx = None
        self.log_text.delete("1.0", "end")
        self.status_var.set("Press 'Run Search' to begin.")
        self.draw_array()

    def next_step(self):
        if not self.steps:
            return
        if self.step_index >= len(self.steps) - 1:
            self.status_var.set(self._final_message())
            self.playing = False
            self.play_btn.configure(text="▶ Auto Play")
            return
        self.step_index += 1
        self._log_current_step()
        self.draw_array()
        if self.step_index == len(self.steps) - 1:
            self.status_var.set(self._final_message())

    def prev_step(self):
        if self.step_index <= 0:
            self.step_index = -1
            self.draw_array()
            self.status_var.set("At start. Press Next Step to begin.")
            return
        self.step_index -= 1
        self.draw_array()
        self.status_var.set(f"Step {self.step_index + 1} of {len(self.steps)}")

    def toggle_play(self):
        if not self.steps:
            return
        self.playing = not self.playing
        self.play_btn.configure(text="⏸ Pause" if self.playing else "▶ Auto Play")
        if self.playing:
            self._auto_step()

    def _auto_step(self):
        if not self.playing:
            return
        if self.step_index >= len(self.steps) - 1:
            self.playing = False
            self.play_btn.configure(text="▶ Auto Play")
            return
        self.next_step()
        delay = int(self.speed_var.get())
        self.after(delay, self._auto_step)

    def _final_message(self):
        algo_name = "Interpolation Search" if self.algo_choice.get() == "interpolation" else "Binary Search"
        if self.result_idx is not None and self.result_idx != -1:
            return (f"✅ {algo_name}: target {self.target} FOUND at index {self.result_idx} "
                    f"using {self.comparisons} comparison(s).")
        return (f"❌ {algo_name}: target {self.target} NOT FOUND "
                f"after {self.comparisons} comparison(s).")

    def _log_current_step(self):
        s = self.steps[self.step_index]
        line = f"Step {self.step_index + 1}: low={s['low']}, high={s['high']}, pos={s['pos']}, arr[pos]={self.arr[s['pos']]}"
        if s.get("found"):
            line += "  -> MATCH!"
        elif s.get("move") == "right":
            line += "  -> arr[pos] < target, move right"
        elif s.get("move") == "left":
            line += "  -> arr[pos] > target, move left"
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_array(self):
        self.canvas.delete("all")
        if not self.arr:
            return

        self.update_idletasks()
        width = max(self.canvas.winfo_width(), 400)
        height = max(self.canvas.winfo_height(), 300)

        n = len(self.arr)
        margin_x = 20
        available_w = width - 2 * margin_x
        bar_w = max(available_w / n, 2)
        max_val = max(self.arr) if self.arr else 1
        min_val = min(self.arr) if self.arr else 0
        val_range = max(max_val - min_val, 1)

        base_y = height - 60
        top_pad = 30
        max_bar_h = base_y - top_pad

        current = self.steps[self.step_index] if (0 <= self.step_index < len(self.steps)) else None

        for i, val in enumerate(self.arr):
            x0 = margin_x + i * bar_w
            x1 = x0 + bar_w * 0.85
            bar_h = top_pad + max_bar_h * ((val - min_val) / val_range)
            y0 = base_y - bar_h + top_pad
            y0 = base_y - (max_bar_h * ((val - min_val) / val_range))
            y1 = base_y

            color = GREY
            if current:
                if current.get("found") and i == current["pos"]:
                    color = GREEN
                elif i == current["pos"]:
                    color = YELLOW
                elif i == current["low"]:
                    color = BLUE
                elif i == current["high"]:
                    color = RED
                elif current["low"] <= i <= current["high"]:
                    color = "#5c5e78"  # within active range, slightly lighter
                else:
                    color = "#33344a"  # eliminated

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

            # value label (only if there's room)
            if bar_w > 14 or n <= 40:
                self.canvas.create_text((x0 + x1) / 2, y0 - 10, text=str(val),
                                         fill=FG, font=("Consolas", 8))
            if bar_w > 10 or n <= 60:
                self.canvas.create_text((x0 + x1) / 2, base_y + 12, text=str(i),
                                         fill="#9092a8", font=("Consolas", 7))

        # target line label
        if self.target is not None:
            self.canvas.create_text(margin_x, 14, anchor="w",
                                     text=f"Target = {self.target}", fill=ACCENT,
                                     font=("Segoe UI", 11, "bold"))

        if current:
            info = f"low={current['low']}  high={current['high']}  interpolated pos={current['pos']}  arr[pos]={self.arr[current['pos']]}"
            self.canvas.create_text(width - margin_x, 14, anchor="e", text=info,
                                     fill=FG, font=("Consolas", 10))


if __name__ == "__main__":
    app = SearchVisualizer()
    app.mainloop()