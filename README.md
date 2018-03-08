# cs262-logical-clock Lab Notebook
## How the model was built
### General Considerations
We began by writing a Machine() class, which would act as the virtual machine/clock. Before beginning, we considered a few things--such as how the machines would communicate with each other, whether we would need to use sockets, etc.

We decided to bypass sockets by using Python's multiprocessing package. By using the Queue() class from this library, we were able to create message queues that could be accessed, altered, and shared simultaneously across all the different processes of virtual machines being run. We ensured that the virtual machines were  being run in parallel by using the Process() class from multiprocessing. Indeed, the logs indicated the same system start time for each of the machines, so they all began running simultaneously. All of the plumbing, instantiation of processes and variables, and general setup of the program was done in run.py. The file vm.py only contains the Machine() class.
### Machine() class -- vm.py
Since the machines communicate using multiprocessing queues instead of sockets, they each must have access to all of the queues. When a Machine object is initialized, it receives its randomly generated number of ticks (per second), a list of the message queues of all machines being run, its own id, and the id's of the other machines (these id's are used to determine which message queue belongs to which machine).

One issue that came up




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
