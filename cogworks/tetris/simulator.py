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


def simulate(state, zoid_gen, move_gen, scorer, tie_breaker, lookahead=1):

    def best_future(state, zoids):
        if len(zoids) == 0:
            # No more zoids, so score the current state
            return state, scorer(state)

        # Compute futures from move_gen
        futures = (state.future(zoids[0], *move) for move in move_gen(state, zoids[0]))

        # Recursively evaluate futures to compute ultimate scores
        futures = (best_future(future, zoids[1:]) for future in futures)

        # Find the best options
        choices = []
        best = -float('inf')
        for (future, score) in (f for f in futures if f is not None):
            if score >= best:
                if best < score:
                    choices = []
                    best = score
                choices.append(future)

        if len(choices) == 0:
            return None
        elif len(choices) == 1:
            return choices[0], best
        else:
            return tie_breaker(choices), best

    while True:
        # Slice out 'visible' zoids using lookahead
        zoids = tuple(itertools.islice(zoid_gen, 0, lookahead))
        best = best_future(state, zoids)
        if best is not None:
            state = best[0]
            yield state
            if len(zoids) > 1:
                # Push all yet-unplaced zoids back into front of zoid_gen
                zoid_gen = itertools.chain(zoids[1:], zoid_gen)
        else:
            break
