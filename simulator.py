#!/usr/bin/python
import platform, sys
if platform.system() == 'Linux':
    sys.path.insert(1,"lib.linux-x86_64-2.7")
from tetris_cpp import *
from boards import print_board, all_zoids
import time, random


class TetrisSimulator(object):

    """A board object that supports assessment metrics and future simulations"""

    # modifiers for the run
    how_scores = False
    show_options = False
    option_step = .1
    show_choice = False
    choice_step = .5

    # pieces from the PENTIX variant of Tetris.
    # pieces = ["BIG_T","BIG_I","BIG_J","BIG_L","BIG_S","BIG_Z",
    #              "PLUS","U","BIG_V","D","B","W",
    #              "J_DOT","L_DOT","J_STILT","L_STILT","LONG_S","LONG_Z"]

    def __init__(self, board=None, curr=None, next=None, controller=None,
                 show_scores=False, show_options=False, show_result=True,
                 show_choice=False, option_step=0, choice_step=0,
                 name="Controller", seed=time.time(), overhangs=False,
                 force_legal=True):
        """
        Initializes the simulator object.
            board : a board representation [20 rows, 10 columns]
            curr : a boards.tetris_zoid object
            next : a boards.tetris_zoid object
            controller : a dictionary of feature names and their relative
            weights
            show_scores : whether to display the scores of the current moves
            show_options : whether to print POTENTIAL move as it is considered
            show_result : whether to print the results of each game
            show_choice : whether to show the CHOSEN move
            option_step : the delay time (in seconds) for displaying each
            option (COSTLY)
            choice_step : the delay time (in seconds) for displaying each
            choice (COSTLY)
            name : the name given for logging and tracking purposes (printed
            during long runs)
            overhangs : if enabled, uses a more robust system for determining
            possible moves
            force_legal : enables an A* search to determine if overhang moves
            are actually legal (COSTLY)
        """
        self.sequence = random.Random(seed)

        if board:
            self.space = board
        else:
            self.space = tetris_cow2(rows=20)

        if curr:
            self.curr_z = curr
        else:
            self.curr_z = self.sequence.choice(all_zoids.values())

        if next:
            self.next_z = next
        else:
            self.next_z = self.sequence.choice(all_zoids.values())

        self.name = name

        self.overhangs = overhangs
        self.force_legal = force_legal

        if controller:
            self.controller = controller
        else:  # default Dellacherie model
            self.controller = {"landing_height": -1,
                               "eroded_cells": 1,
                               "row_trans": -1,
                               "col_trans": -1,
                               "pits": -4,
                               "cuml_wells": -1}

        # display options saved
        self.show_result = show_result
        self.show_scores = show_scores
        self.show_options = show_options
        self.show_choice = show_choice

        self.option_step = option_step
        self.choice_step = choice_step

        # output scores initialized
        self.lines = 0
        self.l = {1: 0, 2: 0, 3: 0, 4: 0}
        self.score = 0
        self.level = 0
        # self.stats_dict = {}

    # GAME METHODS >>>>>

    def get_random_zoid(self):
        """generates a new random zoid. duplicates are generally avoided"""

        # generate random, but with dummy value 7
            #[7? in the specs, but what good is it?]
        z_id = self.sequence.choice(range(len(self.zoids) + 1))
        # then repeat/dummy check, and reroll *once*
        if not self.curr_z or z_id == len(self.zoids):
            return self.sequence.choice(range(len(self.zoids)))
        elif self.zoids[z_id] == self.curr_z:
            return self.sequence.choice(range(len(self.zoids)))

        return z_id

    def new_zoids(self):
        """pure random selection"""
        self.curr_z = self.next_z
        self.next_z = self.sequence.choice(all_zoids.values())

    def update_score(self):
        """Scores the board. Should be called immediately after a move
        is made"""
        clears = sum(all(row) for row in self.space)
        self.lines += clears
        if clears in self.l:
            self.l[clears] += 1
            self.score += {1: 40, 2: 100, 3: 300, 4: 1200}[clears] * \
                (self.level + 1)
        self.level = int(self.lines / 10)

    # <<<<< GAME METHODS

    # DISPLAY >>>>>

    def printscores(self):
        """print the scores"""
        print("Name:\t" + str(self.name))
        print("Level:\t" + str(self.level))
        print("Score:\t" + str(self.score))
        print("Lines:\t" + str(self.lines))
        print "\t(1: %d  2: %d  3: %d  4: %d)" \
            % (self.l[1], self.l[2], self.l[3], self.l[4])
        print

    def printspace(self, space=None):
        """generic space-printing.
        Now that the board engine is decoupled from this class, it's probably
        a good idea to migrate this to boards._helpers"""

        space = space or self.space
        # print("+" + "-"*len(space[0])*2 + "+")
        print("+" + "-" * space.col_count() * 2 + "+")
        # for i in range(len(space)):
        for i in space.rows(all=True):
            row = ({0: '  ', 1: '[]', 2: 'WM'}[j] for j in space.row_iter(i))
            print '|%r|%d' % (''.join(row), str(len(space - i - 1)))
            print "+" + "-" * space.col_count() * 2 + "+"
        numline = " " + " ".join(str(x) for x in space.cols())
        print numline

    def printcontroller(self, feats=False):
        """print the controller's values"""
        for k in sorted(self.controller.keys()):
            outstr = k.ljust(15) + ":\t"
            if feats:
                outstr += str(feats[k]) + "\t(" + \
                    ('%3.3f' % self.controller[k]).rjust(8) + ")"
            else:
                outstr += ('%3.3f' % self.controller[k]).rjust(8)
            print(outstr)

    # u"\u2b1c"
    # u"\u2b1c"
    # u"\u27DD"

    # <<<<< DISPLAY

    # METHODS TO GET PERCEPTS >>>>>

    def get_options(self):
        """Generates the list of options"""
        if self.overhangs:
            raise Exception("support for overhangs has not been implemented")
        else:
            self.options = self.possible_moves()
            # self.options = [x for x in self.possible_moves() if not x[5]]

        return self.options

    def possible_moves(self):
        """generates a list of possible moves via the Straight-Drop method
            for each orientation, it drops the zoid straight down in each
            column."""
        zoid = self.curr_z
        options = []
        for orient in xrange(4):
            zoid.set_orient(orient)
            # get the indices of all occupied cells in the zoid
            crds = [(i, j) for i in zoid.rows()
                    for j in zoid.cols() if zoid[i, j]]
            for c in self.space.cols():
                # stop if we run off the board
                if c + zoid.col_count() > self.space.col_count():
                    break

                # find where the zoid rests
                heights = tuple(self.get_height(col) for col in
                                self.space.col_space())
                # start at the lowest column height
                r = min(heights[c:c + zoid.col_count()])
                try:
                    # then keep checking the next row until all cells in the
                    # board are unoccupied
                    while any(self.space[r + i, c + j] for i, j in crds):
                        r += 1
                except IndexError:
                    # can't place the zoid in this column
                    continue
                else:
                    options.append((orient, (r, c)))

        return options

    def get_features(self, space, prev_space=None, convert=False):
        """retrieves all of the features for a given space"""

        if convert:
            for r in space.rows():
                for c in space.cols():
                    space[r, c] = int(bool(space[r, c]))

        cleared_space = space.get_cow()
        cleared_space.check_full(True)

        cleared_space_cols = cleared_space.col_space()

        # heavy calculations
        all_heights = [self.get_height(x) for x in cleared_space_cols]
        wells = self.get_wells(all_heights)

        diffs = [all_heights[i + 1] - x for i,
                 x in enumerate(all_heights[:-1])]
        all_pits, pit_rows, lumped_pits = self.get_all_pits(cleared_space_cols)
        pit_depths = [self.get_pit_depth(x) for x in cleared_space_cols]

        features = {}

        # height dependent
        features["mean_ht"] = sum(all_heights) * 1.0 / len(all_heights) * 1.0
        features["max_ht"] = max(all_heights)
        features["min_ht"] = min(all_heights)
        features["all_ht"] = sum(all_heights)
        features["max_ht_diff"] = features["max_ht"] - features["mean_ht"]
        features["min_ht_diff"] = features["mean_ht"] - features["min_ht"]
        features["column_9"] = all_heights[-1]

        # cleared dependent
        features["cleared"] = sum(all(row) for row in space)
        features["cuml_cleared"] = sum(range(1, features["cleared"] + 1))
        features["tetris"] = 1 if features["cleared"] == 4 else 0
        features["move_score"] = features["cleared"] * (self.level + 1)

        # trans dependent
        features["col_trans"] = sum(self.get_all_transitions(
                                    cleared_space_cols))
        features["row_trans"] = sum(self.get_all_transitions(cleared_space))
        features["all_trans"] = features["col_trans"] + features["row_trans"]

        # well and height dependent
        features["wells"] = sum(wells)
        features["cuml_wells"] = sum(sum(range(1, x + 1)) for x in wells)
        features["deep_wells"] = sum([i for i in wells if i != 1])
        features["max_well"] = max(wells)

        # pit dependent
        features["pits"] = sum(all_pits)
        features["pit_rows"] = len(pit_rows)
        features["lumped_pits"] = lumped_pits

        # pit depth dependent
        features["pit_depth"] = sum(pit_depths)
        if features["pits"] * 1.0 == 0:
            features["mean_pit_depth"] = 0
        else:
            features["mean_pit_depth"] = features["pit_depth"] * 1.0 / \
                features["pits"] * 1.0

        # diff and height dependent
        features["cd_1"] = diffs[0]
        features["cd_2"] = diffs[1]
        features["cd_3"] = diffs[2]
        features["cd_4"] = diffs[3]
        features["cd_5"] = diffs[4]
        features["cd_6"] = diffs[5]
        features["cd_7"] = diffs[6]
        features["cd_8"] = diffs[7]
        features["cd_9"] = diffs[8]
        features["all_diffs"] = sum(diffs)
        features["max_diffs"] = max(diffs)
        features["jaggedness"] = sum([abs(d) for d in diffs])

        # previous space
        if prev_space:
            prev_cols = zip(*prev_space)
            prev_heights = [self.get_height(i) for i in prev_cols]
            prev_pits = self.get_all_pits(prev_cols)[0]

            features["d_max_ht"] = features["max_ht"] - max(prev_heights)
            features["d_all_ht"] = features["all_ht"] - sum(prev_heights)
            features["d_mean_ht"] = features["mean_ht"] - \
                (sum(prev_heights) * 1.0 / len(prev_heights) * 1.0)
            features["d_pits"] = features["pits"] - sum(prev_pits)

        else:
            features["d_max_ht"] = None
            features["d_all_ht"] = None
            features["d_mean_ht"] = None
            features["d_pits"] = None

        # independents
        features["landing_height"] = self.get_landing_height(space)

        features["pattern_div"] = self.get_col_diversity(cleared_space_cols)

        features["matches"] = self.get_matches(space)

        # if "tetris_progress" in keys or "nine_filled" in keys or all:
        tetris_progress, nine_filled = self.get_tetris_progress(cleared_space)
        features["tetris_progress"] = tetris_progress
        features["nine_filled"] = nine_filled

        features["full_cells"] = self.get_full_cells(cleared_space)

        features["weighted_cells"] = self.get_full_cells(cleared_space,
                                                         row_weighted=True)

        features["eroded_cells"] = sum(list(i).count(2) if all(i) else 0
                                       for i in space)
        features["cuml_eroded"] = sum(range(1, features["eroded_cells"]))

        return features

    def get_height(self, v):
        for i, x in enumerate(v):
            if x != 0:
                return len(v) - i
        return 0

    # !# parallelize
    def get_full_cells(self, space, row_weighted=False):
        """counts the total number of filled cells"""
        if not row_weighted:
            return sum(sum(True for i in row if i) for row in space)
        total = 0
        for i, row in enumerate(space):
            total += sum(len(space) - i for c in row if c)

        return total

    # Pits
    # !# need to represent pits as a list of unique pits with a particular length;

    """isolating"""

    def get_pits(self, v):
        """For one column, search for the number of covered empty cells
            returns:
             a list of the rows in which pits exist
             a 'lumped' measure of pits. adjacent pits considered one pit"""
        state = v[0]
        pits = 0
        lumped_pits = 0
        curr_pit = 0
        rows = []
        row = 18
        for i in v[1:]:
            if i != 0:
                state = 1
                curr_pit = 0  # lumped pit ends.
            if i == 0 and state == 1:  # top detected and found a pit
                if curr_pit == 0:  # we hadn't seen a pit yet
                    lumped_pits += 1  # so this is a new lumped pit
                curr_pit = 1
                pits += 1
                rows.append(row)
            row -= 1
        return rows, lumped_pits

    """isolating"""

    def get_matches(self, space):
        """detect the total number of matched edges for a given zoid
        placement."""
        matches = 0
        # for r in range(len(space)):
        #     for c in range(len(space[r])):
        for r in space.rows():
            for c in space.cols():
                if space[r, c] == 2:
                    # down
                    if r + 1 >= len(space):
                        matches += 1
                    else:
                        if space[r + 1, c] == 1:
                            matches += 1
                    # left
                    if c - 1 < 0:
                        matches += 1
                    else:
                        if space[r, c - 1] == 1:
                            matches += 1
                    # right
                    # if c + 1 >= len(space[r]):
                    if c + 1 >= space.col_count():
                        matches += 1
                    else:
                        if space[r, c + 1] == 1:
                            matches += 1
                    # up, rarely
                    if r - 1 >= 0:
                        if space[r - 1, c] == 1:
                            matches += 1
        return matches

    """isolating"""
    # !# parallelize

    def get_all_pits(self, colspace):
        """get pit values for all columns,
            returns:
             count of all pits [col_pits]
             list of rows containing pits [row_pits]
             adjacently lumped pits [lumped_pits]"""
        col_pits = []
        pit_rows = []
        lumped_pits = 0
        for i in colspace:
            pits, lumped = self.get_pits(i)
            lumped_pits += lumped
            col_pits.append(len(pits))
            pit_rows = [j for j in pits if j not in pit_rows]
        return(col_pits, pit_rows, lumped_pits)

    """isolating"""

    def get_landing_height(self, space):
        """determine the bottommost height of a zoid placement"""
        for i in space.rows():
            if 2 in space.row_iter(i):
                return i

    def get_transitions(self, v):
        """for one vector, get the number of transitions from empty to
        full, or vice versa"""
        state = v[0]
        trans = 0
        for i in v[1:]:
            if i == 0 and state != 0:
                trans += 1
                state = 0
            elif i != 0 and state == 0:
                trans += 1
                state = 1
        return trans

    # !# parallelize
    def get_all_transitions(self, space):
        """get transitions for all vectors in a space (generic)"""
        return [self.get_transitions(list(row)) for row in space]

    def get_col_diversity(self, colspace):
        """determine how many times a pattern is repeated
        lower values mean the pattern is less diverse, and more ordered"""
        patterns = []
        for i in range(len(colspace) - 1):
            pattern = []
            for j in range(len(colspace[i])):
                pattern.append(colspace[i][j] - colspace[i + 1][j])
            patterns.append(pattern)

        return len(patterns)

    def get_pit_depth(self, v):
        """detect the depth of all pits in a vector"""
        state = 0
        depth = 0
        curdepth = 0
        for i in v:
            # found first full cell
            if state == 0 and i != 0:
                curdepth += 1
                state = 1
            # found another full cell
            elif state != 0 and i != 0:
                curdepth += 1
            # found a pit! commit current depth to total
            elif state != 0 and i == 0:
                depth += curdepth
        return depth

    def get_wells(self, heights, cumulative=False):
        """determine the number of wells
        wells are columns with higher columns on either side"""
        heights = [len(self.space)] + heights + [len(self.space)]

        wells = []
        for i in range(1, len(heights) - 1):
            ldiff = heights[i - 1] - heights[i]
            rdiff = heights[i + 1] - heights[i]
            if ldiff < 0 or rdiff < 0:
                wells.append(0)
            else:
                wells.append(min(ldiff, rdiff))

        return wells

    def nine_filled(self, row):
        """determines if a row has 9 cells filled
            useful in determining tetris progress"""
        filled = 0
        for i in range(len(row)):
            if row[i] != 0:
                filled += 1
            if row[i] == 0:
                ix = i
        if filled == 9:
            return ix
        else:
            return None

    def get_tetris_progress(self, space):
        """determines the current progress toward scoring a tetris
         e.g. - if four rows have 9 cells filled
             #and the 9th cell is in the same column for each
             #and there is nothing above that column
             #tetris_progress = 4, i.e. a tetris is available"""
        # eating a LOT of the processing
        # complicated measure JKL cooked up
        # e.g. - if four rows have 9 cells filled
                # and the 9th cell is in the same column for each
                # and there is nothing above that column
                # tetris_progress = 4, i.e. a tetris is available
        # newspace = copy.deepcopy(space)
        # newspace.reverse()
        return 0, 0

        nine_count = 0

        progress = 0
        prev_col = -1
        prev_col = -1

        # from the bottom up
        for r in range(1, len(space) + 1):
            r_ix = len(space) - r
            # col = self.nine_filled(space[r_ix])
            col = self.nine_filled(list(space.row_iter(r_ix)))

            # found a filled row
            if col is not None:
                nine_count += 1
                # new column, reset counter
                if col != prev_col:
                    if r == 1:  # first row
                        progress = 1
                        prev_col = col
                        stagnated = False
                    else:
                        if space[r_ix + 1, col] != 0:  # if there's a block below, we can restart

                            progress = 1
                            prev_col = col
                            stagnated = False
                        else:
                            progress = 0
                            prev_col = -1
                # same column, increase counter
                elif col == prev_col and not stagnated:
                    progress += 1

            # no nine-count row detected
            else:
                # column is blocked, reset progress and column
                try:
                    space[r_ix, prev_col]
                except:
                    print r_ix
                    print prev_col

                if space[r_ix, prev_col] != 0:
                    progress = 0
                    prev_col = -1
                # otherwise, progress stagnates here
                else:
                    stagnated = True
        return progress, nine_count

    # <<<<< METHODS TO GET PERCEPTS

    # CONTROLLERS >>>>>

    def control(self, orient, pos):
        """returns an integer corresponding to the score of a move given the
        orientation and position to place the current zoid"""
        zoid = self.curr_z.get_copy()
        zoid_board = self.space.get_cow()
        zoid_board.imprint_zoid(zoid, orient=orient, pos=pos, value=2)
        features = self.get_features(zoid_board, self.space)
        return sum(features[x] * self.controller[x] for x in self.controller)

    def run(self, max_eps=None, printstep=500):
        """runs the simulator
            generates possible moves and chooses one
            loops until game_over or max_eps is exceeded"""
        ep = 0
        while ep != max_eps and self.get_options():
            # generate options and features
            scores = {x: self.control(*x) for x in self.options}
            best_moves = tuple(k for k, v in scores.items()
                               if v == max(scores.values()))
            orient, pos = self.sequence.choice(best_moves)
            self.space.imprint_zoid(self.curr_z, orient=orient, pos=pos)
            self.update_score()
            self.new_zoids()
            # the True parameter means full rows are counted *and* cleared
            self.space.check_full(True)

            if self.show_scores or ep % printstep == 0 and not \
                    printstep == -1:
                print("\nEpisode: " + str(ep))
                self.printscores()
            ep += 1

            if self.show_choice:
                print_board(self.space, entire=True, show_full=True)
                time.sleep(self.choice_step)

        if self.show_result:
            print("\n\nGame Over\nFinal scores:")
            print("Episodes: " + str(ep))
            self.printscores()
            self.printcontroller()
            print("\n")

        return({"lines": self.lines,
                "l1": self.l[1],
                "l2": self.l[2],
                "l3": self.l[3],
                "l4": self.l[4],
                "score": self.score,
                "level": self.level,
                "eps": ep})

    # <<<<< CONTROLLERS


def main(argv):

    controller1 = {"landing_height": -1,
                   "eroded_cells": 1,
                   "row_trans": -1,
                   "col_trans": -1,
                   "pits": -4,
                   "cuml_wells": -1}

    # DTS controller, from Dellacherie + Thiery & Scherrer; 35,000,000
    # rows?!!?!
    controller2 = {"landing_height": -12.63,
                   "eroded_cells": 6.60,
                   "row_trans": -9.22,
                   "col_trans": -19.77,
                   "pits": -13.08,
                   "cuml_wells": -10.49,
                   "pit_depth": -1.61,
                   "pit_rows": -24.04}

    # bad controller for demonstration's purposes
    controller3 = {"landing_height": 1,
                   "eroded_cells": 1,
                   "row_trans": -1,
                   "col_trans": -1,
                   "pits": 1,
                   "cuml_wells": -1}

    # Introducing overhangs

    osim = TetrisSimulator(
        controller=controller1,
            board=tetris_cow2(),
            curr=all_zoids["L"],
            next=all_zoids["S"],
            show_choice=True,
            show_scores=True,
            show_options=True,
            option_step=.3,
            choice_step=1,
            seed=1
    )

    # enable for speed test
    osim.show_options = False
    osim.choice_step = 0

    osim.run()

    # overhangs allowed, but legality not enforced
    # osim.overhangs, osim.force_legal = True, False
    # osim.run()

    # legality enforced
    # osim.overhangs, osim.force_legal = True, True
    # osim.run()


if __name__ == "__main__":
    main(sys.argv)
