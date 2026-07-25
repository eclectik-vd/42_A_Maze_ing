all: install run

install:
	@# uv sync est TRES intelligent :P
	@# il lit aveuglément le lockfile (uv.lock) existant,
	@# crée le .venv s'il est absent,
	@# y installe exactement les dépendances issues du `pyproject.toml`.
	uv sync --group app

update:
	@# pour forcer la mise à jour de uv.lock si il y a eu modif manuelle
	@# des dépendances dans pyproject.toml
	uv lock --upgrade
	uv sync --group app

test:
	uv run pytest tests/

run:
	uv run a_maze_ing.py config.txt

build:
	@# lire pyproject.toml et générer archives .tar.gz et .whl dans dist/
	uv build

debug:
	uv run python3 -m pdb a_maze_ing.py config.txt

lint:
	@# Les outils liront leurs configurations,
	@# respectivement consignées dans `.flake8` et `pyproject.toml`
	uv run flake8 .
	uv run  mypy .

lint-strict:
	uv run flake8 .
	uv run  mypy --strict .

# supprime tout ce qui est régénérable automatiquement
clean:
	rm -rf .mypy_cache .pytest_cache build dist
	@find . -type d -name "__pycache__" -exec rm -rf {} +

# supprime en plus ce qui nécessite une action manuelle pour être reconstruit
fclean: clean
	rm -rf .venv uv.lock

.PHONY: all install update run build debug lint lint-strict clean fclean