import pytest
from pydantic import ValidationError

from src.maze_app.parsing.config_parser import parse_config
from src.maze_app.parsing.models import MazeConfig


def test_fichier_introuvable(tmp_path):
    # construit un chemin (un objet `Path`) qui pointe vers un fichier, dans un dossier temporaire propre
    fichier = tmp_path / "config.txt"
    # /!\ `fichier` est un objet `Path`, pas une string...

    # `with` ne doit entourer QUE l'appel censé échouer
    with pytest.raises(FileNotFoundError):
        # `parse_config(file_path: str)` attend une string, il faut convertir l'objet `Path`.
        parse_config(str(fichier))


def test_ligne_sans_egal(tmp_path):
    # construit un chemin (un objet `Path`) qui pointe vers un fichier, dans un dossier temporaire propre
    fichier = tmp_path / "config.txt"
    # /!\ `fichier` est un objet `Path`, pas une string...

    # `with` ne doit entourer QUE l'appel censé échouer
    with pytest.raises(FileNotFoundError):
        # `parse_config(file_path: str)` attend une string, il faut convertir l'objet `Path`.
        parse_config(str(fichier))


def test_fichier_vide(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("")

    # assert doit vérifier l'égalité
    assert parse_config(str(fichier)) == {}


def test_fichier_commentaires(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("# uniquement du commentaire")

    # assert doit vérifier l'égalité
    assert parse_config(str(fichier)) == {}


def test_fichier_lignes_vides(tmp_path):
    fichier = tmp_path / "config.txt"
    fichier.write_text("#\n\n")

    # assert doit vérifier l'égalité
    assert parse_config(str(fichier)) == {}
