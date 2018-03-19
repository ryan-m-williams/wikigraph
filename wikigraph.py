import argparse, requests, json
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--cat", "-C", help="top category")
parser.add_argument("--depth", "-D", help="walk depth", type=int, default=3)
parser.add_argument("--vcount", help="vertices count", action="store_true")
parser.add_argument("--vlist", help="vertices list", action="store_true")
parser.add_argument("--ecount", help="edge count", action="store_true")
parser.add_argument("--elist", help="edge list", action="store_true")
args = parser.parse_args()

if args.cat:
	cat_title = args.cat
else:
	cat_title = "Category:Computer_security"

if args.depth >= 0:
	depth = args.depth
else:
	depth = 3


graphd = defaultdict(list)
baseurl = "https://en.wikipedia.org/w/api.php?"
fmt = "format=json&"
act = "action=query&"
lst = "list=categorymembers&"
nms = "cmnamespace=14&"
lim = "cmlimit=100&"


def get_data(url_string):

	try:
		url = requests.get(url_string) 
		data = url.json()
	except UnicodeEncodeError as e:
		error = e
		print(error)
		print(url_string)

	return data

def build_rel(top_cat):

	url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20")
	cont = True
	while cont:

		in_data = get_data(url_string)

		cat_list = in_data["query"]["categorymembers"]
		if cat_list != []:
			for i in cat_list:
				graphd[top_cat].append(i['title'])	
				#print(i['title'])
		if "continue" in in_data:
			url_string = baseurl + fmt + act + lst + nms + lim + "cmtitle=" + top_cat.replace(" ","%20") + "&cmcontinue=" + in_data["continue"]["cmcontinue"] 
		else:
			cont = False





build_rel(cat_title)

if depth >= 1:
	for i in graphd[cat_title]:
		build_rel(i)
		if depth >= 2:
			for j in graphd[i]:
				if j not in graphd:
					build_rel(j)
					if depth >= 3:
						for k in graphd[j]:
							if k not in graphd:
								build_rel(k)


if args.vcount:
	print(len(graphd.keys()))
elif args.vlist:
	for i in graphd.keys():
		print(i)


