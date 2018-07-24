import itertools

def move_drop(state, zoid):
    board = state.board
    for rot in range(0, len(zoid)):
        orient = zoid[rot]
        for col in range(0, board.cols() - orient.shape[1] + 1):
            highest = max(board.height(col + c) for c in range(0, orient.shape[1]))
            row = board.rows() - highest - orient.shape[0]
            if not board.overlaps(orient, row, col):
                while not board.overlaps(orient, row + 1, col):
                    row += 1
                yield (rot, row, col)

def move_with_overhang_slide(move_gen):

    def augmented_gen(state, zoid):
        board = state.board
        for (rot, row, col) in move_gen(state, zoid):
            # Pass on the original move as-is
            yield (rot, row, col)
            orient = zoid[rot]

            # Check if there is an overhang to the right of the move
            if col + orient.shape[1] < board.cols() and row > board.rows() - board.height(col + orient.shape[1]):
                # Slide to the left, yielding every legal placement as a move
                for c in reversed(range(board.cols() - orient.shape[1], col, -1)):
                    if not board.overlaps(orient, row, c):
                        r = row
                        while not board.overlaps(orient, r + 1, c):
                            r += 1
                        yield (rot, r, c)
                    else: break

            # Check if there is an overhang to the left of the move
            if col > 0 and row > board.rows() - board.height(col - 1):
                # Slide to the right, yielding every legal placement as a move
                for c in reversed(range(0, col)):
                    if not board.overlaps(orient, row, c):
                        r = row
                        # Lower the piece, if possible
                        while not board.overlaps(orient, r + 1, c):
                            r += 1
                        yield (rot, r, c)
                    else: break

    return augmented_gen

def policy_best(scorer, tie_breaker):
    # Like builtin max, but returns all elements that have max value
    def all_max(itr, key):
        group = []
        max = None
        for e in itr:
            k = key(e)
            if max is None or max < k:
                # e is new max, since previous max is strictly less
                group = []
                max = k
            elif k < max:
                # e cannot be a max, so skip it
                continue
            # k >= max
            # e is a max, so add to group
            group.append(e)
        return group

    def pick_best(futures):
        maxes = all_max(futures, scorer)
        if len(maxes) == 0:
            return None
        elif len(maxes) == 1:
            return maxes[0]
        else:
            return tie_breaker(maxes)
    return pick_best

def simulate(state, zoid_gen, move_gen, move_policy, lookahead=1):
    assert lookahead > 0
    while True:
        # Slice out 'visible' zoids using lookahead
        zoids = tuple(itertools.islice(zoid_gen, 0, lookahead))
        # Create a stack of future pools
        # First layer is simply the current state
        pool_stack = [[state]]

        # Fill remaining pool layers by generating possible futures from previous layer
        for zoid in zoids:
            pool_stack.append([
                prev.future(zoid, *move)
                for prev in pool_stack[-1]
                for move in move_gen(prev, zoid)
            ])

        # Apply the move policy to the farthest non-empty future pool
        next = None
        while next is None and len(pool_stack) > 1:
            pool = pool_stack.pop()
            if pool:
                next = move_policy(pool)

        if next is not None:
            # Backtrack to find first move on the path to this far-future, and yield it
            while next.prev is not state:
                next = next.prev
            yield next

            # Reset for the next iteration
            state = next
            # Push all yet-unplaced zoids back into front of zoid_gen, if any
            if len(zoids) > 1:
                zoid_gen = itertools.chain(zoids[1:], zoid_gen)
        else:
            # There are no possible moves, so the simulation is over
            break
