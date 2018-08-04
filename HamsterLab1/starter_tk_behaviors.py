'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.
   This is a program that is provided to students in Robot AI class.
   Students use this it to build different Hamster behaviors.

   Name:          tk_behaviors_starter.py
   By:            Qin Chen
   Last Updated:  5/10/18

   PROPRIETARY and CONFIDENTIAL
   ========================================================================*/
'''
import sys
import time
import threading
import Tkinter as tk
from HamsterAPI.comm_ble import RobotComm	# no dongle
#from HamsterAPI.comm_usb import RobotComm	# yes dongle

################################
# Hamster control
################################
class RobotBehaviorThread(threading.Thread):
	def __init__(self, robotList):
		super(RobotBehaviorThread, self).__init__()
		self.go = False
		self.done = False
		self.robotList = robotList
		self.currentNote = 1
		self.acceleration = 0.1
		return

	def run(self):
		robot=None
		while not self.done:
			for robot in self.robotList:
				if robot and self.go:
					#############################################
					# START OF YOUR WORKING AREA!!!
					#############################################
					robot.set_wheel(0, 100)
					robot.set_wheel(1, 100)

					# ==============
					# MUSICAL JAMS
					# ==============
					'''
					robot.set_musical_note(int(self.currentNote))
					self.currentNote += self.acceleration
					if self.currentNote > 88 or self.currentNote < 1:
						self.acceleration = -self.acceleration
					'''

					


					#############################################
					# END OF YOUR WORKING AREA!!!
					#############################################					
		# stop robot activities, such as motion, LEDs and sound
		# clean up after exit button pressed
		if robot:
			robot.reset()
			time.sleep(0.1)
		return

class GUI(object):
	def __init__(self, root, robot_control):
		self.root = root
		self.robot_control = robot_control
		root.geometry('250x30')
		root.title('Hamster Control')

		b1 = tk.Button(root, text='Go')
		b1.pack(side='left')
		b1.bind('<Button-1>', self.startProg)

		b2 = tk.Button(root, text='Exit')
		b2.pack(side='left')
		b2.bind('<Button-1>', self.stopProg)
		return
	
	def startProg(self, event=None):
		self.robot_control.go = True
		return

	def stopProg(self, event=None):
		self.robot_control.done = True		
		self.root.quit() 	# close window
		return

#################################
# Don't change any code below!! #
#################################

def main():
    # instantiate COMM object
    gMaxRobotNum = 1; # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'  
    robotList = comm.robotList

    behaviors = RobotBehaviorThread(robotList)
    behaviors.start()

    frame = tk.Tk()
    GUI(frame, behaviors)
    frame.mainloop()

    comm.stop()
    comm.join()
    print("terminated!")

if __name__ == "__main__":
    sys.exit(main())