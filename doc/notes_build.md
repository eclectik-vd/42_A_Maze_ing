## `.tar.gz` et `.whl` 

Ce sont des **archives** (cf `.zip`) spécialisées pour la distribution de code Python :
- **`.tar.gz`** = code source du package simplement compressé. Pour (ré)installer le package, il faudra (re)construire localement ce dossier complet du projet.
- **`.whl`** (*wheel*) = version **prête à l'emploi**, ne nécessitera pas de compilation/construction, juste un `pip install` pour le déposer dans le bon dossier.

En plus du code Python, ces archives contiennent des métadonnées (nom, version, dépendances...) tirées du `pyproject.toml`.
## pyproject.toml

#### outil

`uv build` doit savoir avec quel outil construire le package.
Il faut choisir un **build-backend** , l'outil qui sait transformer le code + les métadonnées en `.tar.gz`/`.whl`  : **`hatchling`** est le plus simple et recommandé (léger et sans `setup.py` à écrire) pour un projet géré avec `uv`.

#### portée du package

`hatchling` sait détecter **automatiquement** un module unique quand son nom correspond au nom du projet, dans un dossier `src/`.  Par ex,  `hatchling` saurait reconnaître tout seul le layout  `src/mazegen.py`.

Mais pour être explicite, ie ne pas compter sur une détection automatique moins lisible et plus chiante à expliquer/déboguer, mieux vaut le configurer explicitement :
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# pour le .whl uniquement
[tool.hatch.build.targets.wheel]
# empaqueter UNIQUEMENT ce fichier
include = ["src/mazegen.py"]
[tool.hatch.build.targets.wheel.sources]
# "rebaser" le contenu de `src/` vers la racine du wheel
"src" = ""

# pour le `.tar.gz` (ooops, par défaut `hatchling` embarque tout ce qui n'est pas ignoré par le .gitignore)
[tool.hatch.build.targets.sdist]
include = [
    "src/mazegen.py",
    "pyproject.toml", # ce fichier dit à `pip`/`build` avec quel outil et comment construire le package
    "README.md",      # référencé explicitement dans les métadonnées, son contenu sera la description longue du package
    "LICENSE.md",     # bonne pratique, la licence doit accompagner un module réutilisable et redistribuable
]
```


/!\ Il faut EVITER que le package installe AUSSI `arcade`, `pydantic` et `colorama`  /!\ 

1. adapter le `pyproject.toml` en modifiant les dépendances :
```toml
# le package mazegen n'a besoin de rien d'externe
dependencies = []

[dependency-groups]
dev = [
    "flake8>=7.3.0",
    "mypy>=2.1.0",
    "pytest>=9.1.1",
]
app = [
    "arcade>=3.3.3",
    "colorama>=0.4.6",
    "pydantic>=2.13.4",
]
```

2. adapter le Makefile en mettant à jour la cible `install` pour qu'elle installe ce dont l'app a besoin en local :
```makefile
install:
	# le groupe `dev` est inclus par défaut par `uv sync`, mais `app` doit être demandé explicitement...
	uv sync --group app
```

## make build

Une fois le `pyproject.toml` correctement paramétré, `make build` va créer automatiquement `mazegen-<version>-py3-none-any.whl` et `mazegen-<version>.tar.gz` :
```bash
uv build
# uv lit le `pyproject.toml`
# puis crée les deux archives dans un dossier `dist/`.
```

## pip install

On récupère ensuite le module depuis la racine du répertoire où on aura copié `dist` :
```bash
# installation via le .whl
pip install dist/mazegen-0.1.0-py3-none-any.whl
# Processing ./dist/mazegen-0.1.0-py3-none-any.whl
# Installing collected packages: mazegen
# Successfully installed mazegen-0.1.0
```

ou bien :
```bash
# installation via le .tar.gz
pip install dist/mazegen-0.1.0.tar.gz
# `pip` décompresse l'archive,
# lit `pyproject.toml` pour savoir quel build-backend appeler (ici `hatchling`),
# appelle ce backend pour fabriquer un wheel à la volée.
```

Une fois installé, l'utilisateur pourra faire `from mazegen import MazeGenerator`, usage à préciser dans la docstring.

## Vérifs que tout roule

#### module autonome ?

Pour vérifier que le module est autonome, le tester **en isolation totale** , donc dans un venv vide.

Si on a copié `dist/` dans un répertoire `correction` :
```bash
cd correction

# créer et activer un venv
python3 -m venv check_mazegen
source check_mazegen/bin/activate

#installer le package
pip install dist/mazegen-0.1.0-py3-none-any.whl

# générer un labyrinthe
python -c "from mazegen import MazeGenerator; maze = MazeGenerator(width=10, height=10, entry_coord=(0, 0), exit_coord=(9, 9), seed=42, perfect=True, output_file='maze.txt'); maze.generate()"
# => le dossier correction contient désormais maze.txt avec le labyrinthe et sa solution :)
```

#### Reproductibilité avec `seed` ?

Deux instances avec le même seed doivent produire la même grille :
```bash
python -c "
from mazegen import MazeGenerator
m1 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed1.txt')
m2 = MazeGenerator(width=10, height=10, entry_coord=(0,0), exit_coord=(9,9), seed=42, perfect=True, output_file='seed2.txt')
m1.generate(); m2.generate()
assert m1.grid == m2.grid, 'Grilles différentes malgré le même seed !'
print('OK : reproductibilité confirmée')
"
```

#### Gestion d'erreur sur taille invalide

Par ex lever `ValueError` si `width`/`height` < 3 :
```
python -c "
from mazegen import MazeGenerator
try:
    MazeGenerator(width=2, height=2, entry_coord=(0,0), exit_coord=(1,1), seed=1, perfect=True, output_file='x.txt')
    print('ERREUR : aucune exception levée')
except ValueError as e:
    print('OK :', e)
"
```






