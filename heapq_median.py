import heapq

def heap_view(tree, max_level = 4):
    '''A horizontal ascii tree of a specified maximum number of levels.'''
    # The 1-based depth is the bit length of the 1-based node's index
    depth = lambda n: (n+1).bit_length() - 1

    # Generate the in-order traversal order of the node indexes for the
    # specified number of levels
    ordered_indexes = []
    for level in range(max_level + 1):
        min_index = (2**level)-1
        level_indexes = range(min_index, 2*(min_index) + 1)
        # Insert the node indexes for the next level on even array indexes
        for (n, node_index) in enumerate(level_indexes):
            ordered_indexes.insert(2*n, node_index)

    # Start building the lines (one line per node)
    ret = []
    for n in ordered_indexes:
        try:
            # Indent the node based on its depth
            ret.append('    '*depth(n) + str(tree[n]))
        except IndexError:
            # Just skip missing nodes
            pass
    # Use an ellipsis to indicate that the tree was truncated
    if len(tree) > len(ordered_indexes):
        ret.append('    '*depth(len(ordered_indexes)) + '...')
    return '\n'.join(ret)

class Heap(object):
    '''A heap implemented using heapq.'''
    def __init__(self):
        self.values = []

    def push(self, value):
        '''Add a node to the heap.'''
        heapq.heappush(self.values, value)

    def pop(self):
        '''Remove and return the root node from the heap.'''
        return heapq.heappop(self.values)

    def root(self):
        '''Return the root node of the heap without removal.'''
        return self.values[0]

    def __len__(self):
        return len(self.values)

    def __str__(self):
        return heap_view(self.values)

class MinHeap(Heap):
    '''Wrapper for Heap base class, which is already a min heap.'''
    pass

class MaxHeap(Heap):
    '''Negates input/output of Heap base class to implement a max heap.'''
    def push(self, value):
        # Push the negative so the largest value is on top of the heap
        # This is required because heapq is a min heap
        Heap.push(self, -value)

    def pop(self):
        # Don't forget the inverse of the negation we made on entry
        return -Heap.pop(self)

    def root(self):
        # Don't forget the inverse of the negation we made on entry
        return -Heap.root(self)

class MedianHeap(object):
    '''A heap that retrieves the median of streamed data in O(n log n).
    
    update() is O(1) typical, O(log n) worst case
    median() is O(1)
    '''
    def __init__(self):
        # Heap of values higher than the median
        self.high = MinHeap()
        # Heap of values lower than the median
        self.low = MaxHeap()

    def update(self, value):
        '''Add a new value, maintaining the heap invariant.'''
        # Get the current median
        median = self.median()

        # Push the value onto the appropriate heap (equal defaults to high)
        if value < median:
            self.low.push(value)
        else:
            self.high.push(value)

        # Keep the heaps balanced in size by popping the top value from the 
        # larger heap and pushing it onto the smaller heap
        if len(self.high) < len(self.low):
            self.high.push(self.low.pop())
        elif len(self.high) > len(self.low):
            self.low.push(self.high.pop())

    def median(self):
        '''Median of the current dataset. Returns None on empty heap.'''
        # The median is the root of the larger heap
        if len(self.high) < len(self.low):
            median = self.low.root()
        elif len(self.high) > len(self.low):
            median = self.high.root()
        # If the lists are the same length, the median is the average of
        # the two middle elements
        else:
            try:
                median = (self.low.root() + self.high.root()) / 2.0
            except IndexError:
                # There are no values in either heap (initial condition)
                median = None

        return median

def test_shuffled_range(count):
    import random
    mh = MedianHeap()
    vals = range(count)
    if len(vals) == 0:
        exp = None
    elif (len(vals) % 2):
        exp = vals[len(vals)//2]
    else:
        exp = (vals[len(vals)//2] + vals[(len(vals)//2)-1]) / 2.0
    random.shuffle(vals)
    for x in vals:
        mh.update(x)
    assert mh.median() == exp, 'exp: %f, got: %f'%(exp, mh.median())
    assert abs(len(mh.low) - len(mh.high)) <= 1, 'Corrupt MedianHeap!'

def test(values, expected):
    mh = MedianHeap()
    for x in values:
        mh.update(x)
    values.sort()
    if len(values) == 0:
        exp = None
    elif (len(values) % 2):
        exp = values[len(values)//2]
    else:
        exp = (values[len(values)//2] + values[(len(values)//2)-1]) / 2.0
    assert mh.median() == exp, 'exp: %f, got: %f'%(exp, mh.median())
    assert abs(len(mh.low) - len(mh.high)) <= 1, 'Corrupt MedianHeap!'
    

if __name__ == "__main__":
    map(test_shuffled_range, [0, 1, 3, 10, 30, 61])
    test([-5000, 60, 25, 40000, 394875, -28634876, -20, -13, -23746], -13)
    print 'Self test passed!'