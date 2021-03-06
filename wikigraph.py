import time, argparse, requests, json
from collections import defaultdict

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

def build_rel(top_cat):

	print("start build rel - {0}".format(time.time() - starttm))
	url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20")
	cont = True
	while cont:

		print("get data - {0}".format(time.time() - starttm))
		in_data = get_data(url_string)

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



print("Initial - {0}".format(time.time() - starttm))

build_rel(cat_title)
print("build rel - {0}".format(time.time() - starttm))
print("Level 0 - {0}".format(time.time() - starttm))

if depth >= 1:
	for i in graphd[cat_title]:
		print("Level 1 - {0} - {1}".format(i,time.time() - starttm))
		build_rel(i)
		print("build rel - {0} - {1}".format(i,time.time() - starttm))
		if depth >= 2:
			for j in graphd[i]:
				print("Level 2 - {0} - {1}".format(j,time.time() - starttm))
				if j not in graphd:
					build_rel(j)
					print("build rel - {0} - {1}".format(j,time.time() - starttm))
					if depth >= 3:
						for k in graphd[j]:
							print("Level 3 - {0} - {1}".format(k,time.time() - starttm))
							if k not in graphd:
								build_rel(k)
								print("build rel - {0} - {1}".format(k,time.time() - starttm))
print("graphd complete - {0}".format(time.time() - starttm))

for l in sorted(graphd.values()):
	for v in l:
		if v not in graphd:
			graphd[v]

print("graphd empty keys - {0}".format(time.time() - starttm))

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
	
