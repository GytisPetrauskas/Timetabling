# Optimized coloring;
# Algorithms used: Modification of Tabu Search;

import copy
import random
from random import randrange, randint
from objects.graph import Graph as graphs
from collections import deque
from datetime import datetime
import sys

# Create a copy of some list;
def makeCopy(old):
	new = copy.deepcopy(old)
	return new

# Tabu search algorithm;
def tabu_search(graph_, col):
	data = makeCopy(graph_)
	# Start counting duration;
	duration_start = datetime.now()
	# Initialize best coloring variable;
	best_coloring = None
	# Set the amount of colors to begin trying to color with;
	if col-2 <= 1:
		colors_needed = 2
	else:
		colors_needed = col-2
	# Algorithm modification;
	while not best_coloring:
		A = {}
		tabu_list = []
		max_tabu_size = 10
		stopping_condition = 1000
		for i in range(len(data)):
			data[i].color = random.choice(range(colors_needed))
		best_candidate = random.choice(data)
		for iteration in range(stopping_condition):
			neighborhood = []
			fitness = 0
			for i in range(len(data)):
				for j in data[i].neighbours:
					if data[i].color == data[j].color:
						if data[i] not in neighborhood:
							neighborhood.append(i)
						if data[j] not in neighborhood:
							neighborhood.append(j)
						fitness += 1
			if fitness == 0:
				break
			for iteration_second in range(100):
				data_alternative = makeCopy(data)
				candidate_alternative = random.choice(neighborhood)
				color = random.choice(range(colors_needed))
				while color == data[candidate_alternative]:
					color = random.choice(range(colors_needed))
				data_alternative[candidate_alternative].color = color
				fitness_second = 0
				for i in range(len(data)):
					for j in data[i].neighbours:
						if data_alternative[i].color == data_alternative[j].color:
							fitness_second += 1
				def _aspiration_is_better(A, fitness, fitness_second):
					if fitness not in A:
						A[fitness] = fitness-1
					if A[fitness] >= fitness_second:
						return True
					else:
						return False 
				if fitness > fitness_second and _aspiration_is_better(A, fitness, fitness_second) and (candidate_alternative, color) in tabu_list:
					A[fitness] = fitness_second-1
					tabu_list.remove((candidate_alternative, color))
					break
				elif fitness < fitness_second and (candidate_alternative, color) in tabu_list:
					continue
				break
			tabu_list.append((candidate_alternative, color))
			data = data_alternative
			if len(tabu_list) > max_tabu_size:
				tabu_list.pop(0)
		if fitness == 0:
			best_coloring = 1
		else:
			colors_needed += 1
	# End duration timer;
	duration_end = datetime.now()
	return data, duration_end-duration_start
