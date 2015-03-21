__author__ = 'neo'

import random
from collections import deque

import math
import ConfigParser


class Clock():
    def __init__(self,time=0):
        self.time = time
    def getTime(self):
        return self.time
    def setTime(self,time):
        self.time=time

class System:
    """
        Stores Information about the System.

        @serviceTime:       The distribution object for the service time.
        @thinkTime:         The distribution object for the think time of the system.
        @timeout:           The distribtion object for the timeout of the system.
        @numProcessors:     The number of processors in the system.
        @contextSwitchTime: The context switch time of the system.
        @timeQuantum:       The time quantum/slice of the system.
        @maxThreads:        The maximum number of threads in the system.
        @bufferSize:        The size of the buffer in the system.
        @processors:        A list of all the processor objects in the system.
        @threadPool:        The threadpool object of the system.
        @reqBuffer:         The buffer object of the system.
    """

    def __init__(self, serviceTimeDist, thinkTimeDist, timeoutDist, numProcs,
                 contextSwitchTime, timeQuantum, maxThreads, bufferSize):
        self.serviceTime = serviceTimeDist
        self.thinkTime = thinkTimeDist
        self.timeout = timeoutDist
        self.numProcessors = numProcs
        self.contextSwitchTime = contextSwitchTime
        self.timeQuantum = timeQuantum
        self.maxThreads = maxThreads
        self.bufferSize = bufferSize


        self.processors = []

        self.InitProcessors()
        self.InitThreadPool()
        self.InitBuffer()

        self.clock = Clock()
    def InitProcessors(self):
        for i in range(self.numProcessors):
            self.processors.append(Processor(i, processorState['idle']))

    def InitThreadPool(self):
        self.threadPool = ThreadPool(self.maxThreads)

    def InitBuffer(self):
        self.reqBuffer = Buffer(self.bufferSize)


requestState = {'thinking': 0, 'executing': 1, 'buffered': 2,
                'inRunQueue': 3}


class Request:
    """
        Represents a request in the simulation.

        @timeStamp:     The time at which the request arrived into the system
        @reqId:         The Id of the request
        @state:         The state of the request. Possible states are
                            - thinking
                            - executing
                            - buffered (No free threads in the system)
                            - inRunQueue (of a processor)
        @serviceTime:   The service time of the request
        @remServiceTime:The remaining service time of the request (Round Robin)
        @timeout:       The timeout of the request
        @threadId:      The thread Id allocated to the request
    """

    def __init__(self, state, timeStamp, reqId, serviceTime, timeout):
        self.state = state
        self.timeStamp = timeStamp
        self.reqId = reqId
        self.threadId = None
        self.serviceTime = serviceTime
        self.remServiceTime = serviceTime
        self.timeout = timeout

    def UpdateServiceTime(self, updateTime):
        if self.remServiceTime - updateTime < 0:
            raise Exception("Update makes remaining service time negative!")
        else:
            self.remServiceTime -= updateTime


class Buffer:
    """
        A queue for requests which could not be allocated a thread because
        none were free when they arrived.
    """

    def __init__(self, maxQueueSize):
        self.maxQueueSize = maxQueueSize
        self.requestQueue = deque([])

    def QueueRequest(self, request):
        if len(self.requestQueue) is self.maxQueueSize:
            raise Exception("Request Queue is full")
        else:
            self.requestQueue.append(request)

    def DequeueRequest(self):
        try:
            request = self.requestQueue.popleft()
        except IndexError:
            raise Exception("Request Buffer is empty!")
        return request


class ThreadPool:
    """
        Represents the pool of threads available in the system

        @maxNumThread:      The maximum number of threads in the system
        @numBusyThreads:    The number of busy threads in the system
        @threadList:        A list to keep track of every thread in the system.
                            The index of an entry in this list is the thread Id.
                            Each entry of the list is a tupule representing a
                            thread. The tupule is of the form (reqId, coreId)
                            representing the core the thread is running on and
                            the request executing on the thread.
    """

    def __init__(self, maxNumThreads):
        self.maxNumThreads = maxNumThreads
        self.numBusyThreads = 0

        self.threadList = []
        for i in range(0, maxNumThreads):
            self.threadList.append((-1, -1))

    # To free a thread. Find the relevant entry in the thread list and
    # set it to (-1, -1)
    def FreeThread(self, reqId, procId):
        if self.numBusyThreads is 0:
            raise Exception("No allocated threads in the system!")
        else:
            try:
                threadId = self.threadList.index((reqId, procId))
            except:
                raise Exception("Thread with reqId and procId not found")
            self.threadList[threadId] = (-1, -1)
            self.numBusyThreads -= 1

    # To allocate a thread. Find a free thread (-1, -1) and allocate it.
    def AllocateThread(self, reqId, procId):
        if self.numBusyThreads is self.maxNumThreads:
            return -1
        else:
            try:
                threadId = self.threadList.index((-1, -1))
            except:
                raise Exception("Could not find a free thread in the system")
            self.threadList[threadId] = (reqId, procId)
            self.numBusyThreads += 1
            return threadId


processorState = {'idle': 0, 'busy': 1}


class Processor:
    """
        Represents a processor in the system.

        @procId:    The Id of the processor
        @state:	    The current state of the processor.
                    The processor can be:
                        - Busy
                        - Idle
        @runQueue:  The run queue of threads on the processor
                    The head of the queue represents the thread
                    currently executing on the cpu.
    """

    def __init__(self, procId, state):
        self.procId = procId
        self.state = state
        self.runQueue = deque([])

    def AddThread(self, thread):
        self.runQueue.append(thread)

    def RemoveThread(self):
        try:
            thread = self.runQueue.popleft()
        except IndexError:
            raise Exception("Processor's runqueue is empty!")
        return thread

    # Schedule the next job on the runqueue in a Round Robin fashion.
    def ScheduleNext(self):
        thread = self.RemoveThread()
        self.AddThread(thread)


eventType = {'arrival': 0, 'departure': 1, 'quantumExpired': 2,
             'scheduleNext': 3, 'timeout': 4}


class Event:
    """
        Represents an event in the simulation.

        @__id:          The event id
        @eventType:     The type of event
                            - arrival
                            - departure
                            - quantum Expired (on a processor)
                            - schedule Next
                            - timeout
        @timeStamp:     The time at which the event occurs
        @data:          For an event of type Quantum Done, Schedule Next,
                        and departure, this stores the processor Id on which
                        the event occurs. For an event of type Arrival, this
                        stores the request Id. For a timeout, this stores the
                        request Id.
        @cancelled      0:Event not cancelled
                        1:Event was cancelled, and hence not needed to be handled
                        This member is used to handle the removal of timeout event from event list, if timeout doesn't occur when an event departs
    """

    def __init__(self, timeStamp, eventType, data):
        self.__id = None
        self.timeStamp = timeStamp
        self.eventType = eventType
        self.data = data
        self.cancelled = 0


class EventList:
    """
    A min heap of events
    """

    def __init__(self):
        self.heap = []
        self.id = 0  # will give a unique id to each event


    def AddEvent(self, event):
        """
        add event 'event', which is of type event to minheap of events
        assign an id to it
        return the assigned id
        """
        event.__id = id
        id += 1
        self.AddToHeap(event)
        return event.__id

    def RemoveEvent(self):
        """
        Remove and return next event with least timestamp
        """
        raise NotImplementedError

    # Heap specific methods:-
    def LeftChildIndex(self, node):
        """

        :param node: 
        :return: index of rightChildIndex
        """
        return 2 * node + 1

    def RightChildIndex(self, node):
        return 2 * node + 2

    def ParentIndex(s, node):
        return int(math.floor((node - 1) / 2))

    def Swap(self, node1, node2):
        temp = self.heap[node1]
        self.heap[node1] = self.heap[node2]
        self.heap[node2] = temp

    def Exists(self, node):
        if node < len(self.heap) and node >= 0:
            return True
        else:
            return False

    # end of heapify helper functions

    def HeapifyAtposition(self, node):
        s = self

        if self.Exists(self.RightChildIndex(node)) and self.Exists(self.LeftChildIndex(node)):
            if self.heap[self.RightChildIndex(node)].timestamp < self.heap[node].timestamp:
                s.swap(s.RightChildIndex(node), node)
                s.HeapifyAtposition(s.RightChildIndex(node))
                return True
            elif s.heap[s.LeftChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.swap(s.LeftChildIndex(node), node)
                s.HeapifyAtposition(s.LeftChildIndex(node))
                return True
            else:
                return False
        elif s.Exists(s.RightChildIndex(node)):
            if s.heap[s.RightChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.swap(s.RightChildIndex(node), node)
                s.HeapifyAtposition(s.RightChildIndex(node))
                return True
        elif s.Exists(s.LeftChildIndex(node)):
            if s.heap[s.LeftChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.Swap(s.LeftChildIndex(node), node)
                s.HeapifyAtposition(s.RightChildIndex(node))
                return True
        else:
            return False


    def AddToHeap(s, value):
        s.heap.append(value)
        nodeIndex = len(s.heap) - 1

        while s.Exists(s.ParentIndex(nodeIndex)):
            if not s.HeapifyAtposition(s.ParentIndex(nodeIndex)):
                break
            else:
                nodeIndex = s.ParentIndex(nodeIndex)


    def Heapify(self):
        """
        :rtype : None
        """
        for i in range(len(self.heap) - 1, -1, -1):
            self.HeapifyAtposition(i)


distType = {'constant': 0, 'uniform': 1, 'normal': 2, 'exponential': 3}


class Distribution:
    def __init__(self, **distParams):
        """

        :param distribution_parameters: parameters to characterise a distribution, some examples:-

        type=distType.constant,value=2 #delta function ?
        type=distType.uniform,a=2,b=3 (starting and ending, default=0,1)
        type=distType.normal,mean=2,variance=3
        type=distType.exponential,lambda_val=2

        usage: d=distribution(type=distType.exponential,lambda_val=2)
        will create an object of exponential distribution.
        Each distribution will have a method sample() which will return a RV variable from that distribution
        """
        self.__type = distParams['type']

        if self.__type is distType['constant']:
            self.__value = float(distParams['value'])

        elif self.__type is distType['uniform']:
            if len(distParams) is 1:  # a and b not specified, assuming uniform in [0,1]
                self.__a = 0.0
                self.__b = 1.0
            elif len(distParams) is 3:  # a and b both specified for uniform distribution
                self.__a = float(distParams['a'])
                self.__b = float(distParams['b'])
            else:
                raise Exception('Improper number of arguments for uniform distribution')

        elif self.__type is distType['normal']:
            self.__mean = float(distParams['mean'])
            self.__variance = float(distParams['variance'])

        elif self.__type is distType['exponential']:
            self.__lambda = float(distParams['lambda_val'])

        else:
            raise Exception('unknown distribution')

    def sample(self):
        if self.__type is distType['constant']:
            return self.__value

        elif self.__type is distType['uniform']:
            return random.uniform(self.__a, self.__b)

        elif self.__type is distType['normal']:
            return random.gauss(self.__mean, (self.__variance) ** 2)

        elif self.__type is distType['exponential']:
            return -(1.0 / self.__lambda) * math.log(1.0 - random.uniform(0, 1))  # by default log uses base e

        else:
            raise Exception('Distribution not handled by sample()')


class Simulation:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('simulation.cfg')

        self.randomSeed = config.getint('System', 'randomSeed')
        self.numClients=config.getint('Simulation', 'numClients')

        serviceTimeDist = self.GetDistributionObject(config, 'ServiceTime')
        thinkTimeDist = self.GetDistributionObject(config, 'ThinkTime')
        timeoutDist = self.GetDistributionObject(config, 'Timeout')

        self.system = System(serviceTimeDist, thinkTimeDist, timeoutDist,
                             config.getint('System', 'numProcessors'),
                             config.getfloat('Processor', 'contextSwitchTime'),
                             config.getfloat('Processor', 'timeQuantum'),
                             config.getint('System', 'maxThreads'),
                             config.getint('System', 'bufferSize'))

        self.eventList = EventList()

        self.requestList=[]
        self.InitRequestList(numberOfClients=self.numClients,self.system.clock)

    def GetDistributionObject(self, config, parameter):
        distribution = config.get(parameter, 'distribution')

        if distribution == "'constant'":
            return Distribution(type=distType['constant'],
                                value=config.getfloat(parameter, 'value'))
        elif distribution == "'uniform'":
            return Distribution(type=distType['uniform'],
                                a=config.getfloat(parameter, 'a'),
                                b=config.getfloat(parameter, 'b'))
        elif distribution == "'normal'":
            return Distribution(type=distType['normal'],
                                mean=config.getfloat(parameter, 'mean'),
                                variance=config.getfloat(parameter, 'variance'))
        elif distribution == "'exponential'":
            return Distribution(type=distType['exponential'],
                                lambda_val=config.getfloat(parameter,
                                                           'lambda_val'))

    def EventHandler(self, event):
        pass

    # Add a scheduleNext event to the eventList, and update the processors
    # runqueue.
    def HandleQuantumExpired(self, event):
        newEvent = Event(event.timeStamp + self.system.contextSwitchTime,
                         eventType['scheduleNext'], event.data)
        self.eventList.AddEvent(newEvent)
        self.system.processors[event.data].ScheduleNext()
        self.system.processors[event.data].state = processorState['idle']

    # Add a departure or a quantum expired event based on the remaining
    # service time of the event at the head of the processors run queue.
    def HandleScheduleNext(self, event):
        remTime = self.system.processors[event.data].runQueue[0].remServiceTime
        if remTime < self.system.timeQuantum:
            newEvent = Event(event.timeStamp + remTime, eventType['departure'],
                             event.data)
        else:
            newEvent = Event(event.timeStamp + self.system.timeQuantum,
                             eventType['quantumExpired'], event.data)
        self.eventList.AddEvent(newEvent)

    def InitRequestList(self, numberOfClients,clock):
        for i in range(numberOfClients):
            newRequest=Request(requestState['thinking'],clock.getTime(),i,)
            self.requestList.append(1)
