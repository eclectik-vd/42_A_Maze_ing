  

QUESTIONS

- [x] You must implement the maze generation as a unique class (e.g., ‘MazeGenerator‘) inside a standalone module that can be imported in a future project.
- [x] Makefile `all` = install + run
- [x] width/height max : 200 -> 100 ? => à mentionner dans le readme



CODE

- [ ] FIX : crash sur [ctrl]+[C] en display ascii
		=> ajouter try/except sur KeyboardInterrupt
- [ ] MANDATORY : build (Enzo)
- [ ] MANDATORY : afficher message quand 42 pattern ne peut pas être inclus dans le labyrinthe
- [ ] ! MyPy KO sur tests/test_player.py
- [ ] transformer en variables les 64, 32... du code display
- [ ] DOC : maj flux global dans readme
- [ ] FIX : # start_x, start_y = self.entry_coord dans solve_maze()


- [x] FIX : seed regenerate bug si pas int...
- [x] FIX : ascii menu contient 4 choix et propose `choice (1-5)`
- [x] MANDATORY : afficher chemin (ASCII)
- [x] REFACT : dossier mazegen pour modulariser mazegen.py
- [x] FIX : .export.py à appeler après chaque génération VS inclure dans mazegen
- [x] FIX : .gitignore
- [x] FIX : output AVANT display
- [x] FIX : git add licence
- [x] FIX : export OUTPUT après chaque (re)génération
- [x] BONUS : déplacements du joueur avec Arcade
- [x] youpi qd joueur sur case arrivee
- [x] BONUS : labyrinthe imparfait sans cul-de-sac
- [x] BONUS : paramètres en ligne de commande : seed, display_mode, perfect  
- [x] BONUS : test pytest 
- [x] BONUS : sons / musique


README
- [ ] 4/ module réutilisable : à rédiger/vérifier/corriger...
- [ ] 2/ architecture : mettre à jour arbo slim avec architecture finale
- [ ] ressources : manque packaging
- [ ] redim capt (taille + poids)
- [ ] Trad en anglais Gemini
- [x] flux global : verif avec Enzo + maj mef flowchart avec styles persos
- [x] NE PAS re-numéroter sous la forme 1  1.1  1.2  1.3 ... 2  2.1  2.2  

NETTOYAGE
- [ ] supprimer/transférer (Obsidian ou doc) dossiers/fichiers/commentaires superflus
- [ ] typehints
- [ ] docstring
- [ ] flake8 mypy
- [ ] CHECK maze_analyzer
- [ ] CHECK CORR BENJI


