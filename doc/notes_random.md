
## BUG : module `random` global partagé

*cf tests d'utilisation du package mazegen* '(

#### Ce qui (va faire croire que ça) marche :
```bash
python -c "
from mazegen import MazeGenerator
maze1 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed1.txt')
maze1.generate()
maze2 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed2.txt')
maze2.generate()
assert maze1.grid == maze2.grid, 'Grilles différentes malgré le même seed !'
print('OK : reproductibilité confirmée')
"
# OK : reproductibilité confirmée
```

#### Ce qui (montre visiblement que ça) bugge :
```bash
python -c "
from mazegen import MazeGenerator
maze1 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed1.txt')
maze2 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed2.txt')
maze1.generate(); maze2.generate()
assert maze1.grid == maze2.grid, 'Grilles différentes malgré le même seed !'
print('OK : reproductibilité confirmée')
"
# Traceback (most recent call last):
#   File "<string>", line 6, in <module>
# AssertionError: Grilles différentes malgré le même seed !
```

#### WTF ?

Le module utilise `random.seed(...)` puis `random.choice(...)`, ie le **générateur global** de Python, un état unique partagé par tout le programme :

```python
maze1 = MazeGenerator(..., seed=42, ...)   # random.seed(42)
# état global remis à 42
maze2 = MazeGenerator(..., seed=42, ...)   # random.seed(42)
# état global remis à 42
maze1.generate()                           # consomme plein de nombres aléatoires,
# état global modifié, avancé... n'est PAS du tout à l'état "seed=42"
maze2.generate()                           # KO car repart de l'état LAISSÉ par maze1.generate()
```

Ca explique que le comportement n'est pas reproductible si on a deux instances actives en même temps... Or un module réutilisable a vocation à être instancié plusieurs fois dans le même programme, par ex. générer un labyrinthe pour l'affichage arcade puis un autre pour un test.

## DEBUG : random.Random

La solution est un générateur aléatoire propre à chaque instance.

#### Module `random`

Le module `random` utilisé avec `random.seed(...)` ou `random.choice(...)` cache en réalité un objet unique de type `Random` : on a, pour tous les programmes, un seul et même générateur de nombre aléatoires. Donc chaque appel `random.choice(...)` consomme les nombres aléatoires de cet unique générateur.
*Genre un unique dé que tout les joueurs se partagerait* :P 

#### Classe `random.Random` 

Elle permet de fabriquer son propre générateur, to-ta-le-ment **indépendant** :D

```python
import random

my_random_1 = random.Random(33)   # mon propre générateur, initialisé avec la graine 33
my_random_2 = random.Random(33)   # un AUTRE générateur, initialisé EGALEMENT avec 33

print(my_random_1.choice(["a", "b", "c"]))   # toujours le même résultat pour seed=33
print(my_random_2.choice(["a", "b", "c"]))   # identique à my_random_1, car même graine

print(my_random_1.choice(["a", "b", "c"]))   # 2e tirage de my_random_1 : avance SON état à lui
print(my_random_2.choice(["a", "b", "c"]))   # 2e tirage de my_random_2 : toujours identique au 2e de my_random_1
```

*Youpi yop* : `my_random_1` et `my_random_2` ont chacun a **leur propre mémoire interne** et ne sont pas affectés par l'utilisation de l'autre.


#### A RETENIR

Le module `random` de base en Python est un état *global*, donc dans une bibliothèque `pip` professionnelle on bannira :
```python
random.seed(a_seed)
```

/!\ ***Effet de bord catastrophique*** /!\

Cela modifierait et figerait la génération de nombres aléatoires de **TOUTE** l'application dans laquelle on importerait un package avec ce code. Une bibliothèque professionnelle doit TOUJOURS instancier son propre générateur de nombres aléatoires (PRNG, Pseudo Random Number Generator) local, qui n'affectera que l'objet en question.

```python
# créer un nouvel objet de type `Random` :
# ie une "machine à nombres pseudo-aléatoires" complète et autonome, initialisée avec la valeur `seed`
self._rng = random.Random(seed)
```

Cet objet, stocké dans `self._rng`, est **rattaché à l'instance** (`self`) et non **PAS** au module global.

Désormais, pour une même graine, `self._rng.choice(...)`, `self._rng.shuffle(...)`... produiront toujours la même séquence de résultats : elle est modifiée **UNIQUEMENT** par les appels faits sur **CE** `self._rng` là précisément.

Pour initialiser un générateur d'aléatoire réellement imprévisible (par ex basé sur l'horloge système), sans graine fixe :
```python
self._rng = random.Random(None)
```

Chaque instance créée sans `seed` explicite aura un comportement différent à chaque exécution, ie le comportement souhaité quand on ne souhaite pas la reproductibilité.
