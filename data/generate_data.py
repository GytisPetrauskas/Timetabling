import random
from random import randrange, randint
import math

def genClassrooms(q, f_q, min_size, max_size):
	#--- CLASSROOMS
	classrooms = []
	for f in range(f_q):
		# Adding one classroom of max size to each faculty;
		if q==1:
			for i in range(1):
				classrooms.append(['Classroom'+str(len(classrooms)), max_size, 'Faculty'+str(f)])
		elif q>1:
			for i in range(1):
				classrooms.append(['Classroom'+str(len(classrooms)), max_size, 'Faculty'+str(f)])
			for i in range(1, q):
				classrooms.append(['Classroom'+str(len(classrooms)), randint(min_size, max_size), 'Faculty'+str(f)])
	if f_q == 1:
		for i in range(2):
			classrooms.append(['Classroom'+str(len(classrooms)), max_size, 'Faculty'+str(f)])
	return classrooms


def genGroups(q, min_size, max_size):
	#--- GROUPS
	groups = []
	for i in range(q):
		groups.append(['Group'+str(i), randint(min_size, max_size)])
	return groups

def genCourses(lect_q, groups):
	#--- COURSES
	courses = []
	courses_with_ten_credits = []
	subject_no = 0
	for g in groups:
		# Randomizing how many subjects per subject group will have ten credits
		if 2 not in courses_with_ten_credits:
			how_many_will_have_ten_credits = randint(0, 2)
		else:
			how_many_will_have_ten_credits = randint(0, 1)
		courses_with_ten_credits.append(how_many_will_have_ten_credits)
		# Creating subjects
		if how_many_will_have_ten_credits == 0:
			for i in range(6):
				courses.append(['Subject'+str(i+subject_no), 5.0, g[0]])
			subject_no += 6
		elif how_many_will_have_ten_credits == 1:
			which_has_ten_credits = randint(0, 5)
			for i in range(5):
				if i == which_has_ten_credits:
					courses.append(['Subject'+str(i+subject_no), 10.0, g[0]])
				else:
					courses.append(['Subject'+str(i+subject_no), 5.0, g[0]])
			subject_no += 5
		elif how_many_will_have_ten_credits == 2:
			which_have_ten_credits = [0, 0]
			while which_have_ten_credits[0] == which_have_ten_credits[1]:
				which_have_ten_credits = []
				for i in range(2):
					which_have_ten_credits.append(randint(0, 4))
			for i in range(4):
				if i in which_have_ten_credits:
					courses.append(['Subject'+str(i+subject_no), 10.0, g[0]])
				else:
					courses.append(['Subject'+str(i+subject_no), 5.0, g[0]])
			subject_no += 4
	# Appoint lecturers equally
	lecturer_appointments = {}
	for i in range(lect_q):
		lecturer_appointments['Lecturer'+str(i)] = int(math.ceil(len(courses)/lect_q))
	for i in courses:
		# Find if all lecturers can still have a subject appointed
		available_lecturers = []
		for key, value in lecturer_appointments.items():
			if value > 0:
				available_lecturers.append(key)
		if available_lecturers == []:
			for key, value in lecturer_appointments.items():
				lecturer_appointments[key] = int(math.ceil(len(courses)/lect_q))
				available_lecturers.append(key)
		appointed_lecturer = random.choice(available_lecturers)
		i.append(appointed_lecturer)
		lecturer_appointments[appointed_lecturer] -= 1
	return courses

def genData(group_q, lecturer_q, classroom_q, faculty_q):
	# Min and Max size of classrooms and groups respectively;
	# Note: Change this according to your preferences;
	min_size = 20
	max_size = 40
	#

	classrooms = genClassrooms(classroom_q, faculty_q, min_size, max_size)
	groups = genGroups(group_q, min_size, max_size)
	courses = genCourses(lecturer_q, groups)
	
	return courses, groups, classrooms