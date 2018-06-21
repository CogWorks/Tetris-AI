import itertools


def simulate(state, zoid_gen, scorer, tie_breaker, lookahead=1):

    def best_future(state, zoids):
        if len(zoids) == 0:
            # No more zoids, so score the current state
            return state, scorer(state)

        # Compute best non-losing futures
        futures = itertools.ifilter(
            lambda future: future is not None,
            (best_future(future, zoids[1:]) for future in state.futures(zoids[0]))
        )

        # Find the best options
        choices = []
        best = -float('inf')
        for (future, score) in futures:
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
