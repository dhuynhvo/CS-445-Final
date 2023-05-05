import networkx as nx
import random as rd

class Packet:
    def __init__(self, routerID, edgeID = [-1,-1], edgeD = 0): # for the edge ID, left is start and right is end respective to victim router

        self.routerID = routerID
        self.edgeID = edgeID
        self.edgeD = edgeD

class Tree:
    def __init__(self, edge = [], distance = 0):

        self.recPath = []
        self.combinedList = []
        self.victim = G.Node

    def combineLists(self, listOfEdge, listOfDistance):
        for i in range(0, len(listOfEdge)):
            self.combinedList[i] = [listOfEdge[i], listOfDistance[i]]
            

    


G = nx.Graph()
recPath = nx.Graph()
edgeList = [[1,2], [2,3], [3,4], [4,5], [5,6], [6,19], [18,19],
            [7,8], [8,9], [9,10], [10,11], [11,12], [12,19], 
            [13,14], [14,15], [15,16], [16,17], [17,18], [19,20]]

for i in range (1,21):
    G.add_node(i, prob = .8, id = i, packet = Packet(i, [i,i], 1), sendChance = .0008, distance = 0)

emptyList = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
totalPacketsSent = 0

attrs = {20: {"markCount": emptyList, "edgeList": [], "edgeDList": []}}

nx.set_node_attributes(G, attrs)
G.add_edges_from(edgeList)
attacker = rd.randint(1,19)
G.nodes[attacker]['sendChance'] = .8
attacker2 = rd.randint(1,19)
G.nodes[attacker2]['sendChance'] = .8

def countPacket(nodeID):
    startID = nodeID
    G.nodes[20]['markCount'][startID] += 1

def countEdgePacket(node):
    G.nodes[20]['edgeList'].append(node['packet'].edgeID)
    G.nodes[20]['edgeDList'].append(node['packet'].edgeD)

def sendPacket(node, graph):

    sendTo = 0
    nl = [n for n in graph.neighbors(node['id'])]
    length = len(nl)
    for i in range(length):
        if sendTo < nl[i]:
            sendTo = nl[i]
    
    if node['id'] != 20:
        #print("Hop To: ", sendTo)
        G.nodes[sendTo]['packet'] = node['packet']

        if rd.random() < G.nodes[sendTo]['prob']:
            G.nodes[sendTo]['packet'] = Packet(G.nodes[sendTo]['id'])
        node['packet'] = Packet(node['id'])
        sendPacket(G.nodes[sendTo], G)

    else:
        #print(node['packet'].routerID)
        countPacket(node['packet'].routerID)
        graph.nodes[20]['packet'] = Packet(20)

def sendEdgePacket(node, graph):
    sendTo = 1
    nl = [n for n in graph.neighbors(node['id'])]
    length = len(nl)
    for i in range(length):
        if sendTo < nl[i]:
            sendTo = nl[i]
    
    if node['id'] != 20:
        #print("Hop To: ", sendTo)
        graph.nodes[sendTo]['packet'] = node['packet']

        if graph.nodes[sendTo]['prob'] > rd.random():
            graph.nodes[sendTo]['packet'].edgeID[0] = graph.nodes[sendTo]['id']
            graph.nodes[sendTo]['packet'].edgeID[1] = 0
            graph.nodes[sendTo]['packet'].edgeD = 0

            node['packet'] = Packet(node['id'], [node['id'], node['id']], 1)

        else:
            if graph.nodes[sendTo]['packet'].edgeD == 0:
                graph.nodes[sendTo]['packet'].edgeID[1] = graph.nodes[sendTo]['id']
            graph.nodes[sendTo]['packet'].edgeD += 1
            node['packet'] = Packet(node['id'], [node['id'], node['id']], 0)

        sendEdgePacket(G.nodes[sendTo], graph)

    else:
            countEdgePacket(node)
            graph.nodes[20]['packet'] = Packet(20, [20, 20], 0)


def nodeSampling(totalPacks, marksArray, normProb, offset):
    mls = []
    length = dict(nx.all_pairs_shortest_path_length(G))
    for i in range(1,20):
        G.nodes[i]['distance'] = length[20][i]
        if marksArray[i]/totalPacks > (((1 - normProb) ** (G.nodes[i]['distance'])) * normProb) + offset:
            mls.append(i)

    return mls

def edgeSampling(pathG ,edgeL, edgeDL, totalPacks, normProb, offset):

    tupleList = []
    suspiciousEdges = [0] * 21
    mls = []
    for i in range(0,len(edgeL)):
    #print (i, ": ", G.nodes[20]['edgeList'][i])
    #print (i, ": ", G.nodes[20]['edgeDList'][i])

        #short = nx.shortest_path_length(G, edgeL[i][0], 20)
        if (edgeDL[i] == 0):
            pathG.add_edge(edgeL[i][0], 20, weight=0)
            #print("Found weird distance from packet: ", i, " : ", G.nodes[20]['edgeList'][i], "Distance: ", G.nodes[20]['edgeDList'][i])

        else:
            pathG.add_edge(edgeL[i][0], edgeL[i][1], weight=edgeDL[i])
            #insert edge (w.start,w.end,w.distance) into G

    for u, v, a in pathG.edges(data=True):
        #if pathG.has_edge(u, 20):

        if pathG.has_edge(u, 20):
            eShort = nx.shortest_path_length(pathG, u, 20)
        
        else:
            eShort = 0

        if eShort == a["weight"]:
            #print("Found weird distance from packet: ", i, " : ", G.nodes[20]['edgeList'][i], "Distance: ", G.nodes[20]['edgeDList'][i])
            #print(a, short)
            #pathG.remove_edge(u, v)
            tupleList.append((u,v))

    for i in range(0,len(G.nodes[20]['edgeList'])):
    #print (i, ": ", G.nodes[20]['edgeList'][i])
    #print (i, ": ", G.nodes[20]['edgeDList'][i])

        short = nx.shortest_path_length(G, G.nodes[20]['edgeList'][i][0], 20)
        if (short < G.nodes[20]['edgeDList'][i]):
            #print("Found weird distance from packet: ", i, " : ", G.nodes[20]['edgeList'][i], "Distance: ", G.nodes[20]['edgeDList'][i])
            suspiciousEdges[G.nodes[20]['edgeList'][i][0]] += 1

    for i in range(1,21):
        if suspiciousEdges[i] > 20 * offset:
            mls.append(i)

    return mls



###############################################################################################################################



testRange = 3000

print("Attacker1 was: ", attacker)
print("Attacker2 was: ", attacker2)


for i in range(0,testRange):
        for i in range(1,21):
            chance = rd.random()
            if chance < G.nodes[i]['sendChance']:
                totalPacketsSent += 1
                sendPacket(G.nodes[i], G)

nodeSuspects = nodeSampling(totalPacketsSent, G.nodes[20]['markCount'], G.nodes[20]['prob'], 0)
print("Node Sampling Suspects: ", nodeSuspects)
print("Total Packets Sent: ", totalPacketsSent)
totalPacketsSent = 0

for i in range(0,testRange):
        for i in range(1,20):
            chance = rd.random()
            if chance < G.nodes[i]['sendChance']:
                totalPacketsSent += 1
                sendEdgePacket(G.nodes[i], G)

edgeSuspects = edgeSampling(recPath, G.nodes[20]['edgeList'], G.nodes[20]['edgeDList'], totalPacketsSent, G.nodes[20]['prob'], 3)
print("Edge Sampling Suspects: ", edgeSuspects)
print("Total Packets Sent: ", totalPacketsSent)
totalPacketsSent = 0
