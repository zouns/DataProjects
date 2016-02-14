from random import random, randint
import math
import pylab
from sklearn import cross_validation
from sklearn.neighbors import KNeighborsRegressor


weightsdomain = [(0,20)]*4

def wineprice(rating, age):
	peak_age = rating-50

	# Calculate price based on rating
	price = rating/2
	if age>peak_age:
		# Past its peak, goes bad in 5 years
		price = price*(5-(age-peak_age))
	else:
		# Increases to 5x original value as it approaches its peak
		price = price*(5*((age+1)/peak_age))
	if price<0: price = 0
	return price


# Creating dataset
def wineset1(n=300):
	rows=[]
	for i in range(n):
		# Create a random age and rating
		rating = random()*50+50
		age = random()*50

		# Get reference price
		price = wineprice(rating, age)

		# Add some noise
		price *= (random()*0.4+0.8)

		# Add to the dataset
		rows.append({'input':(rating,age),'result':price})
	return rows

	# Add some scale needing variables
def wineset2(n=300):
	rows=[]
	for i in range(n):
		# Create a random age and raating
		rating = random()*50+50
		age = random()*50

		aisle = float(randint(1,20))
		bottlesize = [375.0, 750.0, 1500.0, 3000.0][randint(0,3)]

		# Get reference price
		price = wineprice(rating, age)
		price *= (bottlesize/750)

		# Add some noise
		price *= (random()*0.9+0.2)

		# Add to the dataset
		rows.append({'input':(rating,age,aisle,bottlesize),'result':price})
	return rows

	# Add unleasured variables
def wineset3(n=300):
	rows = wineset1(n)
	for row in rows:
		if random()<0.5:
			# Wine was bought at a discount store
			row['result']*=0.6
	return rows

# Rescaling the data
def rescale(data, scale):
	scaleddata = []
	for row in data:
		scaled = [row['input'][i]*scale[i] for i in range(len(scale))]
		scaleddata.append({'input':scaled, 'result':row['result']})
	return scaleddata

# Optimizing the scale
def createcostfunction(algf,data):
	def costf(scale):
		sdata = rescale(data,scale)
		return crossvalidate(algf,sdata,trials=10)
	return costf

# Calculate the probability of being in a certain range
def probguess(data,vec1,low,high,k=5,weightf=gaussian):
	dlist = getdistances(data,vec1)
	nweight = 0.0
	tweight = 0.0

	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		weight = weightf(dist)
		v = data[idx]['result']

		# Is this point in the range?
		if v>=low and v<=high:
			nweight += weight
		tweight += weight
	if tweight==0: return 0

	# The probability is the weights in the range
	# divided by all the weights
	return nweight/tweight

# Plot the cumulative probability
def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
	t1 = pylab.arange(0.0,high,0.1)
	cprob = pylab.array([probguess(data,vec1,0,v,k,weightf) for v in t1])
	pylab.plot(t1,cprob)
	pylab.show()

def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
	# Make a range for the prices
	t1 = pylab.arange(0.0,high,0.1)

	# Get the probabilities for the entire range
	probs = [probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]

	# Smooth them by adding the gaussian of the nearby probabilities
	smoothed = []
	for i in range(len(probs)):
		sv = 0.0
		for j in range(0,len(probs)):
			dist = abs(i-j)*0.1
			weight = gaussian(dist,sigma=ss)
			sv += weight*probs[j]
		smoothed.append(sv)
	smoothed = pylab.array(smoothed)

	pylab.plot(t1,smoothed)
	pylab.show()

# With scikit learn
def scigaussian(distarray):
	return [math.e**(-dist**2/(2*100.0**2)) for dist in distarray]

def sciknnestimate(data,vec1,k=3):
	neigh = KNeighborsRegressor(n_neighbors=k, weights=scigaussian)
	neigh.fit([data[i]['input'] for i in range(len(data))],[data[i]['result'] for i in range(len(data))])
	return neigh.predict([vec1])

def scicrossvalidate(data,k=3):
	X_train, X_test, y_train, y_test = cross_validation.train_test_split([data[i]['input'] for i in range(len(data))],[data[i]['result'] for i in range(len(data))], test_size=0.4, random_state=0)
	neigh = KNeighborsRegressor(n_neighbors=k, weights=scigaussian)
	neigh.fit(X_train,y_train)
	return neigh.score(X_test,y_test)

def scicreatecostfunction(data):
	def costf(scale):
		sdata = rescale(data,scale)
		return 1.0/scicrossvalidate(sdata)
	return costf	


# Home made
def gaussian(dist,sigma=100.0):
	return math.e**(-(dist**2)/(2*(sigma**2)))


def euclidean(vec1,vec2):
	d = 0.0
	for i in range(len(vec1)):
		d += (vec2[i]-vec1[i])**2
	return math.sqrt(d)

def getdistances(data,vec1):
	distancelist = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distancelist.append((euclidean(vec1,vec2),i))
	distancelist.sort()
	return distancelist

def knnestimate(data,vec1,k=4):
	# Get sorted distances
	dlist = getdistances(data,vec1)
	avg = 0.0

	# Take the average of the top k results
	for i in range(k):
		idx = dlist[i][1]
		avg += data[idx]['result']
	avg = avg/k
	return avg

def weightedknn(data,vec1,k=5,weightf=gaussian):
	# Get distances
	dlist = getdistances(data,vec1)
	avg = 0.0
	totalweight = 0.0

	# Get weighted average
	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		weight = weightf(dist)
		avg += weight*data[idx]['result']
		totalweight += weight
	avg = avg/totalweight
	return avg

def dividedata(data,test=0.05):
	trainset = []
	testset = []
	for row in data:
		if random()<test:
			testset.append(row)
		else:
			trainset.append(row)
	return trainset,testset

def testalgorithm(algf,trainset,testset):
	error = 0.0
	for row in testset:
		guess = algf(trainset,row['input'])
		error += (row['result']-guess)**2
	return error/len(testset)

def crossvalidate(algf,data,trials=100,test=0.05):
	error = 0.0
	for i in range(trials):
		trainset,testset = dividedata(data,test)
		error += testalgorithm(algf,trainset,testset)
	return error/trials















