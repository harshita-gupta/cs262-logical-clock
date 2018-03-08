
# CS262 Logical Clock Lab Notebook
## Usage
Clone the repo and run: python run.py "log_file_name"

where log_file_name is the prefix you want for each of your log files' names (our program will create a log for each machine and name them according to the prefix you choose). 

For example: python run.py "log_trial_1"

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

We run our first set of trials for three machines with tick/second values ranging from 1 to 6, selected randomly. For our analysis, we analyze statistics about jumps in logical clock time stamp and the amount of items in the queue.

#### Trial 1:
Tick values: 2, 6, 6
In this trial, one machine is significantly slower than the other two.
##### Jumps:
| Ticks   | 2               | 6             | 6             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 14              | 3             | 3             |
| Average | 0.0504201680672 | 1.21848739496 | 1.21568627451 |
| Mode    | 30              | 282           | 286           |

Trial one reveals that since the slowest machine does not progress very far into the queue, it updates its logical clock less than the other two machines, as indicated by the average jump of 0.05 compared to the 1.2.

The queue for the faster machines are empty at termination, while the queue for the slowest machine has 80 items in it.

#### Trial 2:
Tick values: 6, 6, 6

On this trial, the randomly generated tick/second values all ended up the same. This trial proved the intuitive hypothesis that when all the machines run at the same speed, the logical clocks across all three machines would have few jumps and end the process with close to zero items remaining in the queues. The largest jump value appearing on a queue was 7, and the mode jump value was 1. The queue length remained at 0-1, only rising to 2 once across all three machines.

#### Trial 3:
Tick values: 1, 4, 6

In this trial, the three machines in concern are spread out fairly evenly along the possible speeds.

| Ticks   | 4               | 6             | 1             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 2               | 15            | 7             |
| Average | 1.09523809524   | 4.01694915254 | 1.62605042017 |
| Mode    | 17              | 323           | 161           |

By comparing this trial to trial 1, we see that the jump made by the fastest machine (ticks=6) are greater on average due to the fact that there are now TWO machines slower than it, rather than just one. This indicates that as the number of machines grow, it is likely that the jumps and skew in the logical clock of the fastest machine will increase to a problematic extent.

#### Trial 4:
Tick values: 4, 1, 3

| Ticks   | 4               | 1             | 3             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 2               | 11            | 8             |
| Average | 1.09663865546   | 3.22033898305 | 1.45810055866 |
| Mode    | 215             | 18            | 137           |


Max queue lengths: 0, 15, 1

This trial shows two faster machines closer in speed with one machine lagging farther behind. We see here that the two faster machines (ticks=4, ticks=3) keep up with the message queue pool, and have similar average and maximum jumps. The cost of having two machines one order of magnitude away from each other appears to not be as serious as any of our other configurations.

#### Trial 5:
Tick values: 1, 1, 6

| Ticks   | 1               | 1             | 6             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 18              | 18            | 2             |
| Average | 5.62711864407   | 5.23728813559 | 1.11764705882 |
| Mode    | 11              | 15            | 315           |

Max queue lengths: 13, 17, 0

This configuration, when contrasted with Trial 1, reveals that the jumps and lag are not determined by the ratio of speeds of machines, as we had earlier postulated, but are determined by the most common speed. In this case, since the fastest machine with ticks=6 was in the minority, the pace for the network was set by the two slower machines(ticks=1). This is why the average jump was lower for the fastest machine in this case, while the average jump was higher for the fast machines in the case of trial 5. This reveals that the highest jumps will occur for the machines with the most common speed setting.


### Reducing the probability of internal events

Running the same tick values as in the above experiments, but with a reduced probability of internal events (from .7 to .25), these are the results that we had (excluding trial 2 due to no valuable comparative information).

#### Trial 1:
Tick values: 2, 6, 6

##### Jumps:
| Ticks   | 2               | 6             | 6             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 10              | 3             | 3             |
| Average | 2.25210084034   | 1.49299719888 | 1.49019607843 |
| Mode    | 45              | 206           | 200           |


#### Trial 3:
Tick values: 1, 4, 6

In this trial, the three machines in concern are spread out fairly evenly along the possible speeds.

| Ticks   | 4               | 6             | 1             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 6               | 6             | 3             |
| Average | 2.0             | 1.86974789916 | 1.25280898876 |
| Mode    | 25              | 108           | 269           |


#### Trial 4:
Tick values: 4, 1, 3

| Ticks   | 4               | 1             | 3             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 2               | 6             | 5             |
| Average | 1.25210084034   | 2.32203389831 | 1.65363128492 |
| Mode    | 178             | 24            | 92            |


#### Trial 5:
Tick values: 1, 1, 6

| Ticks   | 1               | 1             | 6             |
|---------|-----------------|---------------|---------------|
| Min     | 1               | 1             | 1             |
| Max     | 10              | 10            | 2             |
| Average | 2.67796610169   | 2.52542372881 | 1.25280898876 |
| Mode    | 21              | 24            | 266           |



In all the above cases, we see that the average, min, max, and mode jumps move closer to the averages of the three machines. The discord between the three machines is thus significantly reduced, likely since keeping the machines in sync is prioritized over carrying out internal operations, and fewer updates occur to the clock of faster machines due to internal events reduced the skew between machines.

The updates to the logical clocks are more constrained by the average speed of the communications between the system components, which are constrained by the speeds of the slower machines.

###  Smaller variation in the clock cycles 
Additionally, we experimented with smaller variations in the clock cycles of the machines. We set the number of ticks per second (TPS) to be ~50, which is quite rapid. We did not vary the number of ticks across machines by much--they were all ~50 TPS, give or take 2-3 ticks. We observed that none of the queues grew past 1 or 2 in length, as 50 TPS ensured that they were dequeued almost as quickly as they were enqueued. We also observed that clock times had very small jumps and did not observe notable drift between the 3 different logical clocks. We surmise that since the machines were rapidly communicating with each other, local clock times were updated quickly and constantly, allowing little time for jumps to "accumulate." The constant communication allowed the machines to better synchronize their times, which meant less drift from one machine to another. Indeed, smaller variations in clock cycles at high speeds ensures more reliable timekeeping in a distributed system. 

### Original experiment


## Conclusions

The experimental analysis confirmed the following intuitive conclusion:
1) At any given moment in time, the slowest machines will have the most unprocessed items in their queue.

And also led to the following new/unexpected insight:
1) In a distributed system, the average and most common jump will be larger on the machines with the most common speed, rather than on the faster machines.
2) Fewer internal events helped to keep machines with different speeds in sync more, and prevented clock skew.


Our experiments suggest serious concerns for machines in a distributed system where an important machine lags significantly behind the rest in speed, in this case the inconsistency of the logical clock is not made up for by the ability of the machine to process queuries quickly. Thus, a rogue machine is much more harmful if it is a rogue slow machine, than a rogue fast machine. In this case, a few minutes of running the system resulted in a large backup of messages for slower machines, and the slower machines sending responses to the faster machines that are far out of date, don't adequately respond to events occuring with the faster machines, and potentially contain irrelevant information.

