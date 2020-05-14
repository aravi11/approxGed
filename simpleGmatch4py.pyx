# Gmatch4py use networkx graph 
import networkx as nx 
# import the GED using the munkres algorithm
import gmatch4py as gm

g1=nx.complete_bipartite_graph(5,4)
g2=nx.complete_bipartite_graph(6,4)

ged=gm.GraphEditDistance(1,1,1,1) # all edit costs are equal to 1

result=ged.compare([g1,g2],None)

print(ged.distance(result))
print("Hello")
