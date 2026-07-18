import pytest
from pydantic import ValidationError

from src.maze_app.parsing.models import MazeConfig


# Création d'un dictionnaire valide de référence
@pytest.fixture
def config_valide():
	# un dict que `parse_config()` produirait à partir de `config,txt`
    return {
	    "WIDTH": "100", "HEIGHT": "100",
		"ENTRY": "0,0", "EXIT": "6,10",
		"OUTPUT_FILE": "maze.txt",
	}


# ----- TEST pour chacun des 5 champs potentiellement manquant -----

# @pytest.mark.parametrize permet de définir plusieurs ensembles d'arguments et de fixtures
@pytest.mark.parametrize("champ_manquant", ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",])
# un `config_valide` propre est injecté par pytest qui va chercher la fixture correspondante
def test_champ_obligatoire_manquant(config_valide, champ_manquant):	
    # on simule successivement l'absence d'un champ obligatoire en le supprimant
    del config_valide[champ_manquant]

    with pytest.raises(ValidationError):
        MazeConfig(**config_valide)


def test_width_is_int(config_valide):
    config_valide["WIDTH"] = "NOT AN INT"

    with pytest.raises(ValidationError):
        MazeConfig(**config_valide)
