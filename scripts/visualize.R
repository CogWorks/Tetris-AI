
require(ggplot2)

#load the file
Tetriser <- read.delim("~/Lab/Projects/Tetris-AI/runs/Tetriser2.tsv")


#extract the generation information from the name field
#Tetriser$generation = as.numeric(sub("G","",sub("_.*","",as.character(Tetriser$name))))


ggplot(data=Tetriser[Tetriser$type=="result",],aes(x=generation, y=l4)) +
  geom_point() + 
  geom_line()

ggplot(data=Tetriser[Tetriser$type=="result",],aes(x=generation, y=eps)) +
  geom_point() + 
  geom_line()

ggplot(data=Tetriser[Tetriser$type=="result",],aes(x=generation, y=score)) +
  geom_point() + 
  geom_line()

#plot the feature weights over time
ggplot(data=Tetriser[Tetriser$type=="result",]) + 
  geom_line(aes(x=generation,y=landing_height),color="red") + 
  geom_line(aes(x=generation,y=eroded_cells),color="orange") + 
  geom_line(aes(x=generation,y=row_trans),color="yellow") + 
  geom_line(aes(x=generation,y=col_trans),color="green") + 
  geom_line(aes(x=generation,y=pits),color="blue") + 
  geom_line(aes(x=generation,y=cuml_wells),color="purple") + 
  geom_line(aes(x=generation,y=tetris),color="brown") + 
  geom_line(aes(x=generation,y=tetris_progress),color="black")

#plot the normalized feature weights over time
ggplot(data=Tetriser[Tetriser$type=="result",]) + 
  geom_line(aes(x=generation,y=landing_height_norm),color="red") + 
  geom_line(aes(x=generation,y=eroded_cells_norm),color="orange") + 
  geom_line(aes(x=generation,y=row_trans_norm),color="yellow") + 
  geom_line(aes(x=generation,y=col_trans_norm),color="green") + 
  geom_line(aes(x=generation,y=pits_norm),color="blue") + 
  geom_line(aes(x=generation,y=cuml_wells_norm),color="purple") + 
  geom_line(aes(x=generation,y=tetris_norm),color="brown") + 
  geom_line(aes(x=generation,y=tetris_progress_norm),color="black")
