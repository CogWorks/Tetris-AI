from __future__ import division

from cogworks import feature


# Determines if the given feature is a 'helper' feature, denoted with the prefix '__'.
# Helper features are used to compute other features, and may return non-numerical values.
def is_helper(feature):
    return feature.__name__.startswith('__')

import numpy as np

# Height Features

# __heights:
#   The height of each of the board' columns, as a list indexed by column.
#   NOTE: This is a helper feature, and should only be used for computing other features.
@feature.define()
def __heights(state):
    return [state.board.height(c) for c in range(0, state.board.cols())]

# mean_ht:
#   The average height of the columns.
@feature.define(__heights)
def mean_ht(_, __heights):
    return sum(__heights) / len(__heights)

# max_ht:
#   The maximum height of the columns.
@feature.define(__heights)
def max_ht(_, __heights):
    return max(__heights)

# min_ht:
#   The minimum height of the columns.
@feature.define(__heights)
def min_ht(_, __heights):
    return min(__heights)

# all_ht:
#   The sum of the heights of the columns.
@feature.define(__heights)
def all_ht(_, __heights):
    return sum(__heights)

# max_ht_diff:
#   The difference between the tallest column and the average column height.
@feature.define(max_ht, mean_ht)
def max_ht_diff(_, max_ht, mean_ht):
    return max_ht - mean_ht

# min_ht_diff:
#   The difference between the average column height and the shortest column.
@feature.define(mean_ht, min_ht)
def min_ht_diff(_, mean_ht, min_ht):
    return mean_ht - min_ht

# Cleared Features

# cleared:
#   The number of rows cleared by the previous move.
@feature.define()
def cleared(state):
    return len(state.delta.cleared)

# cuml_cleared:
#   The sum from 1 to cleared.
#   Computed using the formula for the sum of natural numbers.
@feature.define(cleared)
def cuml_cleared(_, cleared):
    return cleared * (cleared + 1) / 2

# tetris:
#   1 if four rows were cleared (that is, a tetris was performed), otherwise 0.
@feature.define(cleared)
def tetris(_, cleared):
    return cleared // 4

# move_score:
#   The number of points earned.
#   Computed as the number of cleared rows times the state's level.
#   NOTE: This is not equal to the actual difference in State.score.
@feature.define(cleared)
def move_score(state, cleared):
    return cleared * (state.prev.level() + 1)

# Transition Features

# col_trans:
#   The number of times that two adjacent cells in the same column mismatch.
@feature.define()
def col_trans(state):
    return np.sum(np.diff(state.board.data, axis=0))

# row_trans:
#   The number of times that two adjacent cells in the same row mismatch.
@feature.define()
def row_trans(state):
    return np.sum(np.diff(state.board.data, axis=1))

# all_trans:
#   The total number of times that two adjacent cells mismatch.
#   Computed as the sum of col_trans and row_trans.
@feature.define(col_trans, row_trans)
def all_trans(_, col_trans, row_trans):
    return col_trans + row_trans
# Well Features

# __wells:
#   The depth of each column with respect to its adjacent columns, as a list.
#   If a column is not shorter than both of its neighbors, it has a value of 0.
#   Otherwise, its value is how much shorter it is than its shortest neighbor.
#   NOTE: This is a helper feature, and should only be used for computing other features.
@feature.define(__heights)
def __wells(state, __heights):
    __heights = [state.board.rows()] + __heights + [state.board.rows()]
    return [
        max(0, min(__heights[i - 1], __heights[i + 1]) - __heights[i])
        for i in range(1, len(__heights) - 1)
    ]

# wells:
#   The sum of the well values for each column.
@feature.define(__wells)
def wells(_, __wells):
    return sum(__wells)

# cuml_wells:
#   The sum from 1 to wells.
#   Computed using the formula for the sum of natural numbers.
@feature.define(__wells)
def cuml_wells(_, __wells):
    return sum(x * (x + 1) / 2 for x in __wells)

# deep_wells:
#   The sum of the well values that are greater than one.
@feature.define(__wells)
def deep_wells(_, __wells):
    return sum(i for i in __wells if i > 1)

# max_well:
#   The largest well value.
@feature.define(__wells)
def max_well(_, __wells):
    return max(__wells)

# pit features

# __pits:
#   A collection of empty cells with filled cells above them, as a list.
#   Each element is the set of rows in which a well is found for the column corresponding to the
#   element's index.
#   NOTE: This is a helper feature, and should only be used for computing other features.
@feature.define(__heights)
def __pits(state, __heights):
    return [
        {
            r for r in range(state.board.rows() - __heights[c] + 1, state.board.rows())
            if not state.board[r,c]
        }
        for c in range(0, state.board.cols())
    ]

# pits:
#   The total number of pits.
@feature.define(__pits)
def pits(_, __pits):
    return sum(len(rows) for rows in __pits)

# pit_rows:
#   The number of rows with pits.
@feature.define(__pits)
def pit_rows(_, __pits):
    return len({r for rows in __pits for r in rows})

# lumped_pits:
#   The number of pits after collapsing column-wise adjacent pits.
#   Computed by counting pits that do not have another pit directly above them.
@feature.define(__pits)
def lumped_pits(_, __pits):
    return len({
        (r,c)
        for (c, rows) in enumerate(__pits)
        for r in rows
        if r - 1 not in rows
    })

# pit_depth:
#   The sum of the depths of every pit, where the depth is the number of non-pits above a cell.
@feature.define(__heights, __pits)
def pit_depth(state, __heights, __pits):
    return sum(
        len(set(range(state.board.rows() - __heights[c], r)) - __pits[c])
        for (c, rows) in enumerate(__pits)
        for r in rows
    )

# mean_pit_depth:
#   The average pit depth.
@feature.define(pit_depth, pits)
def mean_pit_depth(_, pit_depth, pits):
    return pit_depth / pits if pits != 0 else 0

# Difference Features

# __diffs:
#   The difference in height between a column and its right neighbor.
#   NOTE: This is a helper feature, and should only be used for computing other features.
@feature.define(__heights)
def __diffs(_, __heights):
    return [__heights[i + 1] - x for i,x in enumerate(__heights[:-1])]

# cd_n:
#   The difference in height between column n-1 and n.
cd_1 = feature.define(__diffs)(lambda _, __diffs: __diffs[0], name='cd_1')
cd_2 = feature.define(__diffs)(lambda _, __diffs: __diffs[1], name='cd_2')
cd_3 = feature.define(__diffs)(lambda _, __diffs: __diffs[2], name='cd_3')
cd_4 = feature.define(__diffs)(lambda _, __diffs: __diffs[3], name='cd_4')
cd_5 = feature.define(__diffs)(lambda _, __diffs: __diffs[4], name='cd_5')
cd_6 = feature.define(__diffs)(lambda _, __diffs: __diffs[5], name='cd_6')
cd_7 = feature.define(__diffs)(lambda _, __diffs: __diffs[6], name='cd_7')
cd_8 = feature.define(__diffs)(lambda _, __diffs: __diffs[7], name='cd_8')
cd_9 = feature.define(__diffs)(lambda _, __diffs: __diffs[8], name='cd_9')

# all_diffs:
#   The sum of all column differences.
@feature.define(__diffs)
def all_diffs(_, __diffs):
    return sum(__diffs)

# max_diffs:
#   The maximum column difference.
@feature.define(__diffs)
def max_diffs(_, __diffs):
    return max(__diffs)

# jaggedness:
#   The sum of absolute differences among columns.
@feature.define(__diffs)
def jaggedness(_, __diffs):
    return sum(abs(diff) for diff in __diffs)

# Delta Features

# d_max_ht:
#   The difference between max_ht of this state and the previous one.
@feature.define(max_ht, feature.with_transformed_state(lambda state: state.prev, max_ht))
def d_max_ht(_, max_ht, p_max_ht):
    return max_ht - p_max_ht

# d_all_ht
#   The difference between all_ht of this state and the previous one.
@feature.define(all_ht, feature.with_transformed_state(lambda state: state.prev, all_ht))
def d_all_ht(_, all_ht, p_all_ht):
    return all_ht - p_all_ht

# d_mean_ht
#   The difference between mean_ht of this state and the previous one.
@feature.define(mean_ht, feature.with_transformed_state(lambda state: state.prev, mean_ht))
def d_mean_ht(_, mean_ht, p_mean_ht):
    return mean_ht - p_mean_ht

# d_pits
#   The difference between pits of this state and the previous one.
@feature.define(pits, feature.with_transformed_state(lambda state: state.prev, pits))
def d_pits(_, pits, p_pits):
    return pits - p_pits

# Miscellaneous Features

# landing_height:
#   The height of the row containing the bottom-most cell of the previously placed zoid.
@feature.define()
def landing_height(state):
    return state.board.rows() - (state.delta.row + state.delta.zoid[state.delta.rot].shape[0])

# pattern_div:
#   The number of unique transitions between adjacent columns.
@feature.define()
def pattern_div(state):
    return np.unique(np.diff(state.board.data.astype(int)), axis=1).shape[1]

# __nine_filled:
#   A mapping from row to the only empty space in that column, if such a space exists.
#   Otherwise, the row will not be present as a key.
#   NOTE: This is a helper feature, and should only be used for computing other features.
@feature.define()
def __nine_filled(state):
    return {
        row: unfilled[0]
        for row in range(0, state.board.rows())
        for unfilled in np.nonzero(~state.board[row, ::])
        if len(unfilled) == 1
    }

# nine_filled:
#   The number of rows with only one empty column.
@feature.define(__nine_filled)
def nine_filled(_, __nine_filled):
    return len(__nine_filled)

# tetris_progress:
#   The maximal number of contiguous rows that share their only empty column, which is empty in
#   every higher row.
@feature.define(__nine_filled)
def tetris_progress(state, __nine_filled):
    progress = 0
    covered = set()
    for row in range(0, state.board.rows()):
        # Whatever columns are filled cover lower rows
        covered |= set(np.nonzero(state.board[row, ::])[0])
        col = __nine_filled.get(row)
        if col is not None:
            if col not in covered:
                # Uncovered and nine-filled, so that's progress
                progress += 1
            else:
                # Covered, so no more progress can be made
                break
        elif len(covered) < state.board.cols():
            # No tetris available for the row, so progress resets
            progress = 0
        else:
            # Everything has been covered, so no more progress can be made
            break

    return progress

# full_cells:
#   The number of non-empty cells.
@feature.define()
def full_cells(state):
    return np.sum(state.board.data)

# weighted_cells:
#   The sum of non-empty cells, weighted multiplicatively by height.
@feature.define()
def weighted_cells(state):
    return np.sum(np.sum(state.board.data, axis=1) * range(state.board.rows(), 0, -1))

# eroded_cells:
#   The number of cells that were cleared from the previously placed zoid.
@feature.define()
def eroded_cells(state):
    return sum(
        sum(state.delta.zoid[state.delta.rot][row - state.delta.row])
        for row in state.delta.cleared
    )

# cuml_eroded:
#   The sum from 1 to eroded_cells.
#   Computed with the formula for the sum of natural numbers.
@feature.define(eroded_cells)
def cuml_eroded(_, eroded_cells):
    return eroded_cells * (eroded_cells + 1) / 2
