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
    pieces = ["I", "O", "T", "S", "Z", "J", "L"]
    
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
    
    
    def __init__(self,board = None, curr = None, next = None, controller = None, 
                    show_scores = False, show_options = False, show_result = True, show_choice = False,
                    option_step = 0, choice_step = 0, name = "Controller", seed = time.time() * 10000000000000.0):
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
            self.curr_z = self.pieces[self.sequence.randint(0,len(self.pieces)-1)]
            
        if next:
            self.next_z = next
        else:
            self.next_z = self.pieces[self.sequence.randint(0,len(self.pieces)-1)]
        
        self.name = name
        
        if controller:
            self.controller = controller
        else: #default Dellacherie model
            self.controller = {"landing_height":-1,
                            "eroded_cells":1,
                            "row_trans":-1,
                            "col_trans":-1,
                            "pits":-4,
                            "cuml_wells":-1}
        
        
        self.show_result = show_result
        self.show_scores = show_scores
        self.show_options = show_options
        self.show_choice = show_choice
    
        self.option_step = option_step
        self.choice_step = choice_step
        
        #self.heights = self.get_heights(self.space)
        #self.pits = self.get_all_pits(self.space)
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
        self.options = self.possible_moves()
        
        #cull game-ending options
        non_ending = []
        for i in self.options:
            if not i[5]:
                non_ending.append(i)
        self.options = non_ending
    
    #function that takes a board state and a zoid, and optionally the move made
        #returns a choice (row, col, rot)
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
        self.next_z = self.pieces[self.sequence.randint(0,len(self.pieces)-1)]
    
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
                simboard, ends_game = self.possible_board(c,r,row)
                features = self.get_features(simboard,prev_space = space, all = False)
                opt = [c,r,row,simboard,features, ends_game]
                options.append(opt)
                
        if self.show_options:
            self.printoptions(options)
        
        return options
    
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
    
    def detect_collision(self, col, rot, row, zoid = False, space = False):
        if not zoid:
            zoid = self.curr_z
        if not space:
            space = self.space
        
        shape = self.shapes[zoid][rot]
        
        #set column and row to start checking
        x = col
        y = len(space) - row
        
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
        for k in sorted(self.controller.keys()):
            outstr = k.ljust(15) + ":\t" 
            if feats:
                outstr += str(feats[k]) + "\t(" + ('%3.3f'%self.controller[k]).rjust(8) + ")"
            else:
                outstr += ('%3.3f'%self.controller[k]).rjust(8)
            print(outstr)

    
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
        
        cleared_space_cols = self.get_cols(cleared_space)
        
        features = {}
        
        keys = self.controller.keys()
        
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
        
        all_heights = self.get_heights(cleared_space_cols)
        
        wells = self.get_wells(all_heights)
        
        diffs = []
        for i in range(0,len(all_heights)-1):
            diffs.append(all_heights[i+1] - all_heights[i])
        
        all_pits, pit_rows, lumped_pits = self.get_all_pits(cleared_space_cols)
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
            prev_cols = self.get_cols(prev_space)
            prev_heights = self.get_heights(prev_cols)
            prev_pits = self.get_all_pits(prev_cols)[0]
            
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
    
    #!# Work to remove this entirely! Unnecessary processing!
    #transform the space to be column-wise, rather than rows
    def get_cols(self, space):
        
        #out = []
        #for i in range(0, len(space[0])):
        #    out.append(self.get_col(i, space))
        
        return zip(*space)
    
    
    ### FEATURES
    
    #Heights
    def get_height(self, v):
        for i in range(0, len(v)):
            if v[i] != 0:
                return len(v) - i
        return 0
    ###
    
    #!# parallelize
    def get_heights(self, colspace):
        out = []
        for i in colspace:
            out.append(self.get_height(i))
        return(out)
    ###
    
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
    
    def get_pits(self, v):
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
    ###
    
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
    
    #!# parallelize
    def get_all_pits(self, colspace):
        col_pits = []
        pit_rows = [] 
        lumped_pits = 0
        for i in colspace:
            pits, lumped = self.get_pits(i)
            lumped_pits += lumped
            col_pits.append(len(pits))
            for j in pits:
                if j not in pit_rows:
                    pit_rows.append(j)
        return(col_pits, pit_rows, lumped_pits)
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
        options = self.options
        options = self.evaluate(self.controller, options)
        choice = random.randint(0, len(options)-1)
        
        if self.show_choice:
            self.printopt(options[choice])
            if self.choice_step >0:
                time.sleep(self.choice_step)
        
        self.move(options[choice])
        return options[choice]
    
    
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
            try:
                self.control()
            except TypeError:
                print("IT'S THAT ONE WEIRD ERROR. YOU KNOW THE ONE.")
                
            
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
                "level":self.level})
    
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
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,0,0,0])
    testboard.append([0,0,0,0,0,0,0,1,0,1])
    testboard.append([0,0,0,0,0,0,1,1,1,1])
    testboard.append([0,0,0,1,1,1,1,1,1,1])
    testboard.append([0,1,1,1,1,1,1,1,1,1])
    testboard.append([0,1,1,1,1,1,1,1,1,1])
    testboard.append([1,0,1,1,1,1,1,0,1,1])
    testboard.append([1,0,1,1,1,1,1,1,1,1])
    testboard.append([1,1,1,1,1,1,1,0,1,1])
    
    return testboard


    
    
#Run main.
def main(argv):
    
    #default Dellacherie controller; 660,000 lines avg / game in literature!
    controller1 = {"landing_height":-1,
                "eroded_cells":1,
                "row_trans":-1,
                "col_trans":-1,
                "pits":-4,
                "cuml_wells":-1}
    
    
    #DTS controller, from Dellacherie + Thiery & Scherrer; 35,000,000 rows?!!?!
    controller2 = {"landing_height":-12.63,
                "eroded_cells":6.60,
                "row_trans":-9.22,
                "col_trans":-19.77,
                "pits":-13.08,
                "cuml_wells":-10.49,
                "pit_depth":-1.61,
                "pit_rows":-24.04}
    
    #bad controller for demonstration's purposes
    controller3 = {"landing_height":1,
                "eroded_cells":1,
                "row_trans":-1,
                "col_trans":-1,
                "pits":1,
                "cuml_wells":-1}
    
    sim = TetrisSimulator(controller = controller1, 
                        show_choice = True, 
                        show_options = True, 
                        option_step = .02, 
                        choice_step = .5,
                        seed = 1
                        )
    
    sim2 = TetrisSimulator(board = testboard(), curr = "S", next = "S" )
    sim2_feats = sim2.report_move_features(col = 4, row = 7, rot = 0, offset = 0, printout = True)
    
    for i, k in enumerate(sorted(sim2_feats.keys())):
        print i, k, sim2_feats[k]
    
    print(sim.predict(testboard(), "Z"))
    
    #sim.run()
    


if __name__ == "__main__":
    main(sys.argv)
###
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
###


"""
Requirements:

Take arbitrary board.
Generate random zoids appropriately. (7bag? default? pure random? What did they use?)

Generate all possible (simple) moves.
    -with and without line clears

Execute moves:
    Be able to clear lines (easy, check filled, pop them out)
    Keep track of lines cleared.

For classic controllers:
Generate HOST of features for a given board state.

"""


#sim.do_move(0,0,19)
  #sim.printboard()
  #print(sim.game_over)
  
  #board.report()
  
  
  #sim.printboard()
  #options = sim.possible_moves()
  #sim.printoptions(options, timestep = 1)
  
  
  
  
  #randboard = TetrisBoardStats(get_random_space(10,20,12))
  #randboard.set_random_pieces()
  #randboard.report()


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
"""
######################################################################

######################################################################

######################################################################

######################################################################
    def set_zoids(self, curr, next):
        self.curr_z = curr
        self.next_z = next
    ###
    
    def set_board(self, board):
        self.space = self.convert_board(board)
    ###
    
    def convert_board(self, board):
        reboard = []
        for i in board:
            line = []
            for j in i:
                if j == 0:
                    line.append(0)
                else:
                    line.append(1)
            reboard.append(line)
        return reboard
    ###
    
    def print_stats(self):
        for i in self.stats_dict:
            print(i, self.stats_dict[i])
        print()
    ###
    
    def set_random_zoids(self):
        self.curr_z = self.pieces[random.randint(0,6)]
        self.next_z = self.pieces[random.randint(0,6)]
    ###
        
    stats_header =[
    "height", 
    "avgheight", 
    "pits", 
    "roughness", 
    "ridge_len", 
    "ridge_len_sqr", 
    "tetris_available",
    "tetris_progress",
    "filled_rows_covered",
    "tetrises_covered",
    "good_pos_curr",
    "good_pos_next",
    "good_pos_any"
    ]
    
    def get_stats(self):
        stats = {}
        stats["height"] = sum(self.heights)
        stats["avgheight"] = sum(self.heights)/10
        stats["pits"] = sum(self.pits)
        stats["roughness"] = sum(self.row_roughs)
        stats["ridge_len"] = self.get_ridge_jag(self.ridge)
        stats["ridge_len_sqr"] = self.get_ridge_jag(self.ridge, fun = lambda a:a*a)
        
        tetrisop = self.tetris_status(self.space)
        stats["tetris_available"] = tetrisop[0]
        stats["tetris_progress"] = tetrisop[1]
        stats["filled_rows_covered"] = sum(tetrisop[2])
        tetrises_covered = 0
        for i in tetrisop[2]:
            tetrises_covered += i / 4
        stats["tetrises_covered"] = tetrises_covered
        
        curr_matches = self.match_piece(self.ridge, self.curr_z)
        next_matches = self.match_piece(self.ridge, self.next_z)
        all_matches = self.match_piece(self.ridge, "all")
        
        stats["curr_matches"] = curr_matches
        
        curr_nopits = self.filter_matches(curr_matches, pits = 0)
        next_nopits = self.filter_matches(next_matches, pits = 0)
        all_nopits = self.filter_matches(all_matches, pits = 0)
        
        stats["good_pos_curr"] = len(curr_nopits)
        stats["good_pos_next"] = len(next_nopits)
        stats["good_pos_any"] = len(all_nopits)
        
        self.stats_dict = stats
        
        return stats
    ###
    
    def report(self):
        print("Board:")
        self.printspace(self.space)
        #printspace(self.get_cols(space))
        
        print("CurrZoid",self.curr_z,"NextZoid",self.next_z)
        
        print("Heights:")
        print(self.heights , " => " , sum(self.heights), "Avg:", sum(self.heights)/10 )
        
        print("Pits:")
        print(self.pits , " => " , sum(self.pits) )
        
        print("Column Roughness:")
        print(self.col_roughs , " => " , sum(self.col_roughs) )
        print("Row Roughness:")
        print(self.row_roughs , " => " , sum(self.row_roughs) )
        print("Total roughness = " , sum(self.col_roughs) + sum(self.row_roughs) )
        
        
        print("Ridge:")
        print(self.ridge)
        print("Ridge-len= ", self.get_ridge_length(self.ridge))
        print("Ridge-jag: abs=", self.get_ridge_jag(self.ridge), " sqr=", self.get_ridge_jag(self.ridge, fun = lambda a:a*a) )
        print("Height-jag: abs=",  self.get_height_jag(self.heights),  " sqr=" , self.get_height_jag(self.heights, fun = lambda a:a*a) )
        
        print("Tetris opportunities:")
        tetris_stat = self.tetris_status(self.space)
        print("Status:    " , tetris_stat)
        print("Progress:  ", self.stats_dict["tetris_progress"])
        print("Available: ", self.stats_dict["tetris_available"])
        print("Filled rows covered: ", self.stats_dict["filled_rows_covered"])
        
        print("Piecewise matches:")
        print("Pitless: Current ", self.curr_z, self.stats_dict["good_pos_curr"])
        print("Pitless: Next    ", self.next_z, self.stats_dict["good_pos_next"])
        print("Pitless: Any     ", self.stats_dict["good_pos_any"])
        
        matchstr = "Type\tRot\tRow\tCol\tPit\tLt\tRt\tCont\tProfile\n"
        for i in self.stats_dict["curr_matches"]:
            for j in i:
                matchstr += str(j) + "\t"
            matchstr += "\n"
        print(matchstr)
            
"""
"""
        #self.check_match_quality(ridge, self.get_piece_ridge("I", 0))
        #match_pieces(ridge, all = True)
        #match_pieces(ridge, p1 = "L")
        print("Current Piece:", self.curr_z)
        curmatch = self.match_piece(self.ridge, self.curr_z)
        print("  Num possible:", len(curmatch))
        
        curfilt = self.filter_matches(curmatch, ldiff = 0, rdiff = 0, pits = 0)
        print("  Perfects:", len(curfilt))
        self.printlist(curfilt)
        
        curfilt = self.filter_matches(curmatch, pits = 0)
        print("  Bottoms:", len(curfilt))
        self.printlist(curfilt)
        
        
        print("Next Piece:", self.next_z)
        nextmatch = self.match_piece(self.ridge, self.next_z)
        print("  Num possible:", len(nextmatch))
        #self.printlist(nextmatch)
        
        nextfilt = self.filter_matches(nextmatch, ldiff = 0, rdiff = 0, pits = 0)
        print("  Perfects:", len(nextfilt))
        self.printlist(nextfilt)
        
        nextfilt = self.filter_matches(nextmatch, pits = 0)
        print("  Bottoms:", len(nextfilt))
        self.printlist(nextfilt)
        
        print("All Pieces:")
        allmatch = self.match_piece(self.ridge, "all")
        self.printlist(self.filter_matches(allmatch, pits = 0))
"""
"""
    ###
    def update_stats(self):
        
        self.heights = self.get_heights(self.space)
        self.pits = self.get_all_pits(self.space)
        self.col_roughs = self.get_roughs(self.space, columns = True)
        self.row_roughs = self.get_roughs(self.space, columns = False)
        self.ridge = self.get_ridge(self.space)
        self.matches = []
        
        self.get_stats()
    ###
    
    #Roughness
    def get_roughness(self, v):
        state = v[0]
        rough = 0
        for i in v[1:]:
         if i != state:
             rough += 1
             state = i
        return rough
    ###
    
    def get_roughs(self, space, columns = False):
        out = []
        if columns:
            space = self.get_cols(space)
        for i in space:
            out.append(self.get_roughness(i))
        return(out)
    ###
    
    
    #Pits
    
    #need to represent pits as a list of unique pits with a particular length;
    
    def get_pits(self, v):
        state = v[0]
        pits = 0
        for i in v[1:]:
            if i == 1:
                state = 1
            if i == 0 and state == 1:
                pits += 1
        return pits
    ###
    
    def get_all_pits(self, space):
        space = self.get_cols(space)
        out = []
        for i in space:
            out.append(self.get_pits(i))
        return(out)
    ###
    
    def get_filled(self, vect):
        sum = 0
        for i in vect:
            if i != 0:
                sum += 1
        return sum
    ###
    
    
    def find_empty(self, vect):
        for i in range(0, len(vect)):
            if vect[i] == 0:
                return i
    ###
    
    
    
    
    def get_ridge(self, space):
        heights = self.get_heights(space)
        out = []
        out.append(heights[0] - len(space))
        for i in range(0, len(heights)-1):
            out.append(heights[i+1] - heights[i])
        out.append(len(space) - heights[-1])
        return out
    ###
    
    def get_ridge_length(self, ridge):
        ridge = ridge[1:-1]
        return(sum(map(abs, ridge)) + 10)
    
    def get_ridge_jag(self, ridge, fun = abs):
        ridge = ridge[1:-1]
        return(sum(map(fun, ridge)))
    ###
    
    def get_height_jag(self, heights, fun = abs):
        avg = sum(heights) * 1.0 / len(heights) * 1.0
        errs = map(lambda a:a-avg, heights)
        return sum(map(fun,errs))
    ###
    
    
    
    #put this into a hash table, you dolt. 
    def get_piece(self, p, r):
        ridge = False
        shape = []
        if p == "O":
            if r == 0:
                ridge = [-2,0,2]
                shape.append([1,1])
                shape.append([1,1])
                
        if p == "I":
            if r == 0:
                ridge = [-1,0,0,0,1]
                shape.append([1,1,1,1])
            if r == 1:
                ridge = [-4, 4]
                shape.append([1])
                shape.append([1])
                shape.append([1])
                shape.append([1])
        if p == "Z":
            if r == 0:
                ridge = [-1, -1, 0, 1]
                shape.append([1, 1, 0])
                shape.append([0, 1, 1])
            if r == 1:
                ridge = [-2, 1, 2]
                shape.append([0, 1])
                shape.append([1, 1])
                shape.append([1, 0])
        if p == "S":
            if r == 0:
                ridge = [-1, 0, 1, 1]
                shape.append([0, 1, 1])
                shape.append([1, 1, 0])
            if r == 1:
                ridge = [-2, -1, 2]
                shape.append([1, 0])
                shape.append([1, 1])
                shape.append([0, 1])
        if p == "T":
            if r == 0:
                ridge = [-1, -1, 1, 1]
                shape.append([1, 1, 1])
                shape.append([0, 1, 0])
            if r == 1:
                ridge = [-3, 1, 1]
                shape.append([0, 1])
                shape.append([1, 1])
                shape.append([0, 1])
            if r == 2:
                ridge = [-1, 0, 0, 1]
                shape.append([0, 1, 0])
                shape.append([1, 1, 1])
            if r == 3:
                ridge = [-1, -1, 3]
                shape.append([1, 0])
                shape.append([1, 1])
                shape.append([1, 0])
        if p == "L":
            if r == 0:
                ridge = [-2, 1, 0, 1]
                shape.append([1, 1, 1])
                shape.append([1, 0, 0])
            if r == 1:
                ridge = [-1, -2, 3]
                shape.append([1, 1])
                shape.append([0, 1])
                shape.append([0, 1])
            if r == 2:
                ridge = [-1, 0, 0, 2]
                shape.append([0, 0, 1])
                shape.append([1, 1, 1])
            if r == 3:
                ridge = [-3, 0, 1]
                shape.append([1, 0])
                shape.append([1, 0])
                shape.append([1, 1])
        if p == "J":
            if r == 0:
                ridge = [-1, 0, -1, 2]
                shape.append([1, 1, 1])
                shape.append([0, 0, 1])
            if r == 1:
                ridge = [-1, 0, 3]
                shape.append([0, 1])
                shape.append([0, 1])
                shape.append([1, 1])
            if r == 2:
                ridge = [-2, 0, 0, 1]
                shape.append([1, 0, 0])
                shape.append([1, 1, 1])
            if r == 3:
                ridge = [-3, 2, 1]
                shape.append([1, 1])
                shape.append([1, 0])
                shape.append([1, 0])
        if ridge:
            return [shape, ridge]
        else:
            return False
    ###
    
    def get_piece_shape(self, p, r):
        return self.get_piece(p,r)[0]
    ###
    
    def get_piece_ridge(self, p, r):
        return self.get_piece(p,r)[1]
    ###
    
    ##Use to select viable piece positions
    # !! Cannot handle overhangs!
    #match structure = [column, pits, left, right, contour, [profile]]
    
    # !! Broken for T and J blocks (leftmost column containing pit)
    def check_match_quality(self, vect, trgt):
        matches = []
        
        #vector is zoid ridge, target is subset ridge
        for i in range(0, len(vect) - len(trgt) + 1):
            profile = []
            
            #leftside match
            profile.append(trgt[0] - vect[i])
            
            #middle and right matches
            v_hts = [0]
            t_hts = [0]
            v_ht = 0
            t_ht = 0
            profile.append(0)
            for j in range(1, len(trgt)):
                v_ht += vect[i+j]
                t_ht += trgt[j]
                v_hts.append(v_ht)
                t_hts.append(t_ht)
                profile.append(v_ht - t_ht)
            
            pits = 0
            mid = profile[1:-1]
            if mid:
                if max(mid) > 0:
                    for k in range(0, len(profile)):
                        profile[k] -= max(mid)
                    for k in range(0, len(t_hts)):
                        t_hts[k] += max(mid)
                pits = sum(map(abs, mid))
            
            left = profile[0] 
            right = profile[-1]
            
            contours = self.matched_contours(vect, trgt, v_hts[:-1], t_hts[:-1], i)
            
            matches.append([i, pits, left, right, contours, profile])
            #print(matches[-1])
        return matches
    ###
    
    
    #!#!# Not working correctly; doesn't account for split-level problem
    ###        working better, but needs extensive bug testing
    def matched_contours(self, vect, trgt, v_hts, t_hts, pos):
        sides = 0
        slice = vect[pos:pos+len(trgt)]
        
        if slice[0] <= 0 and t_hts[0] >= v_hts[0]:
            leftside = v_hts[0] + abs(slice[0]) - t_hts[0]
            if leftside < 0:
                leftside = 0
            if leftside > abs(trgt[0]):
                leftside = abs(trgt[0])
            sides += leftside
            
        for i in range(1, len(slice) - 1):
            if t_hts[i-1] >= v_hts[i-1]:
                if t_hts[i-1] == v_hts[i-1]:
                    sides += 1
                if t_hts[i] >= v_hts[i] and slice[i] == trgt[i]:
                    sides += abs(trgt[i])
        
        if t_hts[-1] == v_hts[-1]:
            sides += 1
            
        if slice[-1] >= 0 and t_hts[-1] >= v_hts[-1]:
            rightside = v_hts[-1] + abs(slice[-1]) - t_hts[-1]
            if rightside < 0:
                rightside = 0
            if rightside > abs(trgt[-1]):
                rightside = abs(trgt[-1])
            sides += rightside
        return sides
    ###
            
    #output: type, rotation, row, column, pits, ldiff, rdiff, contours, [profile]
    def match_piece(self, ridge, piece):
        pieces = ["O","I","Z","S","T","L","J"]
        
        out = []
        
        for p in pieces:
            if p == piece or piece == "all":
                for i in range(0,4):
                    p_ridge = self.get_piece(p, i)
                    if p_ridge:
                        matches = self.check_match_quality(ridge, p_ridge[1])
                        for match in matches:
                            p_ht = len(p_ridge[0])
                            col_ht = self.heights[match[0]]
                            row = p_ht + col_ht - 1
                            out.append([p,i,row] + match)
        return out
     
    ###
    
    #good for filtering categorically, and for using arbitrary piece sizes
    def filter_matches(self, matches, ldiff = -1000, rdiff = -1000, pits = 1000, mode = ""):
        out = []
        
        for m in matches:
            if m[4] <= pits and m[5] >= ldiff and m[6] >= rdiff:
                out.append(m)
        
        return out
    ###
    
    
    
    
    
    #outputs [position, row, height, is-available?]
    # Not working for left side; entering debug mode
    def tetris_opps(self, space):
        out = [] #all candidates
        heights = self.get_heights(space)
        
        #get the workspace and reverse it, checking bottom to top
        workspace = []
        for i in space:
            workspace.append(i)
        workspace.reverse()
        
        prev_pos = -1
        run = 1
        
        #if this row is filled with all-but-one, set the "pos" to that column
        if self.get_filled(workspace[0]) == len(workspace[0])-1:
            prev_pos = self.find_empty(workspace[0])
        
        #start the run and check the rest of the workspace
        for i in range(1, len(workspace)):
            #failcase: found a non-full row heading up.
            if self.get_filled(workspace[i]) != len(workspace[i])-1: #found non-full row
                if(run > 0 and prev_pos > -1):
                    out.append([prev_pos, i - run, run])
                run = 1
                prev_pos = -1
            #otherwise, found a good row to add
            else: 						    #found full row
                pos = self.find_empty(workspace[i])
                
                #if filled row changed...
                if pos != prev_pos:			        #if position differs, revert
                    if(run > 0 and prev_pos > -1):
                        out.append([prev_pos, i - run, run])
                    run = 1
                    prev_pos = pos
                
                #otherwise increment the run
                else:							#increment
                    run += 1
        
        #truncate current run after iterating through whole board.
        if(run > 0 and prev_pos > -1):
            out.append([prev_pos, i - run, run])
        
        #compute coveredness using height values. 
        for i in range(0, len(out)):
            if heights[out[i][0]] <= out[i][1]:
                out[i].append(True)
            else:
                out[i].append(False)
        
        #return: list of opps, [column, start-height, runlength, open-top?]
        return out
    ###
    
    
    #need to be able to detect if the block below is filled, i.e. tetris-able
    
    def tetris_status(self, space):
        candidates = self.tetris_opps(space)
        heights = self.get_heights(space) #allow "truth" status only if height is equivalent for the operative column
        #print(candidates)
        out = 0
        failed = []
        onground = False #check for "floating" tetrises
        for cand in candidates:
            #if top open, update
            if cand[3]:
                #and this is the highest "progress" so far
                if out < cand[2]:
                    out = cand[2]
                    onground = heights[cand[0]] == cand[1]
            #otherwise, append to failed
            else:
                failed.append(cand[2])
        return [out>=4 and onground, out, failed]
    ###
    
    def get_random_space(self, x,y,height):
        space = []
        for i in range(0, y):
            row = []
            if i >= y - height:
                for j in range(0, x):
                    row.append(random.randint(0,1))
                space.append(row)
            else:
                space.append([0]*x)
        return space
    ###






    
#gets the leftmost board column the piece occupies
def zoid_x(diff_board):
    for j in range(0, len(diff_board[0])):
        for i in range(0, len(diff_board)):
            if diff_board[i][j] != 0: #found a non-empty column
                return j
    return -1

#gets the topmost board row the piece occupies
def zoid_y(diff_board):
    for i in range(0, len(diff_board)):
        for j in range(0, len(diff_board[0])):
            if diff_board[i][j] != 0: #found a non-empty row
                return len(diff_board) - i
    return -1
        

def get_zoid_loc(board, prev_board, top_offset = 0):
    diff = board_diff(board, prev_board, top_offset)
    return [zoid_x(diff), zoid_y(diff)]
    
    
###########################################################
##################################
##############
######
###
##
#
#


"""


