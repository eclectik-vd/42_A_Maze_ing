**Principe BFS** : explorer le graphe **niveau par niveau** (tous les voisins à distance *k* avant de passer à distance *k+1*), grâce à une **file** (`collections.deque`).

=> Le premier chemin qui atteint la sortie est nécessairement le plus court.

```mermaid
flowchart TD
    Start(["solve_maze()"]) --> Init["already_met = {entrée}<br>to_explore =<br>([(entrée, chemin vide)])"]
    Init --> Loop{"to_explore<br>vide ?"}
    Loop -->|oui| Fail(["aucun chemin trouvé :<br>RuntimeError"])
    Loop -->|non| Pop["to_explore.popleft()<br>(x, y, chemin)"]
    Pop --> IsExit{"(x, y) == sortie ?"}
    IsExit -->|oui| Found(["retourne le chemin<br>(ex: 'SSEESESSEEN')"])
    IsExit -->|non| Neighbors["pour N, E, S, W :<br>si pas de mur<br>ET pas déjà visité"]
    Neighbors --> Enqueue["already_met.add<br>to_explore.append<br>(x, y, chemin + direction)"]
    Enqueue --> Loop
```

Le chemin est représenté comme une **chaîne de caractères** (`"N"`, `"E"`, `"S"`, `"W"`), construite au fur et à mesure de l'exploration.