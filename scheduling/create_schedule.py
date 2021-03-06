import random
import copy
import sys
from math import floor

sys.path.append('../')
from objects.schedule import Schedule as sch

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

def setDays(data):
	global days
	days = data

def getDays():
	return days

def slots():
	days = getDays()
	hours = [
				'8.30 - 10.00',
				'10.15 - 12.00',
				'12.00 - 14.00',
				'14.00 - 16.00',
				'16.00 - 18.00',
				'18.00 - 20.00'
			]
	slots = []
	for d in days:
		for h in hours:
			# e.g. slots[0] = Monday : 8.30 - 10.00;
			slots.append(d+':'+h)
	return slots

def getSlots(q):
	no_of_slots = len(slots())
	randomized_slots = []
	for i in range(q):
		slot = None
		while slot in randomized_slots or slot == None:
			slot = random.randrange(0, no_of_slots)
		randomized_slots.append(slot)
	randomized_slots = sorted(randomized_slots)
	return randomized_slots


def createSchedule(data, algo, slots_for_schedule):
	schedule = []
	for i in range(len(data)):
		for j in data[i]:
			schedule.append(sch(j, slots_for_schedule[i], algo))
	return schedule

def scheduleForTable(schedule, slot_no):
	algorithms = getAlgorithms(schedule)
	dispersed_schedules = []
	for i in range(4):
		dispersed_schedules.append([])
		for j in range(slot_no):
			dispersed_schedules[-1].append([])
	for i in schedule:
		if i.activity_algorithm == 'greedy':
			dispersed_schedules[0][i.activity_time_slot].append(i)
		elif i.activity_algorithm == 'dsatur':
			dispersed_schedules[1][i.activity_time_slot].append(i)
		elif i.activity_algorithm == 'rlf':
			dispersed_schedules[2][i.activity_time_slot].append(i)
		elif i.activity_algorithm == 'tabu':
			dispersed_schedules[3][i.activity_time_slot].append(i)
	return dispersed_schedules

def getAlgorithms(schedule):
	algorithms = []
	for i in schedule:
		if i.activity_algorithm not in algorithms:
			algorithms.append(i.activity_algorithm)
	return algorithms

def dfs(used, data, vertex, order):
	if vertex not in used:
		try:
			order.append(vertex)
			used.add(vertex)
			for neighbour in data[vertex]:
				dfs(used, data, neighbour, order)
		except KeyError:
			order.append('*')
	return order

def makeSchedule(original_data, algorithm):
	data = copy.deepcopy(original_data)
	data.sort(key=len, reverse=True)
	available_slots = list(range(len(slots())))
	slot_no = len(available_slots)
	# Find collisions
	collisions = {}
	for i in range(len(data)):
		collisions[i] = {}
		for j in range(i, len(data)):
			if i != j:
				collisions[i][j] = 0
		if collisions[i] == {}:
			collisions.pop(i, None)
	for i in range(len(data)):
		for j in range(len(data[i])):
			for k in range(i, len(data)):
				for l in range(len(data[k])):
					if i != k:
						if data[i][j].group == data[k][l].group and data[i][j].faculty != data[k][l].faculty:
							collisions[i][k] += 1
						if data[i][j].lecturer == data[k][l].lecturer and data[i][j].faculty != data[k][l].faculty:
							collisions[i][k] += 1
	# Sorting collisions
	collisions_sorted = []
	for i in collisions.keys():
		for j, k in collisions[i].items():
			collisions_sorted.append(str(i)+':'+str(j)+':'+str(k))
	collisions_sorted.sort(key=lambda x: x.split(':')[2])
	# get only the ones with no conflicts
	collisions_sorted_no_conflicts = []
	for i in collisions_sorted:
		if int(i.split(':')[-1]) == 0:
			collisions_sorted_no_conflicts.append(i)
	
	collis = {}
	for i in collisions_sorted_no_conflicts:
		if i.split(':')[0] in collis:
			collis[i.split(':')[0]].append(i.split(':')[1])
		else:
			collis[i.split(':')[0]] = [i.split(':')[1]]
	# get road for elements with no conflicts
	visited = set()
	order = []
	if collis != {}:
		order = dfs(visited, collis, list(collis.keys())[0], order)
		if order[-1] == '*':
			del order[-1]
	# add elements with conflicts to the current road (order)
	total_colors = list(range(len(data)))
	for i in total_colors:
		if str(i) not in order:
			order.append('*')
			order.append(i)

	not_optimal = copy.deepcopy(order)
	for i in not_optimal:
		if i == '*':
			not_optimal.remove(i)
	if len(available_slots) < len(order):
		# not enough time slots
		message = 'Can\'t make a schedule for: '+algorithm+'.'
		failed = None
		return failed, message
	elif len(available_slots) == len(not_optimal):
		# not enough time slots to free intervals for travelling between faculties
		message = 'Travelling between faculties is not accounted for: '+algorithm+'.'
		schedule = []
		for i in range(len(original_data)):
			for j in original_data[i]:
				schedule.append(sch(j, available_slots[i], algo))
		return schedule, message
	elif len(available_slots) >= len(order):
		# normal scheduling
		message = 'Scheduling complete for: '+algorithm+'.'
		space_index = []
		for i in range(len(order)):
			if order[i] == '*':
				space_index.append(i)
		used_slots = 0
		schedule = []
		next_day = [i*6+6 for i in range(int(len(available_slots)/6))]
		for i in order:
			# if we do not need a window
			if i != '*':
				for j in data[int(i)]:
					schedule.append(sch(j, available_slots[0], algorithm))
				available_slots.pop(0)
				used_slots += 1
			else: # if we need a window
				# if window in 6, 12, ...
				# it means that we dont need a window, because the next spot will be on the upcoming day
				if available_slots[0] in [6, 12, 18, 24, 30, 36]:
					continue
				else:
					available_slots.pop(0)
					used_slots += 1
		message = 'Scheduling complete for: '+algorithm+'.'
		return schedule, message
	
