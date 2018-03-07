import time 

'''
Class for each virtual machine clock. 

:param msg_queues: a dictionary containing list of message queues 
'''
class Machine(object): 
	def __init__(self, ticks, msg_queues, id): 
		self.ticks = ticks 
		self.id = id 
		self.msg_queues = msg_queues 

	def record_log(self, msg): 
		file = open("log_" + str(self.id) + ".log", 'w')
		file.write(msg)
