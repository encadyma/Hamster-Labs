import sys
import time
import Tkinter as tk
import Queue
import threading

from starter_grid_graph import GridGraph
from starter_bfs import BFS
from starter_grid_graph_display import GridGraphDisplay

from HamsterAPI.comm_ble import RobotComm

robotList = []
shouldGo = True


def run_walker(robot_list, q):
    global n
    n = None

    while shouldGo:
        while not q.empty():
            n = q.get()

        # print 'current status: {0}\r'.format(n),

        if robotList:
            robot = robot_list[0]

            if n == 'black_left':
                robot.set_wheel(0, 0)
                robot.set_wheel(1, 20)
            elif n == 'black_right':
                robot.set_wheel(0, 20)
                robot.set_wheel(1, 0)
            elif n == 'forward':
                robot.set_wheel(0, 40)
                robot.set_wheel(1, 40)
            elif n == 'black_forward':
                robot.set_wheel(0, 80)
                robot.set_wheel(1, 80)
                time.sleep(0.2)
            else:
                robot.set_wheel(0, 0)
                robot.set_wheel(1, 0)

            # robot.set_wheel(0, 0)
            # robot.set_wheel(1, 0)

            time.sleep(0.01)


def run_beeper(robot_list, q):
    global n
    n = None

    while shouldGo:
        while not q.empty():
            n = q.get()

        if robotList:
            robot = robot_list[0]

            if n == 'black_forward':
                robot.set_musical_note(32)
                time.sleep(0.1)
            else:
                robot.set_musical_note(0)

            # robot.set_wheel(0, 0)
            # robot.set_wheel(1, 0)

            time.sleep(0.01)


def run_watcher(robot_list, q):
    while shouldGo:
        if robotList:
            robot = robot_list[0]

            if robot.get_floor(0) < 20 or robot.get_floor(1) < 20:
                q.put('black_forward')
                robot.set_musical_note(32)
                time.sleep(0.2)
                robot.set_musical_note(0)
            elif abs(robot.get_floor(1) - robot.get_floor(0)) < 20:
                q.put('forward')
            else:
                if robot.get_floor(1) > robot.get_floor(0):
                    q.put('black_left')
                else:
                    q.put('black_right')

            time.sleep(0.01)

def get_task_queue():
    queue = Queue.Queue()




def main():
    global robotList

    comm = RobotComm(1)
    comm.start()

    robotList = comm.robotList

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

    program = GridGraphDisplay(frame, graph)
    program.display_graph()

    program.highlight_path(shortest[0])
    print(shortest[0])

    queue = Queue.Queue()

    watcher = threading.Thread(name='watcher', target=run_watcher, args=(robotList, queue))
    watcher.start()

    walker = threading.Thread(name='walker', target=run_walker, args=(robotList, queue))
    walker.start()

    beeper = threading.Thread(name='beeper', target=run_beeper, args=(robotList, queue))
    beeper.start()

    # program.gui_root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
