import os

## UNTESTED - Predict function - given a board and a zoid and a controller, returns best placement as determined by the controller 

def predict(space, zoid, controller):
        sim = TetrisSimulator(controller = controller)
        sim.space = sim.convert_space(space)
        sim.curr_z = zoid
        
        sim.get_options()
        return sim.control()
        
def getboard(space):
        """reads in a TetrisSimulator and 
           returns the board represented as a list of lists"""
        board = []
        for i in range(20):
    		row = []
    		for j in range(10):
    		    row.append(space[i,j])
    		board.append(row)
    	return board
    	
# >>>>> METHODS FOR FILE MANAGEMENT
    	
def setup_epfile(simulator):
        """ Sets up episode file """
        
        # Searches for directory. If not found, create it
        if not os.path.exists(simulator.logdir):
            os.makedirs(simulator.logdir)  
        
    	simulator.logname = os.path.join(simulator.logdir,simulator.filename)
    	
    	simulator.ep_header = ["episode_number","level","score","lines_cleared",
    	                    "zoid_sequence","curr_zoid","next_zoid","danger_mode",
                            "tetrises_game","tetrises_level","agree","board_rep",
                            "all_diffs","all_ht","all_trans","cd_1","cd_2","cd_3",
                            "cd_4","cd_5","cd_6","cd_7","cd_8","cd_9","cleared",
                            "col_trans","column_9","cuml_cleared","cuml_eroded",
                            "cuml_wells","d_all_ht","d_max_ht","d_mean_ht","d_pits",
                            "deep_wells","eroded_cells","full_cells","jaggedness",
                            "landing_height","lumped_pits","matches","max_diffs",
                            "max_ht","max_ht_diff","max_well","nine_filled",
                            "pattern_div","pit_depth","pit_rows","pits","row_trans",
                            "tetris","tetris_progress","weighted_cells","wells","\n"]
                    
        # Finalizes file path and writes episode header to file        
    	simulator.epfile_path = simulator.logname + ".tsv"
    	simulator.epfile = open(simulator.epfile_path + ".incomplete","w")
    	write_episode(simulator,simulator.ep_header)
    	
def write_episode(simulator,specified=None,ep_num=None,board=None):
    """ Writes episode to file """
    # If what is to be written is specified, write that instead.
    # Otherwise, write the episode
    if specified:
        data = specified 
    else:
        # Gather data
        episode_number = ep_num
        lines_cleared = 0   
        zoid_sequence = []
        danger_mode = False 
        tetrises_game = 0    
        tetrises_level = 0   
        agree = None
        board_rep = getboard(board)
        name_curr_z = simulator.label_zoid(simulator.curr_z)
        name_next_z = simulator.label_zoid(simulator.next_z)    
            
        features = simulator.get_features(simulator.space)
        move_score = features['move_score']
        d_max_ht = features['d_max_ht']
        d_pits = features['d_pits']
        row_trans = features['row_trans']
        deep_wells = features['deep_wells']
        cuml_wells = features['cuml_wells']
        min_ht_diff = features['min_ht_diff']
        mean_ht = features['mean_ht']
        max_ht_diff = features['max_ht_diff']
        cd_4 = features['cd_4']
        cd_5 = features['cd_5']
        cd_6 = features['cd_6']
        cd_7 = features['cd_7']
        cd_1 = features['cd_1']
        cd_2 = features['cd_2']
        lumped_pits = features['lumped_pits']
        min_ht = features['min_ht']
        jaggedness = features['jaggedness']
        cuml_eroded = features['cuml_eroded']
        pit_rows = features['pit_rows']
        d_mean_ht = features['d_mean_ht']
        max_ht = features['max_ht']
        eroded_cells = features['eroded_cells']
        all_trans = features['all_trans']
        pattern_div = features['pattern_div']
        d_all_ht = features['d_all_ht']
        all_ht = features['all_ht']
        matches = features['matches']
        landing_height = features['landing_height']
        wells = features['wells']
        column_9 = features['column_9']
        cuml_cleared = features['cuml_cleared']
        all_diffs = features['all_diffs']
        col_trans = features['col_trans']
        tetris = features['tetris']
        cleared = features['cleared']
        tetris_progress = features['tetris_progress']
        full_cells = features['full_cells']
        cd_3 = features['cd_3']
        weighted_cells = features['weighted_cells']
        pits = features['pits']
        mean_pit_depth = features['mean_pit_depth']
        nine_filled = features['nine_filled']
        max_well = features['max_well']
        cd_8 = features['cd_8']
        pit_depth = features['pit_depth']
        max_diffs = features['max_diffs']
        cd_9 = features['cd_9']
            
        # Data added to list to be displayed on file
    	data = [episode_number,simulator.level,simulator.score,lines_cleared, 
    	              zoid_sequence,name_curr_z,name_next_z,
    	              danger_mode,tetrises_game,tetrises_level,
    	              agree,board_rep,all_diffs,all_ht,all_trans,cd_1,cd_2,
    	              cd_3,cd_4,cd_5,cd_6,cd_7,cd_8,cd_9,cleared,
    	              col_trans,column_9,cuml_cleared,cuml_eroded,
    	              cuml_wells,d_all_ht,d_max_ht,d_mean_ht,d_pits,
                      deep_wells,eroded_cells,full_cells,jaggedness,
                      landing_height,lumped_pits,matches,max_diffs,
                      max_ht,max_ht_diff,max_well,nine_filled,
                      pattern_div,pit_depth,pit_rows,pits,row_trans,
                      tetris,tetris_progress,weighted_cells,wells,"\n"]
        
    # Checks whether data is string or not
    # (data needs to be a list for this to be added)
    if isinstance(data,str):
    	data_list = [data]
    else:
    	data_list = data
    	    
    # Adds tab character and newline to data_list 
    # before writing it to the file
    out = "\t".join(map(str,data_list))+"\n"
    simulator.epfile.write(out)
    	
def close_epfile(simulator):
    """ Episode file closure """
    simulator.epfile.close()
    os.rename(simulator.epfile_path + ".incomplete", simulator.epfile_path)
    
# <<<<< METHODS FOR FILE MANAGEMENT
    
