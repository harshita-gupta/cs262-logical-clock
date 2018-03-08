from vm import Machine
import sys
from random import randint
from multiprocessing import Process, Queue, Value
import time

# initialize variables
n = 3
msg_qs = [Queue() for x in xrange(n)]
ticks = [randint(1, 6) for x in range(n)]

# ticks = [1, 5, 10]
q0_size = Value('i', 0)
q1_size = Value('i', 0)
q2_size = Value('i', 0)

# initialize VMs
v0 = Machine(ticks[0], msg_qs, 0, 1, 2, sys.argv[1])
v1 = Machine(ticks[1], msg_qs, 1, 0, 2, sys.argv[1])
v2 = Machine(ticks[2], msg_qs, 2, 0, 1, sys.argv[1])

# start each process
p0 = Process(target=v0.run, args=(q0_size, q1_size, q2_size))
p1 = Process(target=v1.run, args=(q1_size, q0_size, q2_size))
p2 = Process(target=v2.run, args=(q2_size, q0_size, q1_size))

p0.start()
p1.start()
p2.start()

time.sleep(60)

p0.terminate()
p1.terminate()
p2.terminate()
