###################################################################
# THIS VERSION doesn't support 'go' button as in Version3. 
# COLLISION CHECKING for simulated robot is implemented this time.
# by Qin Chen, 5/29/2018
###################################################################
import Tkinter as tk
import sys
import time
import math
import threading
from HamsterAPI.comm_ble import RobotComm
from tk_hamster_simulation_starter import *

gRobotList = []

class GUIpart(object):    
    def __init__(self, gui_root, vWorld):
        self.gui_root = gui_root
        self.vWorld = vWorld

        # instance variables
        self.button4=None
        self.button5=None
        self.button6=None
        self.button8=None
        self.button11=None
        self.rCanvas = None
        self.initUI()

    def initUI(self):
        self.gui_root.title("Hamster Simulator")
        canvas_width = 440 # half width
        canvas_height = 300 # half height
        vRobot = self.vWorld.vrobot
        #creating tje virtual appearance of the robot
        
        self.rCanvas = tk.Canvas(self.gui_root, bg="white", width=canvas_width*2, height=canvas_height*2)
        self.rCanvas.pack()
        self.vWorld.canvas = self.rCanvas
        self.vWorld.canvas_width = canvas_width
        self.vWorld.canvas_height = canvas_height

        # visual elements of the virtual robot 
        poly_points = [0,0,0,0,0,0,0,0]
        vRobot.poly_id = self.rCanvas.create_polygon(poly_points, fill='blue') #robot
        vRobot.prox_l_id = self.rCanvas.create_line(0,0,0,0, fill="red") #prox sensors
        vRobot.prox_r_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        vRobot.floor_l_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white") #floor sensors
        vRobot.floor_r_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        #time.sleep(1)

        button0 = tk.Button(self.gui_root,text="Grid")
        button0.pack(side='left')
        button0.bind('<Button-1>', self.drawGrid)

        button1 = tk.Button(self.gui_root,text="Clear")
        button1.pack(side='left')
        button1.bind('<Button-1>', self.clearCanvas)

        button2 = tk.Button(self.gui_root,text="Reset")
        button2.pack(side='left')
        button2.bind('<Button-1>', self.resetvRobot)

        button3 = tk.Button(self.gui_root,text="Map")
        button3.pack(side='left')
        button3.bind('<Button-1>', self.drawMap)

        self.button4 = tk.Button(self.gui_root,text="Trace")
        self.button4.pack(side='left')
        self.button4.bind('<Button-1>', self.toggleTrace)

        self.button5 = tk.Button(self.gui_root,text="Prox Dots")
        self.button5.pack(side='left')
        self.button5.bind('<Button-1>', self.toggleProx)

        self.button6 = tk.Button(self.gui_root,text="Floor Dots")
        self.button6.pack(side='left')
        self.button6.bind('<Button-1>', self.toggleFloor)

        self.button11 = tk.Button(self.gui_root,text="Real Robot")
        self.button11.pack(side='left')
        self.button11.bind('<Button-1>', self.toggleRobot)

        button9 = tk.Button(self.gui_root,text="Exit")
        button9.pack(side='left')
        button9.bind('<Button-1>', self.exit_prog)

        self.gui_root.bind("<KeyPress>", self.keydown)
        self.gui_root.bind("<KeyRelease>", self.keyup)

        return

    def keydown(self, event):
        if event.char == 'w':
            self.move_up()
        elif event.char == 's':
            self.move_down()
        elif event.char == 'a':
            self.move_left()
        elif event.char == 'd':
            self.move_right()
        return

    def keyup(self, event):
        if event.char == 'w' or event.char == 's' or event.char == 'a' or event.char == 'd':
            self.stop_move()
        return

    def drawGrid(self, event=None):
        print "draw Grid"
        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        x1 = 0
        x2 = canvas_width*2
        y1 = 0
        y2 = canvas_height*2
        del_x = 20
        del_y = 20
        num_x = x2 / del_x
        num_y = y2 / del_y
        # draw center (0,0)
        self.rCanvas.create_rectangle(canvas_width-3,canvas_height-3,canvas_width+3,canvas_height+3, fill="red")
        # horizontal grid
        for i in range (0,num_y):
            y = i * del_y
            self.rCanvas.create_line(x1, y, x2, y, fill="yellow")
        # verticle grid
        for j in range (0, num_x):
            x = j * del_x
            self.rCanvas.create_line(x, y1, x, y2, fill="yellow")
        return

    def drawMap(self, event=None):
        self.vWorld.draw_map()
        return

    def resetvRobot(self, event=None):
        #vRobot.reset_robot()
        self.vWorld.vrobot.x = 200
        self.vWorld.vrobot.y = 0
        self.vWorld.vrobot.a = -1.571
        self.vWorld.goal_achieved = True
        self.vWorld.goal_list_index = 0
        return

    def clearCanvas(self, event=None):
        self.rCanvas.delete("all")
        poly_points = [0,0,0,0,0,0,0,0]
        self.vWorld.vrobot.poly_id = self.rCanvas.create_polygon(poly_points, fill='blue')
        self.vWorld.vrobot.prox_l_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        self.vWorld.vrobot.prox_r_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        self.vWorld.vrobot.floor_l_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        self.vWorld.vrobot.floor_r_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        return

    def toggleTrace(self, event=None):
        if self.vWorld.trace == True:
            self.vWorld.trace = False
            self.button4["text"] = "Trace"
        else:
            self.vWorld.trace = True
            self.button4["text"] = "No Trace"
        return

    def toggleProx(self, event=None):
        if self.vWorld.prox_dots == True:
            self.vWorld.prox_dots = False
            self.button5["text"] = "Prox Dots"
        else:
            self.vWorld.prox_dots = True
            self.button5["text"] = "No Prox Dots"
        return

    def toggleFloor(self, event=None):
        if self.vWorld.floor_dots == True:
            self.vWorld.floor_dots = False
            self.button6["text"] = "Floor Dots"
        else:
            self.vWorld.floor_dots = True
            self.button6["text"] = "No Floor Dots"
        return

    def toggleRobot(self, event=None):
        if self.vWorld.real_robot:
            robot = self.vWorld.real_robot
            robot.set_wheel(0,0)
            robot.set_wheel(1,0)
            self.vWorld.real_robot = False
            print "simulated robot"
            self.button11["text"] = "Real Robot"
        else:
            if (len(gRobotList) > 0):
                self.vWorld.real_robot = gRobotList[0]
                robot = self.vWorld.real_robot
                robot.set_wheel(0, self.vWorld.vrobot.sl)
                robot.set_wheel(1, self.vWorld.vrobot.sr) 
                self.button11["text"] = "Simulation"
                print "connected to robot", self.vWorld.real_robot
            else:
                print "please turn on robot"
        return

    def toggleGo(self, event=None):
        if self.vWorld.go:
            self.vWorld.go = False
            print "Pause"
            self.button8["text"] = "Go"
        else:
            self.vWorld.go = True
            print "Go"
            self.button8["text"] = "Pause"
        return

    def getGoal(self, event):
        self.vWorld.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, outline = "blue")
        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        self.vWorld.goal_x = event.x - canvas_width
        self.vWorld.goal_y = canvas_height - event.y 
        print "selected goal: ", self.vWorld.goal_x, self.vWorld.goal_y
        return

    def move_up(self, event=None):
        self.vWorld.vrobot.sl = 30
        self.vWorld.vrobot.sr = 30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_down(self, event=None):
        self.vWorld.vrobot.sl = -30
        self.vWorld.vrobot.sr = -30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_left(self, event=None):
        self.vWorld.vrobot.sl = 10
        self.vWorld.vrobot.sr = 30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_right(self, event=None):
        self.vWorld.vrobot.sl = 30
        self.vWorld.vrobot.sr = 10
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def stop_move(self, event=None):
        self.vWorld.vrobot.sl = 0
        self.vWorld.vrobot.sr = 0
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def exit_prog(self, event=None):
        self.vWorld.gQuit = True
        self.gui_root.quit()
        for robot in gRobotList:
            robot.reset()
        return

    def draw_virtual_world(self):       
        self.vWorld.draw_robot()
        self.vWorld.draw_prox("left")
        self.vWorld.draw_prox("right")
        self.vWorld.draw_floor("left")
        self.vWorld.draw_floor("right")
        self.gui_root.after(50, self.draw_virtual_world)
        return
        return

class VirtualHamsterWorld(object):
    def __init__(self):
        self.vrobot = None
        self.vworld = None
        self.gQuit = False
        self.create_world()

    def create_world(self):       
        self.vrobot = virtual_robot()
        self.vrobot.t = time.time()

        #create the virtual worlds that contains the virtual robot
        self.vworld = virtual_world()
        self.vworld.vrobot = self.vrobot
        
        #objects in the world
        self.vworld.map = []

        # take out map to test real robot
        # local obstacle avoidance using APF
        rect1 = [-100, -180, 0, -140]
        rect2 = [-140, -180, -100, -80]
        rect3 = [-100, 140, 0, 180]
        rect4 = [-140, 80, -100, 180]
        rect5 = [0, -50, 40, 50]
        rect6 = [-260, -20, -220, 20]
        rect7 = [40, 60, 140, 100]

        self.vworld.area = [-300,-200,300,200]

        self.vworld.add_obstacle(rect1)
        self.vworld.add_obstacle(rect2)
        self.vworld.add_obstacle(rect3)
        self.vworld.add_obstacle(rect4)
        self.vworld.add_obstacle(rect5)
        self.vworld.add_obstacle(rect6)
        self.vworld.add_obstacle(rect7)

        # set initial pose of robot wrt robot coordinate system
        self.vworld.vrobot.x = 200  # 200 pixels to the right from center(origin of robot coor. syst.)
        self.vworld.vrobot.y = 0
        self.vworld.vrobot.a = 1.5*3.1415    # facing west
    
        return

    # Update data components of the simulator.
    def update_virtual_world(self):
        waiting_for_robot = True

        while waiting_for_robot and self.vworld.real_robot:
            if len(gRobotList) > 0:
                robot = gRobotList[0] 
                waiting_for_robot = False
                print "connected to robot"
            else:
                print "waiting for robot to connect"
            time.sleep(0.1)

        noise_prox = 35 # noise level for proximity
        noise_floor = 20 #floor ambient color - if floor is darker, set higher noise
        p_factor = 1.3 #proximity conversion - assuming linear
        #prox_conv_l = [0, 0, 0, 60, 50, 40, 30, 20, 20]
        prox_conv_l = [85,85,82,75,67,59,51,47,40,35]
        prox_conv_r = [85,85,82,75,67,59,51,47,40,35]

        #################################
        # Find the value of distance factor for your Hamster

        d_factor = 1.055  # travel distance conversion
        #################################

        # wa_factor = 17.5 #turning speed of -15 vs angle
        b = 30 #distance in mm, between two wheels

        vrobot = self.vworld.vrobot

        while not self.gQuit:
            t = time.time()
            del_t = t - vrobot.t
            vrobot.t = t # update the tick

            # compute new pose
            ms = (vrobot.sl*del_t+vrobot.sr*del_t)/2 #speed of the center
            new_vrobot_a = vrobot.a + (vrobot.sl-vrobot.sr)*del_t/b
            new_vrobot_x = vrobot.x + ms * math.sin(vrobot.a) * d_factor
            new_vrobot_y = vrobot.y + ms * math.cos(vrobot.a) * d_factor

            ##########################
            # If in collision, Hamster should stop moving, which means no update
            # of its pose.
            ##########################
            if not self.vworld.in_collision(new_vrobot_a, new_vrobot_x, new_vrobot_y):
                vrobot.a = new_vrobot_a
                vrobot.x = new_vrobot_x
                vrobot.y = new_vrobot_y

            while (vrobot.a >= 3.1415):
                vrobot.a -= 6.283

            # update sensors
            if (self.vworld.real_robot):    # convert prox sensor readings to number of pixels for the red beams
                robot = self.vworld.real_robot
                prox_l = robot.get_proximity(0)
                prox_r = robot.get_proximity(1)

                if (prox_l > noise_prox):
                    i = 0
                    while (prox_conv_l[i] > prox_l) and (i < 9):
                        i += 1
                    if (vrobot.dist_l and vrobot.sl == 0 and vrobot.sr == 0):
                        vrobot.dist_l = vrobot.dist_l*2.0 + i*10 + 10 - (prox_l - prox_conv_l[i])*10/(prox_conv_l[i-1] - prox_conv_l[i])
                        vrobot.dist_l = vrobot.dist_l / 3.0
                    else:
                        vrobot.dist_l = i*10 + 10 - (prox_l - prox_conv_l[i])*10/(prox_conv_l[i-1] - prox_conv_l[i])
                else:
                    vrobot.dist_l = False

                if (prox_r > noise_prox):
                    i = 0
                    while (prox_conv_r[i] > prox_r) and (i < 9):
                        i += 1
                    if (vrobot.dist_r and vrobot.sl == 0 and vrobot.sr == 0):
                        vrobot.dist_r = vrobot.dist_r*2.0 +i*10 + 10 - (prox_r - prox_conv_r[i])*10/(prox_conv_r[i-1] - prox_conv_r[i])
                        vrobot.dist_r = vrobot.dist_r / 3.0
                    else:
                        vrobot.dist_r = i*10 + 10 - (prox_r - prox_conv_r[i])*10/(prox_conv_r[i-1] - prox_conv_r[i])
                else:
                    vrobot.dist_r = False
            else:               # simulate prox sensors
                self.vworld.get_vrobot_prox("left")
                self.vworld.get_vrobot_prox("right")

            if (self.vworld.real_robot):
                floor_l = robot.get_floor(0)
                floor_r = robot.get_floor(1)
            else:
                floor_l = 100 #white
                floor_r = 100
            if (floor_l < noise_floor):
                vrobot.floor_l = floor_l
            else:
                vrobot.floor_l = False

            if (floor_r < noise_floor):
                vrobot.floor_r = floor_r
            else:
                vrobot.floor_r = False

            time.sleep(0.05)
        return

def main():
    global gRobotList

    gMaxRobotNum = 1 # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'
    gRobotList = comm.robotList
    
    root = tk.Tk() #root

    world_handle = VirtualHamsterWorld()
    t_update_world = threading.Thread(name='update_world', target=world_handle.update_virtual_world)
    t_update_world.daemon = True
    t_update_world.start()

    gui_handle = GUIpart(root, world_handle.vworld)
    gui_handle.draw_virtual_world()     # this method runs in main thread

    root.mainloop()

    comm.stop()
    comm.join()

if __name__== "__main__":
    sys.exit(main())