import client
import ast
import random

VISITED_COLOR = "#400000"
FRONTIER_COLOR = "red3"

# AUXILIAR

class Queue:
    def __init__(self):
         self.queue_data = []

    def isEmpty(self):
        if len(self.queue_data) == 0:
            return True
        else:
            return False

    def pop(self):
        return self.queue_data.pop(0)

    def insert(self,element):
        return self.queue_data.append(element)

    def getQueue(self):
        return self.queue_data

# SEARCH AGENT

class Node:
    def __init__(self,state,parent,action,path_cost):
        self.state = state
        self.parent = parent
        self.action =action
        self.path_cost = path_cost

    def getState(self):
        return self.state

    def getParent(self):
        return self.parent

    def getAction(self):
        return self.action

    def getPathCost(self):
        return self.path_cost

    def getParent(self):
        return self.parent


class Agent:
    def __init__(self):
        self.c = client.Client('127.0.0.1', 50001)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.visited_nodes = Queue()
        self.frontier_nodes = Queue()
        self.weightMap =[]
        self.goalNodePos =(0,0)
        self.state = (0,0)
        self.maxCoord = (0,0)



    def getConnection(self):
        return self.res

    def getGoalPosition(self):
        msg = self.c.execute("info", "goal")
        goal = ast.literal_eval(msg)
        # test
        print('Goal is located at:', goal)
        return goal

    def getSelfPosition(self):
        msg = self.c.execute("info", "position")
        pos = ast.literal_eval(msg)
        # test
        print('Received agent\'s position:', pos)
        return pos

    def getWeightMap(self):
        msg = self.c.execute("info", "map")
        w_map = ast.literal_eval(msg)
        # test
        print('Received map of weights:', w_map)
        return w_map

    def getPatchCost(self,pos):
        return self.weightMap[pos[0]][pos[1]]

    def getMaxCoord(self):
        msg = self.c.execute("info","maxcoord")
        max_coord =ast.literal_eval(msg)
        # test
        print('Received maxcoord', max_coord)
        return max_coord

    def getObstacles(self):
        msg = self.c.execute("info","obstacles")
        obst =ast.literal_eval(msg)
        # test
        print('Received map of obstacles:', obst)
        return obst

    # COM MODIFICAÇÕES NO SERVIDOR
    def getObjectsAt(self, x, y):
        msg = self.c.execute("info", str(x)+","+str(y))
        return ast.literal_eval(msg)

    # COM MODIFICAÇÕES NO SERVIDOR
    def isVisitable(self, x, y):
        return all(obj != "obstacle" and obj != "bomb" for obj in self.getObjectsAt(x,y))

    def step(self,pos,action):
        if action == "east":
            if pos[0] + 1 < self.maxCoord[0]:
                new_pos = (pos[0] + 1, pos[1])
            else:
                new_pos =(0,pos[1])

        if action == "west":
            if pos[0] - 1 >= 0:
                new_pos = (pos[0] - 1, pos[1])
            else:
                new_pos = (self.maxCoord[0] - 1, pos[1])


        if action == "north":
            if pos[1] + 1 < self.maxCoord[1]:
                new_pos = (pos[0], pos[1] + 1 )
            else:
                new_pos = (pos[0], 0)

        if action == "south":
            if pos[1] - 1 >= 0:
                new_pos = (pos[0], pos[1] - 1)
            else:
                new_pos = (pos[0], self.maxCoord[1] - 1 )
        return new_pos


    def getNode(self,parent_node,action):
        state = self.step(parent_node.getState(),action)
        pathCost = parent_node.getPathCost() + self.getPatchCost(state)
        return Node(state, parent_node, action, pathCost)

    def printNodes(self,type,nodes,i):
        print(type," (round ",i," )")
        print("state | path cost")
        for node in nodes.getQueue():
            print(node.getState(),"|", node.getPathCost())

    def printPath(self, node):
        n = node
        n_list = []
        while n.getPathCost() != 0:
            n_list.insert(0,[n.getState(), n.getPathCost()])
            n = n.getParent()
        print("Final Path", n_list)

    def mark_visited(self, node):
        # self.c.execute("mark_visited", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + VISITED_COLOR)

    def mark_frontier(self, node):
        # self.c.execute("mark_frontier", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + FRONTIER_COLOR)

    def think(self):
        # Get the position of the Goal
        self.goalNodePos = self.getGoalPosition()
        # Get information of the weights for each step in the world ...
        self.weightMap = self.getWeightMap()
        # Get max coordinates
        self.maxCoord = self.getMaxCoord()
        # Get the initial position of the agent
        self.state = self.getSelfPosition()
        # Start thinking
        i = 0

        #Add first node (root)
        root = Node(self.state,None,"",0)
        self.visited_nodes.insert(root)
        self.mark_visited(root)
        # Get the first four nodes. They are not in the same position of the root node.
        for dir in ["north","east","south","west"]:
            self.frontier_nodes.insert(self.getNode(root, dir))
            self.mark_frontier(self.getNode(root, dir))

        # test
        self.printNodes("Frontier", self.frontier_nodes, i)
        self.printNodes("Visitied", self.visited_nodes, i)

        # Cycle expanding nodes following the sequence in frontier nodes.
        for i in range (150):

            node_to_expand = self.frontier_nodes.pop()
            self.state = node_to_expand.getState()

            #print("Node's position (expand):", self.state)
            if node_to_expand.getState() not in [n.getState() for n in self.visited_nodes.getQueue()]:
                self.visited_nodes.insert(node_to_expand)
                self.mark_visited(node_to_expand)

            for dir in ["north", "east", "west", "south"]:
                new_node = self.getNode(node_to_expand, dir)
                if new_node.getState() not in [n.getState() for n in self.frontier_nodes.getQueue()]\
                        and new_node.getState() not in [n.getState() for n in self.visited_nodes.getQueue()]\
                        and self.isVisitable(*new_node.getState()):
                    self.frontier_nodes.insert(new_node)
                    self.mark_frontier(new_node)
                    if new_node.getState() == self.goalNodePos:
                        node = new_node
                        node_list = []
                        while node.getPathCost() != 0:
                            node_list.insert(0, [node.getState(), node.getPathCost()])
                            node = node.getParent()
                        return node_list

        input("Waiting for return!")

    def turn_and_go(self, direction):
        if direction == "south":
            left, right, back = "east", "west", "north"
        elif direction == "north":
            left, right, back = "west", "east", "south"
        elif direction == "east":
            left, right, back = "north", "south", "west"
        elif direction == "west":
            left, right, back = "south", "north", "east"
        if self.getSelfDirection() == back:
            self.c.execute("command", "right")
            self.c.execute("command", "right")
        elif self.getSelfDirection() == right:
            self.c.execute("command", "left")
        elif self.getSelfDirection() == left:
            self.c.execute("command", "right")
        self.c.execute("command", "forward")

    def do(self, path):
        self.c.execute("command", "set_steps")
        for node in path:
            coords = node[0]
            position = self.getSelfPosition()
            dx, dy = coords[0]-position[0], coords[1]-position[1]

            if abs(dx) != 1:
                dx = -dx
            if abs(dy) != 1:
                dy = -dy

            if dy > 0:
                self.turn_and_go("south")  # , "east", "west", "north")
            elif dy < 0:
                self.turn_and_go("north")  # , "west", "east", "south")
            elif dx > 0:
                self.turn_and_go("east")  # , "north", "south", "west")
            else:
                self.turn_and_go("west")  # , "south", "north", "east")
        input("Waiting for return")

    def getSelfDirection(self):
        return self.c.execute("info", "direction")


#STARTING THE PROGRAM:
def main():
    print("Starting client!")
    ag = Agent()
    if ag.getConnection() != -1:
        path = ag.think()
        if path is not None:
            ag.do(path)
        else:
            print("Goal not found!")

main()