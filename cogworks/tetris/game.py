import numpy as np
import collections

from copy import deepcopy

class Zoid:

    def __init__(self, name, shape, rots):
        self.name = name
        self.shapes = tuple(np.rot90(shape, k=-i) for i in range(0, rots))

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
            top = self.rows() - row - np.nonzero(orient[::, c])[0][0]
            if top >= self.heights[col + c]:
                self.heights[col + c] = top

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

    def __eq__(self, other):
        return np.array_equal(self.data, other.data)

    def __ne__(self, other):
        return not np.array_equal(self.data, other.data)

    def __deepcopy__(self, memo):
        clone = Board(self.rows(), self.cols(), zero=False)
        np.copyto(clone.data, self.data)
        clone.heights = list(self.heights)
        return clone

class State:

    class Delta:
        def __init__(self, zoid, rot, row, col, cleared):
            self.zoid = zoid
            self.rot = rot
            self.row = row
            self.col = col
            self.cleared = cleared

    def __init__(self, prev, board, cleared=None, delta=None):
        self.prev = prev
        self.board = board
        self.cleared = cleared
        self.delta = delta

        if self.cleared is None:
            self.cleared = collections.defaultdict(int)

    def __getstate__(self):
        deltas = []
        ancestor = self
        while ancestor.prev is not None:
            d = ancestor.delta
            deltas.append((d.zoid, d.rot, d.row, d.col))
            ancestor = ancestor.prev

        return (ancestor.board, ancestor.cleared, deltas)

    def __setstate__(self, state):
        board, cleared, deltas = state
        prev = State(None, board, cleared=cleared, delta=None)
        while deltas:
            next = prev.future(*deltas.pop())
            prev = next
        self.prev = prev.prev
        self.board = prev.board
        self.cleared = prev.cleared
        self.delta = prev.delta

    def lines_cleared(self, simultaneously=None):
        if simultaneously is not None:
            return self.cleared[simultaneously]

        return sum(count * times for (count, times) in self.cleared.items())

    def level(self):
        return self.lines_cleared() // 10

    def score(self, points=(0, 40, 100, 300, 1200)):
        score = 0
        while self.delta is not None:
            score += points[len(self.delta.cleared)] * (self.level() + 1)
            self = self.prev
        return score

    def future(self, zoid, rot, row, col):
        # Copy important info from this state
        board = deepcopy(self.board)
        cleared = self.cleared.copy()

        # Compute future info with copies
        board.imprint(zoid[rot], row, col)
        full = frozenset(board.full())
        delta = State.Delta(zoid, rot, row, col, full)
        if len(full) > 0:
            cleared[len(full)] += 1
            board.clear(full)

        # Create future state with this as the previous one
        return State(self, board, cleared=cleared, delta=delta)
