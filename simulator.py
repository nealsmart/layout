import networkx as nx

#The player unit, the entity that joins a team and moves around the map
class Unit:
    def __init__(self, team, startPosition, graph):
        self.team = team
        self.position = startPosition
        self.nextPosition = None
        self.counter = 0
        self.defending = False
        self.path = []
        self.graph = graph
        self.rotate = 1
        self.goal = -1
    
	#give the unit a new goal node to begin moving to
    def setGoal(self, goalPosition):
        self.goal = goalPosition
        self.path = nx.dijkstra_path(self.graph, self.position, self.goal)
        self.counter = 0
        self.path.pop(0)
        #if self.path:
#            print(self.path)
        if len(self.path)>0:
            self.nextPosition = self.path.pop(0)
        else:
            self.nextPosition = self.position
#            print(self.position, self.nextPosition)
        if self.position != self.nextPosition:
            self.counter = self.graph[self.position][self.nextPosition]['weight']
    
    def doObjective(self):
        if self.position == self.goal:
            self.defending = True
            print('goal is reached')
        else:
            self.defending = False
            self.move()
    #Fired every cycle, make the unit move if it's moving        
    def move(self):
        if self.counter > 0:
#            print(' ',self.counter)
            self.counter -= 1
        else:
#            print('moving to next node: ',self.nextPosition)
            self.position = self.nextPosition
            if self.path:
                self.nextPosition = self.path.pop(0)
                self.counter = self.graph[self.position][self.nextPosition]['weight']
    
    def isDefending(self):
        return self.defending
    
    def isAtGoal(self):
        #print(self.goal, self.position)
        if self.goal == self.position:
            return True
        else:
            return False
    
    def getNodes(self):
#        print(self.position, self.nextPosition)
        return (self.position, self.nextPosition)
    
    def getPosition(self):
        return self.position
    def getGoal(self):
        return self.goal
    def getCounter(self):
        return self.counter
    def getNextPosition(self):
        return self.nextPosition
    def getPath(self):
        return self.path
    def getRotate(self):
        return self.rotate
    def setRotate(self, rotate):
        self.rotate = rotate
		
import random
random.seed()

#make a standard 5v5 team
def makeTeams(graph, info, ctUnits, tUnits):
    ctUnits = []
    tUnits = []
    for i in range(5):
        ctUnits.append(Unit('ct',info['ctspawn'],graph))
    for i in range(5):
        tUnits.append(Unit('t',info['tspawn'],graph))
    return (ctUnits, tUnits)

#Set CT goals to holding positions, set T goal to a bombsite
def assignTargets(graph, info, ctUnits, tUnits):
    holdPositions = info['holdnodes']
    i=0
    for ct in ctUnits:
        ct.setGoal(holdPositions[i%len(holdPositions)])
        i += 1
#    rand = random.randint(0,len(holdPositions))
#    for t in tUnits:
#        t.setGoal(holdPositions[rand])
    rand = random.randint(0,1)
    if rand == 0:
        goal = info['a']
    else:
        goal = info['b']
    for t in tUnits:
        t.setGoal(goal)
    return goal

#See if two units are in range of each other across the board
def checkConflict(ctUnits, tUnits):
    for ct in ctUnits:
        for t in tUnits:
            if set(ct.getNodes()).intersection(t.getNodes()):
                #print('ct at',ct.getNodes(),'fighting t at',t.getNodes())
                result = getLoser(ct, t)
                try:
                    ctUnits.remove(result)
                    #print('ct loss')
                    break
                except:
                    temp = 0
                try:
                    tUnits.remove(result)
                    #print('t loss')
                    break
                except:
                    temp = 0

#Generate loser based on whether or not a unit is defending
def getLoser(A, B):
    #defense gets 60-40 advantage
    #random.seed()
    rand = random.randint(0,9)
    #print(rand, A.isAtGoal(), B.isAtGoal())
    if A.isAtGoal():
        if(rand>4):
            return A
        else:
            return B
    elif B.isAtGoal():
        if(rand>4):
            return B
        else:
            return A
    else:
        if(rand<5):
            return A
        else:
            return B

#Move game state forward, end game if one team eliminated			
def increment(goal, ctUnits, tUnits):
    #if a ct dies all change ct goal to likely bombsite
    try:
        if ctUnits[0].getRotate() == 1:
            if len(ctUnits) < 5:
                for ct in ctUnits:
                    ct.setGoal(goal)
                    ct.setRotate(0)
    except:
        temp = 0
    #check if either team is eliminated
    if len(tUnits) == 0:
        return 0
    if len(ctUnits) == 0:
        return 1
    #make all units move
    #print('moving units')
    for ct in ctUnits:
        ct.move()
    for t in tUnits:
        t.move()
    checkConflict(ctUnits, tUnits)
    return -1
    
        
#global ctUnits
#global tUnits
#Simulate game, end in tie after 100 cycles
def runTest(graph, info, ctUnits, tUnits):
    #rotate = 1
    (ctUnits, tUnits) = makeTeams(graph, info, ctUnits, tUnits)
    goal = assignTargets(graph, info, ctUnits, tUnits)
    flag = -1
    limit = 0
    while(flag < 0 and limit < 100):
        ctPos = []
        ctGoal = []
        tPos = []
        tGoal = []
        for ct in ctUnits:
            ctPos.append(ct.getPosition())
            ctGoal.append(ct.getGoal())
        for t in tUnits:
            tPos.append(t.getPosition())
            tGoal.append(t.getGoal())
        #print('CT Position: ', ctPos, ', Goal:', ctGoal)
        #print('T Position: ', tPos, ', Goal:', tGoal)
        #print(ctUnits[1].getPosition(), ctUnits[1].getNextPosition(), ctUnits[1].getGoal(), ctUnits[1].getCounter(), ctUnits[1].getPath())
        flag = increment(goal, ctUnits, tUnits)
        limit += 1
    if(flag == 1):
        return 't win'
    elif(flag == 0):
        return 'ct win'
    else:
        return 'everybody loses'
		
		
#runTest(G)
#Repeat game 'count' times, return win rate for CT
def getResults(count, graph, info, ctUnits, tUnits):
    ct = 0
    t = 0
    tie = 0
    for i in range(count):
        result = runTest(graph, info, ctUnits, tUnits)
        if result == 'ct win':
            ct += 1
        elif result == 't win':
            t += 1
        else:
            tie += 1
    return 'CT win rate: '+ str(ct/(ct+t)*100)+'%' 
