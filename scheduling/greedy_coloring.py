import copy
from datetime import datetime
from multiprocessing import Process
from multiprocessing import Pool
from time import sleep
import threading

greedy_time = dsatur_time = rlf_time = None

def greedyGraphColoring(graph):
	greedy_welsh_powell = copy.deepcopy(graph)
	d_satur = copy.deepcopy(graph)
	recursive_largest_first = copy.deepcopy(graph)
	# Threads
	t1 = threading.Thread(target=greedyWelshPowell, args=(greedy_welsh_powell,))
	t2 = threading.Thread(target=dSatur, args=(d_satur,))
	t3 = threading.Thread(target=recursiveLargestFirst, args=(recursive_largest_first,))
	# Need this so the program doesn't throw an error
	t1.setDaemon(True)
	t2.setDaemon(True)
	t3.setDaemon(True)
	# Starting threads
	t1.start()
	t2.start()
	t3.start()
	# Joining them, so they end together
	t1.join()
	t2.join()
	t3.join()
	durations = {}
	# Getting the colors used for each algorithm
	max_greedy = max_dsatur = max_rlf = 0
	for i in range(len(greedy_welsh_powell)):
		if greedy_welsh_powell[i].color > max_greedy:
			max_greedy = greedy_welsh_powell[i].color
		if d_satur[i].color > max_dsatur:
			max_dsatur = d_satur[i].color
		if recursive_largest_first[i].color > max_rlf:
			max_rlf = recursive_largest_first[i].color
	# Saving the time it took for each algorithm to run
	durations['Greedy'] = str(greedy_time)
	durations['DSatur'] = str(dsatur_time)
	durations['RecursiveLargestFirst'] = str(rlf_time)

	return greedy_welsh_powell, d_satur, recursive_largest_first, durations

def greedyWelshPowell(graph):
	greedy_time_start = datetime.now()
	sorted_by_degree = {}
	for i in graph:
		sorted_by_degree[i] = len(i.neighbours)
	sorted_by_degree = sorted(sorted_by_degree.items(), reverse=True,key=lambda x:x[1])
	order = []
	for i in sorted_by_degree:
		order.append(i[0])
	order[0].color = 0
	color = 1
	for i in order:
		for j in range(color):
			used = [graph[k].color for k in i.neighbours]
			if j not in used:
				i.color = j
				break
		if i.color == None:
			i.color = color
			color += 1
	greedy_time_end = datetime.now()
	global greedy_time
	greedy_time = greedy_time_end-greedy_time_start
	return graph

def dSatur(graph):
	uncolored = graph.copy()
	uncolored[0].color = 0
	color = 1
	uncolored.pop(0)
	dsatur_time_start = datetime.now()
	while uncolored != []:
		v = uncolored[0]
		sat_degree = v.status
		degree = len(v.neighbours)
		for i in uncolored:
			if i.status >= sat_degree:
				v = i
				sat_degree = i.status
				degree = len(i.neighbours)
		for i in range(color):
			used = [graph[k].color for k in v.neighbours]
			if i not in used:
				v.color = i
				break
		if v.color == None:
			v.color = color
			color += 1
		uncolored.remove(v)
	dsatur_time_end = datetime.now()
	global dsatur_time
	dsatur_time = dsatur_time_end-dsatur_time_start
	return graph

def recursiveLargestFirst(graph):
	rlf_time_start = datetime.now()
	# S = []
	uncolored = graph.copy()
	for_another_color = []
	color = 0
	while uncolored != []:
		color += 1
		Si = []
		while uncolored != []:
			v = uncolored[0]
			Si.append(v)
			for n in v.neighbours:
				if graph[n] not in for_another_color and graph[n] in uncolored:
					for_another_color.append(graph[n])
					uncolored.remove(graph[n])
			uncolored.remove(v)
		for s in Si:
			s.color = color-1
		uncolored = for_another_color
		for_another_color = []
	rlf_time_end = datetime.now()
	global rlf_time
	rlf_time = rlf_time_end-rlf_time_start
	return graph