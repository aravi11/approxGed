
# import the GED using the munkres algorithm
import gmatch4py as gm
import networkx as nx 
import collections
import csv
import pickle
from collections import OrderedDict
import json
import concurrent.futures as cf
import time


iter = 0
def getFinishedStatus():
    iter +=1
    print('*******\t' + str(iter)+ "\t*******")


def getGraphDiff(files):

    dotFile_data_path = './DotFiles/'
    file1 = files.split(',')[0]
    file2 = files.split(',')[1]
    g1_name = file1.split('.')[0]  # gets the name of first dotFile without its extension
    g2_name = file2.split('.')[0]  # gets the name of second dotFile without its extension
    #print("\n Started pair:  "+ str(g1_name) + ', ' + str(g2_name))

    graph_1 = nx.drawing.nx_pydot.read_dot(str(dotFile_data_path) + str(file1))
    graph_2 = nx.drawing.nx_pydot.read_dot(str(dotFile_data_path) + str(file2))

    jsonData = getJsonData(graph_1, graph_2)
    dumpJson(jsonData, g1_name, g2_name)


    #print("\n >>>Finished pair:  "+ str(g1_name) + ', ' + str(g2_name))
    #getFinishedStatus()
    #print('Total time : '+str(totalTime)+ '\n')

'''
def runParallelCode(pairList):

    with cf.ProcessPoolExecutor(max_workers =2) as executor:

        try:
            for future in cf.as_completed((executor.map(getGraphDiff, pairList, timeout=5000000)), timeout=5000000):
                print(str(type(future.result())))
                if str(type(future.result())) == "<class 'NoneType'>":
                    pass
                else:
                    print(future.result(timeout=5000000))

        except cf._base.TimeoutError:
            print("Time limit exceeded")
            pass
'''

def runParallelCode(pairList):

    with cf.ProcessPoolExecutor(max_workers =2) as executor:

        try:
            result = executor.map(getGraphDiff, pairList, timeout=5000000)
            for r in result:
                if str(type(r)) == "<class 'NoneType'>":
                    pass
                else:
                    print(r)

        except cf._base.TimeoutError:
            print("Time limit exceeded")
            pass

def getJsonData(graph_1,graph_2):

    g1_edgeList = []
    g2_edgeList = []

    # convert the node labels which are strings to sorted integers without affecting the node attributes.
    sortedIntGraph_1 = nx.relabel.convert_node_labels_to_integers(graph_1, first_label=0, ordering='sorted', label_attribute=None)
    sortedIntGraph_2 = nx.relabel.convert_node_labels_to_integers(graph_2, first_label=0, ordering='sorted', label_attribute=None)

    g1_edgeTuple = list(sortedIntGraph_1.edges(data=False))
    g2_edgeTuple = list(sortedIntGraph_2.edges(data=False))

    # get graph edge lists
    for i in g1_edgeTuple:
        g1_edgeList.append(list(i))

    for i in g2_edgeTuple:
        g2_edgeList.append(list(i))

    # get graph attributes in the ascending order as the node labels
    nodeLabelList_g1 = []
    nodeLabelList_g2 = []

    nodeList_g1 = list(sortedIntGraph_1.nodes(data=True))
    nodeList_g2 = list(sortedIntGraph_2.nodes(data=True))

    for i in range(len(nodeList_g1)):
        if nodeList_g1[i][0] == i:
            nodeLabelList_g1.insert(i, nodeList_g1[i][1].get('label').replace('"', ''))

    for i in range(len(nodeList_g2)):
        if nodeList_g2[i][0] == i:
            nodeLabelList_g2.insert(i, nodeList_g2[i][1].get('label').replace('"', ''))

    # get graph edit distance
    #ged = nx.graph_edit_distance(sortedIntGraph_1, sortedIntGraph_2, node_match=return_eq) Commented since its too time expensive

   #Gmatch4py code for calculating ged

    #abs_ged = gm.BP_2(1,1,1,1)
    ged=gm.GraphEditDistance(1,1,1,1) # all edit costs are equal to 1

    #hed = gm.HED(1,1,1,1)

    result = ged.compare([sortedIntGraph_1, sortedIntGraph_2], None)

    # generate the json files
    jsonDict = {}
    jsonDict["graph_1"] = g1_edgeList
    jsonDict["graph_2"] = g2_edgeList
    jsonDict["labels_1"] = nodeLabelList_g1
    jsonDict["labels_2"] = nodeLabelList_g2
    jsonDict["ged"] = int(result[0][1])

    #print(jsonDict)
    return jsonDict


def return_eq(node1, node2): #function to compare the node labels 
    return node1['label']==node2['label']

def dumpJson(jsonFile, g1, g2): #function to dump the Json files 
    outPath = './outFiles/'
    with open(str(outPath)+ str(g1) + '::::'+ str(g2) + '.json', 'w') as fp:
        json.dump(jsonFile, fp)

def main(): #main function from where the program starts

    dotFileList= []
    #dotFile_data_path = './DotFiles/test'

    with open('./filenames.txt', 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            dotName = str(row).replace('[', '').replace(']','').replace("'","").strip()
            dotFileList.append(dotName)

    print("Total number of graph files: " + str(len(dotFileList)))

    counter = 0
    len_dotFileList = len(dotFileList)
    totalGraphJsons = len_dotFileList * len_dotFileList  #total number of graph similarity json samples
    print("Total Graph Similarity json samples: " + str(int(totalGraphJsons)))
    pairList = []
    #Code for generating graph Similarity json. Takes a non-symmetric pair of graphs from a list and returns their json data
    for dotFile_i in dotFileList:
        for dotFile_j in dotFileList:
            pairList.append(str(dotFile_i + ','+ str(dotFile_j)))

    print("<<<<<<<<<<<<<<<<<<<<<< " + str(len(pairList)))

    runParallelCode(pairList)

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

