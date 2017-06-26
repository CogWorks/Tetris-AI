# Cross Entropy Reinforcement Learning Script

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
def generate_mask(features, dropout_prob):
	mask = {}
	
	for f in features:
		drop = numpy.random.uniform()

		if drop > dropout_prob:
			mask[f] = 1 #keep this feature
		else:
			mask[f] = 0 #discard this feature

	return mask
				

def generate_controller(start, tols, mask, rng):
    new_controller = {}
    
    #for each feature
    for k in sorted(start.keys()):
        #generate a new value around
        	val = rng.gauss(start[k],numpy.sqrt(tols[k]))

	#add to the controller if the mask allows it
        	new_controller[k]= val*mask[k]
        
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
        #the idea here is to reduce the noise added to weights with value 0, to give them a chance to stay low
        counterbalance = 1.0-numpy.exp(-0.01-numpy.absolute(mean))
        new_tolerances[k] = tol*tol + noise*counterbalance

    
    return new_controller, new_tolerances

#The following methods define the norm in use for regularization

def zero_norm_of_features(controller, tol):
	norm = 0
	for k in sorted(controller.keys()):
		if numpy.absolute(controller[k])>tol:
			norm+=1
	return norm

def one_norm_of_features(controller):
	norm = 0
	for k in sorted(controller.keys()):
		norm+=numpy.absolute(controller[k])
	return norm

def two_norm_of_features(controller):
	norm = 0
	for k in sorted(controller.keys()):
		m=controller[k] #so that the weight only needs to be retrieved once, may be significant for long runs
		norm+=m*m
	return norm

def norm(controller, norm_type):
	if norm_type==0:
		return zero_norm_of_features(controller,0.01)
	elif norm_type==1:
		return one_norm_of_features(controller)
	elif norm_type==2:
		return two_norm_of_features(controller)
	else:
		raise ValueError('Other norms are not supported at this time.')

#This method is also for regularization. It computes the value of the parameter that measures how much regularization to use.
#In typical machine learning applications, this parameter is often denoted by a lambda.
#This method relies on access to the generation number in the CERL training, and so it must be placed here for minimal disruption.
       
def updatePenalty(update_type, initial_value, update_parameter, generation):
	penalty = initial_value
	if update_type != 'none':
		if update_type == 'linear':
			penalty += generation*update_parameter
		elif update_type == 'exponential':
			penalty *= numpy.exp(generation*update_parameter)
		elif (update_type == 'step' and generation <= update_parameter):
			penalty = 0
	return penalty


#These two lists define the categories for the data this method produces.
header = ["session","optimize","depth","controllers","survivors","episodes",
            "noise","initial_value","variance","session_seed",
            "game_seed","name","generation","type","game_num","repetition"]
outputs = ["lines","l1","l2","l3","l4","score","level","eps","norm_of_weights"]

def write_header(file, features):
    vars = []
    for i in features:
        vars.append(i + "_var")
    
    norms = []
    for i in features:
        norms.append(i + "_norm")
    #The file writes the header and output lists joined by tabs for parsing purposes, and moves to a new line
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
    
    #do the vars if present. Searches the dictionary of features provided and writes the value for each one.
    for f in features:
        if vars:
            outlist.append(str(vars[f]))
        else:
            outlist.append("")
    
    #do the outputs if present. Searches the dictionary of outputs provided and writes the value for each one.
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
    
    parser.add_argument('-ip','--initial_penalty',
			action = "store", dest = "initial_penalty",
			type = float, default = 0,
			help = "The initial strength of the regularization coefficient")

    parser.add_argument('-rt','--regularization_type',
			action = "store", dest = "regularization_type",
			type = str, default = 'none',
			help = "How regularization strength will be updated. Choices are linear, exponential, step, and none")

    parser.add_argument('-rtp','--regularization_type_parameter', action = "store",
			dest = "regularization_type_parameter",
			type = float, default = 0,
			help = "Extra parameter required. Generation number for step, otherwise a number multiplied by generation 				and put through some function to determine penalty strength.")

    parser.add_argument('-no','--norm',action = "store",
			dest = "norm_type", type = int, default = 0,
			help = "The type of penalty norm to use. Choices are 0, length of feature list, 1 absolute value of 				features, 2 sum of squared features.")

    parser.add_argument( '-dr', '--drop',
                        action = "store", dest = "dropout_prob",
                        type = float, default = 0,
                        help = "Set the probability a weight is set to 0 when a new controller is generated.")

    parser.add_argument( '-gcw', '--given_controller_weights',
                        action = "store", dest = "given_controller_weights",
                        type = float, nargs = '+',
                        default = [0.0],
                        help = "Provide a default list of weights. Must match length of features vector.")

    parser.add_argument( '-gcv', '--given_controller_variance',
                        action = "store", dest = "given_controller_variances",
                        type = float, nargs = '+',
                        default = [0.0],
                        help = "Provide a default list of variances. Must match length of features vector.")
    
    #harvest argparse
    args = parser.parse_args()
    #For the regularization project, the file name has been generalized to include regularization parameters for reference
    file_seed = args.output_file + args.regularization_type + str(args.regularization_type_parameter) + str(args.initial_penalty)+ str(args.norm_type)
    
    #the path is searched for a directory called runs. If it does not exist, it is created. All runs are stored here.
    if not os.path.exists("runs"):
        os.makedirs("runs")
    outfile = open("runs/" + '-'.join(file_seed) + ".incomplete.tsv", "w")
        
    depth = args.depth
    controllers = args.controllers
    survivors = args.survivors
    episodes = args.episodes
    noise = args.noise
    dim_noise = args.dim_noise
    initial_penalty = args.initial_penalty
    regularization_type = args.regularization_type
    regularization_type_parameter = args.regularization_type_parameter
    norm_type = args.norm_type
    dropout_prob = args.dropout_prob
    report_every = args.report_every
    initial_val = args.initial_val
    given_controller_weights = args.given_controller_weights
    given_controller_variances = args.given_controller_variances
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

    #Generates the length of the start controller weights, variances and feature list, these must match for start_controller to be used
    given_controller_weight_length = len(given_controller_weights)
    given_controller_variance_length = len(given_controller_variances)
    features_length = len(features)

    #If the lengths match, the start controller uses the weights from given_controller. If not, the initial value is given for all
    #weights. Variance is set the same way regardless (for now).
    if given_controller_weight_length == features_length:
        
	start_controller = dict(zip(features, given_controller_weights))

        if given_controller_variance_length == features_length:

            tolerances = dict(zip(features, given_controller_variances))

        else:

            for f in features:

                tolerances[f] = variance

    else:

        for f in features:
    
            start_controller[f] = initial_val
            tolerances[f] = variance
        
    
    write_controller(outfile, session_variables, "G" + str(0), features, start_controller, 
                        vars = tolerances, type = "base", gen = 0)

    #generates a 'mask' that allows all the features
    list_of_ones = [1] * features_length
    allow_all_features = dict(zip(features, list_of_ones))


    
    #This is the main loop. In each iteration, a new generation of controllers is tested.
    for x in range (0, depth):
        
        #session_vars, name, features, controller, vars = False, outs = False
        
        
        results = []

        #A mask is generated. This selects the features that half the population will ignore.
        mask = generate_mask(features, dropout_prob)
        
        for a in range(0, controllers):

   
            #Decides if this controller is in the unmasked or masked group, and generates it accordingly
            if a < (controllers/2):
                random_controller = generate_controller(start_controller, tolerances, mask, rng = rng)
            else:
                random_controller = generate_controller(start_controller, tolerances, allow_all_features, rng = rng) 

            controller_name = "G" + str(x + 1) + "_" + str(a+1)
            norm_of_weights = norm(random_controller, norm_type)
	    penalty_strength = updatePenalty(regularization_type,initial_penalty,regularization_type_parameter, x)
            penalty = norm_of_weights*penalty_strength
            game_seed = rng.randint(0,100000)
            
            #A simulation object is created using simulator.py methods, and a game is played
            sim = TetrisSimulator(controller = random_controller, show_choice = show_choice, show_result = show_result, choice_step = v_step, name = controller_name, seed = game_seed)
            sim_result = sim.run(penalty, max_eps = episodes, printstep = report_every)
	    sim_result['norm_of_weights'] = norm_of_weights #to allow the norm of the weights of the controller to be seen as output 
            
            #session_vars, name, features, controller, vars = False, outs = False
            write_controller(outfile, session_variables, controller_name, features, random_controller, 
                            outs = sim_result, game_seed = game_seed, type = "search", gen = x + 1, num = a+1, rep = 1)
            
            results.append([random_controller, sim_result])
            
        #the controllers are sorted. The function takes the controller argument and looks for the appropriate objective.    
        sorted_results = sorted(results, key=lambda k: k[1][optimize])
        
        #for d in sorted_results:
        #    print d[1]["lines"]

	#The best scores are taken by looping from the end of the sorted_results list    
        top_results = sorted_results[-survivors:]
    
        top_controllers = []
            
        for f in top_results:
            top_controllers.append(f[0])
        
	#The survivors are merged to generate the base controller for the next generation.
        start_controller, tolerances = merge_controllers(top_controllers, noise)
	norm_of_weights = norm(start_controller, norm_type)
        
        #For data comparison purposes, the scores of the result controller on standardized games are collected.
        test_results = []
        for g in range(0,test_games):
            test_seed = 10001 + g
            for r in range(0, test_reps):
                test_name = "G" + str(x + 1) + "_T" + str(g+1) + "_R" + str(r+1)
                test_sim = TetrisSimulator(controller = start_controller, show_result = show_result, show_choice = show_choice, choice_step = v_step, name = test_name, seed = test_seed)
                test_res = test_sim.run(0, max_eps = episodes, printstep = report_every)
                test_res['norm_of_weights'] = norm_of_weights #to allow the norm of the weights of the controller to be seen as output, but this doesn't say what type of norm being used. Check file name for that.

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
        
	#The random noise added to prevent early convergence is decreased.
        noise = noise * dim_noise
        
    outfile.close()
    os.rename("runs/" + '-'.join(file_seed) + ".incomplete.tsv", "runs/" + '-'.join(file_seed)+".tsv")
    
