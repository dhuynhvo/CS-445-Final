#Authors: Grant Davis and Dan Huynhvo
#CS 445: Internet Security Final Project
#Network Congestion Simulation

import sys
import networkx as nx
import random as rd
from datetime import datetime
import matplotlib.pyplot as plt
import os

# Output to networkdata.txt
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
    G.add_node(i, prob=.8, id=i, packet=Packet(i, [i, i], 1), sendChance=.0008, distance=0, rate_limit=10, 
               sent_packets=0, user_type="normal", activity_level=1, blacklisted=False)

# Add edges to the graph
for edge in edgeList:
    G.add_edge(edge[0], edge[1], delay=1)
    
# Set the attributes for the DDoS attack nodes
num_attackers = rd.randint(2, 5)
ddos_nodes = rd.sample(range(1, 20), num_attackers)
for node in ddos_nodes:
    G.nodes[node]['sendChance'] = 0.8
    G.nodes[node]['rate_limit'] = 20
    G.nodes[node]['user_type'] = "attacker"
    G.nodes[node]['activity_level'] = 10

# Function to calculate average edge delay in the network
def average_edge_delay(G):
    total_delay = 0
    for edge in G.edges:
        total_delay += G.edges[edge]['delay']
    return total_delay / len(G.edges)

# Function to detect congestion in the network
def detect_congestion(G, threshold_factor=5):
    avg_edgeD = average_edge_delay(G)
    return avg_edgeD > threshold_factor

# Function to prevent the DDoS attack
def prevent_ddos(G, ddos_nodes):
    for node in ddos_nodes:
        G.nodes[node]['rate_limit'] = 1
        G.nodes[node]['activity_level'] = 1
        G.nodes[node]['sendChance'] = G.nodes[node]['sendChance'] * G.nodes[node]['activity_level']

# Function to blacklist known malicious actors
def blacklistAttackers(G, ddos_nodes):
    for node in ddos_nodes:
        if G.nodes[node]['user_type'] == "attacker":
            G.nodes[node]['blacklisted'] = True

# Function to allow edges between any node neighboring and behind a malicious actor to the target router 20
def createEdgeToTarget(G):
    for node in G.nodes:
        neighbors = list(G.neighbors(node))
        for i in neighbors:
            if G.nodes[i]['blacklisted'] == True and G.nodes[node]['id'] < G.nodes[i]['id'] and G.nodes[node]['blacklisted'] == False:
                G.add_edge(node, 20, delay=1)

def save_network(G, title="Network Topology", filename="network_topology.png"):
    pos = nx.spring_layout(G, seed=42)
    node_colors = []
    
    for node in G.nodes():
        if G.nodes[node]['user_type'] == 'attacker' and G.nodes[node]['activity_level'] > 1:
            node_colors.append('red')
        elif G.nodes[node]['user_type'] == 'normal' and G.nodes[node]['activity_level'] > 1:
            node_colors.append('orange')
        else:
            node_colors.append('skyblue')
    
    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, font_size=12, font_weight="bold")
    labels = nx.get_edge_attributes(G, 'delay')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=12)
    plt.title(title)
    plt.savefig(filename)
    plt.close()

# Simulate network traffic
totalPacketsSent = 0
attack_detected = False
packets_by_user_type = {'normal': 0, 'attacker': 0}
steps_to_detect_attack = 0

for step in range(1000):
    # Send packets for each node based on their sendChance and rate_limit
    for node in G.nodes:
        if rd.random() < G.nodes[node]['sendChance'] and G.nodes[node]['sent_packets'] < G.nodes[node]['rate_limit']:
            totalPacketsSent += 1
            packets_by_user_type[G.nodes[node]['user_type']] += 1
            if(G.nodes[node]['blacklisted'] == False):
                G.nodes[node]['sent_packets'] += 1
            
            # Simulate packet sending logic and update edge delays
            neighbors = list(G.neighbors(node))
            target_node = rd.choice(neighbors)
            edge = (node, target_node) if G.has_edge(node, target_node) else (target_node, node)
            if(G.nodes[node]['blacklisted'] == False):
                G.edges[edge]['delay'] += G.nodes[node]['activity_level']
    
    # Detect congestion and prevent DDoS attack if detected
    if not attack_detected and detect_congestion(G):
        blacklistAttackers(G, ddos_nodes)
        createEdgeToTarget(G)
        steps_to_detect_attack = step
        attack_detected_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Congestion detected at step {step} ({attack_detected_time})! Preventing DDoS attack.")
        save_network(G, title=f"Network Topology at Congestion (Step {step})", filename="network_topology_congestion.png")
        prevent_ddos(G, ddos_nodes)
        attack_detected = True
        # Log details of the detected attack
        print("Attack details:")
        for node in ddos_nodes:
            print(f" - Attacker: {node}, Activity level: {G.nodes[node]['activity_level']}")

    # Reset sent_packets counter for the next simulation step
    for node in G.nodes:
        G.nodes[node]['sent_packets'] = 0

avg_edge_delay_before = average_edge_delay(G)
prevent_ddos(G, ddos_nodes)  # Apply DDoS mitigation
avg_edge_delay_after = average_edge_delay(G)

# Calculate the percentage of packets sent by attackers
percentage_attackers = (packets_by_user_type['attacker'] / totalPacketsSent) * 100

print(f"Total packets sent: {totalPacketsSent}")
print(f"Packets sent by normal users: {packets_by_user_type['normal']}")
print(f"Packets sent by attackers: {packets_by_user_type['attacker']}")
print(f"Number of nodes: {G.number_of_nodes()}, Number of edges: {G.number_of_edges()}")
print(f"Average edge delay before DDoS mitigation: {avg_edge_delay_before:.2f}")
print(f"Average edge delay after DDoS mitigation: {avg_edge_delay_after:.2f}")
print(f"Steps to detect DDoS attack: {steps_to_detect_attack}")
print(f"Percentage of packets sent by attackers: {percentage_attackers:.2f}%")

# Print the final state of the network after the simulation
print("Final state of the network:")
for node in G.nodes:
    print("Node", node, "user_type:", G.nodes[node]['user_type'], "activity_level:", G.nodes[node]['activity_level'])

# Close the output file
sys.stdout.close()
