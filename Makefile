# Choix d'utiliser uv :
# inutile de déclarer des variables pour forcer l'usqge du venv car uv détecte 
# automatiquement l'OS et exécute le bon fichier :
#    .venv/bin/... sous Linux/macOS;
#    .venv\Scripts\... sous Windows.
# => si chgt d'environnement, uv gèrera les chemins spécifiques à l'OS.

# Default rule
all: install
	make run

install:
	# uv sync est TRES intelligent :P
	# il lit aveuglément le lockfile (uv.lock) existant,
	# crée le .venv s'il est absent,
	# y installe exactement les dépendances issues du `pyproject.toml`.
	uv sync

update:
	# pour forcer la mise à jour de uv.lock si il y a eu modif manuelle
	# des dépendances dans pyproject.toml
	uv lock --upgrade
	uv sync

test:
	# TODO: mettre en place des tests avec pytest
	uv run pytest tests/

run:
	uv run a_maze_ing.py config.txt

build:
	# lire pyproject.toml ( /!\ y compléter [build-system] /!\ )
	# générer l'archive .tar.gz et le fichier .whl dans un dossier dist/
	uv build

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

lint:
	# Les outils liront leurs configurations,
	# respectivement consignées dans `.flake8` et `pyproject.toml`
	uv run flake8 .
	uv run  mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

# vérification stricte
lint-strict:
	uv run flake8 .
	uv run  mypy --strict .

# supprimer caches + dossiers de compilation du futur module (`build` et `dist`)
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache build dist

fclean: clean
	rm -rf .venv uv.lock
	@find . -type d -name "__pycache__" -exec rm -rf {} +

# éviter conflits avec des fichiers portant le même nom
.PHONY: all install update run build debug lint lint-strict clean fclean