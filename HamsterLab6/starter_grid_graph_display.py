# Robot Programming
# breadth first search
# by Dr. Qin Chen
# May, 2016

import sys
import tkinter as tk
from starter_grid_graph import GridGraph
from starter_bfs import BFS

##############
# This class supports display of a grid graph. The node location on canvas
# is included as a data field of the graph, graph.node_display_locations.
##############

class GridGraphDisplay(object):
    def __init__(self, frame, graph):
        self.node_dist = 60
        self.node_size = 40
        self.gui_root = frame
        self.canvas = None
        self.graph = graph
        self.nodes_location = graph.node_display_locations
        self.start_node = graph.startNode
        self.goal_node = graph.goalNode

        self.setup_gui()
        return

    def setup_gui(self):
        self.gui_root.geometry('400x400')
        self.canvas = tk.Canvas(self.gui_root, width=400, height=400, bg='white')
        self.canvas.pack(expand=1, fill='both')
        return

    # draws nodes and edges in a graph
    def display_graph(self):
        self.canvas.delete("all")

        for node_name in self.graph.nodes:
            for conn in self.graph.nodes[node_name]:
                self.draw_edge(self.get_node_location(node_name), self.get_node_location(conn), 'black')
            self.draw_node(self.get_node_location(node_name), 'red')

    # path is a list of nodes ordered from start to goal node
    def highlight_path(self, path):
        for node_name in path:
            node = self.get_node_location(node_name)
            self.draw_node(node, 'green')

    def get_node_location(self, name):
        for node_loc in self.nodes_location:
            if node_loc[0] == name:
                return node_loc[0], node_loc[1] * self.node_dist, node_loc[2] * self.node_dist

        return 'None', 0, 0

    # draws a node in given color. The node location info is in passed-in node object
    def draw_node(self, node_e, n_color):
        self.canvas.create_oval(node_e[1], node_e[2], node_e[1] + self.node_size, node_e[2] + self.node_size, fill=n_color)
        self.canvas.create_text(node_e[1] + (self.node_size / 2), node_e[2] + (self.node_size / 2), text=node_e[0])

    # draws an line segment, between two given nodes, in given color
    def draw_edge(self, node1_e, node2_e, e_color):
        self.canvas.create_line(node1_e[1] + (self.node_size / 2), node1_e[2] + (self.node_size / 2), node2_e[1] + (self.node_size / 2), node2_e[2] + (self.node_size / 2), fill=e_color)

def main():
    frame = tk.Tk()
    graph = GridGraph()

    # grid dimension
    graph.set_grid_rows(4)
    graph.set_grid_cols(3)

    # origin of grid is (0, 0) lower left corner
    # graph.obs_list = ([1,1],)    # in case of one obs. COMMA
    graph.obs_list = ([3, 0], [2, 2])

    graph.set_start('0-0')
    graph.set_goal('2-1')

    graph.make_grid()
    graph.connect_nodes()
    graph.compute_node_locations()

    bfs = BFS(graph.nodes)
    shortest = bfs.bfs_shortest_path('0-0', '3-2')

    print(shortest)

    program = GridGraphDisplay(frame, graph)
    program.display_graph()

    program.highlight_path(shortest[0])

    program.gui_root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
