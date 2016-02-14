import urllib, md5, webbrowser, time
from xml.dom.minidom import parseString
import htttplib

apikey = "468414896679303"
secret = "15a9f6a1929fdcfdc73eb9b6175aedee"



FacebookSecureURL = "https://api.facebook.com/restserver.php"

def getsinglevalue(node, tag):
	nl = node.getElementsByTagName(tag)
	if len(nl) > 0:
		tagNode = nl[0]
		if tagNode.hasChildNodes():
			return tagNode.firstChild.nodeValue
	return ''

def callid():
	return str(int(time.time()*10))

class fbsession:
	def __init__(self):
		self.session_secret = None
		self.session_key = None
		self.token = 'CAACEdEose0cBAB5IHfZATuZCNPyrtWDAG1iSYfuEHkZAa0ZA3gtpbkq1ufCZACYlAEYQfV1kyHK0GZBLUF3ZBd5FWsZAZC7v63KFwWe4G0h7079JdgjizOSnFxbHWZB7FHMubiKpZBdZBv7KAzW8ZB02wJKKMbJBtv9I7WX0kraSe90lG6A2XZCnVkPl4aMCqsRKmXLQSha9WS0tbi9UfGQWMPsHI3'
		webbrowser.open(self.getlogin())
		print 'Press enter after logging in:',
		raw_input()
		self.getsession()

		self.conn = htttplib.HTTPConnection('graph.facebook.com')

	def sendrequest(self, args):

		# args['api_key'] = apikey
		# args['sig'] = self.makehash(args)
		# post_data = urllib.urlencode(args)
		# url = FacebookSecureURL + "?" + post_data
		# print url
		# data = urllib.urlopen(url).read()
		# return parseString(data)

	def makehash(self, args):
		hasher = md5.new(''.join([x + '=' + args[x] for x in sorted(args.keys())]))
		if self.session_secret: hasher.update(self.session_secret)
		else: hasher.update(secret)
		return hasher.hexdigest()

	def createtoken(self):
		print "in creattoken()"
		res = self.sendrequest({'method':"facebook.auth.createToken"})
		print res.firstChild.nodeValue
		print getsinglevalue(res, 'token')
		self.token = getsinglevalue(res, 'token')

	def getlogin(self):
		print apikey
		print self.token
		return "http://api.facebook.com/login.php?api_key="+apikey+"&auth_token="+self.token

	def getsession(self):
		doc = self.sendrequest({'method':'facebook.auth.getSession','auth_token':self.token})
		self.session_key = getsinglevalue(doc, 'session_key')
		self.session_secret = getsinglevalue(doc, 'secret')

	def getfriends(self):
		doc = self.sendrequest({'method':'facebook.friends.get', 'session_key':self.session_key,'call_id':callid()})
		results = []
		for n in doc.getElementsByTagName('result_elt'):
			results.append(n.firstChild.nodeValue)
		return results


	def getinfo(self, users):
		ulist = ','.join(users)

		fields = 'gender,current_location,relationship_status,'+'affiliations,hometown_location'

		doc = self.sendrequest({'method':'facebook.users.getInfo', 'session_key':self.session_key, 'call_id':callid(),'users':ulist, 'fields':fields})

		results = {}
		for n,id in zip(doc.getElementsByTagName('result_elt'),users):
			
			# Get the location
			locnode = n.getElementsByTagName('hometown_location')[0]
			loc = getsinglevalue(locnode, 'city')+', '+getsinglevalue(locnode, 'state')

			# Get school
			college = ''
			gradyear = '0'
			affiliations = n.getElementsByTagName('affiliations_elt')
			for aff in affiliations:
				# Type 1 is college
				if getsinglevalue(aff, 'type')=='1':
					college = getsinglevalue(aff, 'name')
					gradyear = getsinglevalue(aff, 'year')

			results[id] = {'gender':getsinglevalue(n,'gender'), 'status':getsinglevalue(n,'relationship_status'), 'location':loc, 'college':college, 'year':gradyear}

		return results











