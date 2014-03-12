
#load the file
Tetriser <- read.delim("X:/Tetris_Project/Tetris-AI/runs/Tetriser.tsv")


#extract the generation information from the name field
Tetriser$generation = as.numeric(sub("G","",sub("_.*","",as.character(Tetriser$name))))


ggplot(data=Tetriser[Tetriser$type=="result",],aes(x=generation, y=l4)) +
  geom_point()

ggplot(data=Tetriser[Tetriser$type=="result",],aes(x=generation, y=score)) +
  geom_point()