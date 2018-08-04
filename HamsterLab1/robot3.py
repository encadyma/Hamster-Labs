import time
from threading import Thread

def t():
	for i in range(10):
		print 'Thread t starts'
		print 'Thread t ends'
		time.sleep(0.1)

def d():
	print 'Thread d starts'
	time.sleep(4)
	print 'Thread d ends'

t1 = Thread(name='Thread t', target=t)
t2 = Thread(name='Thread d', target=d)

t2.setDaemon(True)

t1.start()
t2.start()

# .join: Move the thread
# to block the main process
t1.join()
t2.join()

# Both threads still run at the same time
# when joined.