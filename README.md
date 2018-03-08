# CS262 Logical Clock Lab Notebook 
## How the model was built and design decisions 
### General Considerations 
We began by writing a Machine() class, which would act as the virtual machine/clock. Before beginning, we considered a few things--such as how the machines would communicate with each other, whether we would need to use sockets, etc. 

We decided to bypass sockets by using Python's multiprocessing package. By using the Queue() class from this library, we were able to create message queues that could be accessed, altered, and shared simultaneously across all the different processes of virtual machines being run. We ensured that the virtual machines were  being run in parallel by using the Process() class from multiprocessing. Indeed, the logs indicated the same system start time for each of the machines, so they all began running simultaneously. All of the plumbing, instantiation of processes and variables, and general setup of the program was done in run.py. The file vm.py only contains the Machine() class. 
### Machine() Class: vm.py 
Since the machines communicate using multiprocessing queues instead of sockets, they each must have access to all of the queues. When a Machine object is initialized, it receives its randomly generated number of ticks (per second), a list of the message queues of all machines being run, its own id, and the id's of the other machines (these id's are used to determine which message queue belongs to which machine). In handling the message queues, a machine can pop from its own message queue (if it is not empty), as well as append messages to other machines' message queues (if it is in a send operation). 

One issue that came up unexpectedly was the fact that qsize(), used to find the size of the queue, needed to call a function that was not implemented in MacOS (wth?? ikr??), so we couldn't use that to keep track of the queue lengths. Instead, we found a way to keep track of each queue's size by using multiprocessing's Value() class to initialize integer counts for each queue, representing queue size, that could be accessed and altered consistently across all the machines' processes. Each time a machine retrieves a message from its queue, its queue counter would decrement and each time it pushed a message onto another machine's queue, that machine's queue counter would increment. 

We used Lamport's rules for updating the local logical clocks. This meant, when taking a message off the queue, the local clock would be updated to the received timestamp if that timestamp is greater than the local clock's time, and then incremented by 1. When sending a message, the local clock would be incremented and then the message would be sent with that updated local timestamp. 

We had to decide whether the operation of sending a message to both of the other machines would require the local clock to be updated once or twice. Since the send operations surely could not happen simultaneously, we decided to increment the local clock before each send operation so that it is incremented twice in total. This was motivated by the fact that there could be problems that arise if two machines receive different messages with the same timestamp from one sender. This is also in accordance with the Lamport timestamp algorithm. 

We simulated the machine's clock rate by pausing (using system time) for 1/n seconds after each cycle of operations, where n is the number of ticks per second assigned to the machine. 


## Experiments

### Tick values ranging by order of magnitude

We run our first set of trials for three machines with tick/second values ranging from 1 to 6, selected randomly.

#### Trial 1:
Tick values: 1, 2, 6

#### Trial 2:
Tick values: 6, 6, 6

On this trial, the randomly generated tick/second values all ended up the same. This trial proved the intuitive hypothesis that when all the machines run at the same speed, the logical clocks across all three machines would have few jumps and end the process with close to zero items remaining in the queues. The largest jump value appearing on a queue was 7, and the mode jump value was 1. The queue length remained at 0-1, only rising to 2 once across all three machines.

#### Trial 3:
Tick values: 1, 6, 6

In this trial, one machine was significantly slower than the other two.

#### Trial 4:
Tick values: 1, 2, 5

#### Trial 5:
Tick values: 1, 3, 6
