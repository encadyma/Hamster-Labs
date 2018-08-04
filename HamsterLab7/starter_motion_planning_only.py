'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.

   PROPRIETARY and CONFIDENTIAL

   Creqted by Dr. Qin Chen
   7/2017
   ========================================================================*/
'''

import sys
sys.path.append('../')
import Tkinter as tk
from graph_with_edge_cost import *
from tk_hamster_GUI_Sim import *

class MotionPlanner(object):
    def __init__(self, vWorld, start, goal):
        self.vWorld = vWorld
        self.start = start
        self.goal = goal
        return

    def worker(self):
        print('MotionPlanner is called')
        vWorld = self.vWorld
        start = self.start
        goal = self.goal
        canvas_width = vWorld.canvas_width
        canvas_height = vWorld.canvas_height
        cell_list = Queue.Queue()
        cell_list.put(vWorld.area)
        # inflate obstacles to form C-space
        self.compute_c_obstacles(vWorld, 28)
        obs_list = vWorld.cobs
        vWorld.goal_list = []
        f_cell_list = []

        # Cut inflated obstacles out of C-space and divide workspace into cells from cutting 
        f_cell_list = self.compute_free_cells(cell_list, obs_list)
        # determine connectivity between free cells and locate the point to go from one cell to its neighbor
        point_list = self.compute_free_points(f_cell_list)

        raw_input('press RETURN to show free cells')
        for cell in f_cell_list:
            x1 = cell[0]
            y1 = cell[1]
            x2 = cell[2]
            y2 = cell[3]
            vWorld.canvas.create_rectangle(canvas_width+x1, canvas_height-y1, canvas_width+x2, canvas_height-y2, outline = "orange")

        raw_input('press RETURN to show start and goal')
        # create graph - nodes and edges for the point list
        myGraph = Graph()
        num_points = len(point_list)

        # creating nodes
        myGraph.add_node("s", start)
        myGraph.set_start("s")
        myGraph.add_node("g", goal)
        myGraph.set_goal("g")
        xs = start[0]
        ys = start[1]
        vWorld.canvas.create_oval(canvas_width+xs-6, canvas_height-ys-6, canvas_width+xs+6, canvas_height-ys+6, outline = "green", fill="green")
        xg = goal[0]
        yg = goal[1]
        vWorld.canvas.create_oval(canvas_width+xg-6, canvas_height-yg-6, canvas_width+xg+6, canvas_height-yg+6, outline = "purple", fill="purple")

        raw_input('press RETURN to show points connecting free cells, start, and goal')
        point_num = 1
        for point in point_list:
            myGraph.add_node(str(point_num), point)
            x1 = point[0]
            y1 = point[1]
            vWorld.canvas.create_oval(canvas_width+x1-4, canvas_height-y1-4, canvas_width+x1+4, canvas_height-y1+4, outline = "red")
            if self.connected(point, start, f_cell_list):
                g_cost = math.sqrt((xs-x1)*(xs-x1)+(ys-y1)*(ys-y1))
                # print "creating edge: ", "s", str(point_num), g_cost
                myGraph.add_edge("s", str(point_num), g_cost)
                vWorld.canvas.create_line(canvas_width+x1, canvas_height-y1, canvas_width+xs, canvas_height-ys, fill="black")
            if self.connected(point, goal, f_cell_list):
                g_cost = math.sqrt((xg-x1)*(xg-x1)+(yg-y1)*(yg-y1))
                # print "creating edge: ", "g", str(point_num), g_cost
                myGraph.add_edge("g", str(point_num), g_cost)
                vWorld.canvas.create_line(canvas_width+x1, canvas_height-y1, canvas_width+xg, canvas_height-yg, fill="black")
            point_num += 1

        raw_input("press RETURN to show connectivity")
        if num_points > 1:
            # creating edges
            # print "num points: ", num_points
            next_point = 2
            for i in range (1, num_points+1):
                # print "from: ", i
                point1 = point_list[i-1]
                x1 = point1[0]
                y1 = point1[1]
                for j in range (next_point, num_points+1):
                    # print "to: ", j
                    point2 = point_list[j-1]
                    x2 = point2[0]
                    y2 = point2[1]
                    if (self.connected(point1, point2, f_cell_list)):
                        g_cost = math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
                        # print "creating edge: ", str(i), str(j), g_cost
                        myGraph.add_edge(str(i), str(j), g_cost)
                        vWorld.canvas.create_line(canvas_width+x1, canvas_height-y1, canvas_width+x2, canvas_height-y2)
                next_point += 1

        raw_input('press RETURN to show path')
        # print "search: ", myGraph.queue
        myGraph.Dijkstra()
        path = Queue.LifoQueue()
        if myGraph.nodes["g"].back_pointer:
            path.put(["pose", myGraph.nodes["g"].data[0], myGraph.nodes["g"].data[1], False])
            print("Found path")
            path_node = myGraph.nodes["g"].back_pointer
            while path_node.back_pointer != False:
                px = path_node.data[0]
                py = path_node.data[1]
                path.put(["pose", px, py, False])
                vWorld.canvas.create_oval(canvas_width+px-6, canvas_height-py-6, canvas_width+px+6, canvas_height-py+6, outline = "red", fill="red")
                path_node = path_node.back_pointer
            while not path.empty():
                vWorld.goal_list.append(path.get())
                vWorld.goal_list_index = 0
            print("path: ", vWorld.goal_list)
        else:
            print("failed to find path")
        return

    def compute_c_obstacles(self, vworld, d):
        # save c-space obstacle location info in vWorld.cobs[]
        for obs in vworld.map:
            vworld.cobs.append([obs[0] - d, obs[1] - d, obs[2] + d, obs[3] + d])

    def compute_free_cells(self, cell_list, c_obs_list):
        # get all important points
        points = {}
        f_cell_list = []

        for obs in c_obs_list:
            # [x1, y1, x2, y2]
            # [0 , 1 , 2 , 3]

            # point1: [0, 1]
            # point2: [0, 3]
            # point3: [2, 1]
            # point4: [2, 3]

            if obs[0] not in points:
                points[obs[0]] = []
            points[obs[0]].append((obs[1], obs[3]))

            if obs[2] not in points:
                points[obs[2]] = []
            points[obs[2]].append((obs[1], obs[3]))

        for x in points:


        return f_cell_list

    def two_cells_connected(self, cell1, cell2):
        # Given two free cells, cell1 and cell2.
        # return connecting point[x,y] if two cells are connected
        # return False if not connected

        # We'll term the shortest cell "master" and the other one a "slave".
        # Talked about in terms of cell1

        master = False

        xdist_c1 = abs(cell1[0] - cell1[2])
        xdist_c2 = abs(cell2[0] - cell2[2])

        ydist_c1 = abs(cell1[1] - cell1[3])
        ydist_c2 = abs(cell2[1] - cell2[3])

        if cell1[0] == cell2[2]:      # to the left
            master = [cell1[0], cell1[1] + (ydist_c1 / 2) if ydist_c1 < ydist_c2 else cell2[1] + (ydist_c2 / 2)]
        elif cell1[1] == cell2[3]:    # to the top
            master = [cell1[0] + (xdist_c1 / 2) if xdist_c1 < xdist_c2 else cell2[0] + (xdist_c2 / 2), cell1[1]]
        elif cell1[2] == cell2[0]:    # to the right
            master = [cell1[2], cell1[1] + (ydist_c1 / 2) if ydist_c1 < ydist_c2 else cell2[1] + (ydist_c2 / 2)]
        elif cell1[3] == cell2[1]:    # to the bottom
            master = [cell1[0] + (xdist_c1 / 2) if xdist_c1 < xdist_c2 else cell2[0] + (xdist_c2 / 2), cell1[3]]

        return master


    def compute_free_points(self, f_cell_list):
        # Obstacle free cells are given in f_cell_list
        # This function returns a list of points, each point is on overlapping edge of two conncted obstacle free cells.
        f_cell_points = []
        for cell1 in f_cell_list:
            for cell2 in f_cell_list:
                if cell1 != cell2:
                    connected = self.two_cells_connected(cell1, cell2)
                    if connected:
                        f_cell_points.append(self.two_cells_connected(cell1, cell2))

        return f_cell_points

    def connected(self, point1, point2, cell_list):
        # given two points in c-space and list of free cells.
        # return True if point1 and point2 are connected by a free cell
        # otherwise return False
        x_range = sorted([point1[0], point2[0]])
        y_range = sorted([point1[1], point2[1]])

        for cell in cell_list:
            if [cell[0], cell[2]] == x_range and [cell[1], cell[3]] == y_range:
                return True

        return False
        
class GUI(object):
    def __init__(self, gui_root, vWorld, endCommand):
        self.gui_root = gui_root
        gui_root.title("Motion Planner")
        self.endCommand = endCommand
        self.vWorld = vWorld
        self.start = [200, 0] # robot's start location, goal location is user defined
        self.initUI()
        return

    def initUI(self):
        #creating tje virtual appearance of the robot
        canvas_width = 440 # half width
        canvas_height = 300 # half height
        self.vWorld.canvas_width = canvas_width
        self.vWorld.canvas_height = canvas_height
        rCanvas  = tk.Canvas(self.gui_root, bg="light gray", width=canvas_width*2, height= canvas_height*2)
        self.vWorld.canvas = rCanvas
        rCanvas.pack()

        button0 = tk.Button(self.gui_root,text="Grid")
        button0.pack(side='left')
        button0.bind('<Button-1>', self.drawGrid)

        button1 = tk.Button(self.gui_root,text="Clear")
        button1.pack(side='left')
        button1.bind('<Button-1>', self.clearCanvas)

        button2 = tk.Button(self.gui_root,text="Map")
        button2.pack(side='left')
        button2.bind('<Button-1>', self.drawMap)

        button9 = tk.Button(self.gui_root,text="Exit")
        button9.pack(side='left')
        button9.bind('<Button-1>', self.endCommand)

        rCanvas.bind("<Button-1>", self.getGoal)
        return

    def drawGrid(self, event=None):
        print("draw Grid")
        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        rCanvas = self.vWorld.canvas
        x1 = 0
        x2 = canvas_width*2
        y1 = 0
        y2 = canvas_height*2
        del_x = 20
        del_y = 20
        num_x = x2 / del_x
        num_y = y2 / del_y
        # draw center (0,0)
        rCanvas.create_rectangle(canvas_width-3,canvas_height-3,canvas_width+3,canvas_height+3, fill="red")
        # horizontal grid
        for i in range (0, num_y):
            y = i * del_y
            rCanvas.create_line(x1, y, x2, y, fill="yellow")
        # verticle grid
        for j in range (0, num_x):
            x = j * del_x
            rCanvas.create_line(x, y1, x, y2, fill="yellow")
        return

    def drawMap(self, event=None):
        self.vWorld.draw_map()

    def clearCanvas(self, event=None):
        rCanvas = self.vWorld.canvas
        rCanvas.delete("all")
        return

    def getGoal(self, event):
        self.vWorld.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, outline = "blue")

        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        self.vWorld.goal_x = event.x - canvas_width
        self.vWorld.goal_y = canvas_height - event.y 
        print("selected goal: ",self.vWorld.goal_x, self.vWorld.goal_y)
        s_point = self.start
        g_point = [self.vWorld.goal_x, self.vWorld.goal_y]
        print('start pose(%s, %s): ' % (s_point[0], s_point[1]))
        print('goal pose(%s, %s): ' % (g_point[0], g_point[1]))
        mp = MotionPlanner(self.vWorld, s_point, g_point)
        mp.worker()
        return

class VirtualWorld(object):
    def __init__(self, gui_root):
        self.gui_root = gui_root
        self.gui_handle = None
        self.vWorld = None
        self.create_world()
        return

    def create_world(self):
        self.vWorld = virtual_world()      
        #objects in the world
        self.vWorld.map = []

        #project 3-1
        #rect1 = [-50, 80, 50, 120]
        #rect2 = [100, -50, 140, 50]
        #rect3 = [-160, -50, -120, 50]
        #rect4 = [-50,-180, 50, -140]

        #project 3-2
        #rect1 = [-20, 80, 20, 120]
        #rect2 = [100, -20, 140, 20]
        #rect3 = [-20, -120, 20, -80]
        #rect4 = [-260,-30, -220, 30]
        #rect5 = [-220, -70, -180, -30]
        #rect6 = [-220, 30, -180, 70]

        #bounder of board
        rect1 = [-100, -180, 0, -140]
        rect2 = [-140, -180, -100, -80]
        rect3 = [-100, 140, 0, 180]
        rect4 = [-140, 80, -100, 180]
        rect5 = [0, -50, 40, 50]
        rect6 = [-260, -20, -220, 20]
        rect7 = [40, 60, 140, 100]

        # robot's work space boundary
        self.vWorld.area = [-300,-200,300,200]

        self.vWorld.add_obstacle(rect1)
        self.vWorld.add_obstacle(rect2)
        self.vWorld.add_obstacle(rect3)
        self.vWorld.add_obstacle(rect4)
        self.vWorld.add_obstacle(rect5)
        self.vWorld.add_obstacle(rect6)
        self.vWorld.add_obstacle(rect7)

        self.gui_handle = GUI(self.gui_root, self.vWorld, self.stopProg)
        return

    def stopProg(self, event=None):
        self.gui_root.quit()
        return

def main():
    m = tk.Tk() #root
    v_world = VirtualWorld(m)
    m.mainloop()
    return

if __name__== "__main__":
    sys.exit(main())
