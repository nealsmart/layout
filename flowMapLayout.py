import networkx as nx
import pygraphviz as pg
import random as rand
import math
import copy
import itertools as it
from networkx.algorithms import bipartite

example = [1, 2, 3, 2, 3, 3]
cache = [4, 2, 2, 4, 4, 4, 2, 3, 3, 3, 2, 2, 3, 2, 1, 3, 2, 4, 2, 2]
dust2 = [2, 3, 2, 2, 3, 3, 3, 2, 2, 2, 2, 3, 2, 2, 3, 2, 2, 2, 4, 2, 1, 3]
inferno = [1, 2, 4, 2, 3, 2, 3, 2, 2, 3, 3, 2, 3, 3, 3, 3, 3, 2, 3, 3, 3, 4, 4, 3, 3, 3]
maxlen = 5
G = []

#waiting function for demo
def wait():
	input("Press Enter to continue...")

#demo function, display image at each stage	
def step(input):
	info = {}
	G = newGraph(input)
	drawGraph(G, info, 'jraf')
	wait()	
	randWeight(G)
	drawGraph(G, info, 'jraf')
	wait()
	info['tspawn'] = getTSpawn(G)
	drawGraph(G, info, 'jraf')
	wait()
	info['ctspawn'] = getCTSpawn(G,info)
	drawGraph(G, info, 'jraf')
	wait()
	getAreaControl(G, info)
	drawGraph(G, info, 'jraf')
	wait()
	pruneNodes(G, info)
	drawGraph(G, info, 'jraf')
	wait()
	getBombsites(G, info)
	drawGraph(G, info, 'jraf')
	wait()
	getHoldPaths(G, info)	
	drawGraph(G, info, 'jraf')	
	wait()

#make graph based on input indegree array
def makeGraph(input):
	info = {}
	G = newGraph(input)
	randWeight(G)
	info['tspawn'] = getTSpawn(G)
	info['ctspawn'] = getCTSpawn(G,info)
	getAreaControl(G, info)
	pruneNodes(G, info)
	getBombsites(G, info)
	getHoldPaths(G, info)	
	drawGraph(G, info, 'jraf')
	return G, info

#generate random graphs until we get a planar one
def newGraph(input):
	for x in range(20):
		G = nx.random_degree_sequence_graph(input)
		if nx.is_connected(G) and is_planar(G):
			return G
	return -1

def is_planar(G):
    """
    function checks if graph G has K(5) or K(3,3) as minors,
    returns True /False on planarity and nodes of "bad_minor"
    """
    result=True
    bad_minor=[]
    n=len(G.nodes())
    if n>5:
        for subnodes in it.combinations(G.nodes(),6):
            subG=G.subgraph(subnodes)
            if bipartite.is_bipartite(G):# check if the graph G has a subgraph K(3,3)
                X, Y = bipartite.sets(G)
                if len(X)==3:
                    result=False
                    bad_minor=subnodes
    if n>4 and result:
        for subnodes in it.combinations(G.nodes(),5):
            subG=G.subgraph(subnodes)
            if len(subG.edges())==10:# check if the graph G has a subgraph K(5)
                result=False
                bad_minor=subnodes
    return result #add ,bad_minor if want the offending subnodes (for deletion?)

#give each edge a weight between 1 and maxlen	
def randWeight(graph):	
	for edge in graph.edges():
		graph[edge[0]][edge[1]]['weight'] = rand.randint(1,maxlen)

#prune excess routes		
def pruneNodes(graph, info):
	templist = sorted(info['nodes'], key=lambda k: k['time'], reverse=True)
	tempnodes = sorted(info['nodes'], key=lambda k: k['index'])
	for item in templist:
		index = item['index']
		team = item['team']
		time = item['time']
		neighbors = graph.neighbors(index)
		prune = 1
		for value in neighbors:
			node = tempnodes[value]
			if team == 't':
				if time < node['time'] or node['team'] != 't':
					prune = 0
			elif team == 'ct':
				if time < node['time'] or node['team'] != 'ct':
					prune = 0
			elif team == 'n':
				prune = 0
		if prune == 1:
			#print(item)
			info['nodes'].remove(item)
			if index in info['ct']: info['ct'].remove(index)
			if index in info['t']: info['t'].remove(index)				
			graph.remove_node(index)
		
def randWeightOld(graph): 
	for edge in graph.edges():
		temp = rand.randint(1,8)
		edge.attr['weight'] = temp
		#edge.attr['label'] = temp
		edge.attr['len'] = math.ceil(temp/4.0)

#make Tspawn node with indegree 1		
def getTSpawn(graph): #choose a node with indegree of 1
	for node in range(len(graph.nodes())):
		if graph.degree(node) == 1:
			return node
	return -1

#find node furthest from tspawn, make it ctspawn
def getCTSpawn(graph, info): #find point on 'other end' of graph
	paths = nx.single_source_dijkstra(graph, info['tspawn'])
	max = 0
	lengths = paths[0]
	try:
		for path in range(len(lengths)):
			if lengths[path] > lengths[max]:
				max = path
	except:
		return -1
	return max
	#tree = nx.bfs_tree(graph, tspawn)
	#nodes = nx.topological_sort(tree)
	#return nodes[len(nodes)-1]

#figure who gets to which node first	
def getAreaControl(graph, info):
	ct = info['ctspawn']
	t = info['tspawn']
	info['ct'] = []
	info['t'] = []
	info['n'] = []
	info['nodes'] = []
	for node in graph.nodes():
		ctlen = nx.dijkstra_path_length(graph, node, ct)
		tlen = nx.dijkstra_path_length(graph, node, t)
		if(tlen < ctlen):
			info['nodes'].append({'team': 't', 'time': tlen, 'index': node})
			info['t'].append(node)
			graph.node[node]['team'] = 't'
			graph.node[node]['time'] = tlen
		elif(ctlen < tlen):
			info['nodes'].append({'team': 'ct', 'time': ctlen, 'index': node})
			info['ct'].append(node)
			graph.node[node]['team'] = 'ct'
			graph.node[node]['time'] = tlen			
		else:
			info['nodes'].append({'team': 'n', 'time': tlen, 'index': node})
			info['n'].append(node)
			graph.node[node]['team'] = 'n'
			graph.node[node]['time'] = tlen			

#Find subgraph of ct controlled area that contains both bombsites and has least outgoing connections
#Pretty sure this is an n! algorithm			
def getHoldPaths(graph, info): #subgraph with bombsites within CT area with least amount of outgoing
	sites = (info['a'], info['b'])
	base = tuple(x for x in info['ct'] if x not in sites)
	min = 99999
	info['holdcount'] = min
	info['holdpaths'] = []
	info['holdarea'] = []
	info['holdnodes'] = []
	for count in range(len(base)):
		combo = list(it.combinations(base, len(base)-count))
		for nodes in combo:			
			bound = nx.edge_boundary(graph, sites+nodes)
			#print(len(bound), sites+nodes)
			if len(bound)<min:
				min = len(bound)
				info['holdcount'] = min
				info['holdpaths'] = bound
				info['holdarea'] = sites+nodes
	for paths in info['holdpaths']:
		if graph.node[paths[0]]['team'] == 'ct':
			info['holdnodes'].append(paths[0])
			graph.node[paths[0]]['hold'] = True
		else:
			info['holdnodes'].append(paths[1])
			graph.node[paths[1]]['hold'] = True

#find two bombsites that have two 10-13 second routes inbetween within the ct area
def getBombsites(graph, info):
	info['rotate'] = 0
	info['route1'] = []
	info['route2'] = []
	for A in info['ct']:
		for B in info['ct']:
			min = nx.dijkstra_path_length(graph, A, B) #find shortest path between A and B
			if min <= 13 and min >= 10:	#see if they pass the max/min check of route
				info['a'] = A
				info['b'] = B
				info['rotate'] = 1
				path = nx.dijkstra_path(graph, A, B) #get min path to remove
				info['route1'] = path
				H = copy.deepcopy(graph)
				H.remove_edge(path[0],path[1])
				H.remove_edge(path[len(path)-2], path[len(path)-1])
				try:
					min2 = nx.dijkstra_path_length(H, A, B)
					if min2 <= 15 and min2 >= 10:	#see if they pass the max/min check of route
						info['route2'] = nx.dijkstra_path(H, A, B)
						info['rotate'] = 2
						return #we found at least two, return
				except:
					pass
#graph coloring
def colorRoute(graph, route):
	for i in range(len(route)-1):
		graph[route[i]][route[i+1]]['color']='#866DA6'

#graph coloring		
def colorHold(graph, info):
	#try:
	for edge in info['holdpaths']:
		try:
			graph.get_edge(edge[0], edge[1]).attr.update(style='dashed', color='#8A050C', penwidth='2')
		except:
			graph.get_edge(edge[1], edge[0]).attr.update(style='dashed', color='#8A050C', penwidth='2')
	#for node in info['holdarea']:
	#	graph.get_node(node).attr['style']='dashed'
	#except:
	#	pass
def holdRank(score):
	return {5: 1, 4: 2, 3: 2, 2: 1}.get(score, 0)
def rotScore(score):
	return {1: 1, 0: 0}.get(score, 2)	
def score(graph, info):
	total = rotScore(info['rotate'])+holdRank(info['holdcount'])
	rank = {4: 'Great', 3: 'Good', 2: 'Okay', 1: 'Bad', 0: 'Terrible'}
	color = {4: '#245FA0', 3: '#4BD021', 2: '#F6EF27', 1: '#F6AF27', 0: '#F62C27'}
	graph.add_node('score', label=str(total)+'/4 '+rank[total], style='filled', fillcolor=color[total], fontsize=20)  
	
	
		
def defaultGraph(graph):
	for edge in graph.edges():
		edge.attr['dir'] = 'none'
		edge.attr['penwidth'] = 1.5
#process graph for generating image		
def drawGraph(graph, info, file):
	try:		
		colorRoute(graph, info['route1'])
		colorRoute(graph, info['route2'])	
	except:
		pass
	A = nx.to_agraph(graph)
	defaultGraph(A)	
	try:
		for edge in A.edges():
			if edge.attr['weight']:
				temp = int(edge.attr['weight'])
				edge.attr['label'] = temp
				edge.attr['len'] = math.ceil(temp/(maxlen/2.0))
	except:
		pass
	try:
		for node in info['nodes']:
			temp = A.get_node(node['index'])
			temp.attr['style'] = 'filled'
			temp.attr['label'] = node['time'] #replace labels to show time taken
			if node['team'] == 't':
				temp.attr['fillcolor'] = '#F0DC82'
			elif node['team'] == 'ct':
				temp.attr['fillcolor'] = '#C4D8E2'
	except:
		pass
	try:
		t = A.get_node(info['tspawn'])
		t.attr['label'] = 'T Spawn'
		t.attr['style'] = 'filled'
		t.attr['fillcolor'] = '#DAA520'
		#A.graph_attr['splines']='spline'
	except:
		pass
	try:
		ct = A.get_node(info['ctspawn'])
		ct.attr['label'] = 'CT Spawn'
		ct.attr['style'] = 'filled'
		ct.attr['fillcolor'] = '#1560BD'
	except:
		pass
	try:
		temp = A.get_node(info['a'])
		temp.attr['fillcolor']= '#DC93AF'
	except:
		pass
	try:
		temp = A.get_node(info['b'])
		temp.attr['fillcolor'] = '#DC93AF'
	except:
		pass
	try:
		colorHold(A, info)
	except:
		pass
	try:
		score(A, info)
	except:
		pass
	A.layout()
	A.draw(file+'.png')
