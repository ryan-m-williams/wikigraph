import time, argparse, requests, json, pycurl
from collections import defaultdict
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument("--cat", "-C", help="top category")
parser.add_argument("--depth", "-D", help="walk depth", type=int, default=3)
parser.add_argument("--vcount", help="vertices count", action="store_true")
parser.add_argument("--vlist", help="vertices list", action="store_true")
parser.add_argument("--ecount", help="edge count", action="store_true")
parser.add_argument("--elist", help="edge list", action="store_true")
parser.add_argument("--vout", help="vertices output file")
parser.add_argument("--eout", help="edge output file")

args = parser.parse_args()

if args.cat:
	cat_title = args.cat
else:
	cat_title = "Category:Computer_security"

if args.depth >= 0:
	depth = args.depth
else:
	depth = 3
if args.vout:
	vout = True
	vfile = args.vout
else:
	vout = False
if args.eout:
	eout = True
	efile = args.eout
else:
	eout = False

	
	
starttm = time.time()
graphd = defaultdict(list)
baseurl = "https://en.wikipedia.org/w/api.php?"
fmt = "format=json&"
act = "action=query&"
lst = "list=categorymembers&"
nms = "cmnamespace=14&"
lim = "cmlimit=100&"


def get_data(url_string):

	try:
		print("request url data - {0}".format(time.time() - starttm))
		url = requests.get(url_string) 
		print("save data - {0}".format(time.time() - starttm))
		data = url.json()
	except UnicodeEncodeError as e:
		error = e
		print(error)
		print(url_string)

	return data
	
def init_curl():

	c = pycurl.Curl()

	return c
	
def close_curl(c):

	c.close()
	
def get_data_curl(url_string, c):
	
	data = BytesIO()
	#c = pycurl.Curl()
	c.setopt(c.URL, url_string.encode('UTF-8'))
	c.setopt(c.WRITEFUNCTION, data.write)
	c.perform()
	#c.close()
	dtext = data.getvalue().decode('UTF-8')
	jdata = json.loads(dtext)
	data.close()
	
	return jdata

def build_rel(top_cat, c):

	print("start build rel - {0}".format(time.time() - starttm))
	url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20")
	cont = True
	while cont:

		print("get data - {0}".format(time.time() - starttm))
		in_data = get_data_curl(url_string, c)

		print("build cat list - {0}".format(time.time() - starttm))
		cat_list = in_data["query"]["categorymembers"]
		if cat_list != []:
			print("populate graphd - {0}".format(time.time() - starttm))
			for i in cat_list:
				print("append graphd - {0}".format(time.time() - starttm))
				graphd[top_cat].append(i['title'])	
				#print(i['title'])
		if "continue" in in_data:
			print("continue request - {0}".format(time.time() - starttm))
			url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20") + "&cmcontinue=" + in_data["continue"]["cmcontinue"] 
		else:
			print("done build rel - {0}".format(time.time() - starttm))
			cont = False

def build_rel_rec(top_cat, c, depth):

	print("start build rel - {0}".format(time.time() - starttm))
	url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20")
	cont = True
	while cont:

		print("get data - {0}".format(time.time() - starttm))
		in_data = get_data_curl(url_string, c)

		print("build cat list - {0}".format(time.time() - starttm))
		cat_list = in_data["query"]["categorymembers"]
		if cat_list != []:
			print("populate graphd - {0}".format(time.time() - starttm))
			for i in cat_list:
				print("append graphd - {0}".format(time.time() - starttm))
				if i['title'] not in graphd[top_cat]:
					graphd[top_cat].append(i['title'])
				print("Category: {0} SubCat: {1} Depth: {2}".format(top_cat, i['title'], depth))
				
				if depth > 0:
					build_rel_rec(i['title'], c, depth - 1)
					# else:
						# print("Category depth exhausted - {0} - {1}".format(i['title'],depth)) 
						# graphd[i['title']]

						#print(i['title'])
		# else:
			# print("Category with empty set - {0}".format(top_cat))
			# if top_cat not in graphd:
				# graphd[top_cat]

				
		if "continue" in in_data:
			print("continue request - {0}".format(time.time() - starttm))
			url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20") + "&cmcontinue=" + in_data["continue"]["cmcontinue"] 
		else:
			print("done build rel - {0}".format(time.time() - starttm))
			cont = False			
			
			
c = init_curl()


print("Initial - {0}".format(time.time() - starttm))

build_rel_rec(cat_title, c, depth)
print("build rel - {0}".format(time.time() - starttm))
print("Level 0 - {0}".format(time.time() - starttm))

# if depth >= 1:
	# for i in graphd[cat_title]:
		# print("Level 1 - {0} - {1}".format(i,time.time() - starttm))
		# build_rel(i, c)
		# print("build rel - {0} - {1}".format(i,time.time() - starttm))
		# if depth >= 2:
			# for j in graphd[i]:
				# print("Level 2 - {0} - {1}".format(j,time.time() - starttm))
				# if j not in graphd:
					# build_rel(j, c)
					# print("build rel - {0} - {1}".format(j,time.time() - starttm))
					# if depth >= 3:
						# for k in graphd[j]:
							# print("Level 3 - {0} - {1}".format(k,time.time() - starttm))
							# if k not in graphd:
								# build_rel(k, c)
								# print("build rel - {0} - {1}".format(k,time.time() - starttm))

close_curl(c)
								
print("graphd complete - {0}".format(time.time() - starttm))


for l in sorted(graphd.values()):
	for v in l:
		if v not in graphd:
			graphd[v]

#print("graphd empty keys - {0}".format(time.time() - starttm))

if args.vcount:
	print("Vertex Count: {0}".format(len(graphd.keys())))

if args.vlist:
	for i in sorted(graphd.keys()):
		print(i)

if args.ecount:
	ec = 0
	for i in sorted(graphd.keys()):
		for k in sorted(graphd[i]):
			ec += 1
	print("Edge Count: {0}".format(ec))

if args.elist:
	for i in sorted(graphd.keys()):
		for k in sorted(graphd[i]):
			print("{0} -> {1}".format(i, k))
			
if vout:
	with open(vfile, "w") as outfile:
		for i in sorted(graphd.keys()):
			outfile.write(i + "\n")
			
if eout:
	with open(efile, "w") as outfile:
		for i in sorted(graphd.keys()):
			for k in sorted(graphd[i]):
				outfile.write(i + "\t" + k + "\n")
				

print("All Done - {0}".format(time.time() - starttm))
	
