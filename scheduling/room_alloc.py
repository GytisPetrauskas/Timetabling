import copy
import random


def assignRooms(graph, original_data):
	data = copy.deepcopy(original_data)
	subjects_colored = []
	no_of_colors = 0
	# Get the number of colors
	for i in graph:
		if i.color > no_of_colors:
			no_of_colors = i.color
	# Create a list to save subjects by their color
	for i in range(no_of_colors+1):
		subjects_colored.append([])
	# Fill the list with subjects
	for i in range(len(graph)):
		for j in range(len(subjects_colored)):
			if j == graph[i].color:
				subjects_colored[j].append(data[i])

	def takePropertyForSort(prop):
		return prop.group_size

	colors = []
	additional_colors = []
	faculties_used = []
	faculties = []
	for i in data:
		for j in i.classroom:
			if j.split(':')[2] not in faculties:
				faculties.append(j.split(':')[2])
	for i in subjects_colored:
		if faculties_used != [] and len(faculties_used) == len(faculties):
			faculties_used = []
		if faculties_used == []:
			faculties_used.append(faculties[-1])
		else:
			for j in faculties:
				if j not in faculties_used:
					faculties_used.append(j)
					break
		prioritized_faculty = faculties_used[-1]
		line = i
		count = 0
		while any([isinstance(i.classroom, list) for i in line]):
			list_of_subjects_without_a_room = [i for i in line if isinstance(i.classroom, list)]
			list_of_subjects_without_a_room_sorted = sorted(list_of_subjects_without_a_room, key=takePropertyForSort, reverse=True)
			used_rooms = []
			for j in list_of_subjects_without_a_room_sorted:
				available_rooms = j.classroom
				available_rooms = [k for k in available_rooms if k not in used_rooms]
				try:
					available_rooms_another_faculty = []
					max_size_room = None
					if faculties_used != None:
						available_rooms_another_faculty = [i for i in available_rooms if i.split(':')[2] != faculties_used]
						room_size = [i.split(':')[1] for i in available_rooms_another_faculty]
						max_room_size = max(room_size)
						for i in available_rooms_another_faculty:
							if i.split(':')[1] == max_room_size:
								max_size_room = i
								break
					if max_size_room == None:
						room_size = [i.split(':')[1] for i in available_rooms]
						max_room_size = max(room_size)
						max_size_room = max(available_rooms)
						for i in available_rooms_another_faculty:
							if i.split(':')[1] == max_room_size:
								max_size_room = i
								break
					used_rooms.append(max_size_room)
					j.classroom = max_size_room.split(':')[0]
					j.faculty = max_size_room.split(':')[2]
				except ValueError:
					break
			if count == 0:
				colors.append([i for i in list_of_subjects_without_a_room_sorted if isinstance(i.classroom, str)])
			elif count > 0:
				additional_colors.append([i for i in list_of_subjects_without_a_room_sorted if isinstance(i.classroom, str)])
			count += 1
	for i in additional_colors:
		colors.append(i)
	return colors
