__author__ = 'neo'

import random
from collections import deque

import math
import ConfigParser

printMetrics = True

class Clock():
    def __init__(self,time=0):
        self.__time = time
    def getTime(self):
        return self.__time
    def setTime(self,time):
        self.__time=time

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
        self.serviceTimeDist = serviceTimeDist
        self.thinkTimeDist = thinkTimeDist
        self.timeoutDist = timeoutDist
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

    def UpdateRemainingServiceTime(self, updateTime):
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
            return -1
        else:
            self.requestQueue.append(request)

    def DequeueRequest(self):
        try:
            request = self.requestQueue.popleft()
        except IndexError:
            raise Exception("Request Buffer is empty!")
        return request

    def isEmpty(self):
        return len(self.requestQueue) == 0



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
    def FreeThread(self, request, processor):
        assert isinstance(request,Request),'Expecting an object of class Request'
        assert isinstance(processor,Processor),'Expecting an object of class processor'

        reqId=request.reqId
        procId=processor.procId
        if self.numBusyThreads is 0:
            raise Exception("No allocated threads in the system!")
        else:
            try:
                threadId = self.threadList.index((reqId, procId))
            except:
                raise Exception("Thread with reqId and procId not found")
            departingRequest=processor.RemoveRequest()
            self.threadList[threadId] = (-1, -1)
            self.numBusyThreads -= 1
            return departingRequest

    # To allocate a thread. Find a free thread (-1, -1) and allocate it.
    def AllocateThread(self, request, processor):
        assert isinstance(request,Request),'Expecting an object of class Request'
        assert isinstance(processor,Processor),'Expecting an object of class processor'

        reqId=request.reqId
        procId=processor.procId
        if self.numBusyThreads == self.maxNumThreads:
            return -1
        else:
            try:
                threadId = self.threadList.index((-1, -1))
            except:
                raise Exception("Could not find a free thread in the system")

            processor.AddRequest(request)
            self.threadList[threadId] = (reqId, procId)
            self.numBusyThreads += 1
            return threadId


processorState = {'idle': 0, 'busy': 1,'contextSwitch':2}


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

    def getRunningRequest(self):
        return self.runQueue[0]

    def runQueueEmpty(self):
        return len(self.runQueue)==0

    def AddRequest(self, request):
        self.runQueue.append(request)

    def RemoveRequest(self):
        try:
            request = self.runQueue.popleft()
        except IndexError:
            raise Exception("Processor's runqueue is empty!")
        return request

    # Schedule the next job on the runqueue in a Round Robin fashion.
    def ScheduleNext(self):
        prevRequest = self.RemoveRequest()
        self.AddRequest(prevRequest)
        return prevRequest


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
        @data:          For an event of type Quantum Expired, Schedule Next,
                        and departure, this stores the processor Id on which
                        the event occurs. For an event of type Arrival, this
                        stores the request Id. For a timeout, this stores the
                        request Id.
        @cancelled
                        Interpret this differently in the context of different event handlers.
                        Arrival: if cancelled==1, do not create a timeout event for the request, as it is a request which was picked from buffer in HandleDeparture and not a new request from client. To handle the hackish way we are scheduling an event picket from reqBuffer in HandleDeparture, where we just schedule it's arrival at the current time. without this part of code , there were multiple timeoutEvents that ere being created for the same event if the event were moved to buffer in HandleArrival on not finding a free thread.
                        Timeout: if cancelled==1, do no execute the timeout event, as the request has already departed
    """

    def __init__(self, timeStamp, eventType, data,cancelled=0): #cancelled=0 was added to handle the hackish way we are scheduling an event picket from reqBuffer in HandleDeparture, where we just schedule it's arrival at the current time. without this part of code it there were multiple timeoutEvents that ere being created for the same event if the event were moved to buffer in HandleArrival on not finding a free thread.
        self.__id = None
        self.timeStamp = timeStamp
        self.eventType = eventType
        self.data = data
        self.cancelled = cancelled


class EventList:
    """
    A min heap of events
    """

    def __init__(self):
        self.heap = []
        self.id = 0  # will give a unique id to each event

    @property
    def IsEmpty(self):
        return len(self.heap)==0

    def AddEvent(self, event):
        """
        add event 'event', which is of type event to minheap of events
        assign an id to it
        return the assigned id
        """
        assert isinstance(event,Event),'event object not of event type'

        event.__id = self.id
        self.id += 1
        self.AddToHeap(event)
        return event.__id

    def RemoveEvent(self, eventType, requestId):
        for i in range(len(self.heap)):
            if self.heap[i].eventType == eventType and self.heap[i].data == requestId:
                del self.heap[i]
                break
        self.Heapify()

    def PopEvent(self):
        """
        Remove and return next event with least timestamp
        """
        return self.PopFromHeap()

    def searchTimeoutEvent(self,requestId):
        for i in self.heap:
            if i.eventType==eventType['timeout'] and i.data==requestId:
                return i

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
            if self.heap[self.RightChildIndex(node)].timeStamp <= self.heap[node].timeStamp and self.heap[self.RightChildIndex(node)].timeStamp <= self.heap[self.LeftChildIndex(node)].timeStamp:
                s.Swap(s.RightChildIndex(node), node)
                s.HeapifyAtposition(s.RightChildIndex(node))
                return True
            elif s.heap[s.LeftChildIndex(node)].timeStamp <= s.heap[node].timeStamp and s.heap[s.LeftChildIndex(node)].timeStamp <= s.heap[s.RightChildIndex(node)].timeStamp:
                s.Swap(s.LeftChildIndex(node), node)
                s.HeapifyAtposition(s.LeftChildIndex(node))
                return True
            else:
                return False
        elif s.Exists(s.RightChildIndex(node)):
            if s.heap[s.RightChildIndex(node)].timeStamp < s.heap[node].timeStamp:
                s.Swap(s.RightChildIndex(node), node)
                s.HeapifyAtposition(s.RightChildIndex(node))
                return True
        elif s.Exists(s.LeftChildIndex(node)):
            if s.heap[s.LeftChildIndex(node)].timeStamp < s.heap[node].timeStamp:
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
    def PopFromHeap(s):
        if len(s.heap)==1:
            return s.heap.pop()
        elif len(s.heap)==0:
            return False
        else:
            lastElement=s.heap.pop()
            heapRoot=s.heap[0]
            s.heap[0]=lastElement
            s.HeapifyAtposition(0)
        return heapRoot


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

        self.idCtr=1000 #TODO: this is being used by self.getUniqueRequestId(), remove this when that function changes


        self.config = ConfigParser.ConfigParser()
        self.config.read('simulation.cfg')

        self.randomSeed = self.config.getint('System', 'randomSeed')
        self.numClients=self.config.getint('Simulation', 'numClients')

        self.serviceTimeDist = self.GetDistributionObject(self.config, 'ServiceTime')
        self.thinkTimeDist = self.GetDistributionObject(self.config, 'ThinkTime')
        self.timeoutDist = self.GetDistributionObject(self.config, 'Timeout')

        self.system = System(self.serviceTimeDist, self.thinkTimeDist, self.timeoutDist,
                             self.config.getint('System', 'numProcessors'),
                             self.config.getfloat('Processor', 'contextSwitchTime'),
                             self.config.getfloat('Processor', 'timeQuantum'),
                             self.config.getint('System', 'maxThreads'),
                             self.config.getint('System', 'bufferSize'))

        self.eventList = EventList()

        self.requestIdList=[]
        self.requestList=[] #list of requests that are circulating in the system
        self.InitRequestList()


    def InitRequestList(self):
        system=self.system
        currentTime=self.system.clock.getTime()
        for i in range(self.numClients):
            serviceTime=system.serviceTimeDist.sample()
            timeOut=system.timeoutDist.sample()
            timestamp=currentTime
            requestId=i
            arrivalTime=system.thinkTimeDist.sample()

            self.createRequest(requestState['thinking'],timestamp+arrivalTime,requestId,serviceTime,timeOut)
            self.createEvent(currentTime+arrivalTime,eventType['arrival'],requestId) #schedule an arrival event

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
    def start(self):
        return self.jarvis()

    def jarvis(self):
        eventsProcessed=0
        #while(not self.eventList.IsEmpty):
        while(eventsProcessed<10000):
            event=self.eventList.PopEvent()
            self.EventHandler(event)
            eventsProcessed += 1
        return eventsProcessed

    def EventHandler(self, event):
        #update system clock
        self.system.clock.setTime(event.timeStamp)

        if event.eventType==eventType['arrival']:
            self.HandleArrival(event)
        elif event.eventType==eventType['scheduleNext']:
            self.HandleScheduleNext(event)
        elif event.eventType==eventType['quantumExpired']:
            self.HandleQuantumExpired(event)
        elif event.eventType==eventType['timeout']:
            self.HandleTimeout(event)
        elif event.eventType==eventType['departure']:
            self.HandleDeparture(event)
        else:
            raise Exception('Unknown event type')


    # Add a scheduleNext event to the eventList, and update the processors
    # runqueue, decrement remaining service time of request
    def HandleQuantumExpired(self, event):
        if printMetrics:
            print '['+str(event.timeStamp)+']'+" Quantum Expired on Processor " + str(event.data)

        quantum=self.system.timeQuantum
        currentTime=self.system.clock.getTime()

        self.createEvent(currentTime + self.system.contextSwitchTime,
                         eventType['scheduleNext'], event.data)

        prevRequest=self.system.processors[event.data].ScheduleNext()
        try:
            prevRequest.UpdateRemainingServiceTime(quantum)
        except:
            pass
        self.system.processors[event.data].state = processorState['contextSwitch']

    # Add a departure or a quantum expired event based on the remaining
    # service time of the event at the head of the processors run queue.
    def HandleScheduleNext(self, event):
        if printMetrics:
            print '['+str(event.timeStamp)+']'+" Schedule Next on Processor " + str(event.data)

        #debug
        if event.data >100:
            pass

        processor=self.system.processors[event.data]

        if len(processor.runQueue)<=0:
            raise Exception('runQueue Empty for procId . This wasn\'t expected. A scheduleNext automatically implies a non-empty run-queue'+str(processor.procId))

        remTime = processor.runQueue[0].remServiceTime

        request=processor.runQueue[0]
        #print remTime,processor.runQueue[0].serviceTime,request.reqId,processor.procId

        currenTime=self.system.clock.getTime()

        if remTime < self.system.timeQuantum:
            self.createEvent(currenTime + remTime, eventType['departure'],
                             event.data)
        else:
            self.createEvent(currenTime + self.system.timeQuantum,
                             eventType['quantumExpired'], event.data)
        processor.state=processorState['busy']



    def HandleArrival(self,event):
        if printMetrics:
            print '['+str(event.timeStamp)+']'+" Arrival of Request " + str(event.data)

        requestDropped=0 #status flag
        requestInBuffer=False #status flag
        reqId=event.data
        currentTime=self.system.clock.getTime()

        request=filter(lambda x:x.reqId==reqId,self.requestList)

        if len(request)>1:
            raise Exception('Duplicate request Ids in Simulation.requestList')
        else:
            request=request[0]

        idleProcessor=-1
        for i in self.system.processors:
            if i.state==processorState['idle']:
                idleProcessor=i
                break


        if idleProcessor!=-1 :
            #idle processor was found, set it's state to busy, if threadpool not full
            if self.system.threadPool.AllocateThread(request,idleProcessor) == -1:#threadPool full
                if self.system.reqBuffer.QueueRequest(request) == -1:#buffer full
                    self.dropRequest(request)
                    requestDropped=1
                else:
                    requestInBuffer=True
            else:#threadpool not full

                if request.serviceTime < self.system.timeQuantum:
                    self.createEvent(currentTime+request.serviceTime,eventType['departure'],idleProcessor.procId)
                else:
                    self.createEvent(currentTime+self.system.timeQuantum,eventType['quantumExpired'],idleProcessor.procId)
                self.system.processors[idleProcessor.procId].state=processorState['busy']
        else:
            #put request in runqueue of least busy processor
            leastBusyProcessorSize=self.system.threadPool.maxNumThreads
            leastBusyProcessor=None

            for i in self.system.processors:
                if len(i.runQueue) <= leastBusyProcessorSize:
                    leastBusyProcessor=i
                    leastBusyProcessorSize=len(i.runQueue)

            if self.system.threadPool.AllocateThread(request,
                                                     leastBusyProcessor) == -1:
                if self.system.reqBuffer.QueueRequest(
                        request) == -1:
                #threadPool full
                #buffer full
                    self.dropRequest(request)
                    requestDropped=1
                else:
                    requestInBuffer=True

        if requestDropped == 0 and not event.cancelled : #and not event.cancelled was added to handle the hackish way we are scheduling an event picket from reqBuffer in HandleDeparture, where we just schedule it's arrival at the current time. without this part of code it there were multiple timeoutEvents that ere being created for the same event if the event were moved to buffer in HandleArrival on not finding a free thread.
            #if request was not dropped, schedule a timeout event for it
            self.createEvent(request.timeStamp+request.timeout,eventType['timeout'],request.reqId)

    def HandleDeparture(self,event):
        #free thread
        #create a new thread set thread's state to thinking
        #cancel request's timeout event
        #handle case where there are multiple timeout events of a request (when request already recirculates) -- all except one should have their cancel bit set, else raise an error
        #handle timed out request
        # If request Buffer is not empty, pick the next request fomr there.
        #set processor state to idle or contextSwitch
        if printMetrics:
            print '['+str(event.timeStamp)+']'+" Departure of Request " + str(self.system.processors[event.data].getRunningRequest().reqId)

        procId=event.data
        processor=self.system.processors[procId]
        request=processor.getRunningRequest()
        currentTime=self.system.clock.getTime()

        if request.timeout + request.timeStamp > currentTime:
            timedOut = False

        else:
            timedOut = True

        if not timedOut:
            uniqueId=self.getUniqueRequestId()
            serviceTime=self.system.serviceTimeDist.sample()
            timeOut=self.system.timeoutDist.sample()
            arrivalTime=self.system.thinkTimeDist.sample()
            timeStamp=currentTime
            self.createRequest(requestState['thinking'],currentTime+arrivalTime,uniqueId,serviceTime,timeOut)
            self.createEvent(currentTime+arrivalTime,eventType['arrival'],uniqueId)

        if not timedOut:
            if not self.system.reqBuffer.isEmpty():
                nextRequest = self.system.reqBuffer.DequeueRequest()
                self.createEvent(currentTime,eventType['arrival'],nextRequest.reqId,1) # HACK


        #free thread


        self.system.threadPool.FreeThread(request,processor)
        self.requestList.remove(request)
        self.requestIdList.remove(request.reqId)


        if not timedOut:
            #request hasn't timed out
            #event=self.eventList.searchTimeoutEvent(request.reqId)
            self.eventList.searchTimeoutEvent(request.reqId).cancelled=1
            self.eventList.RemoveEvent(eventType['timeout'], request.reqId)

        #set processor state, create schedule next event

        if processor.runQueueEmpty():
            processor.state=processorState['idle']
        else:
            processor.state=processorState['contextSwitch']
            self.createEvent(currentTime+self.system.contextSwitchTime,eventType['scheduleNext'],processor.procId)



    def HandleTimeout(self,event):


        #create new request in thinking state
        if event.cancelled==1: #this timeout event was cancelled since event departed before timeout
            print '['+str(event.timeStamp)+']'+" Timeout(Cancelled) of Request " + str(event.data)
            return

        currentTime=self.system.clock.getTime()

        if printMetrics:
            print '['+str(event.timeStamp)+']'+" Timeout of Request " + str(event.data)

        request=filter(lambda x:x.reqId == event.data,self.requestList)

        if len(request)>1:
            raise Exception('Duplicate request Ids in Simulation.requestList')
        else:
            try:
                request = request[0]
            except:
                pass

        #create new request
        uniqueId=self.getUniqueRequestId()
        serviceTime=self.system.serviceTimeDist.sample()
        timeOut=self.system.timeoutDist.sample()
        arrivalTime=self.system.thinkTimeDist.sample()
        timeStamp=currentTime

        self.createRequest(requestState['thinking'],currentTime+arrivalTime,uniqueId,serviceTime,timeOut)
        self.createEvent(currentTime+arrivalTime,eventType['arrival'],uniqueId)




    def dropRequest(self,request):
            #create new request at client
            #remove event from request queue
            #called when threadpool and buffer are full


        #create new request
        currentTime=self.system.clock.getTime()

        uniqueId=self.getUniqueRequestId()
        serviceTime=self.system.serviceTimeDist.sample()
        timeOut=self.system.timeoutDist.sample()
        arrivalTime=self.system.thinkTimeDist.sample()
        timeStamp=currentTime

        self.createRequest(requestState['thinking'],currentTime+arrivalTime,uniqueId,serviceTime,timeOut)
        self.createEvent(currentTime+arrivalTime,eventType['arrival'],uniqueId)

        #drop older request
        self.requestIdList.remove(request.reqId)
        self.requestList.remove(request)



    def getUniqueRequestId(self):
        #TODO: write a better algo, take care of wrap around
        self.idCtr += 1
        return self.idCtr
        for i in range(len(self.requestIdList)+1):
            if i not in self.requestIdList:
                return i;

    def createRequest(self, requestState, timeStamp, uniqueId, serviceTime, timeOut):
        if uniqueId in self.requestIdList:
            raise Exception('Id already Exists')

        newRequest=Request(requestState,timeStamp,uniqueId,serviceTime,timeOut)
        self.requestList.append(newRequest)
        self.requestIdList.append(uniqueId)
        return newRequest

    def createEvent(self, timeStamp, eventType, data,cancelled=0):
        #cancelled=0 was added to handle the hackish way we are scheduling an event picket from reqBuffer in HandleDeparture, where we just schedule it's arrival at the current time. without this part of code it there were multiple timeoutEvents that ere being created for the same event if the event were moved to buffer in HandleArrival on not finding a free thread.

        if data is None:
            raise Exception("Event Data is None!")
        newEvent=Event(timeStamp,eventType,data,cancelled)
        self.eventList.AddEvent(newEvent)
        return newEvent


print Simulation().start()