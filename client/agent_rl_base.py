import client
import ast
import random
import time


# Função que executa um episódio.
def episode(c):
    msg = c.execute('info', 'targets')
    targets = ast.literal_eval(msg)
    targetList= []
    for column in range(len(targets)):
        for row in range(len(targets[column])):
            if targets[column][row] == 1:
                targetList.append((column, row))

    msg = c.execute("info", "goal")
    goal = ast.literal_eval(msg)
    commands = ["left", "right", "forward"]
    path = []
    foundGoal = False
    end = False
    while not end:
        msg = c.execute("info", "view")
        objects = ast.literal_eval(msg)
        msg = c.execute("info", "position")
        pos = ast.literal_eval(msg)
        command = random.choice(commands)
        if objects[0] == 'obstacle' or objects[0] == 'bomb':
            c.execute("command", "left")
        else:
            if (pos == goal) or (pos in targetList):
                if pos == goal:
                    print('GOAL found!')
                    foundGoal = True
                else:
                    print('TARGET found!')
                end = True
            else:
                if command == 'forward':
                    direction = c.execute("info", "direction") # Direção para a qual o agente está virado.
                    pos = list(pos)
                    pos.append(direction)
                    pos = tuple(pos)
                    path.append(pos)
                c.execute('command', command)

    print('Path:\n', path)
    return [path, foundGoal]


# Função para atualizar tabela Q learning.
# Recebe como argumentos a respetiva tabela e o percurso feito pelo agente num episódio.
def updateQTable(QTable, path, c):
    msg = c.execute("info", "goal")
    goal = ast.literal_eval(msg)
    lastX, lastY, lastDirection = goal[0], goal[1], 'north'
    size = len(path)
    i = size-1
    while i >= 0:
        newPos = path[i]
        x, y, direction = newPos[0], newPos[1], newPos[2]
        q = 0.9*QTable[lastX][lastY][lastDirection]

        if q > QTable[x][y][direction]:
            QTable[x][y][direction] = q

        lastX, lastY, lastDirection = x, y, direction
        i -= 1

    print('QTable:')
    for column in QTable:
        print(column)

    return QTable


# Função para marcar as setas com a melhor ação possível.
# Recebe a tabela Q Learning final.
def markArrows(QTable, c):
    for column in range(len(QTable)):
        for row in range(len(QTable[column])):
            bestReward = 0
            bestDirection = ''
            for direction in ['north', 'south', 'east', 'west']:
                reward = QTable[column][row][direction]
                if reward > bestReward:
                    bestDirection = direction
                    bestReward = reward
                    c.execute('marrow', bestDirection + ',' + str(row) + ',' + str(column))
                    time.sleep(0.2)


# Main.
def main(numEpisodes):
    c = client.Client('127.0.0.1', 50001)
    res = c.connect()
    if res != -1:
        random.seed()  # To become true random, a different seed is used! (clock time)

        # Inicializar Q Table.
        QTable = []
        msg = c.execute("info", "maxcoord")
        max_coord = ast.literal_eval(msg)
        for n in range(max_coord[0]):
            QTable += [[0] * max_coord[1]]

        for column in range(len(QTable)):
            for row in range(len(QTable[column])):
                QTable[column][row] = {'north': 0, 'south': 0, 'east': 0, 'west': 0}

        msg = c.execute("info", "goal")
        goal = ast.literal_eval(msg)
        for direction in ['north', 'south', 'east', 'west']:
            QTable[goal[0]][goal[1]][direction] = 100  # Reward do Goal igual a 100.

        msg = c.execute('info', 'targets')
        targets = ast.literal_eval(msg)
        for col in range(len(targets)):
            for ro in range(len(targets[col])):
                if targets[col][ro] == 1:
                    for direction in ['north', 'south', 'east', 'west']:
                        QTable[col][ro][direction] = -100  # Reward dos targets.

        for x in QTable:
            print(x)
        # Executar episódios.
        for n in range(numEpisodes):
            print(n + 1, 'º episode')
            path = episode(c)[0]  # Realizar um episódio.
            if episode(c)[1]:
                QTable = updateQTable(QTable, path, c)  # Atualizar matriz Q-learning.
                for y in QTable:
                    print(y)
            if n < numEpisodes-1:
                c.execute("command", "home")  # Voltar ao ponto de partida após um episódio.

        # Depois de concluídos todos os episódios, mostrar setas.
        markArrows(QTable, c)
        input()


main(numEpisodes=50)
