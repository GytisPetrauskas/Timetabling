class Graph():
	# Graph object initialization
	def __init__(self, vertex, neighbours, color, status):
		self.vertex = vertex
		self.neighbours = neighbours
		self.color = color
		self.status = status
	# Creation of a whole graph;
	def createGraph(activities, classrooms):
		# Finding conflicts - marking conflicting vertices as neighbours;
		neighbours = []
		for i in range(len(activities)):
			neighbours.append([])
			for j in range(len(activities)):
				if activities[i].subject == activities[j].subject:
					continue
				elif activities[i].subject != activities[j].subject and activities[i].group == activities[j].group:
					neighbours[i].append(j)
				elif activities[i].subject != activities[j].subject and activities[i].lecturer == activities[j].lecturer and j not in neighbours[i]:
					neighbours[i].append(j)	
		# Adding available class list to every element of activity list;
		for i in activities:
			available_classes = []
			for j in classrooms:
				if j.capacity >= i.group_size:
					available_classes.append(j.classroom+':'+str(j.capacity)+':'+j.faculty)
			i.classroom = available_classes
		# Creating a list of Graph objects;
		graph = []
		for i in range(len(activities)):
			graph.append(Graph(activities[i].subject, neighbours[i], None, 0))
		return graph



		
