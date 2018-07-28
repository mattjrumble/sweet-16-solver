# Find a solution to a puzzle like the following:
#   Find values for A, B, ..., O, P, (let's call them stones), where each stone has a unique integer value between 1 and 16 inclusive.
#   We are given that A+B=C, E+F=G, J+K=L, M+N=O, E+I=M, B*F=J, C-G=K, H-L=P (using the letters interchangeably to mean either the stone or the
#   value of the stone, depending on the context).
# In general, find a solution to the following puzzle:
#   Find values for stones A_1, A_2, ..., A_N, where each stone has a unique integer value between 1 and N inclusive.
#   We are given a set of constraints of the form f(A_x, A_y)=A_z, where A_x, A_y, A_z are different stones, and f is some function between integers.

from copy import copy

class operations:
    def __init__(self):
        self.ops = set()
    def add(self, op):
        self.ops.add(op)
    def get(self, symbol):
        for op in self.ops:
            if op.symbol == symbol:
                return op
        return None

class operation:
    def __init__(self, symbol, func):
        self.symbol = symbol
        self.func = func
        # Generate all possible valid function results as a set of 3-tuples (e.g. given a multiplication function, returns a set of tuples including (2, 3, 6))
        self._vals = set()
        for i in range(1, N+1):
            for j in range(1, N+1):
                if i == j:
                    continue
                k = self.func(i, j)
                if i == k or j == k:
                    continue
                if k not in range(1, N+1):
                    continue
                self._vals.add((i, j, k))
    def __str__(self):
        return 'Operation {}: '.format(self.symbol) + '\n' + str(self._vals)
    def get_vals(self):
        return self._vals.copy()

class stones:
    def __init__(self):
        self.stones = []
        self.i = 0
    def __iter__(self):
        self.i = 0
        return copy(self)
    def __next__(self):
        if self.i < len(self.stones):
            i = self.i
            self.i += 1
            return self.stones[i]
        else:
            raise StopIteration
    def __getitem__(self, key):
        if key >= 0 and key < len(self.stones):
            return self.stones[key]
        else:
            raise IndexError
    def __len__(self):
        # Sum of the number of possible values over all stones
        sum = 0
        for stone in self.stones:
            sum += len(stone)
        return sum
    def __str__(self):
        tmp = []
        for stone in self.stones:
            tmp.append(str(stone))
        return '\n'.join(tmp)
    def str_short(self):
        tmp = ''
        for stone in self.stones:
            tmp += stone.label + str(stone.get_vals()) + ', '
        return tmp[:-2]
    def add(self, stone):
        self.stones.append(stone)
        if len(self.stones) > N:
            raise Exception('More than N stones added')
    def get(self, label):
        for stone in self.stones:
            if stone.label == label:
                return stone
        return None

class stone:
    def __init__(self, label):
        self.label = label
        self._vals = list(range(1, N+1)) # List of possible values the stone may have
        self.constraints_info = [] # Info about all constraints the stone is involved in, and the index of the stone in each constraint's 3-tuple
    def __len__(self):
        return len(self._vals)
    def __str__(self):
        return 'Stone {}: {}'.format(self.label, str(self._vals))
    def get_vals(self):
        return self._vals.copy()
    def set_val(self, val):
        # Set the stone values to just the given value. Typically used for making a guess. We intentionally don't want to
        # propagate the information until the value has been set. This is because it wouldn't work to remove values from this stone
        # until we're left with the one we want. If we were going from [X, Y, Z] TO [Z], it's possible removing X first would
        # propagate and produce a solution where this stone has value Y. Whilst it's good that finds a solution, it's confusing
        # since the point of the function was to set this value to Z. So we don't do that.
        self._vals = [val]
        # Propagate uniqueness to all other stones
        for stone in STONES:
            if stone == self: continue
            stone.remove_val(val)
        # Propagate this new value to the constraints
        self.propagate()
    def set_vals(self, vals):
        # For reseting values after an unsuccessful guess
        self._vals = vals.copy()
    def remove_val(self, val):
        if val in self._vals:
            self._vals.remove(val)
            # If last val left, propagate uniqueness to all other stones
            if len(self) == 1:
                last_val = self._vals[0]
                for stone in STONES:
                    if stone == self: continue
                    stone.remove_val(last_val)
            # If no val left, raise a custom exception
            elif len(self) == 0:
                raise NoSolutions()
            self.propagate()
    def remove_vals(self, vals):
        for val in vals: self.remove_val(val)
    def propagate(self):
        # Look through the possible 3-tuples of each constraint involving this stone. Do any of them have a value for 
        # this stone that's not in our set of possible values? If so, remove that possible 3-tuple from the constraint.
        for info in self.constraints_info:
            constraint = info.constraint
            i = info.i
            for vals in constraint.get_vals():
                if vals[i] not in self._vals:
                    constraint.remove_val(vals)
            
class constraint_info:
    # Information stored by a stone about a constraint that involves it, and the corresponding index in that constraint's 3-tuple
    def __init__(self, constraint, i):
        self.constraint = constraint
        self.i = i
    def __str__(self):
        return 'Constraint = {}\nIndex = {}'.format(self.constraint.str_short(), self.i)

class constraints:
    def __init__(self):
        self.constraints = []
        self.i = 0
    def __iter__(self):
        self.i = 0
        return copy(self)
    def __next__(self):
        if self.i < len(self.constraints):
            i = self.i
            self.i += 1
            return self.constraints[i]
        else:
            raise StopIteration
    def __getitem__(self, key):
        if key >= 0 and key < len(self.constraints):
            return self.constraints[key]
        else:
            raise IndexError
    def __len__(self):
        sum = 0
        for constraint in self.constraints:
            sum += len(constraint)
        return sum
    def __str__(self):
        tmp = []
        for constraint in self.constraints:
            tmp.append(str(constraint))
        return '\n'.join(tmp)
    def add(self, constraint):
        self.constraints.append(constraint)

class constraint:
    # Information about a constraint corresponding to a 3-tuple of stones. Contains the possible values of the 3-tuple of stones,
    # and the information about the constraint itself (e.g. X+Y=Z)
    def __init__(self, label1, label2, label3, op_symbol):
        labels = [label1, label2, label3]
        self.stones = []
        for i in range(3):
            self.stones.append(STONES.get(labels[i]))
            if self.stones[i] is None: raise ValueError("Stone not found for label '{}'".format(labels[i]))
            self.stones[i].constraints_info.append(constraint_info(self, i))

        self.op = OPERATIONS.get(op_symbol)
        if self.op is None: raise ValueError("Operation not found for symbol '{}'".format(op_symbol))

        self._vals = self.op.get_vals()
    def __len__(self):
        return len(self._vals)
    def __str__(self):
        return self.str_short() + '\n' + str(self._vals)
    def str_short(self):
        return 'Constraint: ' + str(self.stones[0].label) + ' ' + self.op.symbol + ' ' + str(self.stones[1].label) + ' = ' + str(self.stones[2].label)
    def get_vals(self):
        return self._vals.copy()
    def set_vals(self, vals):
        # For reseting values after an unsuccessful guess
        self._vals = vals.copy()
    def remove_val(self, val):
        if val in self._vals:
            self._vals.remove(val)
            # If no val left, raise a custom exception
            if len(self) == 0:
                raise NoSolutions()
            self.propagate()
    def propagate(self):
        # Look through each stone's possible values. Are any of them not in any of the possible 3-tuples we have? If so, remove that possible
        # value from the stone.
        for i in range(3):
            stone = self.stones[i]
            for val in stone.get_vals():
                found = False
                for tuples in self._vals:
                    if tuples[i] == val:
                        found = True
                        break
                if not found:
                    stone.remove_val(val)

class backup_info:
    def __init__(self, obj, vals):
        self.obj = obj
        self.vals = vals
                    
class SolutionFound(Exception):
    pass

class NoSolutions(Exception):
    pass

def debug(msg, depth=0):
    if DEBUG:
        for line in str(msg).splitlines():
            print('    ' * depth + line)
 
def print_all():
    print('******************************')
    print(CONSTRAINTS)
    print(STONES)
    print('Total constraint possibilities: ' + str(len(CONSTRAINTS)))
    print('Total stone possibilities: ' + str(len(STONES)))
    print('******************************')

def check_if_solved():
    solution = True
    for stone in STONES:
        if len(stone) != 1:
            solution = False
            break
    if solution: raise SolutionFound

def backup_vals(obj):
    result = []
    for item in obj:
        result.append(backup_info(item, item.get_vals()))
    return result
 
def restore_vals(backup):
    for item in backup:
        item.obj.set_vals(item.vals)
 
def guess_vals(depth):
            
    # Repeat guessing values until we're getting no new information from it
    while True:
        count_before = len(STONES)
        for stone in STONES:
            for val in stone.get_vals():
                if len(stone) != 1:

                    debug('Trying {} for stone {}...'.format(str(val), stone.label), depth)
                    
                    # Backup the values before we make a guess
                    stones_vals_bk = backup_vals(STONES)
                    constraints_vals_bk = backup_vals(CONSTRAINTS)

                    try:
                        stone.set_val(val)
                        check_if_solved()
                        # We didn't find a solution, nor did we find zero solutions, so we have no new information
                        debug('Nothing conclusive', depth)
                        if depth < CUR_MAX_DEPTH:
                            # Go deeper!
                            guess_vals(depth+1)
                        restore_vals(stones_vals_bk)
                        restore_vals(constraints_vals_bk)
                    except NoSolutions:
                        # We found zero solutions, so this value isn't valid
                        debug('Led to zero solutions - removed!', depth)
                        restore_vals(stones_vals_bk)
                        restore_vals(constraints_vals_bk)
                        stone.remove_val(val)
                        debug(STONES.str_short(), depth)
                        check_if_solved()
                      
        if len(STONES) == count_before:
            break
            debug('Stop guessing these values', depth)
        else:
            debug('Guessing these values again...', depth)

# Declare the problem    
N = 16
ABS_MAX_DEPTH = 5 # The maximum depth of searching (however, it may not be necessary to go so deep)
DEBUG = False

OPERATIONS = operations()
OPERATIONS.add(operation('+', lambda x, y: x+y))
OPERATIONS.add(operation('-', lambda x, y: x-y))
OPERATIONS.add(operation('*', lambda x, y: x*y))
def division(x, y):
    if x % y == 0:
        return int(x/y)
    else:
        return 0
OPERATIONS.add(operation('/', division))

STONES = stones()
for i in range(ord('A'), ord('A') + N): STONES.add(stone(chr(i)))

CONSTRAINTS = constraints()
CONSTRAINTS.add(constraint('B', 'C', 'D', '+'))
CONSTRAINTS.add(constraint('F', 'G', 'H', '/'))
CONSTRAINTS.add(constraint('J', 'K', 'L', '-'))
CONSTRAINTS.add(constraint('M', 'N', 'O', '*'))
CONSTRAINTS.add(constraint('E', 'I', 'M', '-'))
CONSTRAINTS.add(constraint('F', 'J', 'N', '-'))
CONSTRAINTS.add(constraint('G', 'K', 'O', '*'))
CONSTRAINTS.add(constraint('H', 'L', 'P', '+'))


try:
    # Kick off the initial propagation. We already used all the information about 3-tuples of stones being involved in operations (that restricted the
    # initial possible 3-tuple values of the constraints). So now we propagate that information to the stones themselves, and any changes in them will
    # propagate to other constraints the stones are a part of. This continues until all information is propagated.
    for constraint in CONSTRAINTS: constraint.propagate()
    check_if_solved()

    # If the problem isn't trivially solveable by just propagating information, we need to start guessing values.
    CUR_MAX_DEPTH = 1
    while CUR_MAX_DEPTH <= ABS_MAX_DEPTH:
        print('Searching with max depth {}...'.format(CUR_MAX_DEPTH))
        debug(STONES.str_short())
        guess_vals(depth=1)           
        CUR_MAX_DEPTH += 1

    # If we don't find any solution in the searching process, we'll never raise a SolutionFound, and will end up here instead.
    print('No solution found, this is as far as I got:')
    print(STONES.str_short())
    print(CONSTRAINTS)

except SolutionFound:
    # If we find a valid solution at any point in the searching process, we'll pop out to here.
    print('Solution found!')
    print(STONES.str_short())
    print(CONSTRAINTS)

except NoSolutions: 
    print('No solutions exist')
    
