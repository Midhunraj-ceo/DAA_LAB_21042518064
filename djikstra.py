import customtkinter as ctk
import heapq
from tkinter import messagebox

# ---------------- Dijkstra Algorithm ---------------- #

def dijkstra(graph, source):
    n = len(graph)

    dist = [float('inf')] * n
    prev = [None] * n

    dist[source] = 0

    pq = [(0, source)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)

        if u in visited:
            continue

        visited.add(u)

        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))

    return dist, prev


def reconstruct_path(prev, source, target):
    path = []

    node = target

    while node is not None:
        path.append(node)
        node = prev[node]

    path.reverse()

    if path and path[0] == source:
        return path

    return []


# ---------------- GUI Functions ---------------- #

def parse_graph(text):
    graph = {}

    lines = text.strip().split("\n")

    for line in lines:
        if not line.strip():
            continue

        parts = line.split(":")
        node = int(parts[0].strip())

        neighbors = []

        if len(parts) > 1 and parts[1].strip():
            edges = parts[1].split(",")

            for edge in edges:
                edge = edge.strip()

                if edge:
                    v, w = edge.split()
                    neighbors.append((int(v), int(w)))

        graph[node] = neighbors

    return graph


def run_dijkstra():
    try:
        graph_text = graph_box.get("1.0", "end")
        graph = parse_graph(graph_text)

        source = int(source_entry.get())

        dist, prev = dijkstra(graph, source)

        output_box.delete("1.0", "end")

        output_box.insert(
            "end",
            f"{'Vertex':<10}{'Distance':<12}{'Path'}\n"
        )

        output_box.insert("end", "-" * 50 + "\n")

        for v in range(len(graph)):
            path = reconstruct_path(prev, source, v)

            path_str = " -> ".join(map(str, path))
            d = dist[v] if dist[v] != float('inf') else "INF"

            output_box.insert(
                "end",
                f"{v:<10}{str(d):<12}{path_str}\n"
            )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ---------------- GUI ---------------- #

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Dijkstra Algorithm Visualizer")
app.geometry("900x650")

title = ctk.CTkLabel(
    app,
    text="Dijkstra Shortest Path Visualizer",
    font=("Arial", 24, "bold")
)
title.pack(pady=15)

instructions = ctk.CTkLabel(
    app,
    text=(
        "Format:\n"
        "0: 1 4, 2 1\n"
        "1: 3 1\n"
        "2: 1 2, 3 5\n"
        "3: 4 3\n"
        "4: 5 2\n"
        "5:"
    ),
    justify="left"
)
instructions.pack()

graph_box = ctk.CTkTextbox(app, width=700, height=180)
graph_box.pack(pady=10)

default_graph = """0: 1 4, 2 1
1: 3 1
2: 1 2, 3 5
3: 4 3
4: 5 2
5:"""

graph_box.insert("1.0", default_graph)

source_frame = ctk.CTkFrame(app)
source_frame.pack(pady=10)

ctk.CTkLabel(
    source_frame,
    text="Source Vertex:"
).pack(side="left", padx=10)

source_entry = ctk.CTkEntry(source_frame, width=100)
source_entry.pack(side="left", padx=10)
source_entry.insert(0, "0")

run_btn = ctk.CTkButton(
    app,
    text="Run Dijkstra",
    command=run_dijkstra
)
run_btn.pack(pady=10)

output_box = ctk.CTkTextbox(app, width=800, height=220)
output_box.pack(pady=10)

app.mainloop()