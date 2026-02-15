#!/usr/bin/env python3
import socket
import time
import ast
import random
import operator # To use with map

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001      # The port used by the server
class Agent:
    def __init__(self,host=HOST,port=PORT):
        self.host = host
        self.port = port
        self.s = None

    def print_message(self,data):
        print("Data:",data)

    def connect(self):
#        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.port))
#            return(0)
#        except:
#            print('A connection error occurred!')
#            return(-1)

    def execute(self, action: object, value: object, sleep_t: object = 0.1) -> object:
        self.s.sendall(str.encode(action+" "+value))
        data = self.s.recv(2048)
        # Test
        # print('Received', repr(data))
        message = data.decode()
        #message(ast.literal_eval(data.decode()))
        time.sleep(sleep_t)
        return message

    def getMaxCoord(self):
        msg = self.execute("info", "maxcoord")
        max_coord = ast.literal_eval(msg)
        # test
        print('Received maxcoord', max_coord)
        return max_coord

    def getTargets(self):
        ''' Return the targets defined in the world.'''
        msg = self.execute("info", "targets")
        res = ast.literal_eval(msg)
        # test
        # print('Received targets:', res)
        return res

    def getTargetsDict(self,targets,max_coord):
        '''Return a dictionary of targets'''
        targets_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                targets_dict[str((x, y))] = targets[x][y]
        return targets_dict

    def getListTargets(self,targets,max_coord):
        targets_list =[]
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                if targets[x][y] == 1:
                    targets_list.append((x,y))
        # Test
        print("Targets List:",targets_list)
        return targets_list

    def getObstacles(self):
        msg = self.execute("info","obstacles")
        obst =ast.literal_eval(msg)
        # test
        print('Received map of obstacles:', obst)
        return obst

    def getObstaclesDict(self, obstacles,max_coord):
        '''Return a dictionary of obstacles:'''
        obst_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                obst_dict[str((x, y))] = obstacles[x][y]
        return obst_dict


    def getReward(self):
        '''Return the matrix of rewards'''
        msg = self.execute("info", "rewards")
        res = ast.literal_eval(msg)
        # test
        # print('Received rewards:', res)
        return res

    def getRewardDict(self,rewards,max_coord):
        '''Return a dictionary of rewards:'''
        rewards_dict = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                rewards_dict[str((x,y))]=rewards[x][y]
        return rewards_dict

    # ---------------------------------------------------
    # Get the coordinates on north, east, south or east
    # ---------------------------------------------------
    def coord_north(self,pos):
        ''' Assuming world is circular, the value of coordinates to north'''
        x,y = pos[0],pos[1]
        if y == 0:  # top
            y1 = max_coord[1] - 1
        else:
            y1 = y - 1
        return (x,y1)

    def coord_south(self,pos):
        ''' Assuming world is circular, the value of coordinates to south'''
        x,y = pos[0],pos[1]
        if y == max_coord[1] - 1:  # bottom
            y2 = 0
        else:
            y2 = y + 1
        return (x,y2)

    def coord_east(self,pos):
        ''' Assuming world is circular, the value of coordinates to east'''
        x,y = pos[0],pos[1]
        if x == max_coord[0] - 1:  # right
            x1 = 0
        else:
            x1 = x + 1
        return (x1,y)

    def coord_west(self,pos):
        ''' Assuming world is circular, the value of coordinates to west'''
        x,y = pos[0],pos[1]
        if x == 0:
            x2 = max_coord[0] - 1
        else:
            x2 = x - 1
        return (x2,y)


    def initializeVTable(self,max_coord,obstacles):
        v_table = {}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                # Value, Number of visits,(x,y,w,z): the places with connection i.e. which are not a wall.
                # If y == max_coord[1] - 1 (bottom)
                # If y == 0 (top)
                # If x == 0 (west)
                # If x == max_coord[0] (east)
                # Obstacles
                north = 0
                east  = 0
                south = 0
                west  = 0
                # If it is an obstacle it has all directions equal to zero!
                if obstacles[str((x,y))] == 1:
                    v_table[str((x, y))] = [0, 0, (north, east, south, west)]
                else:
                    #North
                    if obstacles[str(self.coord_north((x,y)))] == 0: #not an obstacle
                        north = 1
                    #South
                    if obstacles[str(self.coord_south((x,y)))] == 0: #not an obstacle
                        south = 1
                    #East
                    if obstacles[str(self.coord_east((x,y)))] == 0: #not an obstacle
                        east = 1
                    #West
                    if obstacles[str(self.coord_west((x,y)))] == 0: #not an obstacle
                        west = 1
                    v_table[str((x,y))]=[0,0,(north,east,south,west)]
        return v_table


    def initializeQTable(self,max_coord):
        q_table ={}
        for y in range(max_coord[1]):
            for x in range(max_coord[0]):
                q_table[str((x,y))]=[0,0,0,0]
        # Test
        # print("QTable initialized: ", q_table)
        return q_table


    def getPos(self):
        '''Return the actual position of the agent. '''
        msg = self.execute("info", "position",0.01)
        pos = ast.literal_eval(msg)
        # test
        # print('Received agent\'s position:', pos)
        return pos

    def getGoal(self):
        msg = self.execute("info", "goal")
        goal = ast.literal_eval(msg)
        # test
        # print('Received agent\'s goal:', goal)
        return goal

    def clearAllServerArrows(self,qTable):
        ''' Clear all the arrows in the server'''
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                coordinates = (j,i)
                msg = self.execute("uarrow",str(i)+","+str(j),0.05)

    def take_first_elem(self,elem):
        return elem[0]

    def addServerVtableArrows(self,vTable,targets):
        '''Add arrows for vTable'''
        for i in range(max_coord[0]):
            for j in range(max_coord[1]):
                pos = (i, j)
                values = vTable[str(pos)]
                # There are paths to print
                if sum(values[2]) != 0 and pos != self.getGoal() and pos not in targets:
                    values_around = ( vTable[ str(self.coord_north(pos))][0] , vTable[str(self.coord_east(pos))][0], vTable[str(self.coord_south(pos))][0], vTable[str(self.coord_west(pos))][0])

                    # coord_list = list( map(operator.mul, values[2],values_around) )

                    # Test
                    # print("Pos:",pos," has tuple:",coord_list)
                    directions = ["north","east","south","west"]
                    values_dir =[]
                    for k in range(4):
                        if values[2][k] != 0: # Possible direction
                            values_dir.append((values_around[k],directions[k]))
                    values_dir.sort(key=self.take_first_elem)
                    values_dir = values_dir[::-1]
                    arrow_dirs =[]
                    # Test
                    print("Pos:",pos," has ordered list:",values_dir)
                    if len(values_dir) == 1:
                        arrow_dirs.append(values_dir[0][1]) #Get the direction of unique value
                    if len(values_dir) == 2:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        else:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                    if len(values_dir) == 3:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        elif values_dir[0][0] == values_dir[1][0] and values_dir[0][0] > values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                        else: # values_dir[0][0] == values_dir[1][0] == values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                    if len(values_dir) == 4:
                        if values_dir[0][0] > values_dir[1][0]:
                            arrow_dirs.append(values_dir[0][1])
                        elif values_dir[0][0] == values_dir[1][0] and values_dir[0][0] > values_dir[2][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                        elif values_dir[0][0] == values_dir[1][0] == values_dir[2][0] and values_dir[0][0] > values_dir[3][0]:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                        else:
                            arrow_dirs.append(values_dir[0][1])
                            arrow_dirs.append(values_dir[1][1])
                            arrow_dirs.append(values_dir[2][1])
                            arrow_dirs.append(values_dir[3][1])

                    arrow = ""
                    nr = 0
                    if "north" in arrow_dirs:
                        arrow="north"
                        nr = nr + 1
                    if "east" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_east"
                        else:
                            arrow = "east"
                        nr = nr + 1
                    if "south" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_south"
                        else:
                            arrow = "south"
                        nr = nr + 1
                    if "west" in arrow_dirs:
                        if nr > 0:
                            arrow = arrow + "_west"
                        else:
                            arrow = "west"
                    msg = self.execute("marrow", arrow +","+str(j)+","+str(i), 0.05)

    def addServerQtableArrows(self,qTable):
        '''Add arrows for qTable'''
        arrow =""
        for i in range(max_coord[1]):
            for j in range(max_coord[0]):
                coordinates = (j,i)
                coord_list = [qTable.get(str(coordinates))[0], qTable.get(str(coordinates))[1],
                              qTable.get(str(coordinates))[2], qTable.get(str(coordinates))[3]].sort()
                ##res = max(coord_list)
                #test
                print("(",j,",",i,")=",coord_list)
                #All identical
                if coord_list[0] == coord_list[1] == coord_list[2] == coord_list[3]:
                    print("all directions")
                    arrow ="north_south_east_west"
                    #msg = self.execute("marrow", "north_south_east_west" + "," + str(i) + "," + str(j), 0.05)
                # Three equal
                elif coord_list[0] == coord_list[1] == coord_list[2]:
                    arrow ="north_south_east"
                elif coord_list[0] == coord_list[2] == coord_list[3]:
                    arrow ="north_south_west"
                elif coord_list[1] == coord_list[2] == coord_list[3]:
                    arrow ="south_east_west"
                elif coord_list[0] == coord_list[1] == coord_list[3]:
                    arrow ="north_east_west"
                #Two equal
                elif coord_list[0] == coord_list[1]:
                    arrow = "north_east"
                elif coord_list[0] == coord_list[2]:
                    arrow = "north_south"
                elif coord_list[0] == coord_list[3]:
                    arrow = "north_west"
                elif coord_list[1] == coord_list[2]:
                    arrow = "south_east"
                elif coord_list[1] == coord_list[3]:
                    arrow = "east_west"
                elif coord_list[2] == coord_list[3]:
                    arrow = "south_west"
                #One bigest
                else:
                    res = max(coord_list)
                    if res > 0: #not all are zero
                        idx = coord_list.index(res)
                        if  idx == 0:
                            #north
                            arrow = "north"
                        #pos = ast.literal_eval(msg)
                        elif idx == 1:
                            # east
                            arrow = "east"
                        elif idx == 2:
                            # south
                            arrow = "south"
                        else:
                            # west
                            arrow = "west"
                msg = self.execute("marrow", arrow+","+str(i)+","+str(j), 0.05)

    def printVTableValues(self,vTable):
        '''For each state, return the function value...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + '(%3.1f)'%(vTable.get(str(coordinates))[0]) + "|"
            print(str_row)

    def printVTableNVisits(self,vTable):
        '''For each state, return the number of visits...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + '(%3.1f)'%(vTable.get(str(coordinates))[1]) + "|"
            print(str_row)

    def printVTablePaths(self,vTable):
        '''For each state, return possibe paths...'''
        for i in range(max_coord[1]):
            str_row = "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                str_row = str_row + str(vTable.get(str(coordinates))[2]) + "|"
            print(str_row)

    def printQTable(self,qTable):
        for i in range(max_coord[1]):
            row_str_n =  "|"
            row_str_w =  "|"
            row_str_s =  "|"
            for j in range(max_coord[0]):
                coordinates = (j,i)
                f_str_n = '(%3.1f)'%(qTable.get(str(coordinates))[0])
                f_str_s = '(%3.1f)'%(qTable.get(str(coordinates))[2])
                f_str_w = '(%3.1f)'%(qTable.get(str(coordinates))[3])
                f_str_e = '(%3.1f)'%(qTable.get(str(coordinates))[1])
                row_str_n = row_str_n + "    " + f_str_n + "    |"
                row_str_s = row_str_s + "    " + f_str_s + "    |"
                row_str_w = row_str_w + f_str_w + "    " + f_str_e + "|"
            print(row_str_n)
            print(row_str_w)
            print(row_str_s)
            print()

if __name__=="__main__":
    # EXPLORE using Q-LEARNING
    EXPLORATIONS =  500 #number of paths in the world
    VISUALIZATION = 1 #visualize 10 / 10
    # Discount
    discount_constant = 0.9

    agent = Agent(HOST,PORT)
    res = agent.connect()
    if res !=-1:
        # Get goal position
        goal = agent.getGoal()
        max_coord = agent.getMaxCoord()
        # Get targets
        targetsL = agent.getListTargets(agent.getTargets(),max_coord)
        # Get reward
        rewards = agent.getRewardDict(agent.getReward(),max_coord)
        # Test
        #print("Rewards:",rewards)
        # Get obstacles
        obstacles = agent.getObstaclesDict(agent.getObstacles(),max_coord)
        # Test
        print("Obstacles:")
        print(obstacles)
        # Initialize QTable
        #qTable = agent.initializeQTable(max_coord)
        #print("Starting QTable:",qTable)

        # Initialize VTable
        vTable = agent.initializeVTable(max_coord, obstacles)
        # Test
        print("VTable values:")
        agent.printVTableValues(vTable)
        print("VTable visits:")
        agent.printVTableNVisits(vTable)
        print("VTable possible paths (north,east,south,east):")
        agent.printVTablePaths(vTable)
        for i in range(EXPLORATIONS):
            # Move home or move to a aleatory position without obstacles
            #  -- get list of positions not obstacles ...
            #  -- select randomly one of them as first position...
            msg = agent.execute("command", "home", 0.02)
            # Get the initial position
            initial_pos = agent.getPos()

            # Find goal or find target
            # findTarget = False
            findGoal = False
            findTarget = False
            # List of lists [p,d], p = position in coordinates and d = direction of previous movement
            path = []  # Keep the path to the goal

            path.append([initial_pos,""])
            while findGoal == False and findTarget == False:
            #while findGoal == False:
                #Test if it found a goal!
                # Options:
                # -- selecting next movement randomly: north, south, east , west
                # -- following the policy
                # Random
                direction = random.randint(1, 4)
                if direction == 1:
                    value = "north"
                elif direction == 2:
                    value = "south"
                elif direction == 3:
                    value = "east"
                else:
                    value = "west"
                # Selecting Policy
                # ...
                action = "command"
                # Test
                # print("Action Value pair:", action, ":", value)
                msg = agent.execute(action,value,0.02)
                pos = agent.getPos()
                path.append([pos,value]) # New position
                # Test
                # agent.print_message(msg)

                # Final Position
                # if pos == goal or pos in one of the targets!!
                if pos == goal:
                    findGoal = True
                if pos in targetsL:
                    findTarget = True
            # End ...
            print("Found the goal!\n")
            print("Path:",path)
            path_reversed = path[::-1]
            # Final position
            pos = path_reversed[0][0]
            # Remove final position
            del path_reversed[0] # Remove the last element
            incremental_return = rewards[str(pos)]
            vTable[str(pos)][0]=incremental_return
            last_pos = pos # Position is now the last position
            print("Return of the final position,",last_pos,":", incremental_return)


            for step in path_reversed:
                pos = step[0]              # actual position
                reward = rewards[str((pos))]
                movement = step[1]         # movement type
                # Incremental Return R with discount
                incremental_return = reward + discount_constant * incremental_return
                # Get the actual VTable values
                actual_vtable = vTable[str(pos)]
                # Test
                print("Actual vTable value:",actual_vtable[0])
                print("Counting visits in actual vTable:",actual_vtable[1])
                # Get the new value
                new_vtable_count = actual_vtable[1] + 1
                new_vtable_value =actual_vtable[0] + (incremental_return - actual_vtable[0]) / new_vtable_count
                vTable[str(pos)] = [new_vtable_value,new_vtable_count,actual_vtable[2]]
                # Test
                print("For position x=",pos[0]," y=",pos[1],":")
                print("VTable value:",vTable[str(pos)][0])
                print("VTable count:",vTable[str(pos)][1])
                print("VTable directions:",vTable[str(pos)][2])
                print("Incremental return:",incremental_return)
                print("--------------------------------------------------")
                last_pos = pos
                #input()
                # Test
                print("VTable values:")
                agent.printVTableValues(vTable)
                print("VTable visits:")
                agent.printVTableNVisits(vTable)
                print("VTable possible paths (north,east,south,east):")
                agent.printVTablePaths(vTable)
                print("-------------------------------------------------")

            # Test: stops
            if i== 2:
                input()
            if i == 250:
                input()
        
                # Select the direction of agent's movement

                #if pos[0] ==  last_pos[0]: # No movement on x
                #    if pos[1] > last_pos[1] and pos[1] - last_pos[1] == 1:
                #        movement = "north"
                #    elif pos[1] < last_pos[1] and pos[1] - last_pos[1] == -1:
                #        movement = "south"
                #    elif pos[1] == 0 and last_pos[1] == max_coord[1] -1:
                #        movement = "north"
                #    elif  pos[1]== max_coord[1] - 1 and last_pos[1] == 0:
                #        movement = "south"
                #elif pos[1] == last_pos[1]: #There is no movement on YY
                #    if pos[0] > last_pos[0] and pos[0] - last_pos[0] == 1:
                #        movement ="west"
                #    elif pos[0] < last_pos[0] and pos[0] - last_pos[0] == -1:
                #        movement ="east"
                #    elif pos[0]== 0 and last_pos[0] == max_coord[0] - 1:
                #        movement ="west"
                #    elif pos[0]==max_coord[0] - 1 and last_pos[0] == 0:
                #        movement ="east"
                ##else:
                #    # Error: none
                #    movement =""

                # Get the r

                #if movement == "north":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action

                    #if last_value[0] < new_r:
                 #   qTable[str(pos)]= [(new_r + last_value[0]) / 2,last_value[1],last_value[2],last_value[3]]
                #elif movement == "east":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action
                    #if last_value[1] < new_r:
                #    qTable[str(pos)]= [last_value[0],(new_r + last_value[1]) / 2,last_value[2],last_value[3]]

                #elif movement == "south":
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight*last_reward
                #    last_reward = new_r # Reward to send to next action
                    #if last_value[2] < new_r:
                #    qTable[str(pos)]= [last_value[0],last_value[1],(new_r + last_value[2]) / 2,last_value[3]]
                #else:
                #    last_value = qTable[str(pos)]
                #    r = rewards[str(last_pos)]
                #    new_r = r + weight * last_reward
                #    last_reward = new_r  # Reward to send to next action
                    #if last_value[3] < new_r:
                #    qTable[str(pos)]= [last_value[0],last_value[1],last_value[2],(new_r + last_value[3]) / 2]
                #Update weight
                #weight = weight_constant * weight
            # Test
                #print("The movement from ",pos," to ",last_pos," had the direction ", movement )
                #print("New weight:",weight)
                #print("last_reward (feeding next steps:",last_reward)
                #Update movement
            # Test
            # print("The new values for qTable are:")
            # agent.printQTable(qTable)

        # Add Arrows to server (qTable)
        # agent.addServerArrows(qTable)
        agent.addServerVtableArrows(vTable,targetsL)
        input()
