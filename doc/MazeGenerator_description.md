# -------------------------- ATTRIBUTS --------------------------

## Attributs de classe
+ `N`, `E`, `S`, `W`: Bitmasks représentant chacun des 4 murs (Nord, Est, Sud, Ouest) d'une cellule.
+ `ALL_WALLS`: Combinaison des 4 bitmasks (N | E | S | W), état initial d'une cellule avec tous ses murs fermés.
+ `PATTERN_42`: Coordonnées relatives du motif "42" à dessiner dans la grille.
+ `PATTERN_WIDTH`, `PATTERN_HEIGHT`: Dimensions (largeur, hauteur) du motif "42".

## Attribut d'instance interne
+ `_rng`: Générateur pseudo-aléatoire (random.Random), initialisé avec la seed fournie.
+ `_is_generated`: Booléen indiquant si le labyrinthe a déjà été généré (contrôle l'accès à certaines méthodes comme solve_maze ou _make_imperfect).

## Attributs d'instance protégés
+ `_width` (→ property width): Nombre de colonnes de la grille.
+ `_height` (→ property height): Nombre de lignes de la grille.
+ `_entry_coord` (→ property entry_coord): Coordonnées (x, y) de l'entrée du labyrinthe.
+ `_exit_coord` (→ property exit_coord): Coordonnées (x, y) de la sortie du labyrinthe.
+ `_grid` (→ property grid): Grille interne, où chaque cellule est un entier (bitmask des murs).
+ `_exit_path` (→ property exit_path): Chemin (suite de directions) entre l'entrée et la sortie, une fois résolu.

## Attributs d'instance publics
+ `perfect`: Indique si le labyrinthe doit rester parfait (sans boucle).
+ `output_file`: Nom du fichier vers lequel exporter le labyrinthe.
+ `pattern_cells`: Ensemble des cellules verrouillées par le motif "42", si celui-ci a été appliqué.

# -------------------------- METHODES --------------------------

## Instanciation
+ `__init__`: Initialise le générateur et valide les paramètres (taille ≥ 3x3, coordonnées dans la grille, entrée ≠ sortie).

## Properties
+ `width`, `height`, `entry_coord`, `exit_coord`: Accès protégé aux paramètres de configuration fixés à la construction.
+ `grid`: Retourne une copie profonde de la grille interne.
+ `exit_path`: Retourne le chemin trouvé entre l'entrée et la sortie.

## Méthodes internes (privées)
+ `_apply_42_pattern()`: Tente de placer le motif "42" au centre de la grille, en verrouillant les cellules concernées.
+ `_get_unvisited_adjacents()`: Retourne les cellules adjacentes non visitées et valides autour d'une cellule (x, y).
+ `_break_wall()`: Casse le mur d'une cellule dans une direction donnée, ainsi que le mur opposé de la cellule adjacente.
+ `_generate_perfect_maze()`: Génère un labyrinthe parfait (sans boucle) avec l'algorithme du Recursive Backtracker.
+ `_make_imperfect()`: Rend le labyrinthe imparfait en cassant aléatoirement des murs de culs-de-sac.

## Réinitialisation
+ `reset()`: Réinitialise l'état interne du labyrinthe (grille, motif, chemin, flag de génération).
+ `regenerate()`: Réinitialise puis régénère le labyrinthe, avec possibilité de changer la seed.

## Vérification de validité
+ `check_walls_integrity()`: Vérifie la cohérence des murs entre cellules adjacentes.
+ `is_3x3_open()`: Vérifie si une zone 3x3 donnée est entièrement ouverte, sans mur interne.
+ `free_of_open_areas()`: Vérifie qu'il n'existe aucune zone ouverte de 3x3 cellules ou plus dans tout le labyrinthe.

## Résolution et Export
+ `solve_maze()`: Trouve le plus court chemin entre l'entrée et la sortie via un parcours en largeur (BFS).
+ `export_to_file()`: Exporte la grille, les coordonnées d'entrée/sortie et le chemin solution dans output_file.

## Orchestration globale
+ `generate()`: Enchaîne toutes les étapes : génération parfaite, imperfection éventuelle, vérification des règles internes, résolution, puis export.