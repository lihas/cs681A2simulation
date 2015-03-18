__author__ = 'neo'

import math

class eventList:
    """
    A min heap of events
    """

    def __init__(self):
        self.heap = []


    def addEvent(self, event):
        """
        add event 'event', which is of type event to minheap of events
        """
        raise NotImplementedError

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
        if node < len(self.heap) and node>=0:
            return True
        else:
            return False

    #end of heapify helper functions

    def heapifyAtposition(self, node,db=0):
        s = self
        if db==1:
            print node
        if self.exists(self.rightChildIndex(node)) and self.exists(self.leftChildIndex(node)):
            if self.heap[self.rightChildIndex(node)] < self.heap[node]:
                s.swap(s.rightChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
            elif s.heap[s.leftChildIndex(node)] < s.heap[node]:
                s.swap(s.leftChildIndex(node), node)
                s.heapifyAtposition(s.leftChildIndex(node))
                return True
            else:
                return False
        elif s.exists(s.rightChildIndex(node)):
            if s.heap[s.rightChildIndex(node)] < s.heap[node]:
                s.swap(s.rightChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
        elif s.exists(s.leftChildIndex(node)):
            if s.heap[s.leftChildIndex(node)] < s.heap[node]:
                s.swap(s.leftChildIndex(node), node)
                s.heapifyAtposition(s.rightChildIndex(node))
                return True
        else:
            return False


    def addToHeap(s, value):
        s.heap.append(value)
        nodeIndex = len(s.heap) - 1

        while s.exists(s.parentIndex(nodeIndex)):
            if not s.heapifyAtposition(s.parentIndex(nodeIndex),1):
                break
            else:
                nodeIndex = s.parentIndex(nodeIndex)


    def heapify(self):
        """
        :rtype : None
        """
        for i in range(len(self.heap) - 1, -1, -1):
            self.heapifyAtposition(i)

a=eventList()

#a.heap=[2,1,5,3,4,10,99,0,-1,23,22,21,19]
a.heapify()

print a.heap
a.addToHeap(-2)
print a.heap

a.addToHeap(4)
print a.heap

for i in [2,1,5,3,4,10,99,0,-1,23,22,21,19]:
    a.addToHeap(i)

print a.heap
