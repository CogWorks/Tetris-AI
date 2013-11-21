from simulator import TetrisSimulator
import random, numpy


###Functions
def generate_controller(start, tols):
    new_controller = []
    
    #for each feature
    for i in range(0,len(start)):
        #generate a new value around the mean
        val = random.gauss(start[i][1],tols[i])
        
        #and add this pair to the new controller
        new_controller.append([start[i][0],val])
        
    return new_controller

#Takes a list of controllers (lists) with the same number of features
#outputs a new average controller, and the stdev for each value
def merge_controllers(controllers):
    new_controller = []
    tolerances = []
    #for each feature (of all controllers)
    for i in range(0,len(controllers[0])):
        feature = controllers[0][i][0]
        vals = []
        for j in controllers:
            vals.append(j[i][1])
        mean = float(sum(vals)) / float(len(vals))
        tol = numpy.std(vals)
        
        new_controller.append([feature,mean])
        tolerances.append(tol)
    
    return new_controller, tolerances
        


###Script

#staring from Dellacherie model
target_controller = [["landing_height",-1],
                ["eroded_cells",1],
                ["row_trans",-1],
                ["col_trans",-1],
                ["pits",-4],
                ["cuml_wells",-1]]
                
start_controller = [["landing_height",0],
                ["eroded_cells",0],
                ["row_trans",0],
                ["col_trans",0],
                ["pits",0],
                ["cuml_wells",0]]
                
tolerances = [10,10,10,10,10,10]


for a in range(0,10):
	random_controller = generate_controller(start_controller, tolerances)
	print(random_controller)
	working_controllers.append(random_controller)

for b in range (0, len(working_controllers))
	test = TetrisSimulator(controller = working_controllers[i])
	test_result = test.run()
	results.append(test_result)
	
#USAGE: generate_controller(start, tols)
random_controller = generate_controller(start_controller, tolerances)
print(random_controller)
				


#USAGE: merge_controllers(controllers)
c1 = [["landing_height",0],
        ["eroded_cells",0],
        ["row_trans",0],
        ["col_trans",0],
        ["pits",0],
        ["cuml_wells",0]]

c2 = [["landing_height",1],
        ["eroded_cells",1],
        ["row_trans",1],
        ["col_trans",1],
        ["pits",1],
        ["cuml_wells",1]]

c3 = [["landing_height",2],
        ["eroded_cells",2],
        ["row_trans",2],
        ["col_trans",2],
        ["pits",2],
        ["cuml_wells",2]]

c4 = [["landing_height",-1],
        ["eroded_cells",-1],
        ["row_trans",-1],
        ["col_trans",-1],
        ["pits",-1],
        ["cuml_wells",-1]]

print(merge_controllers([c1,c2,c3,c4]))





sim_test = TetrisSimulator(controller = random_controller, show_choice = True, choice_step = 0)

result = sim_test.run()
print result