import client
import ast
import random


class Client:
    '''The class interact with the server sending a string encoded and receive a return of 2048 bits.'''
    def __init__(self,HOST='127.0.0.1',PORT=50001):
        self.host = HOST
        self.port = PORT
    def print_message(self,data):
        print("Data:",data)
    def connect(self):
#       try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.port))
#            return(0)
#       except:
#            print('A connection error occurred!')
#            return(-1)
    def execute(self,action,value,sleep_t = 0.5):
        self.s.sendall(str.encode(action+" "+value))
        data = self.s.recv(2048)
        print('Received', repr(data))
        msg = data.decode()
        #message(ast.literal_eval(data.decode()))
        time.sleep(sleep_t)
        return msg


def getPos():
    '''Return the actual position of the agent. '''
    msg = c.execute("info", "position")
    pos = ast.literal_eval(msg)
    # test
    print('Received agent\'s position:', pos)
    return pos

def getMap():
    '''Return the map of weights: A matrix (x,y) with x the columns and y the rows!'''
    msg = c.execute("info", "map")
    w_map = ast.literal_eval(msg)
    # test
    print('Received map of weights:', w_map)
    return w_map
def getMaxCoord():        
    msg = c.execute("info","maxcoord")
    max_coord =ast.literal_eval(msg)
    # test
    print('Received maxcoord', max_coord)
    return max_coord
def getObstacles():
    msg = c.execute("info","obstacles")
    obst =ast.literal_eval(msg)
    # test
    print('Received map of obstacles:', obst)
    return obst

#RETURN A LIST OF NEXT POSITIONS (not considering the obstacles!)
def getNextPositions(pos):
    '''Return the possible next positions of the agent, given the present position of the agent and considering that the
    walls of the model are an obstacle. If it finds an wall than it will be at the same place.'''
    next_pos = []
    max_coord = getMaxCoord()
    if pos[0] + 1 < max_coord[0]:
        next_pos.append((pos[0]+1,pos[1]))
    if pos[1] + 1 < max_coord[1]:
        next_pos.append((pos[0],pos[1]+1))
    if pos[0] - 1 >= 0:
        next_pos.append((pos[0]-1,pos[1]))
    if pos[1] - 1 >= 0:
        next_pos.append((pos[0],pos[1]-1))
    return next_pos

def main():
    for i in range(2):
        res = getMaxCoord()
        print("Max coord x:",res[0])
        print("Max coord y:",res[1])
        #  Get information of the world
        #  Print the obstacles position
        obstacles = getObstacles()
        #Test: To confirm that the first parameter in matrix is column and the sencond is the row.
        print("Obstacles 0 1 =", obstacles[0][1])
        # Get information of the weights for each step in the world ...
        map = getMap()
        #Test: The same from above.
        print("Example:Weight at x=1 and y=2:", map[1][2])
        # START A CYCLE TO BUILD A LIST OF ALL NEXT STATES ...

        # 1-Get the position of the agent
        pos = getPos()
        # 2-Add to the list of positions already tested
        # (to be implemented)
        # 3-Get list of possible positions from the actual position
        print(getNextPositions(pos))
        # 4-Remove from the list the obstacles!
        # 5-Test if any position in the list is a goal
        # 6-For each element in the list, expand it for the next possible positions (don't include position already in the previous list)
        # Etc
        # Print "Found a Path!"
        # EXECUTE THE PATH!
        #(example from other program:)
        msg = c.execute("info", "view")
        objects = ast.literal_eval(msg)
        if objects[0] == 'obstacle' or objects[0] == 'bomb':
            c.execute("command", "left")
        else:
            res = random.randint(0, 4)
            if res <= 3:
                c.execute("command", "forward")
            else:
                c.execute("command", "right")
    input("Waiting for return!")

#STARTING PROGRAM
print("Starting client!")
c = client.Client('127.0.0.1', 50001)
res = c.connect()
random.seed() #To become true random, a different seed is used! (clock time)
if res!=-1:
    main()


