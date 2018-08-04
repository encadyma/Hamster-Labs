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
import random
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

		# Different Activities
		self.doShy = False
		self.doDance = False
		self.doFollow = False
		return

	def run(self):
		robot=None
		while not self.done:
			for robot in self.robotList:
				if robot and self.go:
					#############################################
					# START OF YOUR WORKING AREA!!!
					#############################################

					if self.doShy:
						if robot.get_proximity(0) > 20 or robot.get_proximity(1) > 20:
							robot.set_musical_note(random.randint(1, 88))
							robot.set_led(0, random.randint(1, 7))
							robot.set_led(1, random.randint(1, 7))
							robot.set_wheel(0, -10 * robot.get_proximity(0))
							robot.set_wheel(1, -10 * robot.get_proximity(1))
						else:
							robot.set_musical_note(0)
							robot.set_led(0, 0)
							robot.set_led(1, 0)
							robot.set_wheel(0, 20)
							robot.set_wheel(1, 20)

					elif self.doFollow:
						robot.set_wheel(0, 2 * robot.get_proximity(1))
						robot.set_wheel(1, 2 * robot.get_proximity(0))

					elif self.doLineFollow:
						# white : 100, black : < 100
						robot.set_wheel(0, 1 * robot.get_floor(0))
						robot.set_wheel(1, 1 * robot.get_floor(1))

						print (robot.get_floor(0), robot.get_floor(1))

					else:				
						robot.set_wheel(0, 100)
						robot.set_wheel(1, 100)
						time.sleep(0.6)
						robot.set_wheel(0, -50)
						robot.set_wheel(1, 50)
						time.sleep(0.6)

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
		root.geometry('500x30')
		root.title('Hamster Control')

		b1 = tk.Button(root, text='Go')
		b1.pack(side='left')
		b1.bind('<Button-1>', self.startProg)		

		bshy = tk.Button(root, text='Shy')
		bshy.pack(side='left')
		bshy.bind('<Button-1>', self.startShy)

		bdance = tk.Button(root, text='Dance')
		bdance.pack(side='left')
		bdance.bind('<Button-1>', self.startDance)

		bfollow = tk.Button(root, text='Follow')
		bfollow.pack(side='left')
		bfollow.bind('<Button-1>', self.startFollow)

		blfollow = tk.Button(root, text='Line Follow')
		blfollow.pack(side='left')
		blfollow.bind('<Button-1>', self.startLineFollow)

		bstop = tk.Button(root, text='Stop')
		bstop.pack(side='right')
		bstop.bind('<Button-1>', self.stopProg)

		b2 = tk.Button(root, text='Exit')
		b2.pack(side='right')
		b2.bind('<Button-1>', self.exitProg)
		return
	
	def startProg(self, event=None):
		self.robot_control.go = True
		self.robot_control.doShy = False
		self.robot_control.doDance = False
		self.robot_control.doFollow = False
		self.robot_control.doLineFollow = False
		return

	def startShy(self, event=None):
		self.robot_control.go = True
		self.robot_control.doShy = True
		self.robot_control.doDance = False
		self.robot_control.doFollow = False
		self.robot_control.doLineFollow = False
		return

	def startDance(self, event=None):
		self.robot_control.go = True
		self.robot_control.doShy = False
		self.robot_control.doDance = True
		self.robot_control.doFollow = False
		self.robot_control.doLineFollow = False
		return

	def startFollow(self, event=None):
		self.robot_control.go = True
		self.robot_control.doShy = False
		self.robot_control.doDance = False
		self.robot_control.doFollow = True
		self.robot_control.doLineFollow = False
		return

	def startLineFollow(self, event=None):
		self.robot_control.go = True
		self.robot_control.doShy = False
		self.robot_control.doDance = False
		self.robot_control.doFollow = False
		self.robot_control.doLineFollow = True

	def stopProg(self, event=None):
		self.robot_control.go = False
		return

	def exitProg(self, event=None):
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