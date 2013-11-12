#!/usr/bin/env python

import sys, random, os, time, copy
import argparse
import curses
import atexit

__version__ = '2013.11.2'

class TetrisSimulator(object):
    """A board object that supports assessment metrics and future simulations"""
    
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
    
    pieces = ["O","I","Z","S","T","L","J"]
        
    shapes =    {  
                "O":{
                    0: [[1,1],[1,1]]
                    },
                "I":{
                    0: [[2,2,2,2]],
                    1: [[2],[2],[2],[2]]
                    },
                "Z":{
                    0: [[3,3,0],[0,3,3]],
                    1: [[0,3],[3,3],[3,0]]
                    },
                "S":{
                    0: [[0,4,4],[4,4,0]],
                    1: [[4,0],[4,4],[0,4]]
                    },
                "T":{
                    0: [[5,5,5],[0,5,0]],
                    1: [[0,5],[5,5],[0,5]],
                    2: [[0,5,0],[5,5,5]],
                    3: [[5,0],[5,5],[5,0]]
                    },
                "L":{
                    0: [[6,6,6],[6,0,0]],
                    1: [[6,6],[0,6],[0,6]],
                    2: [[0,0,6],[6,6,6]],
                    3: [[6,0],[6,0],[6,6]]
                    },
                "J":{
                    0: [[7,7,7],[0,0,7]],
                    1: [[0,7],[0,7],[7,7]],
                    2: [[7,0,0],[7,7,7]],
                    3: [[7,7],[7,0],[7,0]]
                    }
                }
    
    
    def __init__(self, screen, args):
        """Generates object based on given board layout"""

        self.space = []
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        self.space.append([0,0,0,0,0,0,0,0,0,0])
        
        self.args = args
        
        self.controller = getattr(self, 'choose_%s' % self.args.controller)    
        
        self.screen = screen
        curses.curs_set(0)
        
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)#bg
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_YELLOW)#O
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_CYAN)#I
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_RED)#Z
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_GREEN)#S
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)#T
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE)#L
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLUE)#J

        
        self.statswin = curses.newwin(26, 22, 4, 0)
        self.boardwin = curses.newwin(22, 22, 4, 30)
        self.zoidwin = curses.newwin(4, 10, 4, 54)
        
        curses.use_default_colors()
        self.screen.addstr(0, 0, "Tetris Simulator", curses.A_BOLD)
        self.screen.addstr(1, 0, "Version: %s" % __version__)
        self.screen.addstr(2, 0, "Agent Controller: %s" % args.controller)
        self.screen.refresh()

        self.curr_z = random.choice(self.pieces)
        self.next_z = random.choice(self.pieces)
                
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
    
    def get_options(self, printout = False):
        self.options = self.possible_moves(printout = printout)
    
    
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
                if j != 0 and iy >= 0:
                    #print("stamping",iy,ix)
                    if self.space[iy][ix] != 0:
                        self.game_over = True
                    self.space[iy][ix] = j
                ix += 1
            ix = x
            iy += 1
        
        #if self.curr_zoid.overboard( self.board ):
        #     self.game_over()
        self.new_zoids()
        self.clear_lines()
    
    def sim_move(self, col, rot, row, zoid, space):
        x = col
        y = len(space) - row - 1
        ix = x
        iy = y
        for i in self.shapes[zoid][rot]:
            for j in i:
                if j != 0 and iy >= 0:
                    #print("stamping",iy,ix)
                    space[iy][ix] = -j
                ix += 1
            ix = x
            iy += 1
        
        return space
    
    def move(self, movelist):
        self.do_move(movelist[0],movelist[1],movelist[2])
    
    #pure random selection
    def new_zoids(self):
        self.curr_z = self.next_z
        self.next_z = random.choice(self.pieces)
    
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
        
    def possible_moves(self, zoid = None, space = None, printout = False):
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
                simboard = self.possible_board(c,r,row)
                features = self.get_features(simboard)
                opt = [c,r,row,simboard,features]
                options.append(opt)
                
        #if 1:
        #    self.printoptions(options)
        
        return options
    
    def possible_board(self, col, rot, row, zoid = None):
        if not zoid:
            zoid = self.curr_z
            
        newspace = copy.deepcopy(self.space)
        
        self.sim_move(col, rot, row, zoid, newspace)
        
        return newspace
        
    
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
    
    def printscorelabels(self):
        self.statswin.addstr(0,0,"Run:")
        self.statswin.addstr(1,0,"Level:")
        self.statswin.addstr(2,0,"Score:")
        self.statswin.addstr(3,0,"Lines:")
        self.statswin.addstr(4,0,"1:")
        self.statswin.addstr(5,0,"2:")
        self.statswin.addstr(6,0,"3:")
        self.statswin.addstr(7,0,"4:")
        self.statswin.refresh()
        
    def printscores(self):
        self.statswin.addstr(1,8,str(self.level))
        self.statswin.addstr(2,8,str(self.score))
        self.statswin.addstr(3,8,str(self.lines))
        self.statswin.addstr(4,4,str(self.l1))
        self.statswin.addstr(5,4,str(self.l2))
        self.statswin.addstr(6,4,str(self.l3))
        self.statswin.addstr(7,4,str(self.l4))
        self.statswin.refresh()
    
    def printoptions(self, opt = None):
        if not opt:
            opt = self.options
        for i in opt:
            self.printopt(i)
    
    def printopt(self, opt):
        feats = opt[4]
        self.statswin.addstr(9,0,"Col: " + str(opt[0]));self.screen.clrtoeol()
        self.statswin.addstr(10,0,"Rot: " + str(opt[1]));self.screen.clrtoeol()
        self.statswin.addstr(11,0,"Row: " + str(opt[2]));self.screen.clrtoeol()
        self.statswin.addstr(12,0,"Max Ht: " + str(feats["max_ht"]));self.screen.clrtoeol()
        self.statswin.addstr(13,0,"Pits: " + str(feats["pits"]));self.screen.clrtoeol()
        self.statswin.addstr(14,0,"All heights: " + str(feats["all_ht"]));self.screen.clrtoeol()
        self.statswin.addstr(15,0,"Cleared: " + str(feats["cleared"]));self.screen.clrtoeol()
        self.statswin.addstr(16,0,"Landing height: " + str(feats["landing_height"]));self.screen.clrtoeol()
        self.statswin.addstr(17,0,"Eroded cells: " + str(feats["eroded_cells"]));self.screen.clrtoeol()
        self.statswin.addstr(18,0,"Column trans: " + str(feats["col_trans"]));self.screen.clrtoeol()
        self.statswin.addstr(19,0,"Row trans: " + str(feats["row_trans"]));self.screen.clrtoeol()
        self.statswin.addstr(20,0,"Wells: " + str(feats["wells"]));self.screen.clrtoeol()
        self.statswin.addstr(21,0,"Cumulative wells: " + str(feats["cum_wells"]));self.screen.clrtoeol()
        self.statswin.refresh()
        #self.printspace(opt[3])
    
    def printzoid(self, zoid = None):
        if not zoid:
            zoid = self.curr_z
        self.zoidwin.clear()
        self.printspace(self.shapes[zoid][0], self.zoidwin)
    
    def printboard(self):
        self.printspace(self.space, self.boardwin)    
    
    def printspace(self, space, win):
        for i in range(0, len(space)):
            for j in range(0, len(space[i])):
                color = space[i][j]
                if color < 0:
                    win.chgat(i+1,j*2+1,2,0)
                else:
                    win.chgat(i+1,j*2+1,2,curses.color_pair(1+color))
        win.border()
        win.refresh()
        """
        win.addstr("+" + "-"*len(space[0])*2 + "+\n")
        for i in range(0, len(space)):
         out = "|"
         for j in space[i]:
            if j == 0:
             out = out + "    "
            elif j == 1:
             out = out + u"\u2BDD "
            elif j == 2:
             out = out + u"\u2b1c "
         win.addstr(out + "|" + str(len(space)-i-1) + "\n")
        win.addstr("+" + "-"*len(space[i])*2 + "+\n")
        numline = " "
        for j in range(0, len(space[0])):
            numline += str(j) + " "
        win.addstr(numline+"\n")
        """
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
        all_pits = self.get_all_pits(cleared_space)
        col_trans = self.get_col_transitions(cleared_space)
        row_trans = self.get_row_transitions(cleared_space)
        wells = self.get_wells(all_heights)
        
        features = {}
        
        features["max_ht"] = max(all_heights)
        features["pits"] = sum(all_pits)
        features["all_ht"] = sum(all_heights)
        features["cleared"] = self.filled_lines(space)
        features["landing_height"] = self.get_landing_height(space)
        features["eroded_cells"] = self.get_eroded_cells(space)
        features["col_trans"] = sum(col_trans)
        features["row_trans"] = sum(row_trans)
        features["wells"] = sum(wells)
        features["cum_wells"] = self.accumulate(wells)
        
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
        for i in v[1:]:
            if i != 0:
                state = 1
            elif i == 0 and state == 1:
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
    
    def get_landing_height(self, space):
        for i in range(0,len(space)):
            for c in space[len(space)-1-i]:
                if c < 0:
                    return(i)
        
    def get_eroded_cells(self, space):
        cells = 0
        for i in space:
            if self.line_filled(i):
                for c in i:
                    if c < 0:
                        cells += 1
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
                if False:
                    print(j, i[4][j[0]])
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
    
    def do_option(self, choice, show = False):
        if show: self.printopt(choice)
        self.move(choice)
    
    #random controller. "If I Only Had A Brain"
    def choose_random(self, show = False):
        self.do_option(random.choice(self.options))
        
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
                
        self.do_option(choice)
    
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
                
        self.do_option(choice)

    def choose_min_ht_pits_cleared(self, show = False):
        options = self.options
        options = self.prioritize("cleared",options,func = max)
        options = self.prioritize("pits",options,func = min)
        options = self.prioritize("all_ht",options, func = min)
        options = self.prioritize("max_ht",options, func = min)
        
        self.do_option(random.choice(options))
        
    #still needs to eliminate options that would end the game.
    def choose_handcoded(self, show = True):
        options = self.options
        options = self.evaluate([["landing_height",-1],
                            ["eroded_cells",1],
                            ["row_trans",-1],
                            ["col_trans",-1],
                            ["pits",-4],
                            ["cum_wells",-1]], options)
        
        choice = random.choice(options)
        
        if show:
            self.printopt(choice)
            self.printspace(choice[3],self.boardwin)
        
        self.do_option(choice)
        
    def debug(self, out, sleep=0):
        self.screen.addstr(0,0,out)
        self.screen.clrtoeol()
        self.screen.refresh()
        if sleep: time.sleep(sleep)
        
    def run(self, runs):
        #board.report()
        #sim.printboard()
        #options = sim.possible_moves()
        #sim.printoptions(options, timestep = 1)
    
        self.printscorelabels()
        
        i = 0
        
        while i != runs:
            if self.game_over:
                break

            self.statswin.addstr(0,6,"%d" % i)
            self.statswin.refresh()

            #print state
            self.printscores()
            #self.printzoid(zoid = sim.next_z)
            self.printzoid()
            #self.printboard()

            ##generate options and features
            self.get_options()

            self.controller()
            
            i += 1
            #time.sleep(.1)
            
        self.screen.addstr(30,0,"GAME OVER! Press 'q' to quit.", curses.A_BOLD+curses.A_BLINK)
        while True:
            c = self.screen.getch()
            if c == ord('q'):
                break
        #print("\n\nGame Over\nFinal scores:")
        #sim.printscores()

def main(screen, args):
    sim = TetrisSimulator(args=args, screen=screen)
    sim.run(args.runs)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v','--verbose', action='store_true', help="enable verbose output")
    parser.add_argument('-c','--controller', choices=['random','min_ht','min_ht_pits','min_ht_pits_cleared','handcoded'], help="the agent controller", default="handcoded")
    parser.add_argument('-r','--runs', type=int, default=-1, help="number of runs")
    args = parser.parse_args()

    curses.wrapper(main, args)