import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import heapq
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx
import matplotlib.patches as mpatches

# --- Union-Find for Kruskal ---
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return False
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        return True

def kruskal(n, edges):
    """edges: list of (weight, u, v)"""
    edges.sort()  # O(E log E)
    uf   = UnionFind(n)
    mst  = []
    cost = 0
    for w, u, v in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            cost += w
            if len(mst) == n - 1:
                break
    return mst, cost

def prim(n, adj, start=0):
    """adj: adjacency list {u: [(v, w), ...]}"""
    INF    = float('inf')
    key    = [INF] * n
    parent = [-1]  * n
    inMST  = [False] * n
    key[start] = 0
    pq = [(0, start)]
    mst = []
    cost = 0
    while pq:
        w, u = heapq.heappop(pq)
        if inMST[u]: continue
        inMST[u] = True
        if parent[u] != -1:
            mst.append((parent[u], u, w))
            cost += w
        for v, wt in adj.get(u, []):
            if not inMST[v] and wt < key[v]:
                key[v] = wt
                parent[v] = u
                heapq.heappush(pq, (wt, v))
    return mst, cost


class MSTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimum Spanning Tree Visualizer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Data structures
        self.n = 7
        self.edges = [
            (7, 0, 1), (5, 0, 3), (8, 1, 2), (9, 1, 3),
            (7, 1, 4), (5, 2, 4), (15, 3, 4), (6, 3, 5),
            (8, 4, 5), (9, 4, 6), (11, 5, 6)
        ]
        self.adj = {}
        self.update_adjacency_list()
        
        self.kruskal_mst = []
        self.kruskal_cost = 0
        self.prim_mst = []
        self.prim_cost = 0
        
        # Setup styles
        self.setup_styles()
        
        # Create main frames
        self.create_widgets()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Info.TLabel', font=('Courier', 10))
        
    def create_widgets(self):
        """Create main GUI widgets"""
        # Top frame for controls
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Algorithm buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Run Kruskal's Algorithm", 
                  command=self.run_kruskal).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Prim's Algorithm", 
                  command=self.run_prim).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Run Both", 
                  command=self.run_both).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", 
                  command=self.reset_view).pack(side="left", padx=5)
        
        # Load example buttons
        ttk.Separator(control_frame, orient="horizontal").pack(fill="x", pady=10)
        
        example_frame = ttk.Frame(control_frame)
        example_frame.pack(fill="x", pady=5)
        
        ttk.Label(example_frame, text="Load Example:", font=('Helvetica', 10, 'bold')).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 1 (7 nodes)", 
                  command=self.load_example_1).pack(side="left", padx=5)
        ttk.Button(example_frame, text="Example 2 (5 nodes)", 
                  command=self.load_example_2).pack(side="left", padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Graph visualization
        left_frame = ttk.LabelFrame(content_frame, text="Graph Visualization", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.fig_frame = ttk.Frame(left_frame)
        self.fig_frame.pack(fill="both", expand=True)
        
        # Right side - Results
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        
        # Results tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Kruskal tab
        kruskal_tab = ttk.Frame(self.notebook)
        self.notebook.add(kruskal_tab, text="Kruskal's MST")
        self.create_results_tab(kruskal_tab, "kruskal")
        
        # Prim tab
        prim_tab = ttk.Frame(self.notebook)
        self.notebook.add(prim_tab, text="Prim's MST")
        self.create_results_tab(prim_tab, "prim")
        
        # Comparison tab
        comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(comparison_tab, text="Comparison")
        self.create_comparison_tab(comparison_tab)
        
        # Initial visualization
        self.visualize_graph()
        
    def create_results_tab(self, parent, algo_type):
        """Create results tab for an algorithm"""
        text_widget = scrolledtext.ScrolledText(parent, font=('Courier', 9), height=20, width=40)
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store reference
        if algo_type == "kruskal":
            self.kruskal_text = text_widget
        else:
            self.prim_text = text_widget
            
        # Configure tags
        text_widget.tag_config("header", foreground="#1f77b4", font=('Courier', 10, 'bold'))
        text_widget.tag_config("edge", foreground="#2ca02c")
        text_widget.tag_config("cost", foreground="#ff7f0e", font=('Courier', 9, 'bold'))
        text_widget.tag_config("total", foreground="#d62728", font=('Courier', 10, 'bold'))
        
    def create_comparison_tab(self, parent):
        """Create comparison tab"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.comparison_text = scrolledtext.ScrolledText(info_frame, font=('Courier', 10), height=20)
        self.comparison_text.pack(fill="both", expand=True)
        
        self.comparison_text.tag_config("header", foreground="#1f77b4", font=('Courier', 11, 'bold'))
        self.comparison_text.tag_config("metric", foreground="#2ca02c", font=('Courier', 10, 'bold'))
        self.comparison_text.tag_config("value", foreground="#ff7f0e")
        
    def update_adjacency_list(self):
        """Build adjacency list from edges"""
        self.adj = {}
        for w, u, v in self.edges:
            self.adj.setdefault(u, []).append((v, w))
            self.adj.setdefault(v, []).append((u, w))
            
    def load_example_1(self):
        """Load example 1 (7 nodes)"""
        self.n = 7
        self.edges = [
            (7, 0, 1), (5, 0, 3), (8, 1, 2), (9, 1, 3),
            (7, 1, 4), (5, 2, 4), (15, 3, 4), (6, 3, 5),
            (8, 4, 5), (9, 4, 6), (11, 5, 6)
        ]
        self.update_adjacency_list()
        self.reset_view()
        messagebox.showinfo("Success", "Example 1 loaded (7 nodes)")
        
    def load_example_2(self):
        """Load example 2 (5 nodes)"""
        self.n = 5
        self.edges = [
            (4, 0, 1), (2, 0, 3), (5, 1, 2), (7, 1, 3),
            (1, 2, 3), (3, 3, 4), (2, 2, 4)
        ]
        self.update_adjacency_list()
        self.reset_view()
        messagebox.showinfo("Success", "Example 2 loaded (5 nodes)")
        
    def reset_view(self):
        """Reset visualization"""
        self.kruskal_mst = []
        self.kruskal_cost = 0
        self.prim_mst = []
        self.prim_cost = 0
        self.clear_results()
        self.visualize_graph()
        
    def clear_results(self):
        """Clear all result displays"""
        self.kruskal_text.config(state="normal")
        self.kruskal_text.delete("1.0", "end")
        self.kruskal_text.config(state="disabled")
        
        self.prim_text.config(state="normal")
        self.prim_text.delete("1.0", "end")
        self.prim_text.config(state="disabled")
        
        self.comparison_text.config(state="normal")
        self.comparison_text.delete("1.0", "end")
        self.comparison_text.config(state="disabled")
        
    def run_kruskal(self):
        """Run Kruskal's algorithm"""
        self.clear_results()
        self.kruskal_mst, self.kruskal_cost = kruskal(self.n, self.edges[:])
        self.display_kruskal_results()
        self.visualize_graph(highlight_mst="kruskal")
        
    def run_prim(self):
        """Run Prim's algorithm"""
        self.clear_results()
        self.prim_mst, self.prim_cost = prim(self.n, self.adj)
        self.display_prim_results()
        self.visualize_graph(highlight_mst="prim")
        
    def run_both(self):
        """Run both algorithms"""
        self.clear_results()
        self.kruskal_mst, self.kruskal_cost = kruskal(self.n, self.edges[:])
        self.prim_mst, self.prim_cost = prim(self.n, self.adj)
        self.display_kruskal_results()
        self.display_prim_results()
        self.display_comparison()
        self.visualize_graph(highlight_mst="both")
        
    def display_kruskal_results(self):
        """Display Kruskal's algorithm results"""
        text = self.kruskal_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "KRUSKAL'S ALGORITHM\n", "header")
        text.insert("end", "=" * 40 + "\n\n", "header")
        text.insert("end", f"{'Nodes:':<15} {self.n}\n")
        text.insert("end", f"{'Edges:':<15} {len(self.edges)}\n\n")
        
        text.insert("end", "MST Edges (sorted by weight):\n", "header")
        text.insert("end", "-" * 40 + "\n")
        
        for u, v, w in self.kruskal_mst:
            text.insert("end", f"({u} — {v})", "edge")
            text.insert("end", f" : {w}\n", "cost")
            
        text.insert("end", "-" * 40 + "\n")
        text.insert("end", f"Total MST Cost: ", "")
        text.insert("end", f"{self.kruskal_cost}\n", "total")
        text.insert("end", f"Edges in MST: {len(self.kruskal_mst)}\n", "metric")
        
        text.config(state="disabled")
        
    def display_prim_results(self):
        """Display Prim's algorithm results"""
        text = self.prim_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "PRIM'S ALGORITHM\n", "header")
        text.insert("end", "=" * 40 + "\n\n", "header")
        text.insert("end", f"{'Nodes:':<15} {self.n}\n")
        text.insert("end", f"{'Start Node:':<15} 0\n\n")
        
        text.insert("end", "MST Edges (growth order):\n", "header")
        text.insert("end", "-" * 40 + "\n")
        
        for u, v, w in self.prim_mst:
            text.insert("end", f"({u} — {v})", "edge")
            text.insert("end", f" : {w}\n", "cost")
            
        text.insert("end", "-" * 40 + "\n")
        text.insert("end", f"Total MST Cost: ", "")
        text.insert("end", f"{self.prim_cost}\n", "total")
        text.insert("end", f"Edges in MST: {len(self.prim_mst)}\n", "metric")
        
        text.config(state="disabled")
        
    def display_comparison(self):
        """Display comparison of both algorithms"""
        text = self.comparison_text
        text.config(state="normal")
        text.delete("1.0", "end")
        
        text.insert("end", "ALGORITHM COMPARISON\n", "header")
        text.insert("end", "=" * 50 + "\n\n")
        
        text.insert("end", "METRIC COMPARISON:\n", "header")
        text.insert("end", "-" * 50 + "\n")
        text.insert("end", f"{'Metric':<25} {'Kruskal':<15} {'Prim':<15}\n", "metric")
        text.insert("end", "-" * 50 + "\n")
        
        text.insert("end", f"{'MST Cost':<25} {self.kruskal_cost:<15} {self.prim_cost:<15}\n")
        text.insert("end", f"{'Edges in MST':<25} {len(self.kruskal_mst):<15} {len(self.prim_mst):<15}\n")
        text.insert("end", f"{'Same Cost':<25} {'✓' if self.kruskal_cost == self.prim_cost else '✗':<15}\n", "value")
        
        text.insert("end", "\n")
        text.insert("end", "ALGORITHM CHARACTERISTICS:\n", "header")
        text.insert("end", "-" * 50 + "\n")
        text.insert("end", "Kruskal's:\n", "metric")
        text.insert("end", "  • Edge-based approach\n")
        text.insert("end", "  • Sorts edges by weight\n")
        text.insert("end", "  • Uses Union-Find (Disjoint Set)\n")
        text.insert("end", "  • Time: O(E log E)\n\n")
        
        text.insert("end", "Prim's:\n", "metric")
        text.insert("end", "  • Vertex-based approach\n")
        text.insert("end", "  • Grows tree from start vertex\n")
        text.insert("end", "  • Uses Priority Queue\n")
        text.insert("end", "  • Time: O(E log V)\n")
        
        text.config(state="disabled")
        
    def visualize_graph(self, highlight_mst=None):
        """Visualize the graph with matplotlib"""
        # Clear previous figure
        for widget in self.fig_frame.winfo_children():
            widget.destroy()
            
        # Create figure
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create networkx graph
        G = nx.Graph()
        G.add_nodes_from(range(self.n))
        
        edge_labels = {}
        for w, u, v in self.edges:
            G.add_edge(u, v, weight=w)
            edge_labels[(u, v)] = str(w)
            
        # Layout
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, width=2, edge_color="#cccccc", alpha=0.6)
        
        # Highlight MST edges
        if highlight_mst == "kruskal" and self.kruskal_mst:
            mst_edges = [(u, v) for u, v, _ in self.kruskal_mst]
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=mst_edges, width=3, 
                                  edge_color="#d62728", label="Kruskal MST")
                                  
        elif highlight_mst == "prim" and self.prim_mst:
            mst_edges = [(u, v) for u, v, _ in self.prim_mst]
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=mst_edges, width=3,
                                  edge_color="#2ca02c", label="Prim MST")
                                  
        elif highlight_mst == "both":
            if self.kruskal_mst:
                kruskal_edges = [(u, v) for u, v, _ in self.kruskal_mst]
                nx.draw_networkx_edges(G, pos, ax=ax, edgelist=kruskal_edges, width=3,
                                      edge_color="#d62728", label="Kruskal MST")
            if self.prim_mst:
                prim_edges = [(u, v) for u, v, _ in self.prim_mst]
                nx.draw_networkx_edges(G, pos, ax=ax, edgelist=prim_edges, width=3,
                                      edge_color="#2ca02c", label="Prim MST")
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#1f77b4", 
                              node_size=800, edgecolors="black", linewidths=2)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold", 
                               font_color="white")
        
        # Draw edge weights
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax, font_size=8)
        
        ax.set_title(f"Graph Visualization ({self.n} nodes, {len(self.edges)} edges)", 
                    fontsize=12, fontweight='bold')
        ax.axis("off")
        
        if highlight_mst:
            ax.legend(loc="upper left", fontsize=10)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = MSTVisualizer(root)
    root.mainloop()