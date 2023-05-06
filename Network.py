import sys
import networkx as nx
import random as rd

#output to networkdata.txt
sys.stdout = open('networkdata.txt', 'w')

class Packet:
    def __init__(self, routerID, edgeID = [-1,-1], edgeD = 0):
        self.routerID = routerID
        self.edgeID = edgeID
        self.edgeD = edgeD

# Create the network graph
G = nx.Graph()
edgeList = [[1,2], [2,3], [3,4], [4,5], [5,6], [6,19], [18,19],
            [7,8], [8,9], [9,10], [10,11], [11,12], [12,19], 
            [13,14], [14,15], [15,16], [16,17], [17,18], [19,20]]

for i in range(1, 21):
    G.add_node(i, prob=.8, id=i, packet=Packet(i, [i, i], 1), sendChance=.0008, distance=0, rate_limit=10, sent_packets=0, user_type="normal", activity_level=1)

# Set the attributes for the DDoS attack nodes
num_attackers = rd.randint(2, 5)
ddos_nodes = rd.sample(range(1, 21), num_attackers)
for node in ddos_nodes:
    G.nodes[node]['sendChance'] = 0.8
    G.nodes[node]['rate_limit'] = 20
    G.nodes[node]['user_type'] = "attacker"
    G.nodes[node]['activity_level'] = 10

# Function to detect congestion in the network
def detect_congestion(G, threshold_factor=5):
    avg_edgeD = sum([G.nodes[node]['packet'].edgeD for node in G.nodes]) / len(G.nodes)
    return avg_edgeD > threshold_factor * G.nodes[1]['packet'].edgeD

# Function to prevent the DDoS attack
def prevent_ddos(G, ddos_nodes):
    for node in ddos_nodes:
        G.nodes[node]['rate_limit'] = 1
        G.nodes[node]['activity_level'] = 1

# Simulate network traffic
totalPacketsSent = 0
attack_detected = False
for _ in range(1000):
    # Send packets for each node based on their sendChance and rate_limit
    for node in G.nodes:
        if rd.random() < G.nodes[node]['sendChance'] and G.nodes[node]['sent_packets'] < G.nodes[node]['rate_limit']:
            totalPacketsSent += 1
            G.nodes[node]['sent_packets'] += 1
            # Simulate packet sending logic here

    # Detect congestion and prevent DDoS attack if detected
    if not attack_detected and detect_congestion(G):
        print("Congestion detected! Preventing DDoS attack.")
        prevent_ddos(G, ddos_nodes)
        attack_detected = True
        # Log details of the detected attack
        print("Attack details:")
        for node in ddos_nodes:
            print(" - Attacker:", node, "Activity level:", G.nodes[node]['activity_level'])

    # Reset sent_packets counter for the next simulation step
    for node in G.nodes:
        G.nodes[node]['sent_packets'] = 0

print("Total packets sent:", totalPacketsSent)

# Print the final state of the network after the simulation
print("Final state of the network:")
for node in G.nodes:
    print("Node", node, "user_type:", G.nodes[node]['user_type'], "activity_level:", G.nodes[node]['activity_level'])

# Close the output file
sys.stdout.close()
