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

class MedianStruct(object):
    '''A data structure that maintains the median in O(n log n).
    
    update() is O(1) typical, O(log n) worst case
    median(), min(), and max() are O(1)
    '''
    def __init__(self):
        # Heap of values higher than the median
        self.high = MinHeap()
        # Heap of values lower than the median
        self.low = MaxHeap()
        
        self._min = None
        self._max = None
        self._median = None

    def update(self, value):
        '''Add a new value, maintaining the min and max heaps.
        
        Raises RuntimeError on update if the heap have invalid balance.'''
        # Update the min and max
        if (value < self._min) or (self._min is None):
            self._min = value
        if value > self._max:
            self._max = value

        # Push the value onto the appropriate heap (equal defaults to high).
        if value < self._median:
            update_heap = self.low
            static_heap = self.high
        else:
            update_heap = self.high
            static_heap = self.low

        update_heap.push(value)
        balance = len(update_heap) - len(static_heap)
        if balance == 0:
            # The push balanced the heaps, so average the roots
            self._median = (static_heap.root() + update_heap.root()) / 2.0
        elif balance == 1:
            # The push was onto a balanced heap, so use the updated heap's root
            self._median = update_heap.root()
        elif balance == 2:
            # The push was onto an already larger heap, so rebalance the heaps
            static_heap.push(update_heap.pop())
            # Since we just rebalanced, the median is the average of the roots
            self._median = (static_heap.root() + update_heap.root()) / 2.0
        else:
            # We should never get here...
            raise RuntimeError('Invalid heap balance')

    def median(self):
        '''Median of the current dataset. Returns None on empty.'''
        return self._median

    def min(self):
        '''Minimum of the current dataset. Returns None on empty.'''
        return self._min

    def max(self):
        '''Maximum of the current dataset. Returns None on empty.'''
        return self._max

def _test_shuffled_range(count):
    import random
    vals = range(count)
    if count == 0:
        exp = None
    elif count%2:
        exp = count//2
    else:
        exp = (count//2 + (count//2)-1) / 2.0
    random.shuffle(vals)
    return _test(vals)

def _assert_equal(expected, result, name = ''):
    error_string = name + 'Error exp: %s, got: %s'%(str(expected), str(result))
    assert expected == result, error_string

def _test(values, expected_median = None):
    # Get the result from MedianStruct
    start = time.time()
    mh = MedianStruct()
    map(mh.update, values)
    result = mh.median()
    elapsed = time.time() - start
    
    # If an expected result is not provided, get the result naively
    if expected_median is None:
        # Make sure the sort comes after we've updated the MedianStruct
        values.sort()
        if len(values) == 0:
            exp = None
        elif len(values)%2:
            exp = values[len(values)//2]
        else:
            exp = (values[len(values)//2] + values[(len(values)//2)-1]) / 2.0
    else:
        exp = expected_median
    _assert_equal(exp, result, 'Median')

    try:
        exp_min = min(values)
        exp_max = max(values)
    except ValueError:
        exp_min = None
        exp_max = None
    _assert_equal(exp_min, mh.min(), 'Min')
    _assert_equal(exp_max, mh.max(), 'Max')
    
    assert abs(len(mh.low) - len(mh.high)) <= 1, 'Corrupt MedianStruct!'

    return elapsed

if __name__ == "__main__":
    import time
    import cProfile
    
    map(_test_shuffled_range, [0, 1, 3, 10, 30, 61])
    _test([-5000, 60, 25, 40000, 394875, -28634876, -20, -13, -23746], -13)
    _test(range(50000), 24999.5)
    _test(range(49999), 24999)
    print 'Self test passed!'
    
    print 'Profiling...'
    _test(range(100001), 50000)
    _test(range(200001), 100000)
    for x in [49999, 50000, 100000, 100001, 200000, 200001]:
        print '%d values: %f seconds'%(x, _test_shuffled_range(x))
    
    cProfile.run('_test(range(200001), 100000)')