#To-dos

#File-reading
    #be able to read generated files to "pick up where we left off"

#Optional: Need 2-piece look-ahead

#Need to add some ability to play overhangs.

#Need to have some rudimentary constraints added in. (may leave for multitetris proper)

#Need to report how long a controller lived (particularly if it didn't survive the full episode number specified)






## Ideas from Kevin.

# FOCUS on the WORST player, and TERMINATE CALCULATION when they're DEAD. Only the top ten survive. 

# Multithreading within a single CERL run; execute 16 times faster!
# parallel-exec ; takes 100 command lines and makes sure N of them are running on N threads at any time.
    #link to page on CogWorks site inside email. 




from simulator import TetrisSimulator
import random, numpy, argparse, os, time
from time import gmtime, strftime

###Functions
def generate_controller(start, tols, rng):
    new_controller = {}
    
    #for each feature
    for k in sorted(start.keys()):
        #generate a new value around the mean
        val = rng.gauss(start[k],tols[k])
        
        #and add this pair to the new controller
        new_controller[k]= val
        
    return new_controller

#Takes a list of controllers (lists) with the same number of features
#outputs a new average controller, and the stdev for each value
def merge_controllers(controllers, noise):
    new_controller = {}
    new_tolerances = {}
    #for each feature (of all controllers)
    for k in sorted(controllers[0].keys()):
        vals = []
        for c in controllers:
            vals.append(c[k])
        mean = float(sum(vals)) / float(len(vals))
        tol = numpy.std(vals)
        
        new_controller[k] = mean
        new_tolerances[k] = tol + noise
    
    return new_controller, new_tolerances
        


header = ["session","optimize","depth","controllers","survivors","episodes",
            "noise","initial_value","variance","session_seed",
            "game_seed","name","generation","type","game_num","repetition"]
outputs = ["lines","l1","l2","l3","l4","score","level","eps"]

def write_header(file, features):
    vars = []
    for i in features:
        vars.append(i + "_var")
    
    norms = []
    for i in features:
        norms.append(i + "_norm")
    
    outheader = header + features + norms + vars + outputs
    file.write("\t".join(outheader) + "\n")
    
def write_controller(file, session_vars, name, features, controller, game_seed = "NIL", vars = False, outs = False, type = "", gen = 0, num = 0, rep = 0):
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
    
    #do the vars if present
    for f in features:
        if vars:
            outlist.append(str(vars[f]))
        else:
            outlist.append("")
    
    #do the outputs if present
    for o in outputs:
        if outs:
            outlist.append(str(outs[o]))
        else:
            outlist.append("")
    file.write("\t".join(outlist) + "\n")
    

def resume(file):
    controller = {}
    
    return controller

###Script




if __name__ == '__main__':
    
    datestring = strftime("%Y-%m-%d_%H-%M-%S", gmtime())
    
    #defaults from Thierry and Scherrer paper:
        #original controller centered on 0, 
        #original variance 100, (they used variance, we use Standard Deviation; just SQUARE stdev to get this)
        #100 controllers, 
        #10 survivors, 
        #all new variances were varied by the constant 4
    
    parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )
    
    parser.add_argument( '-d', '--depth',
                        action = "store", dest = "depth",
                        type = int, default = 80,
                        help = "Set how many cross-entropy generations to traverse.")
    
    parser.add_argument( '-c', '--controllers',
                        action = "store", dest = "controllers",
                        type = int, default = 100,
                        help = "Set the number of controllers to spawn in each generation.")
    
    parser.add_argument( '-s', '--survivors',
                        action = "store", dest = "survivors",
                        type = int, default = 10,
                        help = "Set how many of the best controllers survive each generation.")
    
    parser.add_argument( '-e', '--episodes',
                        action = "store", dest = "episodes",
                        type = int, default = -1,
                        help = "Set maximum number of episodes for all controllers to play.")
    
    parser.add_argument( '-n', '--noise',
                        action = "store", dest = "noise",
                        type = float, default = 4,
                        help = "Set constant noise value. Set to 0 for non-noisy variance iterations.")
    
    parser.add_argument( '-dn', '--dim_noise',
                        action = "store", dest = "dim_noise",
                        type = float, default = 1.0,
                        help = "Set whether to diminish noise, and by what factor. Defaults to 1.0, no diminishing.")
    
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
    
    parser.add_argument( '-var', '--variance',
                        action = "store", dest = "variance",
                        type = float, default = 100,
                        help = "Set initial variance for cross entropy generation.")
    
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
    
    parser.add_argument( '-op', '--optimize',
                        action = "store", dest = "optimize",
                        type = str, default = "lines",
                        help = "Select what criterion to optimize via cross-entropy: lines, score, level, l1, l2, l3, l4. Defaults to 'lines'.")
    
    parser.add_argument( '-res', '--resume',
                        action = "store", dest = "resume_file",
                        type = str, default = None,
                        help = "Specify an incomplete session log to reconstruct and resume.")
    
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
    
    #harvest argparse
    args = parser.parse_args()
    
    if not os.path.exists("runs"):
        os.makedirs("runs")
    outfile = open("runs/" + args.output_file + ".incomplete.tsv", "w")
        
    depth = args.depth
    controllers = args.controllers
    survivors = args.survivors
    episodes = args.episodes
    noise = args.noise
    dim_noise = args.dim_noise
    report_every = args.report_every
    initial_val = args.initial_val
    variance = args.variance
    features = args.features
    optimize = args.optimize
    test_games = args.test_games
    test_reps = args.test_reps
    show_result = not args.no_results
    resume_file = args.resume_file
    
    random_seed = args.random_seed
    rng = random.Random()
    rng.seed(random_seed)
    
    if args.show_visuals:
        show_choice = True
    else:
        show_choice = False
    v_step = args.visual_step
    
    
    #log headers
    
    session_variables = [args.output_file, optimize, str(depth), str(controllers), str(survivors), str(episodes),
                        str(noise), str(initial_val), str(variance), str(random_seed)]
    
    write_header(outfile, features)
    
    start_controller = {}
    tolerances = {}
    for f in features:
        start_controller[f] = initial_val
        tolerances[f] = variance
        
    
    write_controller(outfile, session_variables, "G" + str(0), features, start_controller, 
                        vars = tolerances, type = "base", gen = 0)
    
    for x in range (0, depth):
        
        #session_vars, name, features, controller, vars = False, outs = False
        
        
        results = []
        
        for a in range(0, controllers):
            random_controller = generate_controller(start_controller, tolerances, rng = rng)
            controller_name = "G" + str(x + 1) + "_" + str(a+1)
            
            game_seed = rng.randint(0,100000)
            
            sim = TetrisSimulator(controller = random_controller, show_choice = show_choice, show_result = show_result, choice_step = v_step, name = controller_name, seed = game_seed)
            sim_result = sim.run(eps = episodes, printstep = report_every)
            
            #session_vars, name, features, controller, vars = False, outs = False
            write_controller(outfile, session_variables, controller_name, features, random_controller, 
                            outs = sim_result, game_seed = game_seed, type = "search", gen = x + 1, num = a+1, rep = 1)
            
            results.append([random_controller, sim_result])
            
            
        sorted_results = sorted(results, key=lambda k: k[1][optimize])
        
        #for d in sorted_results:
        #    print d[1]["lines"]
    
        top_results = sorted_results[-survivors:]
    
        top_controllers = []
            
        for f in top_results:
            top_controllers.append(f[0])
        
        start_controller, tolerances = merge_controllers(top_controllers, noise)
        
        
        test_results = []
        for g in range(0,test_games):
            test_seed = 10001 + g
            for r in range(0, test_reps):
                test_name = "G" + str(x + 1) + "_T" + str(g+1) + "_R" + str(r+1)
                test_sim = TetrisSimulator(controller = start_controller, show_result = show_result, show_choice = show_choice, choice_step = v_step, name = test_name, seed = test_seed)
                test_res = test_sim.run(eps = episodes, printstep = report_every)
                
                test_results.append(test_res)
                write_controller(outfile, session_variables, test_name, features, start_controller, outs = test_res, 
                            game_seed = test_seed, type = "test", gen = x + 1, num = g+1, rep = r+1)
            
        test_avg = {}
        
        for o in outputs:
            val = 0.0
            for r in test_results:
                val += r[o]
            test_avg[o] = val / float(len(test_results))
        
        
        #output resultant controller and its scores
        write_controller(outfile, session_variables, "G" + str(x+1), features, start_controller, 
                        vars = tolerances, outs = test_avg, type = "result", gen = x + 1)
        
        noise = noise * dim_noise
        
    outfile.close()
    os.rename("runs/" + args.output_file + ".incomplete.tsv", "runs/" + args.output_file+".tsv")
    