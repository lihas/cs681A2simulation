__author__ = 'neo'

import math,random





class system:
    """
    Meta information about the system being simulated.
    """

    def __init__(self,service_time_distribution_object,think_time_distribution_object,timeout_distribution_object,number_of_processors,context_switch_time_value,round_robin_time_quantum_value,max_threads,buffer_size):
        """

        :param service_time: Object of type distribution
        :param think_time: Object of type distribution
        :param timeout: Object of type distribution
        :param number_of_processors: integer
        :param context_switch_time: integer
        :param round_robin_time_qantum: integer
        :param max_threads: integer
        :param buffer_size: integer
        """

        # self.arrivalRate=None #Not needed since it will be determined by think time and number of users
        self.serviceTime = service_time_distribution_object
        self.thinkTime = think_time_distribution_object
        self.timeout = timeout_distribution_object  #Object of type distribution
        self.numberOfProcessors = number_of_processors  #Integer
        self.contextSwitchTime = context_switch_time_value  #Integer
        self.timeQuantumRoundRobin = round_robin_time_quantum_value  #Integer
        self.maxThreads = max_threads  #Integer
        self.buffer_size = buffer_size  #Integer

        self.processors = []  # list of processors
        self.threadPool=None #Object of type threadPool
        self.buffer=None #Object of type buffer


        self.initializeProcessors(number_of_processors)
        self.initializeThreadPool(max_threads)
        self.initializeBuffer(buffer_size)


        raise NotImplementedError

    def initializeProcessors(self, number_of_processors):
        for i in range(number_of_processors):
            self.processors.append(processor(i))

    def initializeThreadPool(self, max_threads):
        self.threadPool=threadPool(max_threads)

    def initializeBuffer(self, buffer_size):
        self.buffer=buffer(buffer_size)


class request:
    """
    Each request in the system will have one object
    """

    def __init__(self):
        raise NotImplementedError
        self.state = requestState.thinking;  # any of the members of requestState
        self.timeStamp = None  # time of arrival
        self.id = None
        self.threadId = None  # thread allocated to this request
        self.serviceTime = None
        self.serviceTimeRemaining = None


class requestList:
    def __init__(self):
        raise NotImplementedError
        self.reqauestlist = []


class threadPool:
    """
    To keep an account of requests present in the system.
    index of threadList will be the thread id
    """

    def __init__(self, maxThreads):
        raise NotImplementedError
        self.maxThreads = maxThreads
        self.numberOfBusyThreads = None
        self.threadList = []

    def allocateThread(self):
        raise NotImplementedError

    def freeThread(self):
        raise NotImplementedError


class buffer:
    """
    If thread pool is full enque requests here
    """

    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.bufferList = []

    def addToBuffer(self, request):
        """
        Check if buffer size exceeds self.maxBuffer
        """
        raise NotImplementedError

    def getFromBuffer(self):
        raise NotImplementedError


class event:
    """
    All events in event list will be an object of event class
    data: interpret this depending on type of request. for context switch data will hold cpu-id, for arrival request id. for departure it will be CPU-id
    """

    def __init__(self):
        self.__id = None #Do not set it explicitly, will be set by addEvent Method of eventList
        self.timestamp = None
        self.eventType = None  # of type eventTypes.arrival ,etc.
        self.data = None  # interpret this according to eventType (see documentation of this class)


class eventList:
    """
    A min heap of events
    """

    def __init__(self):
        self.heap = []
        self.id=0 #will give a unique id to each event


    def addEvent(self, event):
        """
        add event 'event', which is of type event to minheap of events
        assign an id to it
        return the assigned id
        """
        event.__id=id
        id+=1
        self.addToHeap(event)
        return event.__id

    def removeEvent(self):
        """
        Remove and return next event with least timestamp
        """
        raise NotImplementedError

    # Heap specific methods:-
    def leftChildIndex(self, node):
        """

        :param node: 
        :return: index of rightChildIndex
        """
        return 2 * node + 1

    def rightChildIndex(self, node):
        return 2 * node + 2

    def parentIndex(s, node):
        return int(math.floor((node - 1) / 2))

    def swap(self, node1, node2):
        temp = self.heap[node1]
        self.heap[node1] = self.heap[node2]
        self.heap[node2] = temp

    def exists(self, node):
        if node < len(self.heap) and node >=0:
            return True
        else:
            return False

    #end of heapify helper functions

    def heapifyAtposition(self, node):
        s = self

        if self.exists(self.rightChildIndex(node)) and self.exists(self.leftChildIndex(node)):
            if self.heap[self.rightChildIndex(node)].timestamp < self.heap[node].timestamp:
                s.swap(s.rightChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
            elif s.heap[s.leftChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.swap(s.leftChildIndex(node), node)
                s.heapifyAtposition(s.leftChildIndex(node))
                return True
            else:
                return False
        elif s.exists(s.rightChildIndex(node)):
            if s.heap[s.rightChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.swap(s.rightChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
        elif s.exists(s.leftChildIndex(node)):
            if s.heap[s.leftChildIndex(node)].timestamp < s.heap[node].timestamp:
                s.swap(s.leftChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
        else:
            return False


    def addToHeap(s, value):
        s.heap.append(value)
        nodeIndex = len(s.heap) - 1

        while s.exists(s.parentIndex(nodeIndex)):
            if not s.heapifyAtposition(s.parentIndex(nodeIndex)):
                break
            else:
                nodeIndex = s.parentIndex(nodeIndex)


    def heapify(self):
        """
        :rtype : None
        """
        for i in range(len(self.heap) - 1, -1, -1):
            self.heapifyAtposition(i)


class processor:
    """
    each processor in the system will have an associated object of processor type
    """

    def __init__(self, id):
        raise NotImplementedError
        self.id = id  # Integer
        self.runQueue = []  # List of request
        self.state = processorState.idle  # processorState.idle or processorState.busy

    def runQueueEnqueue(self):
        """
        make sure the total size of all queues remains less than max size of thread pool.
        """
        raise NotImplementedError

    def runQueueDequeue(self):
        raise NotImplementedError


class simulation:
    def __init__(self, numberOfClients,systemObject,seed):
        #self.processors = []  #Moved to system list of processors
        self.eventlist = eventList()
        self.initializeReqeustList(numberOfClients)
        random.seed(seed)

    def eventHandler(self, event):
        raise NotImplementedError

    def createEvent(self,type,data,timestamp):
        """

        :param type: type of event. eventTypes.arrival , etc.
        :param data: interpret this according to eventType (see documentation of event class)
        :param timestamp: time at which event is scheduled to occur
        """
        raise NotImplementedError

    def startSimulation(self):
        """
        Start simulation
        """

    def initializeReqeustList(self, numberOfClients):
        raise NotImplementedError


#helper classes:-

class distribution:
    def __init__(self, **distribution_parameters):
        """

        :param distribution_parameters: parameters to characterise a distribution, some examples:-

        type=distributionType.constant,value=2 #delta function ?
        type=distributionType.uniform,a=2,b=3 (starting and ending, default=0,1)
        type=distributionType.normal,mean=2,variance=3
        type=distributionType.exponential,lambda_val=2

        usage: d=distribution(type=distributionType.exponential,lambda_val=2)
        will create an object of exponential distribution.
        Each distribution will have a method sample() which will return a RV variable from that distribution
        """
        s=self
        self.__type=distribution_parameters['type']

        if s.__type==distributionType.constant:
            s.__value=float(distribution_parameters['value'])

        elif s.__type==distributionType.uniform:
            if len(distribution_parameters)==1: #a and b not specified, assuming uniform in [0,1]
                s.__a=0.0
                s.__b=1.0
            elif len(distribution_parameters)==3: #a and b both specified for uniform distribution
                s.__a=float(distribution_parameters['a'])
                s.__b=float(distribution_parameters['b'])
            else:
                raise Exception('Improper number of arguments for uniform distribution')

        elif s.__type==distributionType.normal:
            s.__mean=float(distribution_parameters['mean'])
            s.__variance=float(distribution_parameters['variance'])

        elif s.type==distributionType.exponential:
            s.__lambda=float(distribution_parameters['lambda_val'])

        else:
            raise Exception('unknown distribution')

    def sample(self):
        s=self
        if s.__type==distributionType.constant:
          return s.__value

        elif s.__type==distributionType.uniform:
            return random.uniform(s.__a,s.__b)

        elif s.__type==distributionType.normal:
            return random.gauss(s.__mean,(s.__variance)**2)

        elif s.type==distributionType.exponential:
            return -(1.0/s.__lambda)*math.log(1.0-random.uniform(0,1)) #by default log is with base e

        else:
            raise Exception('Distribution not handled by sample()')





# #dictionaries / enums
class eventTypes:
    """
    quantumExpired and scheduleNextRequest are separate events to simulate context switch overhead. when quantumExpired occurs,the CPU will remain idle for a time equal to context swicth time
    """
    arrival = 1  #try to allocate a cpu if any cpu is idle, else queue the request
    departure = 2  #will also mark start of think time
    quantumExpired = 3  #start of context swicth overhead
    scheduleNextRequest = 4  #context swicth overhead done, schedule next request. this will either add a departure event or quantumExpired event
    timeout = 5  #hanle request timeout. if this event occurs create a new event and let the timed out request circulate in the system, when this event departs, drop it from circulation. if on departure we see a request which hasnt timed out, remove its timeout event from event list


class processorState:
    idle = 0
    busy = 1


class requestState:
    thinking = 0
    executing = 1
    buffered = 2
    inRunQueueButNotExecuting = 3


class distributionType:
    constant = 0
    uniform = 1
    normal = 2
    exponential = 3


#main code
system=system(distribution(type=distributionType.uniform,a=10,b=16),distribution(type=distributionType.uniform,a=4,b=8),distribution(type=distributionType.uniform(a=10,b=20)),1,2,4,10,10)
simulation=simulation(6,system,2)