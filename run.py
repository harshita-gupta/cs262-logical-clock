from vm import Machine
from random import randint 

# initialize variables 
n = 3 
msg_queues = [[] for x in range(n)]
ticks = [randint(1,6) for x in range(n)]

# initialize VMs 
v0 = Machine(ticks[0], msg_queues, 0)
v1 = Machine(ticks[1], msg_queues, 1)
v2 = Machine(ticks[2], msg_queues, 2)