# Flask web based project for creating university timetables using Graph coloring algorithms of Graph Theory.
# Bachelor thesis, topic: Timetabling using graph coloring algorithms.
# Gytis Petrauskas 2020

# Python library imports;
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import xlrd
import csv
import sys
import os
import copy
import time

# File imports;
import data.generate_data as gen
from objects.graph import Graph as graphs
from objects.activities import Activities as act
from objects.schedule import Schedule as sch
import scheduling.greedy_coloring as gc
import scheduling.room_alloc as ra
import scheduling.create_schedule as cs
import scheduling.optimized_coloring as oc
import scheduling.algorithm_review as ar
# Upload folder destination;
UPLOAD_FOLDER = os.getcwd()+'/static/uploads/'
# Configurations;
app = Flask(__name__)
app.secret_key = "secret"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd()+'/scheduling.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)


# Database logic;
class Courses(db.Model):
	__tablename__ = 'courses'
	subject = db.Column(db.String(50), primary_key=True)
	credits = db.Column(db.Float, nullable=False)
	group = db.Column(db.String(50), db.ForeignKey('groups.group'), nullable=False)
	lecturer = db.Column(db.String(50), nullable=False)

	courses_groups = db.relationship("Groups", back_populates="groups_courses")
	courses_schedules = db.relationship("Schedules", back_populates="schedules_courses", cascade="all, delete-orphan")


class Classrooms(db.Model):
	__tablename__ = 'classrooms'
	classroom = db.Column(db.String(50), primary_key=True)
	capacity = db.Column(db.Integer, nullable=False)
	faculty = db.Column(db.String(50), nullable=False)

	classrooms_schedules = db.relationship("Schedules", back_populates="schedules_classrooms", cascade="all, delete-orphan")


class Groups(db.Model):
	__tablename__ = 'groups'
	group = db.Column(db.String(50), primary_key=True)
	size = db.Column(db.Integer, nullable=False)

	groups_courses = db.relationship("Courses", back_populates="courses_groups", cascade="all, delete-orphan")
	groups_schedules = db.relationship("Schedules", back_populates="schedules_groups", cascade="all, delete-orphan")


class Schedules(db.Model):
	__tablename__ = 'schedules'
	activity_id = db.Column(db.Integer, primary_key=True)
	activity_subject = db.Column(db.String(50), db.ForeignKey('courses.subject'), nullable=False)
	activity_credits = db.Column(db.Float, nullable=False)
	activity_group = db.Column(db.String(50), db.ForeignKey('groups.group'), nullable=False)
	activity_lecturer = db.Column(db.String(50), nullable=False)
	activity_classroom = db.Column(db.String(50), db.ForeignKey('classrooms.classroom'), nullable=False)
	activity_faculty = db.Column(db.String(50), nullable=False)
	activity_time_slot = db.Column(db.Integer, nullable=False)
	activity_algorithm = db.Column(db.String(50), nullable=False) #greedy, dsatur, rlf

	schedules_courses = db.relationship("Courses", back_populates="courses_schedules") 
	schedules_classrooms = db.relationship("Classrooms", back_populates="classrooms_schedules")
	schedules_groups = db.relationship("Groups", back_populates="groups_schedules")


# Routing and main logic;
#
# Landing page;
@app.route("/")
def index():
    return render_template('pages/index.html')

# Data entry, option chice page;
@app.route("/timetabling", methods=['GET','POST'])
def timetabling():
	courses = Courses.query.all()
	classrooms = Classrooms.query.all()
	groups = Groups.query.all()
	return render_template('pages/timetabling.html', courses=courses, classrooms=classrooms, groups=groups)

# Random data generation;
@app.route('/generate', methods = ['GET', 'POST'])
def generateData():
	# Retrieving data from form fields;
	group_quantity = int(request.form['data_gen_groups'])
	lecturer_quantity = int(request.form['data_gen_lecturers'])
	classroom_quantity = int(request.form['data_gen_classrooms'])
	faculty_quantity = int(request.form['data_gen_faculties'])
	# Reference to data generation file;
	courses, groups, classrooms = gen.genData(group_quantity, lecturer_quantity, classroom_quantity, faculty_quantity)
	# Removing old data;
	removeData('all')
	# Inserting generated data into DB tables;
	for c in courses:
		course = Courses(
			subject=c[0],
			credits=c[1],
			group=c[2],
			lecturer=c[3]
		)
		db.session.add(course)
	for c in classrooms:
		classroom = Classrooms(
			classroom=c[0],
			capacity=c[1],
			faculty=c[2]
		)
		db.session.add(classroom)
	for g in groups:
		group = Groups(
			group=g[0],
			size=g[1]
		)
		db.session.add(group)
	db.session.commit()
	# Reloading the page with a success flash message;
	flash('Random data generated.', 'success')
	return redirect(url_for('timetabling'))

# Work day setting;
@app.route('/setWorkdays', methods= ['GET', 'POST'])
def settingWorkdays():
	# Retrieving chosen days from the form;
	# If no days were selected, redirecting back to the same page with an error message;
	if request.form.getlist('days') == []:
		flash('Select atleast one workday!', 'danger')
		return redirect(url_for('timetabling'))
	# If days are selected, reseting the current work days;
	cs.setDays(request.form.getlist('days'))
	# Reloading the page with a success flash message;
	flash('Workdays set successfully!', 'success')
	return redirect(url_for('timetabling'))

# Retrieving data from .xlsx and inserting it into the DB tables;
@app.route('/getdata', methods = ['GET', 'POST'])
def getData():
	data_ = list(request.form.keys())[0]
	if request.method == 'POST':
		f = request.files[data_]
		# Check if a file was selected before pressing the "upload" button;
		if f.filename == '':
			flash('No file selected!', 'danger')
			return redirect(url_for('timetabling'))
		# Check if file is of .xlsx format;
		if not f.filename.endswith('.xlsx'):
			flash('File format incorrect (Only upload .xlsx files)!', 'danger')
			return redirect(url_for('timetabling'))
		# Save file into the uploads folder;
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
		# Opening the .xlsx file, retrieving data;
		wb = xlrd.open_workbook(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
		sheet = wb.sheet_by_index(0)
		data = []
		for i in range(1, sheet.nrows):
			data.append(sheet.row_values(i))
	# Check if the amount of columns in a file is as needed;
	# If it is in fact correct, delete the old data from DB table and add new data;
	def is_len_correct(data, length):
		correct = True
		for d in data:
			if len(d) != length:
				correct = False
				break
		return correct
	if request.form[data_] == "courses":
		if not is_len_correct(data, 4):
			flash('Data inserted is corrupted!', 'danger')
			return redirect(url_for('timetabling'))
		db.session.query(Courses).delete()
		for d in data:
			to_add = Courses(
				subject=d[0],
				credits=d[1],
				group=d[2],
				lecturer=d[3]
			)
			db.session.add(to_add)
	elif request.form[data_] == "classrooms":
		if not is_len_correct(data, 3):
			flash('Data inserted is corrupted!', 'danger')
			return redirect(url_for('timetabling'))
		db.session.query(Classrooms).delete()
		for d in data:
			to_add = Classrooms(
				classroom=d[0],
				capacity=d[1],
				faculty=d[2]
			)
			db.session.add(to_add)
	elif request.form[data_] == "groups":
		if not is_len_correct(data, 2):
			flash('Data inserted is corrupted!', 'danger')
			return redirect(url_for('timetabling'))
		db.session.query(Groups).delete()
		for d in data:
			to_add = Groups(
				group=d[0],
				size=d[1]
			)
			db.session.add(to_add)
	db.session.commit()
	wb.release_resources()
	# Remove the .xlsx file from the uploads folder;
	for file in os.listdir(UPLOAD_FOLDER):
		if file.endswith('.xlsx'):
			try:
				os.remove(UPLOAD_FOLDER+file)
			except FileNotFoundError:
				continue
	# Reloading the page with a success flash message;
	flash('Data inserted successfully!', 'success')
	return redirect(url_for('timetabling'))

# Insert a single entry into the database by hand;
@app.route('/addsingle', methods = ['GET', 'POST'])
def addSingle():
	data_ = list(request.form.keys())[-1]
	if data_ == "courses":
		subject = request.form['subject']
		credits = request.form['credits']
		group = request.form['group']
		lecturer = request.form['lecturer']
		i = 0
		original = subject
		while (bool(Courses.query.filter_by(subject=subject).first())):
			subject = original
			i+=1
			subject = subject+'_'+str(i)
		to_add = Courses(
			subject=subject, 
			credits=credits, 
			group=group, 
			lecturer=lecturer
		)
	elif data_ == "classrooms":
		classroom = request.form['classroom']
		capacity = request.form['capacity']
		faculty = request.form['faculty']

		if (bool(Classrooms.query.filter_by(classroom=classroom).first())):
			flash('Classroom <'+classroom+'> already exists!','danger')
			return redirect(url_for('timetabling'))
		to_add = Classrooms(
			classroom=classroom, 
			capacity=capacity,
			faculty=faculty
		)
	elif data_ == "groups":
		group = request.form['group']
		size = request.form['size']
		if (bool(Groups.query.filter_by(group=group).first())):
			flash('Group <'+group+'> already exists!','danger')
			return redirect(url_for('timetabling'))
		to_add = Groups(
			group=group, 
			size=size
		)
	db.session.add(to_add)
	db.session.commit()
	# Reloading the page with a success flash message;
	flash('<'+list(request.form.keys())[0]+'> Added successfully!','success')
	return redirect(url_for('timetabling'))

# Removing a single row of data from a selected database table;
@app.route('/removesingle/<data_for>/<name>', methods = ['GET', 'POST'])
def removeSingle(name, data_for):
	# Deletion of a single row for a database table functionality;
	if data_for == 'courses':
		to_delete = Courses.query.filter_by(subject=name).one()
	elif data_for =='classrooms':
		to_delete = Classrooms.query.filter_by(classroom=name).one()
	elif data_for =='groups':
		to_delete = Groups.query.filter_by(group=name).one()
	db.session.delete(to_delete)
	db.session.commit()
	# Reloading the page with a success flash message;
	flash('<'+name+'> deleted successfully!', 'success')
	return redirect(url_for('timetabling'))

# Removing data from single or multiple DB tables;
@app.route('/removedata/<name>', methods = ['GET', 'POST'])
def removeData(name):
	if name == 'courses':
		db.session.query(Courses).delete()
	elif name == 'classrooms':
		db.session.query(Classrooms).delete()
	elif name == 'groups':
		db.session.query(Groups).delete()
	elif name == 'all':
		db.session.query(Courses).delete()
		db.session.query(Classrooms).delete()
		db.session.query(Groups).delete()
	db.session.commit()
	# Reloading the page with a success flash message;
	flash('Old data removed successfully!', 'success')
	return redirect(url_for('timetabling'))

# Creating timetable schedules;
@app.route('/createschedule', methods= [ 'GET', 'POST'])
def createSchedule():
	# Querying current data from DB tables;
	courses = Courses.query.all()
	groups = Groups.query.all()
	classrooms = Classrooms.query.all()
	# Checking if all tables have atleast 1 row of data;
	need_courses = need_groups = need_classrooms = None
	if courses == []:
		need_courses = 'Add some courses'
	if groups == []:
		need_groups = 'Add some groups'
	if classrooms == []:
		need_classrooms = 'Add classrooms'
	# If atleast one of the tables is empty, reloading the page with an error message;
	if need_courses != None or need_groups != None or need_classrooms != None:
		if need_courses != None:
			flash(need_courses, 'danger')
		if need_groups != None:
			flash(need_groups,'danger')
		if need_classrooms != None:
			flash(need_classrooms,'danger')
		return redirect(url_for('timetabling'))
	# Creating Activities objects with the current data in DB tables;
	activities, isFailed = act.createActivities(courses, groups)
	# Checking if data entered is correct;
	if isFailed != None:
		flash(isFailed, 'danger')
		return redirect(url_for('timetabling'))
	# Creating Graph objects (single object is a vertice) and all of them form a graph;
	original_graph = graphs.createGraph(activities, classrooms)
	# Using 3 greedy coloring algorithms on the graph and getting 3 colored graphs, also retrieving each algorithm's coloring duration;
	greedy, dsatur, rlf, durations_greedy = gc.greedyGraphColoring(original_graph)
	# Retrieving the smallest ammount of colors used by one of the three coloring algorithms;
	colors_needed_min_greedy_algo = 0
	temp_greedy = 0
	temp_dsatur = 0
	temp_rlf = 0
	for i in range(len(greedy)):
		if greedy[i].color > temp_greedy:
			temp_greedy = greedy[i].color
		if dsatur[i].color > temp_dsatur:
			temp_dsatur = dsatur[i].color
		if rlf[i].color > temp_rlf:
			temp_rlf = rlf[i].color
	colors_needed_min_greedy_algo = max(temp_greedy, temp_dsatur, temp_rlf)
	# Using the optimised Tabu search algorithm for a fourth coloring, retrieving the colored graph;
	tabusearch, duration_optimized = oc.tabu_search(original_graph, colors_needed_min_greedy_algo)
	# Retrieving all algorithm durations and saving them for later use;
	durations = durations_greedy
	durations['TabuSearch'] = str(duration_optimized)
	ar.setDurations(durations)
	ar.setColoringResults(greedy, dsatur, rlf, tabusearch)
	# Assigning classes for activities of the university;
	activities_greedy = ra.assignRooms(greedy, activities)
	activities_dsatur = ra.assignRooms(dsatur, activities)
	activities_rlf = ra.assignRooms(rlf, activities)
	activities_tabu = ra.assignRooms(tabusearch, activities)
	# Retrieving the number of slots needed with the current classroom assignments;
	no_of_slots = len(cs.slots())
	# Examining if the ammount of slots we have is not less then the ammount needed;
	if len(activities_greedy) > no_of_slots or len(activities_dsatur) > no_of_slots or len(activities_rlf) > no_of_slots or len(activities_tabu) > no_of_slots:
		flash('Not enough time slots for provided data, change up your data!', 'danger')
		return redirect(url_for('timetabling'))
	# Retrieving the maximum ammount of colors needed for an algorithm (One color = one time slot);
	colors_needed = max(len(activities_greedy),len(activities_dsatur),len(activities_rlf),len(activities_tabu))
	# Making the schedule;
	schedule_greedy, message1 = cs.makeSchedule(activities_greedy, 'greedy')
	schedule_dsatur, message2 = cs.makeSchedule(activities_dsatur, 'dsatur')
	schedule_rlf, message3 = cs.makeSchedule(activities_rlf, 'rlf')
	schedule_tabu, message4 = cs.makeSchedule(activities_tabu, 'tabu')
	# Reloading the page with an error message if not a single schedule could be created with current data;
	if schedule_greedy == None and schedule_dsatur == None and schedule_rlf == None and schedule_tabu == None:
		flash('Couldnt create a schedule with all of the algorithms, change up your data!')
		return redirect(url_for('timetabling'))
	# Checking which algorithms didn't have a schedule created for them;
	message_final = ''
	if schedule_greedy == None:
		message_final += message1+'\n'
	if schedule_dsatur == None:
		message_final += message2+'\n'
	if schedule_rlf == None:
		message_final += message3+'\n'
	if schedule_tabu == None:
		message_final += message4+'\n'
	# Saving all schedules in a single list;
	schedules = []
	schedules.append(schedule_greedy)
	schedules.append(schedule_dsatur)
	schedules.append(schedule_rlf)
	schedules.append(schedule_tabu)
	# Removing old data;
	db.session.query(Schedules).delete()
	# Inserting new data;
	for i in range(len(schedules)):
		try:
			for j in schedules[i]:
				data_to_add = Schedules(
					activity_subject = j.activity.subject,
					activity_credits = j.activity.credits,
					activity_group = j.activity.group,
					activity_lecturer = j.activity.lecturer,
					activity_classroom = j.activity.classroom,
					activity_faculty = j.activity.faculty,
					activity_time_slot = j.time_slot,
					activity_algorithm = j.algorithm
				)
				db.session.add(data_to_add)
		except TypeError:
			continue
	db.session.commit()
	# Redirecting to the schedule page with a success flash message;
	flash('Scheduling complete!\n'+message_final, 'success')
	return redirect(url_for('schedule', category='all', filter_key='all'))	

# Schedule page;
@app.route('/schedule/<category>/<filter_key>', methods= [ 'GET', 'POST'])
def schedule(category, filter_key):
	# Filtering logic, loading everything at first, loading the selected data if a filter is selected;
	if category == 'all' and filter_key == 'all':
		schedule = Schedules.query.all()
	elif category == 'groups':
		schedule = Schedules.query.filter_by(activity_group=filter_key)
	elif category == 'lecturers':
		schedule = Schedules.query.filter_by(activity_lecturer=filter_key)
	elif category == 'classrooms':
		schedule = Schedules.query.filter_by(activity_classroom=filter_key)
	elif category == "subjects":
		schedule = Schedules.query.filter(Schedules.activity_subject.contains(filter_key))
	# Redirecting to the data filling page if the schedules hadn't been created yet;
	if schedule == []:
		flash('There is no existing scheduling, create one now!', 'danger')
		return(redirect(url_for('timetabling')))
	# Retrieving data to put into the HTML table;
	data_without_filtering = Schedules.query.all()
	data_for_color_representation = []
	data_for_color_representation.append(Schedules.query.filter_by(activity_algorithm='greedy'))
	data_for_color_representation.append(Schedules.query.filter_by(activity_algorithm='dsatur'))
	data_for_color_representation.append(Schedules.query.filter_by(activity_algorithm='rlf'))
	data_for_color_representation.append(Schedules.query.filter_by(activity_algorithm='tabu'))
	lecturers = Courses.query.group_by(Courses.lecturer)
	classrooms = Classrooms.query.all()
	groups = Groups.query.all()
	subjects = Courses.query.all()
	# Retrieving slots, days, periods for the HTML table;
	slots = cs.slots()
	day = slots[0].split(':')[0]
	days = list(set([i.split(':')[0] for i in slots]))
	times = [i.split(':')[1] for i in slots if day in i]
	# Loading the schedules into HTML table;
	if schedule != None:
		schedule_for_algorithms = cs.scheduleForTable(schedule, len(slots))
	# Loading algorithm data: durations, colors of vertices, ammount of colors used;
	durations = ar.getDurations()
	colorings = ar.getColoringResults()
	used_colors = ar.getUsedColors(colorings)
	# Loading the page with schedules;
	return render_template('pages/schedule.html', 
		schedule=schedule_for_algorithms, 
		db_schedule=schedule, 
		db_classrooms=classrooms,
		db_groups=groups,
		db_lecturers=lecturers,
		db_subjects=subjects,
		days=days, 
		times=times,
		durations=durations,
		data=data_without_filtering,
		data_for_table=data_for_color_representation,
		used_colors=used_colors
	)

# Main function
if __name__ == '__main__':
	# Creating database;
	db.create_all()
	# Setting default workdays;
	cs.setDays(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
	# Running the program
	app.run(debug=False)
