Tetris-AI with Pylearn2
=======================

Workflow
* For each subject
** Load all episodes, split into list(list(features),list(moves))
** Train net
** stop if delta RMSE < threshold