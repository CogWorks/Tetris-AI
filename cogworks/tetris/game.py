import numpy as np
import collections

from copy import deepcopy

class Zoid:

    def __init__(self, name, shape, rots):
        self.name = name
        self.shapes = tuple(np.rot90(shape, k=i) for i in range(0, rots))

    def __repr__(self):
        return 'Zoid.{}'.format(self.name)

    def __len__(self):
        return len(self.shapes)

    def __getitem__(self, rot):
        return self.shapes[rot]

def enum(**kwargs):
    return collections.namedtuple('enum', kwargs)(**kwargs)

zoids = enum(
    classic=enum(
        I=Zoid('I', np.array([[1, 1, 1, 1]], dtype=np.bool_), 2),
        T=Zoid('T', np.array([[1, 1, 1], [0, 1, 0]], dtype=np.bool_), 4),
        L=Zoid('L', np.array([[1, 1, 1], [1, 0, 0]], dtype=np.bool_), 4),
        J=Zoid('J', np.array([[1, 1, 1], [0, 0, 1]], dtype=np.bool_), 4),
        O=Zoid('O', np.array([[1, 1], [1, 1]], dtype=np.bool_), 1),
        Z=Zoid('Z', np.array([[1, 1, 0], [0, 1, 1]], dtype=np.bool_), 2),
        S=Zoid('S', np.array([[0, 1, 1], [1, 1, 0]], dtype=np.bool_), 2),
    ),
)

del enum

class Board:

    def __init__(self, rows, cols, zero=True):
        if zero:
            self.data = np.zeros((rows, cols), dtype=np.bool_)
            self.heights = [0] * cols
        else:
            self.data = np.empty((rows, cols), dtype=np.bool_)

    def rows(self):
        return self.data.shape[0]

    def cols(self):
        return self.data.shape[1]

    def row(self, row):
        return self.data[row]

    def col(self, col):
        return self.data[::, col]

    def height(self, col):
        return self.heights[col]

    def imprint(self, orient, row, col):
        self.data[row:row+orient.shape[0], col:col+orient.shape[1]] |= orient
        for c in range(0, orient.shape[1]):
            self.heights[col + c] = self.rows() - row - np.nonzero(orient[::, c])[0][0]

    def overlaps(self, orient, row, col):
        if row < 0 or col < 0:
            return True
        elif row + orient.shape[0] > self.rows() or col + orient.shape[1] > self.cols():
            return True
        else:
            return np.any(self.data[row:row+orient.shape[0], col:col+orient.shape[1]] & orient)

    def full(self):
        return {r for (r, full) in enumerate(np.all(self.data, axis=1)) if full}

    def clear(self, rows):
        self.data = np.insert(np.delete(self.data, list(rows), 0), 0, np.zeros((len(rows), self.cols()), dtype=np.bool_), axis=0)
        for c in range(0, self.cols()):
            nonzero = np.nonzero(self.col(c))[0]
            if len(nonzero) > 0:
                self.heights[c] = self.rows() - nonzero[0]
            else:
                self.heights[c] = 0

    def __getitem__(self, pos):
        return self.data[pos]

    def __repr__(self):
        return "{}x{} Board@{:#x}".format(self.rows(), self.cols(), id(self))

    def __str__(self):
        return '\n'.join([''.join(['#' if self[i,j] else '.' for j in range(0, self.cols())]) for i in range(0, self.rows())])

    def __deepcopy__(self, memo):
        if self in memo:
            return self

        clone = Board(self.rows(), self.cols(), zero=False)
        np.copyto(clone.data, self.data)
        clone.heights = list(self.heights)
        memo[self] = clone
        return clone

class State:

    CLEARED_POINTS = (0, 40, 100, 300, 1200)

    class Delta:
        def __init__(self, zoid, rot, row, col, cleared):
            self.zoid = zoid
            self.rot = rot
            self.row = row
            self.col = col
            self.cleared = cleared

    def __init__(self, prev, board, cleared=None, score=0, delta=None):
        self.prev = prev
        self.board = board
        self.cleared = cleared
        self.score = score
        self.delta = delta

        if self.prev is not None:
            self.CLEARED_POINTS = self.prev.CLEARED_POINTS
        if self.cleared is None:
            self.cleared = collections.defaultdict(int)

    def __getstate__(self):
        deltas = []
        ancestor = self
        while ancestor.prev is not None:
            d = ancestor.delta
            deltas.append((d.zoid, d.row, d.col, d.rot))
            ancestor = ancestor.prev

        return (ancestor.board, ancestor.cleared, ancestor.score, ancestor.CLEARED_POINTS, deltas)

    def __setstate__(self, state):
        board, cleared, score, POINTS, deltas = state
        prev = State(None, board, cleared=cleared, score=score, delta=None)
        prev.CLEARED_POINTS = POINTS
        while deltas:
            next = prev.future(*deltas.pop())
            prev = next
        self.prev = prev.prev
        self.board = prev.board
        self.cleared = prev.cleared
        self.score = prev.score
        self.delta = prev.delta

    def lines_cleared(self, simultaneously=None):
        if simultaneously is not None:
            return self.cleared[simultaneously]

        return sum(count * times for (count, times) in self.cleared.items())

    def level(self):
        return int(self.lines_cleared() / 10)

    def futures(self, zoid):

        def possible_places(board, orient):
            for col in range(0, board.cols() - orient.shape[1] + 1):
                highest = max(board.height(col + c) for c in range(0, orient.shape[1]))
                row = board.rows() - highest - orient.shape[0]
                if not board.overlaps(orient, row, col):
                    while not board.overlaps(orient, row + 1, col):
                        row += 1

                    yield (row, col)

        # For every possible placement of the current zoid, yield a representative State
        for rot in range(0, len(zoid)):
            for (row, col) in possible_places(self.board, zoid[rot]):
                yield self.future(zoid, row, col, rot)

    def future(self, zoid, row, col, rot):
        # Copy important info from this state
        board = deepcopy(self.board)
        cleared = self.cleared.copy()
        score = self.score

        # Compute future info with copies
        board.imprint(zoid[rot], row, col)
        full = frozenset(board.full())
        delta = State.Delta(zoid, rot, row, col, full)
        if len(full) > 0:
            cleared[len(full)] += 1
            score += self.CLEARED_POINTS[len(full)] * (self.level() + 1)
            board.clear(full)

        # Create future state with this as the previous one
        return State(self, board, cleared=cleared, score=score, delta=delta)
