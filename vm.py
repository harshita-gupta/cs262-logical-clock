from __future__ import division
import sys
import atexit
import signal
from collections import Counter
import time
import os
from random import randint

'''
Class for a virtual machine clock
'''

class Machine(object):
    def __init__(self, ticks, msg_qs, id, id_vm1, id_vm2, log_name):
        self.ticks = ticks
        self.id = id
        self.msg_qs = msg_qs
        self.q = self.msg_qs[self.id]
        self.id_vm1 = id_vm1
        self.id_vm2 = id_vm2
        self.log_name = log_name + "_ticks" + str(self.ticks)
        self.queue_lengths = []
        self.logical_clock_times = []

        # clear log of previous instance if any
        self.clear_log()

    def record_log(self, msg):
        file = open(self.log_name + str(self.id) + ".log", 'a')
        with file as file:
            file.write(msg + "\n\n")

    def clear_log(self):
        filename = self.log_name + str(self.id) + ".log"
        try:
            os.remove(filename)
        except OSError:
            pass

    def get_msg(self):
        msg_time = self.q.get()
        self.q_size.value -= 1
        self.clock = max(msg_time, self.clock) + 1
        self.record_log("RECEIVED message\nGlobal time: "\
            + str(time.time()) + "\nQueue length: "\
            + str(self.q_size.value) + "\nLogical clock time: "\
            + str(self.clock))
        self.queue_lengths.append(self.q_size.value)
        self.logical_clock_times.append(self.clock)

    def sent_log_msg(self):
        log = "SENT message\nGlobal time: "\
            + str(time.time()) + "\nLogical clock time: "\
            + str(self.clock)
        return log

    def send_msg(self):
        r = randint(1, 10)
        if r == 1:
            self.clock += 1
            self.msg_qs[self.id_vm1].put(self.clock)
            self.q_size_vm1.value += 1
            self.record_log(self.sent_log_msg())
            self.queue_lengths.append(self.q_size.value)
            self.logical_clock_times.append(self.clock)

        elif r == 2:
            self.clock += 1
            self.msg_qs[self.id_vm2].put(self.clock)
            self.q_size_vm2.value += 1
            self.record_log(self.sent_log_msg())
            self.queue_lengths.append(self.q_size.value)
            self.logical_clock_times.append(self.clock)

        elif r == 3:
            self.clock += 1
            self.msg_qs[self.id_vm1].put(self.clock)
            self.clock += 1
            self.msg_qs[self.id_vm2].put(self.clock)
            self.q_size_vm1.value += 1
            self.q_size_vm2.value += 1
            self.record_log(self.sent_log_msg())
            self.queue_lengths.append(self.q_size.value)
            self.logical_clock_times.append(self.clock)

        else:
            self.clock += 1
            internal_event = "INTERNAL EVENT\nGlobal time: "\
                + str(time.time()) + "\nLogical clock time: "\
                + str(self.clock)
            self.record_log(internal_event)
            self.queue_lengths.append(self.q_size.value)
            self.logical_clock_times.append(self.clock)

    def print_info(self, *args):
        print
        print self.id, "For a machine with " + str(self.ticks) + " ticks,"
        print self.id, "Clock times:"
        t = self.logical_clock_times
        print t
        jumps = [t[i + 1] - t[i] for i in range(len(t) - 1)]
        print self.id, "average jump", sum(jumps) / float(len(jumps))
        print self.id, "max jump", max(jumps)
        print self.id, "min jump", min(jumps)
        print self.id, "most common jump", Counter(jumps).most_common(1)
        print

        print self.id, "Queue Lengths:"
        t = self.queue_lengths
        jumps = [t[i + 1] - t[i] for i in range(len(t) - 1)]
        print self.id, "average jump", sum(jumps) / float(len(jumps))
        print self.id, "max jump", max(jumps)
        print self.id, "min jump", min(jumps)
        print self.id, "most common jump", Counter(jumps).most_common(1)
        sys.exit(0)

    def run(self, q_size, q_size_vm1, q_size_vm2):
        atexit.register(self.print_info)
        signal.signal(signal.SIGTERM, self.print_info)
        signal.signal(signal.SIGINT, self.print_info)
        self.q_size = q_size
        self.q_size_vm1 = q_size_vm1
        self.q_size_vm2 = q_size_vm2
        self.clock = 0
        self.record_log("Began process at " + str(time.time()) + "\nTicks: "\
            + str(self.ticks))

        while True:
            if not self.q.empty():
                self.get_msg()
            else:
                self.send_msg()
            time.sleep(1 / self.ticks)
