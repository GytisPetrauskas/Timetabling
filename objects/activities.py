class Activities():
	# Activities object initialization
	def __init__(self, subject, credits, group, group_size, lecturer, classroom, faculty):
		self.subject = subject
		self.credits = credits
		self.group = group
		self.group_size = group_size
		self.lecturer = lecturer
		self.classroom = classroom
		self.faculty = faculty
	# Object creation
	def createActivities(courses, groups):
		isFailed = None
		activities = []
		# How many times one subject is taught in a single week;
		for i in courses:
			if i.credits <= 5:
				times_per_week = 1
			elif 5 <= i.credits <= 10:
				times_per_week = 2
			elif 10 <= i.credits <= 15:
				times_per_week = 3
			elif 15 <= i.credits <= 20:
				times_per_week = 4
			else:
				isFailed = 'Course can have a maximum of 20 credits.'
				return None, isFailed
			for j in range(times_per_week):
				activities.append(Activities(i.subject+'_'+str(j), i.credits, i.group, None, i.lecturer, None, None))
		# Adding group size;
		for i in groups:
			for j in activities:
				if i.group == j.group:
					j.group_size = int(i.size)
		return activities, isFailed
