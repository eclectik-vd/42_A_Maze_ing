**pytest est un framework de tests automatisés pour Python.**
```bash
pip install pytest
```

Son rôle est de vérifier que le code fait bien ce qu'il est censé faire, sans avoir à tester manuellement chaque fois qu'on modifie quelque chose.

On écrit des petites fonctions qui « testent » d'autres fonctions du programme, et `pytest` les exécute toutes automatiquement en disant lesquelles passent et lesquelles échouent.

C'est une bonne habitude à prendre :
+ oblige à réfléchir à ce que le code devrait faire, pas juste à l'écrire ;
+ quand on modifie une fonction plus tard, on sait immédiatement si on a cassé autre chose ;
+ il s'agit d'une compétence très demandée professionnellement.
##### tdm
[[#1. Lister les cas]]
[[#2. les imports]]
[[#3. Tests basiques]]
[[#4. Fixtures]]

## 1. Lister les cas

Lister d'abord les cas, pour éviter d'oublier des scénarios et pour disposer d'une checklist claire à cocher au fur et à mesure. Il y a plusieurs **niveaux** d'erreurs possibles, correspondant aux 3 étapes de `load_config()` .
#### Erreurs de syntaxe brute (`parse_config()`)

Erreurs qui concernent la forme du fichier et surviennent avant même que Pydantic n'intervienne :

- [x] Le fichier n'existe pas
      `FileNotFoundError`
- [x] Une ligne (non vide, non commentaire) ne contient pas de `=`
      `ValueError`
- [x] Fichier vide
      retourne un dict vide qui fera échouer la validation Pydantic pour champs manquants
- [x] Fichier avec seulement des commentaires
      retourne un dict vide qui fera échouer la validation Pydantic pour champs manquants
- [x] Fichier avec seulement des lignes vides
      retourne un dict vide qui fera échouer la validation Pydantic pour champs manquants

#### Erreurs de champs manquants (Pydantic champs obligatoires)

Chaque champ obligatoire absent doit lever une `ValidationError` :

- [x] `WIDTH` absent
- [x] `HEIGHT` absent
- [x] `ENTRY` absent
- [x] `EXIT` absent
- [x] `OUTPUT_FILE` absent

#### Erreurs de valeurs invalides (Pydantic contraintes de champ)

Chaque champ invalide doit lever une `ValidationError` :

- [x] `WIDTH` non entier (ex. `WIDTH=abc`)`
- [x] `WIDTH` hors bornes (`< 2` ou `> 200`)
- [x] `HEIGHT` non entier
- [x] `HEIGHT` hors bornes (`< 2` ou `> 200`)
- [x] `ENTRY` mauvais format (pas de virgule, ex. `ENTRY=22`)
- [x] `ENTRY` coordonnées non entières (ex. `ENTRY=a,b`)
- [x] `ENTRY` coordonnée négative (ex. `ENTRY=-1,0`)
- [x] `EXIT` mauvais format (pas de virgule, ex. `EXIT=33`)
- [x] `EXIT` coordonnées non entières (ex. `EXIT=c,d`)
- [x] `EXIT` coordonnée négative (ex. `EXIT=1,-2`)
- [x] `OUTPUT_FILE` extension différente de `.txt`
- [x] `PERFECT` valeur non convertible en booléen (ex. `PERFECT=chaispô)`
- [x] `DISPLAY_MODE` valeur hors `{ascii, arcade}` (ex. `DISPLAY_MODE=3D`)

#### Erreurs de règles métier (`model_validator` — cohérence globale)

Ces règles combinent plusieurs champs entre eux :
- [ ] `entry_coord` avec abscisse `>= width`
- [ ] `entry_coord` avec ordonnée `>= height`
- [ ] `exit_coord` avec abscisse `>= width`
- [ ] `exit_coord` avec ordonnée `>= height`
- [ ] `entry_coord == exit_coord` (entrée et sortie identiques)
- [ ] Cas cumulé : une config qui viole plusieurs règles à la fois
      vérifier que le message contient bien toutes les erreurs, pas seulement la première

[[#tdm|Haut page]]

---

## 2. les imports

+ `pytest` évidemment, pour `pytest.raises(...)` qui permet de vérifier qu'une exception est bien levée.
+ l'exception `ValidationError` de `Pydantic`, quand `MazeConfig(**data)` reçoit des données invalides.
+ Les fonctions et classes qui font le travail de validation :
	+ dans `config_parser.py`, **`parse_config()`** lève `FileNotFoundError` ou `ValueError` si la syntaxe brute du fichier est invalide.
	+ dans `models.py`, **`MazeConfig`** lève `pydantic.ValidationError` si les _valeurs_ sont invalides.

```python
# tests/test_parsing.py

import pytest
from pydantic import ValidationError

from src.maze_app.parsing.config_parser import parse_config
from src.maze_app.parsing.models import MazeConfig
```

> **IMPORTANT** : `pytest` doit ajouter la racine du projet à `sys.path`

 En effet, `Pytest` détecte bien le `rootdir` (`/home/newbie/42_A_Maze_ing`), mais ça ne veut pas dire que ce dossier est automatiquement importable en Python : par défaut, quand `pytest` importe `tests/test_parsing.py`, il remonte l'arborescence des dossiers **tant que** il trouve des `__init__.py`, puis insère dans `sys.path` le **premier dossier sans `__init__.py`** rencontré.
Si le dossier `tests/` n'inclut pas de `__init__.py`, à la place de la racine du projet c'est `tests/` lui-même qui sera ajouté à `sys.path` => `src` ne sera trouvable nulle part et provoquera l'erreur `ModuleNotFoundError: No module named 'src'`.

**Solution recommandée**
L'option officielle intégrée à `pytest` (depuis la version 7) est d'indiquer explicitement à `pytest` d'ajouter `.` (la racine du projet) à `sys.path` avant de collecter les tests, indépendamment de la présence ou non de `__init__.py`.

 Ajouter dans le `pyproject.toml` :
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

[[#tdm|Haut page]]

---

## 3. Tests basiques

##### outil `tmp_path`

Pour tester `parse_config`, il faudra créer des fichiers `config.txt` factices avec du contenu volontairement invalide... mais sans polluer l'espace disque. Pytest fournit une fixture toute prête pour ça : `tmp_path`.

A chaque test, `tmp_path` crée un dossier temporaire unique, automatiquement nettoyé après :

```python
def test_bidon(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("CECI_EST_INVALIDE\n")

    with pytest.raises(ValueError):
        parse_config(str(fichier))
```

##### Quoi mettre dans le `with`

Dans un test avec `pytest.raises`, TOUJOURS se poser la question _"quelle ligne, précisément, doit lever l'exception ?"_
=> ne mettre QUE cette ligne (ou le strict nécessaire) dans le bloc `with`.

Il s'agit d'éviter un piège classique : avec trop de code dans le bloc, une _autre_ ligne pourrait lever l'exception attendue par erreur => le test passerait MAIS ne testerait pas ce que l'on veut.
##### TEST 1 : Fichier qui n'existe pas

```python
def test_fichier_introuvable(tmp_path):
	# construit un chemin (un objet `Path`) qui pointe vers un fichier, dans un dossier temporaire propre
    fichier = tmp_path / "config.txt"
    # /!\ `fichier` est un objet `Path`, pas une string...

    # `with` ne doit entourer QUE l'appel censé échouer
    with pytest.raises(FileNotFoundError):
	    # `parse_config(file_path: str)` attend une string, il faut convertir l'objet `Path`.
        parse_config(str(fichier))
```

##### TEST 2 : Fichier avec ligne invalide

Il faut **créer un vrai fichier**, avec un contenu qui viole la règle `KEY=VALUE`, afin de vérifier qu'une `ValueError` est levée :
```python
def test_ligne_sans_egal(tmp_path):
    # créer le chemin du fichier temporaire avec `tmp_path`
    fichier = tmp_path / "config.txt"
    # écrire une ligne invalide (sans `=`) dans le fichier
    fichier.write_text("une ligne sans le signe egal\n")

    with pytest.raises(ValueError):
	    # appeler `parse_config()` sur ce fichier
        parse_config(str(fichier))
```

Pour vérifier le message d'erreur, en plus du type d'exception levée, l'argument `match` peut vérifier que le message correspond à une regex :
```python
def test_ligne_sans_egal(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("une ligne sans le signe egal\n")

    with pytest.raises(ValueError, match="does not comply KEY=VALUE format"):
        parse_config(str(fichier))
```

>⚠️ PIÈGE ⚠️ `match` traite la chaîne comme une **regex**, pas comme du texte brut.
>Si le message contient un caractère spécial regex (par ex`()` ou `.`), il faudra soit l'échapper avec `re.escape()`, soit tester un extrait du message sans caractères spéciaux.

##### TEST 3 : Fichiers vide, avec seulement des lignes vides, avec seulement des commentaires

Dans le cas d'un fichier ne contenant rien, il s'agira de vérifier qu'un dictionnaire vide est retourné :
```python
def test_fichier_vide_ou_commentaires(tmp_path):
    fichier = tmp_path / "config.txt"
    # créer fichier, sans contenu
    fichier.write_text("")

    # assert doit vérifier l'égalité
    assert parse_config(str(fichier)) == {}
  

def test_fichier_lignes_vides(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("#\n\n")  

    assert parse_config(str(fichier)) == {}


def test_fichier_commentaires(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("# uniquement du commentaire")  

    assert parse_config(str(fichier)) == {}  
```


## 4. Fixtures

Une fixture `pytest` est une **fonction réutilisable** dans plusieurs tests, injectée automatiquement par `pytest` quand on la déclare comme paramètre : elle **prépare une donnée** (ou un objet, une connexion, un fichier...) et **la fournit à un ou plusieurs tests**, sans que ces tests aient besoin de savoir comment elle a été construite.

Si plusieurs tests ont besoin de la même donnée de départ, sans fixture il faudrait la recréer à chaque fois :
```python
# utilisateur = {"nom": "Alice", "age": 30}
# SANS FIXTURE, 3 tests = 3x la même ligne copiée-collée :

def test_un():
    utilisateur = {"nom": "Alice", "age": 30}
    assert utilisateur["nom"] == "Alice"

def test_deux():
    utilisateur = {"nom": "Alice", "age": 30}
    assert utilisateur["age"] == 30

def test_trois():
    utilisateur = {"nom": "Alice", "age": 30}
    utilisateur["age"] += 1
    assert utilisateur["age"] == 31

# et pour changer `"age": 30` en `"age": 25`, il faut le faire à 3 endroits...
```

Une fixture nécessite :
+ le **décorateur `@pytest.fixture`** au-dessus de la fonction qui prépare la donnée ;
+ le **nom de la fixture** comme **paramètre** des fonctions de test qui veulent l'utiliser.

```python
import pytest

@pytest.fixture   # décorateur au-dessus de la fonction qui prépare la donnée
def utilisateur():
    return {"nom": "Alice", "age": 30}


def test_un(utilisateur):   # nom de la fixture comme paramètre
    assert utilisateur["nom"] == "Alice"

def test_deux(utilisateur):   # nom de la fixture comme paramètre
    assert utilisateur["age"] == 30
```

C'est de l'*injection de dépendances* : on n'appelle jamais `utilisateur()`, `pytest` le fait pour nous au bon moment :
+ `pytest` voit que `test_un` a un paramètre appelé `utilisateur`,
+ il cherche une fixture qui s'appelle `utilisateur`,
+ exécute la fixture,
+ injecte sa valeur de retour comme argument du test.

>**IMPORTANT : chaque test reçoit une copie fraîche.**
>Une *variable globale* serait partagée et mutable entre tous les tests, alors que par défaut la *fixture* est ré-exécutée pour chaque test qui la demande : si un test modifie la donnée, ça n'affecte pas les autres tests, chaque test part d'un état propre.
>C'est ce qui rend les tests indépendants les uns des autres => l'ordre d'exécution des tests ne doit JAMAIS influencer leur résultat !

##### Fixture plus riche

Une fixture peut faire plus qu'un simple `return`, par ex préparer puis nettoyer une ressource :
```python
@pytest.fixture
def compte_bancaire():
    print("\n--- Ouverture du compte ---")
    compte = {"solde": 100}
    return compte

def test_depot(compte_bancaire):
    compte_bancaire["solde"] += 50
    assert compte_bancaire["solde"] == 150

def test_solde_initial(compte_bancaire):
    assert compte_bancaire["solde"] == 100
```
```bash
# console :
pytest -s  # `-s` affiche les `print
# affiche :
--- Ouverture du compte ---
--- Ouverture du compte ---
```

##### `tmp_path` : fixture intégrée

`tmp_path` est une fixture livrée avec `pytest` : dès qu'on déclare un paramètre nommé **tmp_path** dans un test, `pytest` reconnaît ce nom réservé et fournit automatiquement un objet `Path` pointant vers un **dossier temporaire**, **vide**, **unique**.

```python
def test_creation_fichier(tmp_path):
	# spécialement pour ce test, un dossier qui n'existait pas avant vient d'être créé sur le disque
    print(tmp_path)  # ex: /tmp/pytest-xyz/test_creation_fichier0
```
```bash
# console :
pytest -s
# affiche :
/tmp/pytest-of-.../pytest-.../test_creation_fichier0
```

+ Écrire et lire un fichier
```python
def test_ecriture_lecture(tmp_path):
	# `tmp_path / "notes.txt"` fonctionne comme une concaténation de chemin
	# grâce à `pathlib.Path`, classe utilisée par `tmp_path`, donc quel que soit l'OS.
    fichier = tmp_path / "notes.txt"         # construit le chemin (n'existe pas encore)
    fichier.write_text("bonjour")            # crée le fichier et écrit dedans

    assert fichier.exists()                  # le fichier existe bien maintenant
    assert fichier.read_text() == "bonjour"  # on peut relire ce qu'on a écrit
```

+ indépendance entre tests
```python
# chaque test obtient un `tmp_path` frais

def test_un(tmp_path):
    (tmp_path / "fichier.txt").write_text("contenu du test 1")
    fichiers = list(tmp_path.iterdir())
    assert len(fichiers) == 1

# ce que `test_un` a écrit sur le disque n'existe pas pour `test_deux`
def test_deux(tmp_path):
    # ce test reçoit un dossier tmp_path totalement différent et vide,
    # même s'il porte "le même nom de paramètre"
    fichiers = list(tmp_path.iterdir())
    assert len(fichiers) == 0
```

## 5. Tests fixtures

##### TEST 4 : Fichiers avec champs obligatoires manquants

```python
# Création d'un dictionnaire "valide de référence", nécessaire pour nombres de tests à venir
@pytest.fixture
def config_valide():
	# ce que `parse_config()` produirait à partir de `config,txt`
    return {
	    "WIDTH": "100", "HEIGHT": "100",
		"ENTRY": "0,0", "EXIT": "6,10",
		"OUTPUT_FILE": "maze.txt",
	}

# ----- TEST pour 1 champ manquant -----

# un `config_valide` propre est injecté par pytest qui va chercher la fixture correspondante
def test_width_manquant(config_valide):
    # on simule l'absence de `WIDTH` en le supprimant
    del config_valide["WIDTH"]

    with pytest.raises(ValidationError):
        MazeConfig(**config_valide)

```

>VOCABULAIRE :
>_fixture_ = donnée réutilisable injectée ;
>_parametrize_ = plusieurs jeux de valeurs pour un même test.
```python
# ----- TEST pour chacun des 5 champs potentiellement manquant -----

# @pytest.mark.parametrize permet de définir plusieurs ensembles d'arguments et de fixtures
@pytest.mark.parametrize("champ_manquant", ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",])
# un `config_valide` propre est injecté par pytest qui va chercher la fixture correspondante
def test_champ_obligatoire_manquant(config_valide, champ_manquant):	
    # on simule successivement l'absence d'un champ obligatoire en le supprimant
    del config_valide[champ_manquant]

    with pytest.raises(ValidationError):
        MazeConfig(**config_valide)
```
