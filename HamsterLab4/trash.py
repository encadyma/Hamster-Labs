'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.
   Stater program of 3-state obstacle avoidance using FSM.

   Name:          starter_tk_3state_avoid.py
   By:            Qin Chen
   Last Updated:  6/10/18

   PROPRIETARY and CONFIDENTIAL
   ========================================================================*/
'''
import sys
import time
import threading
import Tkinter as tk
import Queue
from HamsterAPI.comm_ble import RobotComm	# no dongle
#from HamsterAPI.comm_usb import RobotComm	# yes dongle


class Event(object):
    def __init__(self, event_type, event_data):
        self.type = event_type #string
        self.data = event_data #list of number or character depending on type

##############################
# Finite state machine engine
##############################


class StateMachine(object):
    def __init__(self, name, eventQ_handle):
        self.name = name		# machine name
        self.states = []	# list of lists, [[state name, event, transition, next_state],...]
        self.start_state = None
        self.end_states = []	# list of name strings
        self.q = eventQ_handle
        return

    def set_start_state(self, state_name):
        self.start_state = state_name
        return

    def get_start_state(self):
        return self.start_state

    def add_end_state(self, state_name):
        self.end_states.append(state_name)
        return

    def add_state(self, state, event, callback, next_state):
        self.states.append([state, event, callback, next_state]) # append to list
        return

    # you must set start state before calling run()
    def run(self):
        current_state = self.start_state
        while True:
            if current_state in self.end_states:
                break
            if not self.q.empty():
                e = self.q.get()
                for c in self.states:
                    if c[0] == current_state and c[1] == e:
                        c[2]()  # invoke callback function
                        current_state = c[3] 	# next state
                        break   # get out of inner for-loop
        return


################################
# Hamster control
################################


class RobotBehavior(object):
    def __init__(self, robot_list):
        self.done = False   # set by GUI button
        self.go = False		# set by GUI button
        self.robot_list = robot_list
        self.robot = None
        self.q = Queue.Queue()  # event queue for FSM
        self.spawn_threads()
        self.sm = None
        self.maxGarbage = 3
        self.currentGarbage = 0
        self.watcher = None
        return

    def spawn_threads(self):
        ###########################################################
        # Two threads are created here.
        # 1. create a watcher thread that reads sensors and registers events: obstacle on left, right or no obstacle.
        # This thread runs the method event_watcher() you are going to implement below.
        # 2. Instantiate StateMachine and populate it with avoidance states, triggers, etc. Set start state.
        # 3. Create a thread to run FSM engine.
        ###########################################################

        self.watcher = threading.Thread(name='Watcher', target=self.event_watcher, args=(self.q,))
        self.watcher.daemon = True
        self.watcher.start()

        sm = StateMachine("Robot", self.q)

        sm.add_state('Discover', 'none', self.moving_forward, 'Discover')
        sm.add_state('Discover', 'obs_leveled', self.moving_forward, 'Discover')
        sm.add_state('Discover', 'obs_left', self.turning_right, 'GarbageAlignLeft')
        sm.add_state('Discover', 'obs_right', self.turning_left, 'GarbageAlignRight')
        sm.add_state('Discover', 'flag_border', self.backout, 'BorderBounceAway')
        sm.add_state('Discover', 'max_reached', self.stopping, 'Complete')

        sm.add_state('BorderBounceAway', 'none', self.moving_forward, 'Discover')
        sm.add_state('BorderBounceAway', 'flag_border', self.backout, 'BorderBounceAway')
        sm.add_state('BorderBounceAway', 'max_reached', self.stopping, 'Complete')

        sm.add_state('GarbageAlignLeft', 'none', self.moving_forward, 'Discover')
        sm.add_state('GarbageAlignLeft', 'obs_left', self.turning_right, 'GarbageAlignLeft')
        sm.add_state('GarbageAlignLeft', 'obs_right', self.turning_right, 'GarbageAlignLeft')
        sm.add_state('GarbageAlignLeft', 'obs_leveled', self.moving_forward, 'Carryout')
        sm.add_state('GarbageAlignLeft', 'flag_border', self.carryout_finish, 'Discover')
        sm.add_state('GarbageAlignLeft', 'max_reached', self.stopping, 'Complete')

        sm.add_state('GarbageAlignRight', 'none', self.moving_forward, 'Discover')
        sm.add_state('GarbageAlignRight', 'obs_left', self.turning_left, 'GarbageAlignRight')
        sm.add_state('GarbageAlignRight', 'obs_right', self.turning_left, 'GarbageAlignRight')
        sm.add_state('GarbageAlignRight', 'obs_leveled', self.moving_forward, 'Carryout')
        sm.add_state('GarbageAlignRight', 'flag_border', self.carryout_finish, 'Discover')
        sm.add_state('GarbageAlignRight', 'max_reached', self.stopping, 'Complete')

        sm.add_state('Carryout', 'none', self.moving_forward, 'Carryout')
        sm.add_state('Carryout', 'obs_left', self.moving_forward, 'Carryout')
        sm.add_state('Carryout', 'obs_right', self.moving_forward, 'Carryout')
        sm.add_state('Carryout', 'obs_leveled', self.moving_forward, 'Carryout')
        sm.add_state('Carryout', 'flag_border', self.carryout_finish, 'Discover')
        sm.add_state('Carryout', 'max_reached', self.stopping, 'Complete')

        sm.set_start_state('Discover')
        sm.add_end_state('Complete')

        self.sm = sm

        sm_thread = threading.Thread(name='State Machine', target=sm.run, args=())
        sm_thread.daemon = True
        sm_thread.start()

    def event_watcher(self, q):
        while not self.done:
            if self.robot_list and self.go:
                self.robot = self.robot_list[0]

                if self.currentGarbage >= self.maxGarbage:
                    print 'max number of trash reached'
                    q.put("max_reached")

                if self.robot.get_floor(0) < 20 and self.robot.get_floor(1) < 20:
                    print 'at the border'
                    q.put("flag_border")
                    time.sleep(1.4)

                elif self.robot.get_proximity(0) > 40 or self.robot.get_proximity(1) > 40:
                    if self.robot.get_proximity(0) > 50 and self.robot.get_proximity(1) > 50:
                        q.put('obs_leveled')
                    elif abs(self.robot.get_proximity(0) - self.robot.get_proximity(1)) < 5:
                        print 'leveled'
                        q.put('obs_leveled')
                    elif self.robot.get_proximity(0) > self.robot.get_proximity(1):
                        print 'left obs'
                        q.put("obs_left")
                    else:
                        print 'right obs'
                        q.put("obs_right")
                else:
                    print 'no obs'
                    q.put("none")

                time.sleep(0.01)
        return

    #######################################
    # Implement Hamster movements to avoid obstacle
    #######################################
    def turning_left(self):
        self.robot.set_wheel(0, 20)
        self.robot.set_wheel(1, -20)

    def turning_right(self):
        self.robot.set_wheel(0, -20)
        self.robot.set_wheel(1, 20)

    def moving_forward(self):
        self.robot.set_wheel(0, 80)
        self.robot.set_wheel(1, 80)

    def moving_backward(self):
        self.robot.set_wheel(0, -80)
        self.robot.set_wheel(1, -80)

    def backout(self):
        self.robot.set_wheel(0, -80)
        self.robot.set_wheel(1, -80)
        time.sleep(0.5)

        self.robot.set_wheel(0, -80)
        self.robot.set_wheel(1, 0)
        time.sleep(0.9)

    def carryout_finish(self):
        self.robot.set_wheel(0, -80)
        self.robot.set_wheel(1, -80)
        time.sleep(0.5)

        if self.robot.get_proximity(0) < 40 and self.robot.get_proximity(1) < 40:
            self.robot.set_musical_note(50)
            time.sleep(0.1)
            self.robot.set_musical_note(0)
            time.sleep(0.1)
            self.robot.set_musical_note(30)
            time.sleep(0.1)
            self.robot.set_musical_note(0)
            time.sleep(0.1)

        else:
            self.currentGarbage += 1

            for g in range(self.currentGarbage):
                self.robot.set_musical_note(60)
                time.sleep(0.1)
                self.robot.set_musical_note(0)
                time.sleep(0.1)

        self.backout()

    def stopping(self):
        self.robot.set_wheel(0, 0)
        self.robot.set_wheel(1, 0)

        self.robot.set_musical_note(40)
        time.sleep(0.1)
        self.robot.set_musical_note(0)
        time.sleep(0.1)
        self.robot.set_musical_note(40)
        time.sleep(0.1)
        self.robot.set_musical_note(0)


class GUI(object):
    def __init__(self, root, robot_control):
        self.root = root
        self.robot_control = robot_control

        canvas = tk.Canvas(root, bg="white", width=300, height=250)
        canvas.pack(expand=1, fill='both')
        canvas.create_rectangle(175, 175, 125, 125, fill="green")

        b1 = tk.Button(root, text='Go')
        b1.pack()
        b1.bind('<Button-1>', self.startProg)

        b2 = tk.Button(root, text='Exit')
        b2.pack()
        b2.bind('<Button-1>', self.stopProg)
        return

    def startProg(self, event=None):
        self.robot_control.go = True
        return

    def stopProg(self, event=None):
        self.robot_control.done = True
        self.root.quit() 	# close window
        return


def main():
    gMaxRobotNum = 1 # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'

    robot_list = comm.robotList
    behaviors = RobotBehavior(robot_list)

    frame = tk.Tk()
    GUI(frame, behaviors)
    frame.mainloop()

    comm.stop()
    comm.join()
    return


if __name__ == "__main__":
    sys.exit(main())