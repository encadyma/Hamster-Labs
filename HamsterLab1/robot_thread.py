from Queue import Queue

q = Queue()
q.put(1)
q.put(2)
q.put(3)

q.empty()		# return if the queue is empty
q.qsize()		# => 4

# Hacker tip! use dir(q) to list all methods possible

q.put('four')	# Queues are not homogeneous

# FIFO, this will POP the first element put in.
q.get()			# => 1

