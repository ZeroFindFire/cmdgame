def hour(h,m):
	return h+m/60.0
courses={
	1:[
		(hour(14,0), hour(17,35)),
		],
	2:[
		(hour(14,0), hour(17,35)),
		(hour(19,30), hour(21,55))
		],
	3:[
		(hour(16,55), hour(18,35))
		],
	4:[
		(hour(10,0), hour(12,25)),
		(hour(14,00), hour(17,35))
		],
	5:[
		(hour(14,0), hour(17,35)),
		],
}
works=[
	(hour(9,00), hour(12,00)),
	(hour(13,30), hour(18,00))
]
def cross(a,b):
	m=max(a[0],b[0])
	mx=min(a[1],b[1])
	if m>mx:return 0;
	return mx-m
def work_time():
	total=0.0
	for day in courses:
		course=courses[day]
		up,down=works[0],works[1]
		tmp=0.0
		for ctime in course:
			for work in works:
				tmp+=cross(ctime,work)
		twork=0.0
		for work in works:
			twork+=work[1]-work[0]
		total+=twork-tmp
	return total