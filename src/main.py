# -*- coding: utf-8 -*-

# Nicolas, 2026-02-09
from __future__ import absolute_import, print_function, unicode_literals

<<<<<<< HEAD
import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo
=======
import random
import numpy as np
import pygame

from pySpriteWorld.gameclass import Game
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.ontology import Ontology
>>>>>>> aa6641c (Ajout projet IA + rapport final)

from search.grid2D import ProblemeGrid2D
from search import probleme


<<<<<<< HEAD






=======
>>>>>>> aa6641c (Ajout projet IA + rapport final)
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

<<<<<<< HEAD
def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'mixed-map'
    #game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10  # frames per second
    game.mainiteration()
    player = game.player
    
def main():

    #for arg in sys.argv:
    #iterations = 40 # nb de pas max par episode
    #if len(sys.argv) == 2:
    #    iterations = int(sys.argv[1])
    #print ("Iterations: ")
    #print (iterations)

    init()
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker le contour)
    lMax=nb_lignes-2
    cMin=2
    cMax=nb_cols-2
   
    
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)


    items = [o for o in game.layers["ramassable"]]  #
    nb_fioles = len(items)

    nb_episodes = 2


    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets ou de joueurs
    #-------------------------------

    def item_states(items):
        # donne la liste des coordonnees des items
        return [o.get_rowcol() for o in items]
    
    def player_states(players):
        # donne la liste des coordonnees des joueurs
        return [p.get_rowcol() for p in players]
    


    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs:', nb_players)
    print("fioles:",nb_fioles)
    print("lignes:", nb_lignes)
    print("colonnes:", nb_cols)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo yellow
    # 2 x 8 joueurs
    # 5 fioles jaunes
    #-------------------------------

    team = [[], []]  # 2 équipes
    for o in players:
        (x, y) = o.get_rowcol()
        if x == 2:  # les joueurs de team0 sur la ligne du haut
            team[0].append(o)
        elif x == 18:  # les joueurs de team1 sur la ligne du bas
            team[1].append(o)

    assert len(team[0]) == len(team[1])  # on veut un match équilibré donc équipe de même taille
    nb_players_team = int(nb_players / 2)

    init_states = [[],[]]
    # print(teamA)
    init_states[0] = player_states(team[0])

    # print(teamB)
    init_states[1] = player_states(team[1])


    #-------------------------------

    #-------------------------------
    # Fonctions definissant les positions legales et placement aléatoire
    #-------------------------------

    def around_pos(pos):
        # donne la liste des positions autour d'une pos (x,y) donnee
        x,y=pos
        return [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]

    def around_pos_free(pos):
        return [pos for pos in around_pos(pos) if legal_position(pos)]
=======

def init(_boardname=None):
    global player, game
    name = _boardname if _boardname is not None else 'mixed-map'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 10
    game.mainiteration()
    player = game.player


def main():

    init()

    # ----------------------------------------
    # Initialisation
    # ----------------------------------------

    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols

    lMin = 2
    lMax = nb_lignes - 2
    cMin = 2
    cMax = nb_cols - 2

    players = [o for o in game.layers['joueur']]
    nb_players = len(players)

    items = [o for o in game.layers["ramassable"]]
    nb_fioles = len(items)

    nb_episodes = 3

    print("Lecture carte")
    print("-------------------------------------------")
    print('Joueurs :', nb_players)
    print("Fioles  :", nb_fioles)
    print("Lignes  :", nb_lignes)
    print("Colonnes:", nb_cols)
    print("-------------------------------------------")

    # ----------------------------------------
    # Détection des équipes
    # ----------------------------------------

    team = [[], []]
    for o in players:
        x, y = o.get_rowcol()
        if x == 2:
            team[0].append(o)
        elif x == 18:
            team[1].append(o)

    # ordre stable gauche -> droite
    team[0].sort(key=lambda p: p.get_rowcol()[1])
    team[1].sort(key=lambda p: p.get_rowcol()[1])

    assert len(team[0]) == len(team[1])
    nb_players_team = len(team[0])

    init_states = [[], []]
    init_states[0] = [p.get_rowcol() for p in team[0]]
    init_states[1] = [p.get_rowcol() for p in team[1]]

    # ----------------------------------------
    # Scores cumulés sur tous les épisodes
    # ----------------------------------------

    scores_totaux = [0, 0]

    # ----------------------------------------
    # Fonctions utilitaires
    # ----------------------------------------

    def item_states(items_list):
        return [o.get_rowcol() for o in items_list]

    def player_states(players_list):
        return [p.get_rowcol() for p in players_list]

    def around_pos(pos):
        x, y = pos
        return [
            (x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
            (x,     y - 1),             (x,     y + 1),
            (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)
        ]

    def legal_position(pos):
        row, col = pos
        return (
            (pos not in item_states(items)) and
            (pos not in player_states(players)) and
            (row > lMin) and
            (row < lMax) and
            (col >= cMin) and
            (col < cMax)
        )

    def around_pos_free(pos):
        return [p for p in around_pos(pos) if legal_position(p)]
>>>>>>> aa6641c (Ajout projet IA + rapport final)

    def busy(pos):
        return around_pos_free(pos) == []

<<<<<<< HEAD
    def legal_position(pos):
        row,col = pos
        # une position legale est dans la carte et pas sur une fiole ni sur un joueur
        return ((pos not in item_states(items)) and (pos not in player_states(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)


    def players_around_item(f):
        """
        :param f: objet fiole
        :return: nombre d'objet de chaque team
        """
        are_here = [0,0]
        pos = f.get_rowcol()
        for i in [0,1]:
            for j in team[i]:
                if j.get_rowcol() in around_pos(pos):
                    are_here[i]+=1
        return are_here




    # -------------------------------
    # Strategie aleatoire
    # -------------------------------


    for e in range(nb_episodes):
        priority=[0,1]
        for t in priority:
            print("Team ",t)
            path = []
            choix_fiole = []
            choix_pos = []
            for p in range(0,nb_players_team):
                f = random.choice(items)
                while busy(f.get_rowcol()): # si plus de place on choisit une autre fiole
                    f = random.choice(items)
                choix_fiole.append(f)
                # choisir une position libre autour de la fiole choisie
                chosen_pos = random.choice(around_pos_free(f.get_rowcol()))
                choix_pos.append(chosen_pos)

                pos_player = team[t][p].get_rowcol()
                print("Player ", p, " starting from ", pos_player, " going to potion ", choix_fiole[p].get_rowcol(), " at ", choix_pos[p])

                # -------------------------------
                # calcul A* pour le joueur
                # -------------------------------

                g = np.ones((nb_lignes, nb_cols), dtype=bool)  # une matrice remplie par defaut a True

                for i in range(nb_lignes):  # on exclut aussi les bordures du plateau
                    g[0][i] = False
                    g[1][i] = False
                    g[nb_lignes - 1][i] = False
                    g[nb_lignes - 2][i] = False
                    g[i][0] = False
                    g[i][1] = False
                    g[i][nb_lignes - 1] = False
                    g[i][nb_lignes - 2] = False
                prob = ProblemeGrid2D(pos_player, choix_pos[p], g, 'manhattan')
                path.append(probleme.astar(prob, verbose=False))
                print("Chemin trouvé:", path[p])


                #-------------------------------
                # Boucle principale de déplacements
                #-------------------------------

                # on fait bouger le joueur jusqu'à son but
                # en suivant le chemin trouve avec A*

                for i in range(len(path[p])):  # si le joueur n'est pas deja arrive
                    (row, col) = path[p][i]
                    team[t][p].set_rowcol(row, col)
                    print("pos joueur:",  row, col)

                    # mise à jour du pleateau de jeu
                    game.mainiteration()








        # -------------------------------
        # Calcul des scores
        # -------------------------------


        # calcul du nombre de joueurs autour de chaque fiole
        for o in items:
            print(players_around_item(o))



        # calcul des points
        #TODO

        # remettre les joueurs à leur pos initiale a la fin de l'episode

        for i in [0,1]:
            j=0
            for p in team[i]:
                x,y = init_states[i][j]
                p.set_rowcol(x,y)
                j+=1


    pygame.quit()

    
    #-------------------------------

    
   

if __name__ == '__main__':
    main()
    


=======
    def players_around_item(f):
        """Retourne [nb_joueurs_team0, nb_joueurs_team1] autour de la fiole f."""
        count = [0, 0]
        pos = f.get_rowcol()
        neighbours = around_pos(pos)

        for i in [0, 1]:
            for p in team[i]:
                if p.get_rowcol() in neighbours:
                    count[i] += 1
        return count

    def get_fiole_type(fiole):
        """
        Détermine le type d'une fiole à partir de son tileid.
        """
        TILEID_TO_COLOR = {
            (19, 1): 'yellow',   # coins : (6,6),(6,14),(14,6),(14,14)
            (21, 1): 'green',    # milieu haut/bas : (6,10),(14,10)
            (17, 4): 'red',      # milieu gauche/droite : (10,6),(10,14)
            (18, 4): 'blue',     # centre : (10,10)
        }

        tid = getattr(fiole, 'tileid', None)
        if tid in TILEID_TO_COLOR:
            return TILEID_TO_COLOR[tid]

        print(f"[WARN] tileid inconnu {tid} pour fiole {fiole.get_rowcol()}")
        return 'yellow'

    def resolve_fiole(ftype, count):
        """
        Applique les règles de collecte.
        count = [nb_T0, nb_T1]
        Retourne 0, 1, ou None.
        """
        t0, t1 = count

        if ftype == 'yellow':
            t0_ok = t0 >= 1
            t1_ok = t1 >= 1

            if t0_ok and t1_ok:
                if t0 > t1:
                    return 0
                elif t1 > t0:
                    return 1
                return None
            elif t0_ok:
                return 0
            elif t1_ok:
                return 1
            return None

        elif ftype == 'red':
            t0_ok = t0 >= 2
            t1_ok = t1 >= 2

            if t0_ok and t1_ok:
                if t0 > t1:
                    return 0
                elif t1 > t0:
                    return 1
                return None
            elif t0_ok:
                return 0
            elif t1_ok:
                return 1
            return None

        elif ftype == 'green':
            total = t0 + t1
            if total < 3:
                return None
            if t0 > t1:
                return 0
            elif t1 > t0:
                return 1
            return None

        elif ftype == 'blue':
            t0_ok = t0 >= 2
            t1_ok = t1 >= 2

            if t0_ok and t1_ok:
                if t0 > t1:
                    return 0
                elif t1 > t0:
                    return 1
                return None
            elif t0_ok and t1 == 1:
                return 1
            elif t1_ok and t0 == 1:
                return 0
            elif t0_ok:
                return 0
            elif t1_ok:
                return 1
            return None

        return None

    def build_grid():
        """
        Construit la grille A*.
        Bordures bloquées + cases des fioles bloquées.
        """
        g = np.ones((nb_lignes, nb_cols), dtype=bool)

        for i in range(nb_lignes):
            g[0][i] = False
            g[1][i] = False
            g[nb_lignes - 1][i] = False
            g[nb_lignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nb_cols - 1] = False
            g[i][nb_cols - 2] = False

        for it in items:
            r, c = it.get_rowcol()
            g[r][c] = False

        return g

    # ----------------------------------------
    # Boucle principale des épisodes
    # ----------------------------------------

    for e in range(nb_episodes):
        print(f"\n========== EPISODE {e+1}/{nb_episodes} ==========")

        # priorité inversée à chaque joueur
        for p in range(nb_players_team):

            if (e + p) % 2 == 0:
                priority = [0, 1]
            else:
                priority = [1, 0]

            for t in priority:
                print(f"\n  -- Joueur {p}, équipe {t} --")

                # Choix aléatoire d'une fiole avec une position libre
                f = random.choice(items)
                attempts = 0
                while busy(f.get_rowcol()) and attempts < 20:
                    f = random.choice(items)
                    attempts += 1

                free_positions = around_pos_free(f.get_rowcol())
                if not free_positions:
                    chosen_pos = team[t][p].get_rowcol()
                else:
                    chosen_pos = random.choice(free_positions)

                pos_player = team[t][p].get_rowcol()
                print(f"  Joueur {p} : {pos_player} → fiole {f.get_rowcol()} (pos cible {chosen_pos})")

                # Calcul du chemin A*
                g = build_grid()
                prob = ProblemeGrid2D(pos_player, chosen_pos, g, 'manhattan')
                chemin = probleme.astar(prob, verbose=False)

                # Déplacement du joueur
                for (row, col) in chemin:
                    team[t][p].set_rowcol(row, col)
                    game.mainiteration()

        # ----------------------------------------
        # Calcul des scores de l'épisode
        # ----------------------------------------

        print(f"\n  -- Résultats épisode {e+1} --")
        scores_episode = [0, 0]

        for fiole in items:
            count = players_around_item(fiole)
            ftype = get_fiole_type(fiole)
            winner = resolve_fiole(ftype, count)

            print(f"  Fiole {ftype:6s} {fiole.get_rowcol()} | T0:{count[0]}  T1:{count[1]} → ", end="")
            if winner is not None:
                scores_episode[winner] += 1
                print(f"Équipe {winner} marque !")
            else:
                print("Personne ne marque")

        scores_totaux[0] += scores_episode[0]
        scores_totaux[1] += scores_episode[1]

        print(f"\n  Score épisode : T0={scores_episode[0]}  T1={scores_episode[1]}")
        print(f"  Score cumulé  : T0={scores_totaux[0]}  T1={scores_totaux[1]}")

        # Remise à la position initiale
        for i in [0, 1]:
            for j, p in enumerate(team[i]):
                x, y = init_states[i][j]
                p.set_rowcol(x, y)

        game.mainiteration()

    # ----------------------------------------
    # Résultat final
    # ----------------------------------------

    print("\n==========================================")
    print("           RÉSULTAT FINAL")
    print("==========================================")
    print(f"  Équipe 0 : {scores_totaux[0]} points")
    print(f"  Équipe 1 : {scores_totaux[1]} points")
    if scores_totaux[0] > scores_totaux[1]:
        print("  🏆 Équipe 0 gagne !")
    elif scores_totaux[1] > scores_totaux[0]:
        print("  🏆 Équipe 1 gagne !")
    else:
        print("  🤝 Égalité !")
    print("==========================================")

    pygame.quit()


if __name__ == '__main__':
    main()
>>>>>>> aa6641c (Ajout projet IA + rapport final)
