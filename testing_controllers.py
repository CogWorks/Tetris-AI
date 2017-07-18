from simulator import TetrisSimulator
import random, numpy, argparse, os, time
from time import gmtime, strftime

##Functions
 

#These two lists define the categories for the data this method produces.
header = ["session","episodes","initial_value","session_seed",
            "game_seed","name","type","game_num","repetition"]
outputs = ["lines","l1","l2","l3","l4","score","level","eps"]

def write_header(file, features):
    
    norms = []
    for i in features:
        norms.append(i + "_norm")
    #The file writes the header and output lists joined by tabs for parsing purposes, and moves to a new line
    outheader = header + features + norms + outputs
    file.write("\t".join(outheader) + "\n")
    
def write_controller(file, session_vars, name, features, controller, game_seed = "NIL", outs = False, type = "", gen = 0, num = 0, rep = 0):
    outlist = []
    outlist = outlist + session_vars
    outlist.append(str(game_seed))
    outlist.append(name)
    outlist.append(str(gen))
    outlist.append(type)
    outlist.append(str(num))
    outlist.append(str(rep))
    
    featlist = []
    #get features
    for f in features:
        featlist.append(controller[f])
    
    #add raw values
    outlist = outlist + map(str,featlist)
    
    #but also do those values normalized
    #avg_feat = sum(featlist) / len(featlist)
    
    
    max_feat = max(map(abs,featlist))
    if max_feat == 0:
        max_feat = 1
    
    for f in featlist:
        #outlist.append(str( (f - avg_feat) / max_feat ))
        outlist.append(str( f / max_feat ))
    
    #do the outputs if present. Searches the dictionary of outputs provided and writes the value for each one.
    for o in outputs:
        if outs:
            outlist.append(str(outs[o]))
        else:
            outlist.append("")
    file.write("\t".join(outlist) + "\n")
    

###Script
if __name__ == '__main__':
    
    datestring = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    
    
    parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
    


    parser.add_argument( '-e', '--episodes',
                        action = "store", dest = "episodes",
                        type = int, default = -1,
                        help = "Set maximum number of episodes for all controllers to play.")
    
    
    parser.add_argument( '-i', '--initial',
                        action = "store", dest = "initial_val",
                        type = float, default = 0,
                        help = "Set initial value for the \"start\" controller.")
    
    parser.add_argument( '-tg', '--test_games',
                        action = "store", dest = "test_games",
                        type = int, default = 10,
                        help = "Set number of unique games to test.")
                        
    parser.add_argument( '-tr', '--test_reps',
                        action = "store", dest = "test_reps",
                        type = int, default = 3,
                        help = "Set number of times to run tests on each unique test game.")
    
    
    parser.add_argument( '-r', '--report_every',
                        action = "store", dest = "report_every",
                        type = int, default = 500,
                        help = "How often, in episodes, to report the current scores. -1 disables")
                        
    parser.add_argument( '-v', '--visuals',
                        action = "store_true", dest = "show_visuals", default = False,
                        help = "Show visualizations.")
                        
    parser.add_argument( '-vs', '--visual_step',
                        action = "store", dest = "visual_step", type=float, default = 0,
                        help = "Timestep between choices in seconds.")
                        
    parser.add_argument( '-o', '--output',
                        action = "store", dest = "output_file",
                        type = str, default = datestring,
                        help = "Output file. Extension will be .tsv")
    
    parser.add_argument( '-nr', '--no_results',
                        action = "store_true", dest = "no_results", default = False,
                        help = "Output file. Extension will be .tsv")
                        
    parser.add_argument( '-sd', '--seed',
                        action = "store", dest = "random_seed",
                        type = float, default = time.time(),
                        help = "Set the random number seed for this session. Defaults to current system time time 10 trillion.")
    

    parser.add_argument( '-f', '--features',
                        action = "store", dest = "features",
                        type = str, nargs = '+',
                        default = ["landing_height","eroded_cells","row_trans","col_trans","pits","cuml_wells"],
                        help = """List of all features to be used in the model, separated by spaces. Taken from simulator.py. Select from:\n
                                mean_ht,  max_ht,  min_ht,  all_ht,  \n
                                max_ht_diff,  min_ht_diff,  pits,  cleared,  \n
                                landing_height,  eroded_cells,  col_trans,  row_trans,  \n
                                all_trans,  wells,  cuml_wells,  deep_wells,  \n
                                max_well,  cuml_cleared,  cuml_eroded,  pit_depth,  \n
                                mean_pit_depth,  pit_rows,  column_9,  tetris.\n""")
    


    parser.add_argument( '-gcw', '--given_controller_weights',
                        action = "store", dest = "given_controller_weights",
                        type = float, nargs = '+',
                        default = [0.0],
                        help = "Provide a default list of weights. Must match length of features vector.")


    #harvest argparse
    args = parser.parse_args()
    #For the regularization project, the file name has been generalized to include regularization parameters for reference
    file_seed = args.output_file
    
    #the path is searched for a directory called runs. If it does not exist, it is created. All runs are stored here.
    if not os.path.exists("runs"):
        os.makedirs("runs")
    outfile = open("runs/" + '-'.join(file_seed) + ".incomplete.tsv", "w")
        
    episodes = args.episodes
    report_every = args.report_every
    given_controller_weights = args.given_controller_weights
    features = args.features
    test_games = args.test_games
    test_reps = args.test_reps
    initial_val = args.initial_val
    show_result = not args.no_results
    
    random_seed = args.random_seed
    rng = random.Random()
    rng.seed(random_seed)
    
    if args.show_visuals:
        show_choice = True
    else:
        show_choice = False
    v_step = args.visual_step
    
    
    #log headers
    
    session_variables = [args.output_file, str(episodes), str(initial_val), str(random_seed)]
    
    write_header(outfile, features)
    
    start_controller = {}

    #Generates the length of the start controller weights, variances and feature list, these must match for start_controller to be used
    given_controller_weight_length = len(given_controller_weights)
    features_length = len(features)

    #If the lengths match, the start controller uses the weights from given_controller. If not, the initial value is given for all
    #weights. Variance is set the same way regardless (for now).
    if given_controller_weight_length == features_length:
        
	start_controller = dict(zip(features, given_controller_weights))


    else:

        for f in features:
    
            start_controller[f] = initial_val
        
    
    write_controller(outfile, session_variables, "G" + str(0), features, start_controller, 
                        type = "base", gen = 0)



#For data comparison purposes, the scores of the result controller on standardized games are collected.
    test_results = []
    for g in range(0,test_games):
        test_seed = 10001 + g
        for r in range(0, test_reps):
           test_name = "G" + str(0) + "_T" + str(g+1) + "_R" + str(r+1)
           test_sim = TetrisSimulator(controller = start_controller, show_result = show_result, show_choice = show_choice, choice_step = v_step, name = test_name, seed = test_seed)
           test_res = test_sim.run(0, max_eps = episodes, printstep = report_every)

           test_results.append(test_res)
           write_controller(outfile, session_variables, test_name, features, start_controller, outs = test_res, 
                            game_seed = test_seed, type = "test", gen = 0, num = g+1, rep = r+1)
            
        test_avg = {}
        
        for o in outputs:
            val = 0.0
            for r in test_results:
                val += r[o]
            test_avg[o] = val / float(len(test_results))
        
        
        #output resultant controller and its scores
        write_controller(outfile, session_variables, "G" + str(0), features, start_controller, outs = test_avg, type = "result", gen = 0)

        
    outfile.close()
    os.rename("runs/" + '-'.join(file_seed) + ".incomplete.tsv", "runs/" + '-'.join(file_seed)+".tsv")
