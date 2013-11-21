#to be added
# arguments to set what is printed by the object
# 


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
    
    
    def __init__(self,board = None, curr = None, next = None, controller = None):
        """Generates object based on given board layout"""
        if board:
            self.space = board
        else:
            self.init_board()
            
        if curr:
            self.curr_z = curr
        else:
            self.curr_z = self.pieces[random.randint(0,len(self.pieces)-1)]
            
        if next:
            self.next_z = next
        else:
            self.next_z = self.pieces[random.randint(0,len(self.pieces)-1)]
        
        if controller:
            self.controller = controller
        else: #default Dellacherie model
            self.controller = [["landing_height",-1],
                            ["eroded_cells",1],
                            ["row_trans",-1],
                            ["col_trans",-1],
                            ["pits",-4],
                            ["cuml_wells",-1]]
        
        
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
        z_id = random.randint( 0, len(self.zoids) )

        #then repeat/dummy check, and reroll *once*
        if not self.curr_z or z_id == len(self.zoids):
            return random.randint( 0, len(self.zoids)-1 )
        elif self.zoids[z_id] == self.curr_z:
            return random.randint( 0, len(self.zoids)-1 )

        return z_id
    ###
    
    
    def get_options(self):
        self.options = self.possible_moves()
        
        #cull game-ending options
        non_ending = []
        for i in self.options:
            if not i[5]:
                non_ending.append(i)
        self.options = non_ending
    
    
    #work all of these functions in here
    
    
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
        self.next_z = self.pieces[random.randint(0,len(self.pieces)-1)]
    
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
                features = self.get_features(simboard)
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
    
    def printopt(self, opt):
        feats = opt[4]
        print("Col: " + str(opt[0]))
        print("Rot: " + str(opt[1]))
        print("Row: " + str(opt[2]))
        print("Max Ht: " + str(feats["max_ht"]))
        print("Pits: " + str(feats["pits"]))
        print("All heights: " + str(feats["all_ht"]))
        print("Mean height: " + str(feats["mean_ht"]))
        print("Cleared: " + str(feats["cleared"]))
        print("Landing height: " + str(feats["landing_height"]))
        print("Eroded cells: " + str(feats["eroded_cells"]))
        print("Column trans: " + str(feats["col_trans"]))
        print("Row trans: " + str(feats["row_trans"]))
        print("All trans: " + str(feats["all_trans"]))
        print("Wells: " + str(feats["wells"]))
        print("Cumulative wells: " + str(feats["cuml_wells"]))
        print("Deep wells: " + str(feats["deep_wells"]))
        print("Max well: " + str(feats["max_well"]))
        print("Cumulative clears: " + str(feats["cuml_cleared"]))
        print("Cumulative eroded: " + str(feats["cuml_eroded"]))
        print("Pit depths: " + str(feats["pit_depth"]))
        print("Mean pit depths: " + str(feats["mean_pit_depth"]))
        print("Pit rows: " + str(feats["pit_rows"]))
        self.printspace(opt[3])
    
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
    
    def get_features(self, space):
        
        cleared_space = self.clear_rows(space)
        
        all_heights = self.get_heights(cleared_space)
        all_pits, pit_rows = self.get_all_pits(cleared_space)
        pit_depths = self.get_pit_depths(cleared_space)
        col_trans = self.get_col_transitions(cleared_space)
        row_trans = self.get_row_transitions(cleared_space)
        wells = self.get_wells(all_heights)
        
        features = {}
        
        features["mean_ht"] = sum(all_heights) / len(all_heights)
        features["max_ht"] = max(all_heights)
        features["min_ht"] = min(all_heights)
        features["all_ht"] = sum(all_heights)
        features["max_ht_diff"] = features["max_ht"] - features["mean_ht"]
        features["min_ht_diff"] = features["mean_ht"] - features["min_ht"]
        features["pits"] = sum(all_pits)
        features["cleared"] = self.filled_lines(space)
        features["landing_height"] = self.get_landing_height(space)
        features["eroded_cells"] = self.get_eroded_cells(space)
        features["col_trans"] = sum(col_trans)
        features["row_trans"] = sum(row_trans)
        features["all_trans"] = sum(col_trans) + sum(row_trans)
        features["wells"] = sum(wells)
        features["cuml_wells"] = self.accumulate(wells)
        features["deep_wells"] = sum([i for i in wells if i != 1])
        features["max_well"] = max(wells)
        features["cuml_cleared"] = self.accumulate([features["cleared"]])
        features["cuml_eroded"] = self.accumulate([features["eroded_cells"]])
        features["pit_depth"] = sum(pit_depths)
        features["mean_pit_depth"] = sum(pit_depths) / len(pit_depths)
        features["pit_rows"] = len(pit_rows)
        
        
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
    
    #transform the space to be column-wise, rather than rows
    def get_cols(self, space):
        out = []
        for i in range(0, len(space[0])):
            out.append(self.get_col(i, space))
        return out
    
    
    ### FEATURES
    
    #Heights
    def get_height(self, v):
        for i in range(0, len(v)):
            if v[i] != 0:
                return len(v) - i
        return 0
    ###
    
    
    def get_heights(self, space, columns = True):
        out = []
        if columns:
            space = self.get_cols(space)
        for i in space:
            out.append(self.get_height(i))
        return(out)
    ###
    
    #Pits
    
    #need to represent pits as a list of unique pits with a particular length;
    
    def get_pits(self, v):
        state = v[0]
        pits = 0
        rows = []
        row = 18
        for i in v[1:]:
            if i != 0:
                state = 1
            if i == 0 and state == 1:
                pits += 1
                rows.append(row)
            row -= 1
        return rows
    ###
    
    def get_all_pits(self, space):
        space = self.get_cols(space)
        out1 = []
        out2 = []
        for i in space:
            pits = self.get_pits(i)
            out1.append(len(pits))
            for j in pits:
                if j not in out2:
                    out2.append(j)
        return(out1, out2)
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
    
    def get_all_transitions(self, space, columns = False):
        out = []
        if columns:
            space = self.get_cols(space)
        for i in space:
            out.append(self.get_transitions(i))
        return(out)
    ###
    
    def get_col_transitions(self, space):
        return self.get_all_transitions(space, columns = True)
    
    def get_row_transitions(self, space):
        return self.get_all_transitions(space, columns = False)
    
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
                state = 0
                depth += curdepth
        return depth
            
        
    
    def get_pit_depths(self, space):
        space = self.get_cols(space)
        out = []
        for i in space:
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



    ###### CONTROLLERS
    
    def evaluate(self, vars, opts):
        
        #generate function values
        for i in opts:
            val = 0
            for j in vars:
                val += i[4][j[0]] * j[1]
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
    
    
    def prioritize(self, var, opts, func = min):
        crit = None
        
        for i in opts:
            if crit == None:
                crit = i[4][var]
            else:
                crit = func(crit, i[4][var])
        
        opts2 = []
        for i in opts:
            if i[4][var] == crit:
                opts2.append(i)
        
        return opts2
    
    
    #random controller. "If I Only Had A Brain"
    def choose_random(self, show = False):
        
        options = self.options
        
        choice = random.randint(0,len(options)-1)
        
        if show:
            self.printopt(options[choice])
        
        self.move(options[choice])
        
    
    #controller that minimizes the max-height. 
    def choose_min_ht(self, show = False):
        options = self.options
        
        min = 25
        choice = -1
        for i in range(0,len(options)):
            it = options[i][4]["max_ht"]
            if it < min:
                min = it
                choice = i
                
        if show:
            self.printopt(options[choice])
        
        self.move(options[choice])
    
    #Controller that prioritizes pits above all, then decides based on max height
    #
    # The problem with this kind of hierarchical controller is that it fails
        # to integrate the two values at the same time, maximizing one without
        # any concern whatsoever for the other. 
    def choose_min_ht_pits(self, show = False):
        options = self.options
        
        #discover minimum pits
        min_pits = 9999
        for i in range(0,len(options)):
            pits = options[i][4]["pits"]
            if pits < min_pits:
                min_pits = pits
        
        #reduce choices based on pits
        choices = []
        for i in options:
            if i[4]["pits"] == min_pits:
                choices.append(i)
        
        #decide based on min height
        min_peak = 9999
        choice = -1
        for i in range(0,len(choices)):
            it = choices[i][4]["max_ht"]
            if it < min_peak:
                min_peak = it
                choice = i
        
        if show:
            self.printopt(choices[choice])
        
        self.move(choices[choice])

    def choose_min_ht_pits_cleared(self, show = False):
        options = self.options
        
        options = self.prioritize("cleared",options,func = max)
        options = self.prioritize("pits",options,func = min)
        options = self.prioritize("all_ht",options, func = min)
        options = self.prioritize("max_ht",options, func = min)
        
        #choose leftmost?
        #choice = 0
        
        choice = random.randint(0, len(options)-1)
        
        if show:
            self.printopt(options[choice])
            
            
        self.move(options[choice])

    ###
    # BReaks on a non-illegal move. 
    """
    Traceback (most recent call last):
      File "simulator.py", line 808, in <module>
        main(sys.argv)
      File "simulator.py", line 771, in main
        sim.choose_Dellacherie(show = printout)
      File "simulator.py", line 674, in choose_Dellacherie
        options)
      File "simulator.py", line 542, in evaluate
        val += i[4][j[0]] * j[1]
    TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
    """
    ###
    def choose_Dellacherie(self):
        options = self.options
        
        options = self.evaluate([["landing_height",-1],
                            ["eroded_cells",1],
                            ["row_trans",-1],
                            ["col_trans",-1],
                            ["pits",-4],
                            ["cuml_wells",-1]], 
                            options)
        
        choice = random.randint(0, len(options)-1)
        
        if self.show_choice:
            self.printopt(options[choice])
            if self.choice_step > 0:
                time.sleep(self.choice_step)
            
        self.move(options[choice])
        
    def control(self):
        options = self.options
        options = self.evaluate(self.controller, options)
        choice = random.randint(0, len(options)-1)
        
        if self.show_choice:
            self.printopt(options[choice])
            if self.choice_step >0:
                time.sleep(self.choice_step)
        
        self.move(options[choice])
    
    
    def run(self, eps = -1, printstep = 500):
        max_eps = -1
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
                
            
            if self.show_scores or ep % printstep == 0:
              print("Episode: " + str(ep))
              self.printscores()
            ep += 1 
        
        print("\n\nGame Over\nFinal scores:")
        print("Episodes: " + str(ep))
        self.printscores()
        
        self.lines = 0
        self.l1 = 0
        self.l2 = 0
        self.l3 = 0
        self.l4 = 0
        self.score = 0
        self.level = 0
        
        return({"lines":self.lines,
                "l1":self.l1,
                "l2":self.l2,
                "l3":self.l3,
                "l4":self.l4,
                "score":self.score,
                "level":self.level})
    
def testboard():
    testboard = []
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
    return testboard
    
    
#Run main.
def main(argv):
    
    #default Dellacherie controller; 660,000 lines avg / game in literature!
    controller1 = [["landing_height",-1],
                ["eroded_cells",1],
                ["row_trans",-1],
                ["col_trans",-1],
                ["pits",-4],
                ["cuml_wells",-1]]
    
    
    #DTS controller, from Dellacherie + Thiery & Scherrer; 35,000,000 rows?!!?!
    controller2 = [["landing_height",-12.63],
                ["eroded_cells",6.60],
                ["row_trans",-9.22],
                ["col_trans",-19.77],
                ["pits",-13.08],
                ["cuml_wells",-10.49],
                ["pit_depth",-1.61],
                ["pit_rows",-24.04]]
    
    sim = TetrisSimulator(controller = controller2)
    
    sim.show_scores = True
    sim.show_options = False
    sim.show_choice = True
    
    sim.option_step = .05
    sim.choice_step = 0
    
    sim.run()
    


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


