#to be added
# ability to control zoid sequences
# proper dummy-redundency and/or 7-bag zoid selection

"""
to-do:

 - fanning approach to move selection is quite possible.

 - a system for taking old log files and outputting the NEW, better features per episode.


 - innovation... equilibrium points? i.e. "1 well is allowed, deviation counts against"
    - huh!
    
OPTIMIZATION: based on a 230 second run of depth 10, controllers 20, survivors 4, and episodes 100
 X remove deep-copies where applicable (160 seconds)
 X reduce use of get_cols() (deep copying)
 - Switch to using numpy arrays, and stop using Append (7 seconds total)
 - enable parallelization and graphics processing using opencl and cuda
    - column-wise parallel summations
    - possible_moves function (can look at different moves separately)
 - make features only calculated when needed!!

"""


import sys, random, os, time, copy
import numpy as np
import scipy.stats
import scipy.spatial.distance

pieces = ["I", "O", "T", "S", "Z", "J", "L"]

#!# Work to remove this entirely! Unnecessary processing!
#transform the space to be column-wise, rather than rows
def get_cols(space):
    return zip(*space)

def get_height(v):
    for i in range(0, len(v)):
        if v[i] != 0:
            return len(v) - i
    return 0

def get_heights(colspace):
    return [get_height(i) for i in colspace]
    
def get_pits(v):
    state = v[0]
    pits = 0
    lumped_pits = 0
    curr_pit = 0
    rows = []
    row = 18
    for i in v[1:]:
        if i != 0:
            state = 1
            curr_pit = 0 #lumped pit ends.
        if i == 0 and state == 1:   #top detected and found a pit
            if curr_pit == 0:    #we hadn't seen a pit yet
                lumped_pits += 1    #so this is a new lumped pit
            curr_pit = 1
            pits += 1
            rows.append(row)
        row -= 1
    return rows, lumped_pits
    
def get_all_pits(colspace):
    col_pits = []
    pit_rows = [] 
    lumped_pits = 0
    for i in colspace:
        pits, lumped = get_pits(i)
        lumped_pits += lumped
        col_pits.append(len(pits))
        for j in pits:
            if j not in pit_rows:
                pit_rows.append(j)
    return(col_pits, pit_rows, lumped_pits)

def weighted_choice(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

WEIGHTS_DELLACHERIE = {"landing_height":-1,
                       "eroded_cells":1,
                       "row_trans":-1,
                       "col_trans":-1,
                       "pits":-4,
                       "cuml_wells":-1}

WEIGHTS_DTS = {"landing_height":-12.63,
               "eroded_cells":6.60,
               "row_trans":-9.22,
               "col_trans":-19.77,
               "pits":-13.08,
               "cuml_wells":-10.49,
               "pit_depth":-1.61,
               "pit_rows":-24.04}

WEIGHTS_BAD = {"landing_height":1,
               "eroded_cells":1,
               "row_trans":-1,
               "col_trans":-1,
               "pits":1,
               "cuml_wells":-1}

WEIGHTS_RYAN = {
    "pile_density":1,
    "matches":3,
    "pile_penalty":-3,
    "landing_height":-.5,
    "nine_filled":1.0001
}

PROBS_DELLACHERIE = {"landing_height":(1,min),
                     "eroded_cells":(10,max),
                     "row_trans":(1,min),
                     "col_trans":(1,min),
                     "pits":(1,min),
                     "cuml_wells":(1,min),
                     "matches":(1,max)}

class TetrisController(object):
    """A tetris controller is an algorithm/strategy for solving a single episode
    of tetris."""

    def evaluate(self, sim):
        """This method picks a move."""
        raise NotImplementedError()

    def _print(self, feats=False):
        raise NotImplementedError()

class RandomController(TetrisController):
    """A tetris controller that just picks a random action"""

    def evaluate(self, sim):
        options = sim.options
        return random.choice(options)

class WeightedAverageController(TetrisController):
    """A tetris controler that picks the action that maximizes a 
    weighted feature score."""

    def __init__(self, weights):
        self.weights = weights

    def evaluate(self, sim):
        options = sim.options
        for i in options:
            val = 0
            for j in self.weights.keys():
                val += i[4][j] * self.weights[j]
            i.append(val)
        crit = None
        for i in options:
            if not crit:
                crit = i[-1]
            else:
                crit = max(crit, i[-1])
        out = []
        for i in options:
            if i[-1] == crit:
                out.append(i)
        
        return random.choice(out)

    def _print(self, feats=False):
        out = []
        for k in sorted(self.weights.keys()):
            s = k.ljust(15) + ":\t"
            if feats:
                s += str(feats[k]) + "\t(" + ('%3.3f'%self.weights[k]).rjust(8) + ")"
            else:
                s += ('%3.3f'%self.weights[k]).rjust(8)
            out.append(s)
        print("\n".join(out))

class ProbabilisticController(TetrisController):
    """A tetris controller that picks an action by probabilistically picking
    a single feature to optimize each episode."""
    
    def __init__(self, probabilities):
        self.probabilities = probabilities
        
    def evaluate(self, sim):
        options = sim.options
        probs = [self.probabilities[p][0] for p in self.probabilities]
        strategy_index = weighted_choice(probs)
        strategy = self.probabilities.items()[strategy_index]
        vals = [i[4][strategy[0]] for i in options]
        v = strategy[1][1](vals)
        choices = [i for i in options if i[4][strategy[0]]==v]
        if len(choices) > 1:
            vals = [i[4]["matches"] for i in options]
            v = max(vals)
            choices = [i for i in options if i[4]["matches"]==v]
        return random.choice(choices)

    def _print(self, feats=False):
        out = []
        for k in sorted(self.probabilities.keys()):
            s = k.ljust(15) + ":\t"
            if feats:
                s += str(feats[k]) + "\t(" + ('%3.3f'%self.probabilities[k][0]).rjust(8) + ")"
            else:
                s += ('%3.3f'%self.probabilities[k][0]).rjust(8)
            out.append(s)
        print("\n".join(out))

class TetrisSimulator(object):
    """A board object that supports assessment metrics and future simulations"""
    
    show_scores = False
    show_options = False
    option_step = .1
    show_choice = False
    choice_step = .5
    
    space = []
    heights = []
    pits = []
    col_roughs = []
    row_roughs = []
    ridge = []
    matches = []
    
    lines = 0
    l1 = 0
    l2 = 0
    l3 = 0
    l4 = 0
    score = 0
    level = 0
    
    game_over = False
    
    
    #pieces = ["BIG_T","BIG_I","BIG_J","BIG_L","BIG_S","BIG_Z",
    #              "PLUS","U","BIG_V","D","B","W",
    #              "J_DOT","L_DOT","J_STILT","L_STILT","LONG_S","LONG_Z"]
    
    shapes =    {  
                "O":{
                    0: [[1,1],[1,1]]
                    },
                "I":{
                    0: [[1,1,1,1]],
                    1: [[1],[1],[1],[1]]
                    },
                "Z":{
                    0: [[1,1,0],[0,1,1]],
                    1: [[0,1],[1,1],[1,0]]
                    },
                "S":{
                    0: [[0,1,1],[1,1,0]],
                    1: [[1,0],[1,1],[0,1]]
                    },
                "T":{
                    0: [[1,1,1],[0,1,0]],
                    1: [[0,1],[1,1],[0,1]],
                    2: [[0,1,0],[1,1,1]],
                    3: [[1,0],[1,1],[1,0]]
                    },
                "L":{
                    0: [[1,1,1],[1,0,0]],
                    1: [[1,1],[0,1],[0,1]],
                    2: [[0,0,1],[1,1,1]],
                    3: [[1,0],[1,0],[1,1]]
                    },
                "J":{
                    0: [[1,1,1],[0,0,1]],
                    1: [[0,1],[0,1],[1,1]],
                    2: [[1,0,0],[1,1,1]],
                    3: [[1,1],[1,0],[1,0]]
                    }
                }
    shape_bottoms =    {  
                "O":{
                    0: [0,0]
                    },
                "I":{
                    0: [0,0,0,0],
                    1: [0]
                    },
                "Z":{
                    0: [1,0,0],
                    1: [0,1]
                    },
                "S":{
                    0: [0,0,1],
                    1: [1,0]
                    },
                "T":{
                    0: [1,0,1],
                    1: [1,0],
                    2: [0,0,0],
                    3: [0,1]
                    },
                "L":{
                    0: [0,1,1],
                    1: [2,0],
                    2: [0,0,0],
                    3: [0,0]
                    },
                "J":{
                    0: [1,1,0],
                    1: [0,0],
                    2: [0,0,0],
                    3: [0,2]
                    }
                }
    
    
    def __init__(self,board = None, curr = None, next = None, controller = None, 
                    show_scores = False, show_options = False, show_result = True, show_choice = False,
                    option_step = 0, choice_step = 0, name = "Controller", seed = time.time() * 10000000000000.0,
                    overhangs = False, force_legal = True):
        """Generates object based on given board layout"""
        self.sequence = random.Random()
        self.sequence.seed(seed)
        
        if board:
            self.space = self.convert_space(board)
        else:
            self.init_board()
            
        if curr:
            self.curr_z = curr
        else:
            self.curr_z = pieces[self.sequence.randint(0,len(pieces)-1)]
            
        if next:
            self.next_z = next
        else:
            self.next_z = pieces[self.sequence.randint(0,len(pieces)-1)]
        
        self.name = name
        
        self.overhangs = overhangs
        self.force_legal = force_legal
        
        self.controller = controller
        
        self.show_result = show_result
        self.show_scores = show_scores
        self.show_options = show_options
        self.show_choice = show_choice
    
        self.option_step = option_step
        self.choice_step = choice_step
        
        #self.heights = get_heights(self.space)
        #self.pits = get_all_pits(self.space)
        #self.col_roughs = self.get_roughs(self.space, columns = True)
        #self.row_roughs = self.get_roughs(self.space, columns = False)
        #self.ridge = self.get_ridge(self.space)
        #self.matches = []
        
        self.lines = 0
        self.l1 = 0
        self.l2 = 0
        self.l3 = 0
        self.l4 = 0
        self.score = 0
        self.level = 0
        #self.stats_dict = {}
        
        self.game_over = False
        
        #self.get_stats()
        
    ###
    
    def init_board(self):
        space = []
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        space.append([0,0,0,0,0,0,0,0,0,0])
        
        self.space = space
    
    
    def get_random_zoid( self ):

        #generate random, but with dummy value 7? [in the specs, but what good is it?]
        z_id = sequence.randint( 0, len(self.zoids) )

        #then repeat/dummy check, and reroll *once*
        if not self.curr_z or z_id == len(self.zoids):
            return self.sequence.randint( 0, len(self.zoids)-1 )
        elif self.zoids[z_id] == self.curr_z:
            return self.sequence.randint( 0, len(self.zoids)-1 )

        return z_id
    ###
    
    def set_zoids( self , curr, next):
        self.curr_z = curr
        self.next_z = next
    
    def set_board( self, board):
        self.space = self.convert_space(board)
    
    def report_board_features( self ):
        return self.get_features(self.space)
    
    def report_move_features( self, col, rot, row, offset = -1, printout = False):
        return self.get_move_features(self.space, col, rot, row + offset, self.curr_z, printout = printout)
    
    def get_options(self):
        if self.overhangs:
            self.options = self.possible_moves_under()
        else:
            self.options = self.possible_moves()
        
        #cull game-ending options
        non_ending = []
        for i in self.options:
            if not i[5]:
                non_ending.append(i)
        self.options = non_ending
    
    #function that takes a board state and a zoid, and optionally the move made
        #returns a choice (column, rotation, row)
    def predict(self, space, zoid):
        self.space = self.convert_space(space)
        self.curr_z = zoid
        
        self.get_options()
        return self.control()
        
    
    
    def do_move(self, col, rot, row):
        x = col
        y = len(self.space) - row - 1
        ix = x
        iy = y
        for i in self.shapes[self.curr_z][rot]:
            for j in i:
                if iy < 0:
                    self.game_over = True
                elif j != 0 and iy >= 0:
                    #print("stamping",iy,ix)
                    if self.space[iy][ix] != 0:
                        self.game_over = True
                    self.space[iy][ix] = j
                ix += 1
            ix = x
            iy += 1
        
        #if self.curr_zoid.overboard( self.board ):
        #    self.game_over()
        self.new_zoids()
        self.clear_lines()
    
    def sim_move(self, col, rot, row, zoid, space):
        x = col
        y = len(space) - row - 1
        ix = x
        iy = y
        ends_game = False
        for i in self.shapes[zoid][rot]:
            for j in i:
                if iy < 0:
                    ends_game = True
                if j != 0 and iy >= 0:
                    #print("stamping",iy,ix)
                    space[iy][ix] = 2
                ix += 1
            ix = x
            iy += 1
        
        return ends_game
    
    def move(self, movelist):
        self.do_move(movelist[0],movelist[1],movelist[2])
    
    #pure random selection
    def new_zoids(self):
        self.curr_z = self.next_z
        self.next_z = pieces[self.sequence.randint(0,len(pieces)-1)]
    
    def filled_lines(self, space):
        count = 0
        for r in space:
            if self.line_filled(r):
                count += 1
        return count
    
    def line_filled(self, row):
        for c in row:
            if c == 0:
                return False
        return True
        
    
    def clear_lines(self):
        to_clear = []
        for r in range(0,len(self.space)):
            if self.line_filled(self.space[r]):
                to_clear.append(r)
        
        #print(to_clear)
        clears = len(to_clear)
        
        if clears != 0:
            self.lines += clears
            if clears == 1:
                self.l1 += 1
                self.score += 40 * (self.level + 1)
            if clears == 2:
                self.l2 += 1
                self.score += 100 * (self.level + 1)
            if clears == 3:
                self.l3 += 1
                self.score += 300 * (self.level + 1)
            if clears == 4:
                self.l4 += 1
                self.score += 1200 * (self.level + 1)
            #self.printscores()
        
        self.level = int(self.lines / 10)
        
        newboard = []
        for r in range(0,len(self.space)):
            if not r in to_clear:
                newboard.append(self.space[r])
        for i in range(0,clears):
            newboard.insert(0,[0]*10)
        
        self.space = newboard
                    
    
    def clear_rows(self, space):
        to_clear = []
        for r in range(0,len(space)):
            if self.line_filled(space[r]):
                to_clear.append(r)
        
        newboard = []
        for r in range(0,len(space)):
            if not r in to_clear:
                newboard.append(space[r])
        for i in range(0,len(to_clear)):
            newboard.insert(0,[0]*10)
        
        return newboard
        
    def possible_moves(self, zoid = None, space = None):
        if not zoid:
            zoid = self.curr_z
        if not space:
            space = self.space
        
        options = []
        #for each possible rotation
        for r in range(0,len(self.shapes[zoid])):
            #and each possible column for that rotation
            for c in range(0, len(space[0]) - len(self.shapes[zoid][r][0]) + 1):
                row = self.find_drop(c,r,zoid,space)
                simboard, ends_game = self.possible_board(c,r,row,zoid=zoid)
                features = self.get_features(simboard,prev_space = space, all = False)
                opt = [c,r,row,simboard,features, ends_game]
                options.append(opt)
                
        if self.show_options:
            self.printoptions(options)
        
        return options
    
    def possible_moves_under(self, zoid = None, space = None):
        if not zoid:
            zoid = self.curr_z
        if not space:
            space = self.space
        
        drop_points = self.get_drop_points(space)
        
        candidates = []
        
        for rot in range(0,len(self.shapes[zoid])):
            candidates += self.drop_point_candidates(space, zoid, rot, drop_points)
            
        if self.force_legal:
            candidates = self.legal_dp_candidates(candidates,zoid,space)
        
        options = []
        
        for cnd in candidates:
            c,rt,r = cnd["c"],cnd["rot"],cnd["r"]
            simboard, ends_game = self.possible_board(c,rt,r,zoid=zoid)
            features = self.get_features(simboard,prev_space = space, all = False)
            opt = [c,rt,r,simboard,features,ends_game]
            options.append(opt)
        
        if self.show_options:
            self.printoptions(options)
        
        return options
                
        
    #get a list of drop points {"r":r,"c":c}
    def get_drop_points(self, space):
        points = []
        
        for c in range(0,len(space[0])):
            for r in range(0,len(space)):
                if self.get_cell(r,c,space) == 0:
                    if r == 0:
                        points.append({"c":c,"r":r})
                    elif self.get_cell(r-1,c,space) != 0:
                        points.append({"c":c,"r":r})
        return points
    
    def get_cell(self, r, c, space):
        return space[(len(space)-1)-r][c]
    
    def drop_point_candidates(self, space, zoid, rot, dps):
        z = self.shapes[zoid][rot]
        
        cands = []
        
        for p in dps:
            #for each column of the zoid
            for i in range(0,len(z[0])):
                c = p["c"]-i
                r = p["r"]+len(z)-self.shape_bottoms[zoid][rot][i] - 1
                if not (c < 0 or c + len(z[0]) > len(space[0])):
                  if not self.detect_collision(c,rot,r,zoid,space,off=1):
                    c = {"c":c,"rot":rot,"r":r}
                    if c not in cands:
                        cands.append(c)
        return cands
        
    def legal_dp_candidates(self, cnds, zoid, space):
        candidates = []
        checked = []
        rot = None
        
        def check(c,r,l=0,report = "start"):
            checked.append([c,r])
            #print " "*l,[c,r], report
            if self.detect_collision(c,rot,r,zoid,space,off=1):
                #print " "*l,report,"failed"
                return False
            elif r == len(space)-1:
                #print " "*l,"LEGAL"
                return True
            else:
                if [c-1,r] not in checked and c-1 >= 0:
                    left = check(c-1,r,l+1,"left")
                else:
                    left = False
                if [c+1,r] not in checked and c+1 < len(space[0]) - len(self.shapes[zoid][rot][0]) - 1:
                    right = check(c+1,r,l+1,"right")
                else:
                    right = False
                if [c,r+1] not in checked and r+1 < len(space):
                    up = check(c,r+1,l+1,"up")
                else:
                    up = False
            
                return left or right or up
            
        for cnd in cnds:
            rot = cnd["rot"]
            checked = []
            if check(cnd["c"],cnd["r"]):
                candidates.append(cnd)
        
        return candidates
    
    
    def possible_board(self, col, rot, row, zoid = None):
        if not zoid:
            zoid = self.curr_z
            
        newspace = copy.deepcopy(self.space)
        
        ends_game = self.sim_move(col, rot, row, zoid, newspace)
        
        return newspace, ends_game
        
    def get_move_features(self, board, col, rot, row, zoid, printout = False):
        
        newboard = copy.deepcopy(board)
        
        self.sim_move(col, rot, row, zoid, newboard)
        
        if printout:
            self.printspace(newboard)
        
        return self.get_features(newboard, prev_space = board)
    
    def find_drop(self, col, rot, zoid, space):
        if not zoid:
            zoid = self.curr_z
        if not space:
            space = self.space
        #start completely above the board
        z_h = len(space) + len(self.shapes[zoid][rot])
        for i in range(0, z_h + 1):
            #print("testing height", z_h - i)
            if self.detect_collision(col, rot, z_h - i, zoid, space):
                return z_h - i
        return None
    
    def detect_collision(self, col, rot, row, zoid = False, space = False, off = 0):
        if not zoid:
            zoid = self.curr_z
        if not space:
            space = self.space
        
        shape = self.shapes[zoid][rot]
        
        #set column and row to start checking
        x = col
        y = (len(space)-off) - row
        
        #begin iteration
        ix = x
        iy = y
        
        #for each cell in the shape
        for i in shape:
            for j in i:
                #if this cell isn't empty, and we aren't above the board...
                if j != 0 and iy >= 0:
                    if iy >= len(space):
                        return True
                    #print("checking",iy,ix)
                    if space[iy][ix] != 0:
                        return True
                ix += 1
            ix = x
            iy += 1
        return False
    
    
    
    ### DISPLAY
    
    def printscores(self):
        print("Name:\t" + str(self.name))
        print("Level:\t" + str(self.level))
        print("Score:\t" + str(self.score))
        print("Lines:\t" + str(self.lines))
        print(  "\t(1: " + str(self.l1) + 
                "  2: " + str(self.l2) + 
                "  3: " + str(self.l3) + 
                "  4: " + str(self.l4) + ")")
    
    def printoptions(self, opt = None):
        if not opt:
            opt = self.options
        for i in opt:
            self.printopt(i)
            if self.option_step > 0:
                time.sleep(self.option_step)
    
    def printcontroller(self, feats = False):
        self.controller._print(feats)
    
    def printopt(self, opt):
        feats = opt[4]
        print("\n")
        self.printscores()
        self.printcontroller(feats)
        self.printspace(opt[3])
        #print("Col: " + str(opt[0]))
        #print("Rot: " + str(opt[1]))
        #print("Row: " + str(opt[2]))
        #print("Max Ht: " + str(feats["max_ht"]))
        #print("Pits: " + str(feats["pits"]))
        #print("All heights: " + str(feats["all_ht"]))
        #print("Mean height: " + str(feats["mean_ht"]))
        #print("Cleared: " + str(feats["cleared"]))
        #print("Landing height: " + str(feats["landing_height"]))
        #print("Eroded cells: " + str(feats["eroded_cells"]))
        #print("Column trans: " + str(feats["col_trans"]))
        #print("Row trans: " + str(feats["row_trans"]))
        #print("All trans: " + str(feats["all_trans"]))
        #print("Wells: " + str(feats["wells"]))
        #print("Cumulative wells: " + str(feats["cuml_wells"]))
        #print("Deep wells: " + str(feats["deep_wells"]))
        #print("Max well: " + str(feats["max_well"]))
        #print("Cumulative clears: " + str(feats["cuml_cleared"]))
        #print("Cumulative eroded: " + str(feats["cuml_eroded"]))
        #print("Pit depths: " + str(feats["pit_depth"]))
        #print("Mean pit depths: " + str(feats["mean_pit_depth"]))
        #print("Pit rows: " + str(feats["pit_rows"]))
        #print("Column 9 heght: " + str(feats["column_9"]))
        #print("Scored tetris: " + str(feats["tetris"]))
    
    def printzoid(self, zoid = None):
        if not zoid:
            zoid = self.curr_z
        self.printspace(self.shapes[zoid][0])
    
    def printboard(self):
        self.printspace(self.space)
    
    def printspace(self, space):
        print("+" + "-"*len(space[0])*2 + "+")
        for i in range(0, len(space)):
         out = "|"
         for j in space[i]:
            if j == 0:
             out = out + "  "
            elif j == 1:
             out = out + u"\u2BDD "
            elif j == 2:
             out = out + u"\u2b1c "
         print(out + "|" + str(len(space)-i-1))
        print("+" + "-"*len(space[i])*2 + "+")
        numline = " "
        for j in range(0, len(space[0])):
            numline += str(j) + " "
        print(numline)
    ###
    
    #prints the board with a "drop candidate" position
        #takes a drop point of the format {"r":r,"c",c}
    def printdrop(self, space, drop):
        print("+" + "-"*len(space[0])*2 + "+")
        for i in range(0, len(space)):
         out = "|"
         for jj,j in enumerate(space[i]):
            if j == 0:
             if jj == drop["c"] and i == (len(space)-1)-drop["r"]:
              out = out + "XX"
             else:
              out = out + "  "
            elif j == 1:
             out = out + u"\u2BDD "
            elif j == 2:
             out = out + u"\u2b1c "
         print(out + "|" + str(len(space)-i-1))
        print("+" + "-"*len(space[i])*2 + "+")
        numline = " "
        for j in range(0, len(space[0])):
            numline += str(j) + " "
        print(numline)
        
    
    #u"\u2b1c"
    #u"\u2b1c"
    #u"\u26DD "
    
    def printlist(self, list):
        for i in list:
            print i
    ###
    
    
    ######## FEATURES
    
    def convert_space(self, space):
        newspace = []
        for r in space:
            row = []
            for c in r:
                if c == 0:
                    row.append(0)
                else:
                    row.append(1)
            newspace.append(row)
        return newspace
    
    def get_features(self, space, convert = False, prev_space = False, all = True):
        
        if convert:
            space = self.convert_space(space)
        
        cleared_space = self.clear_rows(space)
        
        cleared_space_cols = get_cols(cleared_space)
        
        features = {}
        
        #keys = self.controller.keys()
        
        """
        #working out a dependency tree.
        dependencies = {
                        "mean_ht":["HEIGHTS"],
                        "max_ht":["HEIGHTS"],
                        "min_ht":["HEIGHTS"],
                        "all_ht":["HEIGHTS"],
                        "max_ht_diff":["HEIGHTS","max_ht","mean_ht"],
                        "min_ht_diff":["HEIGHTS","mean_ht","min_ht"],
                        "column_9":["HEIGHTS"],
                        "cleared":[],
                        "cuml_cleared":["cleared"]
                        "tetris":["cleared"],
                        "move_score":["cleared"],
                        "col_trans":[],
                        "row_trans":[],
                        "all_trans":["col_trans","row_trans"],
                        "wells":["HEIGHTS","WELLS"],
                        "cuml_wells":["HEIGHTS","WELLS"],
                        "deep_wells":["HEIGHTS","WELLS"],
                        "max_well":["HEIGHTS","WELLS"],
                        "pits":["PITS"],
                        "pit_rows":["PITS"],
                        "lumped_pits":["PITS"],
                        "pit_depth":["PIT_DEPTHS"],
                        "mean_pit_depth":["PIT_DETHS"],
                        "cd_1":["DIFFS"],
                        "cd_2":["DIFFS"],
                        "cd_3":["DIFFS"],
                        "cd_4":["DIFFS"],
                        "cd_5":["DIFFS"],
                        "cd_6":["DIFFS"],
                        "cd_7":["DIFFS"],
                        "cd_8":["DIFFS"],
                        "cd_9":["DIFFS"],
                        "all_diffs":["DIFFS"],
                        "max_diffs":["DIFFS"],
                        "jaggedness":["DIFFS"],
                        "d_max_ht":["max_ht"],
                        "d_all_ht":["all_ht"],
                        "d_mean_ht":["mean_ht"],
                        "d_pits":["PITS","pits"],
                        "landing_height":[],
                        "pattern_div":[],
                        "matches":[],
                        "tetris_progress":["TETRIS"],
                        "nine_filled":["TETRIS"],
                        "full_cells":[],
                        "weighted_cells":[],
                        "eroded_cells":[],
                        "cuml_eroded":
                        }
        """
        
        ##heavy calculations
        
        all_heights = get_heights(cleared_space_cols)
        
        wells = self.get_wells(all_heights)
        
        diffs = []
        for i in range(0,len(all_heights)-1):
            diffs.append(all_heights[i+1] - all_heights[i])
        
        all_pits, pit_rows, lumped_pits = get_all_pits(cleared_space_cols)
        pit_depths = self.get_pit_depths(cleared_space_cols)
        
        
        #height dependent
        features["mean_ht"] = sum(all_heights) * 1.0 / len(all_heights) * 1.0
        features["max_ht"] = max(all_heights)
        features["min_ht"] = min(all_heights)
        features["all_ht"] = sum(all_heights)
        features["max_ht_diff"] = features["max_ht"] - features["mean_ht"]
        features["min_ht_diff"] = features["mean_ht"] - features["min_ht"]
        features["column_9"] = all_heights[-1]
        
        #cleared dependent
        features["cleared"] = self.filled_lines(space)
        features["cuml_cleared"] = self.accumulate([features["cleared"]])
        features["tetris"] = 1 if features["cleared"] == 4 else 0
        features["move_score"] = features["cleared"] * (self.level + 1)        
        
        #trans dependent
        features["col_trans"] = sum(self.get_col_transitions(cleared_space_cols))
        features["row_trans"] = sum(self.get_row_transitions(cleared_space))
        features["all_trans"] = features["col_trans"] + features["row_trans"]
        
        #well and height dependent
        features["wells"] = sum(wells)
        features["cuml_wells"] = self.accumulate(wells)
        features["deep_wells"] = sum([i for i in wells if i != 1])
        features["max_well"] = max(wells)
        
        #pit dependent
        features["pits"] = sum(all_pits)
        features["pit_rows"] = len(pit_rows)
        features["lumped_pits"] = lumped_pits
        
        #pit depth dependent
        features["pit_depth"] = sum(pit_depths)
        if features["pits"] * 1.0 == 0:
            features["mean_pit_depth"] = 0
        else:
            features["mean_pit_depth"] = features["pit_depth"] * 1.0 / features["pits"] * 1.0
        
        
        #diff and height dependent
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
        
        #previous space
        if prev_space:
            prev_cols = get_cols(prev_space)
            prev_heights = get_heights(prev_cols)
            prev_pits = get_all_pits(prev_cols)[0]
            
            features["d_max_ht"] = features["max_ht"] - max(prev_heights)
            features["d_all_ht"] = features["all_ht"] - sum(prev_heights)
            features["d_mean_ht"] = features["mean_ht"] - (sum(prev_heights) * 1.0 / len(prev_heights) * 1.0)
            features["d_pits"] = features["pits"] - sum(prev_pits)
        
        else:
            features["d_max_ht"] = None
            features["d_all_ht"] = None
            features["d_mean_ht"] = None
            features["d_pits"] = None

        
        #independents
        pd, pw, ph, pp = self.pile_stats(space)
        features["pile_density"] = pd
        features["pile_width"] = pw
        features["pile_height"] = ph
        features["pile_penalty"] = pp
        
        features["landing_height"] = self.get_landing_height(space)
        
        features["pattern_div"] = self.get_col_diversity(cleared_space_cols)
        
        features["matches"] = self.get_matches(space)
        
        #if "tetris_progress" in keys or "nine_filled" in keys or all: 
        tetris_progress, nine_filled = self.get_tetris_progress(cleared_space)
        features["tetris_progress"] = tetris_progress
        features["nine_filled"] = nine_filled
            
        features["full_cells"] = self.get_full_cells(cleared_space)
        
        features["weighted_cells"] = self.get_full_cells(cleared_space, row_weighted = True)
        
        features["eroded_cells"] = self.get_eroded_cells(space)
        features["cuml_eroded"] = self.accumulate([features["eroded_cells"]])
        
        return features
    
    
    ## Helper functions for manipulating the board space
    
    def get_col(self, col, space):
        out = []
        for i in space:
            out.append(i[col])
        return out
    ###
        
    def get_row(self, row, space):
        return space[row]
    ###
    
    ### FEATURES
        
    def get_full_cells(self, space, row_weighted = False):
        total = 0
        for i in range(0,len(space)):
            val = len(space) - i if row_weighted else 1
            for c in space[i]:
                if c != 0:
                    total += val
        return total

    
    #Pits
    
    #need to represent pits as a list of unique pits with a particular length;
    
    def get_matches(self, space):
        matches = 0
        for r in range(0,len(space)):
            for c in range(0, len(space[r])):
                if space[r][c] == 2:
                    #down
                    if r + 1 >= len(space):
                        matches += 1
                    else:
                        if space[r+1][c] == 1:
                            matches += 1
                    #left
                    if c - 1 < 0:
                        matches += 1
                    else:
                        if space[r][c-1] == 1:
                            matches += 1
                    #right
                    if c + 1 >= len(space[r]):
                        matches += 1
                    else:
                        if space[r][c+1] == 1:
                            matches += 1
                    #up, rarely
                    if r - 1 >= 0:
                        if space[r-1][c] == 1:
                            matches += 1
        return matches
    ###
    
    def get_landing_height(self, space):
        for i in range(0,len(space)):
            if 2 in space[len(space)-1-i]:
                return(i)
        
    def get_eroded_cells(self, space):
        cells = 0
        for i in space:
            if self.line_filled(i):
                cells += i.count(2)
        return cells
    
    #Roughness
    def get_transitions(self, v):
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
    ###
    
    #!# parallelize
    def get_all_transitions(self, space):
        out = []
        for i in space:
            out.append(self.get_transitions(i))
        return(out)
    ###
    
    def get_col_transitions(self, colspace):
        return self.get_all_transitions(colspace)
    
    def get_row_transitions(self, space):
        return self.get_all_transitions(space)
    
    def get_col_diversity(self, colspace):
        patterns = []
        for i in range(0,len(colspace)-1):
            pattern = []
            for j in range(0, len(colspace[i])):
                pattern.append(colspace[i][j] - colspace[i+1][j])
            
            patterns.append(pattern)
        
        patterns2 = []
        for i in patterns:
            if i not in patterns2:
                patterns2.append(i)
        return len(patterns2)
        
    
    def get_pit_depth(self, v):
        state = 0
        depth = 0
        curdepth = 0
        for i in v:
            #found first full cell
            if state == 0 and i != 0:
                curdepth += 1
                state = 1
            #found another full cell
            elif state != 0 and i != 0:
                curdepth += 1
            #found a pit! commit current depth to total
            elif state != 0 and i == 0:
                depth += curdepth
        return depth
            
        
    
    def get_pit_depths(self, colspace):
        out = []
        for i in colspace:
            out.append(self.get_pit_depth(i))
        return(out)
            
    
    def get_wells(self, heights, cumulative = False):
        heights = [len(self.space)] + heights + [len(self.space)]
        
        wells = []
        for i in range(1, len(heights)-1):
            ldiff = heights[i-1] - heights[i]
            rdiff = heights[i+1] - heights[i]
            if ldiff < 0 or rdiff < 0:
                wells.append(0)
            else:
                wells.append(min(ldiff, rdiff))
        
        return wells
    
    def accumulate(self, vector):
        out = 0
        for i in vector:
            for j in range(1,i+1):
                out += j
        return out
    
    def nine_filled(self, row):
        filled = 0
        for i in range(0,len(row)):
            if row[i] != 0:
                filled += 1
            if row[i] == 0:
                ix = i
        if filled == 9:
            return ix
        else:
            return None
    
    def pile_stats(self, space):
        cols = get_cols(space)
        heights = get_heights(cols)
        col_sums = [sum([0 if cc==0 else 1 for cc in c]) for c in cols]
        penalty = [heights[i]-col_sums[i] for i in range(0,len(cols))]
        w = [i for i in range(0,len(heights)) if heights[i]>0]
        ii = min(w)
        jj = max(w)
        width = jj - ii + 1
        height = max(heights)
        s = sum([sum([1 if r>0 else 0 for r in row]) for row in space])
        return (1.0*s/(width*height),width,height,sum(penalty)**1.25)
    
    #eating a LOT of the processing
    def get_tetris_progress(self, space):
        #newspace = copy.deepcopy(space)
        #newspace.reverse()
        
        nine_count = 0
                
        progress = 0
        prev_col = -1
        
        prev_row = []
        #from the bottom up
        for r in range(1,len(space)+1):
            r_ix = len(space)-r
            col = self.nine_filled(space[r_ix])
            
            #found a filled row
            if col != None:
                nine_count += 1
                #new column, reset counter
                if col != prev_col:
                    if r == 1:  #first row
                        progress = 1
                        prev_col = col
                        stagnated = False
                    else:
                        if space[r_ix+1][col] != 0:  #if there's a block below, we can restart
                            progress = 1
                            prev_col = col
                            stagnated = False
                        else:
                            progress = 0
                            prev_col = -1
                #same column, increase counter
                elif col == prev_col and not stagnated:
                    progress += 1
            
            #no nine-count row detected
            else:
                #column is blocked, reset progress and column
                if space[r_ix][prev_col] != 0:
                    progress = 0
                    prev_col = -1
                #otherwise, progress stagnates here
                else:
                    stagnated = True
        return progress, nine_count
            
    ###### CONTROLLERS
    
    def evaluate(self, vars, opts):
        
        #generate function values
        for i in opts:
            val = 0
            for j in vars.keys():
                val += i[4][j] * vars[j]
                #print(j, i[4][j[0]])
            i.append(val)
        
        
        #find highest value
        crit = None
        for i in opts:
            if not crit:
                crit = i[-1]
            else:
                crit = max(crit, i[-1])
        
        #slim down options
        out = []
        for i in opts:
            if i[-1] == crit:
                out.append(i)
        
        return out
    
    
    
    
    def control(self):
        choice = self.controller.evaluate(self)
        
        if self.show_choice:
            self.printopt(choice)
            if self.choice_step >0:
                time.sleep(self.choice_step)
        
        self.move(choice)
        return choice
    
    
    def run(self, eps = -1, printstep = 500):
        max_eps = eps
        ep = 0
        while not self.game_over and ep != max_eps:
            if self.game_over:
                break
            
            ##generate options and features
            self.get_options()
            
            if len(self.options) == 0:
                break
            
            ####controllers
            self.control()
            
            if self.show_scores or ep % printstep == 0 and not printstep == -1:
              print("\nEpisode: " + str(ep))
              self.printscores()
            ep += 1 
        
        if self.show_result:
            print("\n\nGame Over\nFinal scores:")
            print("Episodes: " + str(ep))
            self.printscores()
            self.printcontroller()
            print("\n")
            
        return({"lines":self.lines,
                "l1":self.l1,
                "l2":self.l2,
                "l3":self.l3,
                "l4":self.l4,
                "score":self.score,
                "level":self.level,
                "eps":ep})
    
def testboard():
    testboard = []
    """
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    testboard.append([0,1,0,1,0,1,0,1,0,1])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    testboard.append([0,1,0,1,0,1,0,1,0,1])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    testboard.append([0,1,0,1,0,1,0,1,0,1])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    testboard.append([0,1,0,1,0,1,0,1,0,1])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    testboard.append([0,1,0,1,0,1,0,1,0,1])
    testboard.append([1,0,1,0,1,0,1,0,1,0])
    """
    
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,1])
    testboard.append([0,0,0,0,0,0,0,0,1,1])
    testboard.append([0,0,0,0,0,0,1,0,0,1])
    testboard.append([0,0,0,0,0,0,1,1,1,1])
    testboard.append([0,0,0,1,1,1,1,1,1,1])
    testboard.append([0,0,1,1,1,1,1,1,1,1])
    testboard.append([0,0,1,1,1,1,1,1,1,1])
    testboard.append([0,0,1,1,1,0,0,0,1,1])
    testboard.append([0,0,0,1,0,0,0,1,1,1])
    testboard.append([0,1,1,0,0,0,0,0,1,1])
    
    return testboard


    
    
#Run main.
def main(argv):
    
    controller = WeightedAverageController(WEIGHTS_RYAN)
    #controller = ProbabilisticController(PROBS_DELLACHERIE)
    
    sim = TetrisSimulator(controller = controller,
                #board = testboard(),
                #curr="L", next = "S",
                show_choice = True, 
                show_options = True, 
                option_step = .3, 
                choice_step = 1,
                #seed = 1
                )
    
    sim.show_options = False
    sim.choice_step = 0
    sim.overhangs = False
    sim.force_legal = True 
    #sim.printboard()
    #print sim.pile_density(sim.space)
    sim.run()


if __name__ == "__main__":
    main(sys.argv)
