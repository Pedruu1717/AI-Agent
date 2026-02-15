import client
import ast
import random


def reactive_example_1(c, res: int):
    if res != -1:
        while True:
            msg = c.execute("info", "view")
            objects = ast.literal_eval(msg)
            if objects[0]=='obstacle' or objects[0]=='bomb':
                c.execute("command", "left")
            else:
                if objects[0] == 'goal':
                    end = True
                    print("Found Goal!\n")
                else:
                    res = random.randint(0,4)
                    if res <= 3:
                        c.execute("command", "forward")
                    else:
                        c.execute("command","right")

def reactive_example_2(c,res:int):
    #Exemplo 2:
    if res != -1:
        end = False
        msg = c.execute("command", "set_steps")
        while end == False:
            msg = c.execute("info","view")
            objects = ast.literal_eval(msg)
            if 'obstacle' in objects or 'bomb' in objects:
                c.execute("command","left")
            else:
                if 'goal' in objects:
                    end = True
                    print("Found Goal!\n")
                else:
                  res = random.randint(0,4)
                  if res <= 3:
                      c.execute("command", "forward")
                  else:
                      c.execute("command","right")

def main():
    c = client.Client('127.0.0.1', 50001)
    res = c.connect()
    random.seed()  # To become true random, a different seed is used! (clock time)
    #reactive_example_2()
    reactive_example_2(c, res)


main()
