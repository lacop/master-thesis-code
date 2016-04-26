# Sample to show universality of this library
#
# Implements the well known N-Queens puzzle
# See https://en.wikipedia.org/wiki/Eight_queens_puzzle for details.
#
# Explanation of this code can be found in the text of the thesis.

from instance import *
instance = Instance()

def FalseVector(N):
    return ConstantVector([False]*N)

# Board size
N = 8
board = [BitVector(N) for _ in range(N)]

# At least one 1 in all rows
rots = []
for row in board:
    rot = FalseVector(N)
    for i in range(N):
        rot |= CyclicLeftShift(row, i)
    rot.bits = [True]*N
    rots.append(rot)

# At most one 1 in all rows
for row in board:
    rot = FalseVector(N)
    for i in range(1, N):
        rot |= row & CyclicLeftShift(row, i)
    rot.bits = [False]*N
    rots.append(rot)

# At most one 1 on diagonals
for i in range(N):
    rot = FalseVector(N)
    for j in range(N):
        if i != j:
            rot |= board[i] & LeftShift(board[j], j-i)
            rot |= board[i] & LeftShift(board[j], i-j)
    rot.bits = [False]*N
    rots.append(rot)

# 1 in all columns
row_or = FalseVector(N)
for row in board:
    row_or |= row
row_or.bits = [True]*N

instance.emit(board + [row_or] + rots)
instance.solve(['minisat'])

for row in board:
    print(''.join(('#' if x else '.') for x in row.getValuation(instance)))