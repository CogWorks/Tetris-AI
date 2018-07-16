from __future__ import division
from heapq import nlargest

import collections
import numpy as np

def cross_entropy(feats, width, keep, test_f, stdev, noise, smooth, rng, map_f=map):
    # Interpret features
    if isinstance(feats, collections.Mapping):
        # Weights provided
        feats, weights = zip(*feats.items())
        weights = list(weights)
    else:
        # No weights, default to zero
        feats = list(feats)
        weights = [0] * len(feats)

    # Interpret stdev
    if isinstance(stdev, collections.Mapping):
        # Per-feature stdev
        stdev = [stdev[feat] for feat in feats]
    else:
        # Constant stdev
        stdev = [stdev] * len(feats)

    while True:
        # Generate new weights around the mean
        generation = [
            [rng.gauss(weights[i], stdev[i] + noise) for i in range(0, len(feats))]
            for _ in range(0, width)
        ]

        # Evaluate the weights
        results = map_f(lambda i: (test_f(dict(zip(feats, generation[i]))), i), range(0, width))

        # Collect top performers
        top_weights = list(zip(*(generation[i] for (_, i) in nlargest(keep, results))))

        # Compute mean weights and new deviations
        for i in range(0, len(feats)):
            weights[i] = np.mean(top_weights[i])
            stdev[i] = np.std(top_weights[i])

        # Smooth noise factor
        noise *= smooth

        # Reconstruct weight and stdev feature maps
        yield collections.OrderedDict(zip(feats, weights)), collections.OrderedDict(zip(feats, stdev))
