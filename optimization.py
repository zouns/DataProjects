import random
import math

def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
	# Initialize the values randomly
	vec = [float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]

	while T>0.1:
		# Choose one of the indices
		i = random.randint(0,len(domain)-1)

		# Choose a direction to change it
		dir = random.randint(-step,step)

		# Create a new list with one of the values changed
		vecb = vec[:]
		vecb[i] += dir
		if vecb[i]<domain[i][0]: vecb[i]=domain[i][0]
		elif vecb[i]>domain[i][1]: vecb[i]=domain[i][1]

		# Calculate the current cost and the new cost
		ea = costf(vec)
		eb = costf(vecb)
		p = pow(math.e,(-(eb-ea))/T)

		# Is it better, or does it make the probability cutoff?
		if (eb<ea or random.random()<p):
			vec = vecb

		# Decrease temperature
		T = T*cool

	return vec