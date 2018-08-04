'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.

   Name:          grid_graph_starter.py
   By:            Qin Chen
   Last Updated:  6/10/18
    
   Definition of class GridGraph. Description of all the methods is
   provided. Students are expected to implement the methods for Lab#6.
   ========================================================================*/
'''
import tkinter as tk

class GridGraph(object):
    def __init__(self):
        self.nodes = {} # {node_name: set(neighboring nodes), ...}
        self.startNode = None  # string
        self.goalNode = None    # string
        self.grid_rows = None
        self.grid_columns = None
        self.obs_list = []
        self.node_display_locations = []
        return

    # set number of rows in the grid
    def set_grid_rows(self, rows):
        self.grid_rows = rows

    # set number of columns in the grid
    def set_grid_cols(self, cols):
        self.grid_columns = cols

    # this method is used by make_grid() to create a key-value pair in self.nodes{},
    # where value is created as an empty set which is populated later while connecting
    # nodes.

    def add_node(self, name):
        print('===> created node', name)
        self.nodes[name] = set()

    # set start node name
    def set_start(self, name):
        self.startNode = name

    # returns start node name
    def get_start_node(self):
        return self.startNode

    # set goal node name
    def set_goal(self, name):
        self.goalNode = name

    # return goal node name
    def get_goal_node(self):
        return self.goalNode

    # Given two neighboring nodes. Put them to each other's neighbors-set. This
    # method is called by self.connect_nodes() 
    def add_neighbor(self, node1, node2):
        if not node1 in self.nodes or not node2 in self.nodes:
            # print('\/\/\/\/\/\/ error completing the following operation: out of bound...')
            return

        self.nodes[node1].add(node2)
        self.nodes[node2].add(node1)

    # populate graph with all the nodes in the graph, excluding obstacle nodes
    def make_grid(self):
        for row in range(self.grid_rows):
            for column in range(self.grid_columns):
                if [row, column] in self.obs_list:
                    continue
                self.add_node(str(row) + '-' + str(column))

    # Based on node's name, this method identifies its neighbors and fills the 
    # set holding neighbors for every node in the graph.
    def connect_nodes(self):
        visited = set()
        q = [self.startNode]

        while q:
            node = q.pop(0)
            coords = node.split('-')

            if node in visited:
                continue

            if int(coords[0]) < self.grid_rows - 1:
                self.add_neighbor(node, str(int(coords[0]) + 1) + '-' + coords[1])
                q.append(str(int(coords[0]) + 1) + '-' + coords[1])
                # print('connecting', node, 'to', str(int(coords[0]) + 1) + '-' + coords[1])

            if int(coords[1]) < self.grid_columns - 1:
                self.add_neighbor(node, coords[0] + '-' + str(int(coords[1]) + 1))
                q.append(coords[0] + '-' + str(int(coords[1]) + 1))
                # print('connecting', node, 'to', coords[0] + '-' + str(int(coords[1]) + 1))

            visited.add(node)

    # For display purpose, this function computes grid node location(i.e., offset from upper left corner where is (1,1)) 
    # of display area. based on node names.
    # Node '0-0' is displayed at bottom left corner 
    def compute_node_locations(self):
        self.node_display_locations = []
        for node in self.nodes:
            coords = node.split('-')
            r = int(coords[0])
            c = int(coords[1])

            self.node_display_locations.append((node, c + 1, self.grid_rows - r))

        return

###########################################################
#  A testing program of your implementaion of GridGraph class.
###########################################################
def main():
    graph = GridGraph()
    # grid dimension
    graph.set_grid_rows(4)
    graph.set_grid_cols(3)

    # origin of grid is (0, 0) lower left corner
    # graph.obs_list = ([1,1],)    # in case of one obs. COMMA
    graph.obs_list = ([1, 1], [3, 0], [2, 2])
    
    graph.set_start('0-0')
    graph.set_goal('2-1')
    
    graph.make_grid()
    graph.connect_nodes()

    return

if __name__ == "__main__":
    main()