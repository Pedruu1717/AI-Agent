# Projeto RL de IA

#### Realizado por Manuel Cabral e Pedro Melo - Grupo 5.


##### Neste projeto desenvolvemos uma aprendizagem sem modelo.
- Neste método o agente não conhece recompensas e move-se aleatoriamente pelo mundo até chegar ao Goal, completando assim um episódio.
- Após cada episódio é atualizada a tabela Q Learning. Nesta tabela constam recompensas para cada ação possível em cada estado possível, que são calculadas desde o Goal até à posição inicial, para cada episódio.
- Depois de concluídos todos os episódios são marcadas setas no tabuleiro a indicar a melhor ação a tomar em cada estado. 

###### Nota: Para tornar cada episódio mais "rápido", no ficheiro client.py pode-se alterar no método execute, da classe Client, o parâmetro sleep_t e igualar a 0.