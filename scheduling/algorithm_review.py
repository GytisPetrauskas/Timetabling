import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def setDurations(durations):
	with open('static/durations.json', 'w') as outfile:
		json.dump(durations, outfile)

def getDurations():
	with open('static/durations.json') as json_file:
		data = json.load(json_file)
	return data

def setColoringResults(greedy, dsatur, rlf, tabusearch):
	coloring = {}
	greedy_list = []
	for i in greedy:
		greedy_list.append([i.vertex, i.color])
	dsatur_list = []
	for i in dsatur:
		dsatur_list.append([i.vertex, i.color])
	rlf_list = []
	for i in rlf:
		rlf_list.append([i.vertex, i.color])
	tabu_list = []
	for i in tabusearch:
		tabu_list.append([i.vertex, i.color])

	coloring['greedy'] = greedy_list
	coloring['dsatur'] = dsatur_list
	coloring['rlf'] = rlf_list
	coloring['tabu'] = tabu_list

	createGraphDrawing(greedy, 'greedy.png')
	createGraphDrawing(dsatur, 'dsatur.png')
	createGraphDrawing(rlf, 'rlf.png')
	createGraphDrawing(tabusearch, 'tabu.png')

	with open('static/colorings.json', 'w') as outfile:
		json.dump(coloring, outfile)

def getColoringResults():
	with open('static/colorings.json') as json_file:
		data = json.load(json_file)
	return data

def createGraphDrawing(graph, filename):
	if os.path.exists('static/graphs/'+filename):
		os.remove('static/graphs/'+filename)
	if len(graph) <= 50:
		import networkx as nx

		G = nx.Graph()
		graph_edges = []
		for i in graph:
			G.add_node(i.vertex)
			for j in i.neighbours:
				graph_edges.append([i.vertex, graph[j].vertex])
		for i in graph_edges:
			G.add_edge(i[0], i[1])
		color_map = []
		for i in graph:
			color_map.append(i.color)

		pos = nx.shell_layout(G)
		nx.draw(G, pos, node_color = color_map, with_labels=True)
		plt.margins(0.2)
		plt.savefig('static/graphs/'+filename, format="PNG")

def getUsedColors(data):
	max_colors = {}
	keys = ['Greedy', 'DSatur', 'RecursiveLargestFirst','TabuSearch']
	temp = 0
	for key in data.keys():
		max_ = 0
		for i in data[key]:
			if i[1] > max_:
				max_ = i[1]
		max_colors[keys[temp]] = max_+1
		temp += 1
	return max_colors