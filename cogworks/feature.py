import collections
import functools

# Returns a function that converts an implementation into features with the given dependencies.
#
# In terms of features, an implementation is any callable object that accepts at least one argument.
# The first positional argument refers to the state to be analyzed, while additional arguments refer
# to the evaluations of declared dependencies on the state.
#
# Features themselves are wrapper functions around the implementations they were created from.
# These wrappers accept a state to pass along to the implementation, along with an optional cache to
# consult before computing features.
# As a result, each feature will only be computed once when the evaluation calls share a cache.
def define(*needs):

    def wrap(impl, name=None):
        assert callable(impl)

        if name is not None:
            impl.__name__ = name

        # Wrap the feature implementation to utilize a cache and gather evaluated dependencies
        @functools.wraps(impl)
        def feature(state, cache=None):
            if cache is None:
                cache = {}
            feature.accesses += 1
            if impl in cache:
                result = cache[impl]
            else:
                feature.misses += 1
                result = impl(state, *(need(state, cache=cache) for need in needs))
                cache[impl] = result

            return result
        feature.accesses = 0
        feature.misses = 0
        return feature

    return wrap

# Returns a new feature that evaluates the given feature on a transformed state.
def with_transformed_state(transformer, feature):
    # Does not pass on cache, since a feature may be evaluated on different states
    return lambda state, cache=None: feature(transformer(state))

# Evaluates a collection of features on a given state.
# If features is a Mapping, then it assumed to map features to corresponding weights.
# The results are returned via dict, where each feature is mapped to its result.
def evaluate(state, features):
    cache = {}
    if isinstance(features, collections.Mapping):
        return {f: f(state, cache=cache) * w for (f, w) in features.iteritems()}
    else:
        return {f: f(state, cache=cache) for f in features}
