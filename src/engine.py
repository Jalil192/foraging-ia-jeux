# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import random
import numpy as np
import pygame

from pySpriteWorld.gameclass import Game
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.ontology import Ontology

from search.grid2D import ProblemeGrid2D
from search import probleme


game = Game()


TILEID_TO_COLOR = {
    (19, 1): "yellow",
    (21, 1): "green",
    (17, 4): "red",
    (18, 4): "blue",
}


def init(boardname="mixed-map", fps=10):
    global game
    game = Game("Cartes/" + boardname + ".json", SpriteBuilder)
    game.O = Ontology(True, "SpriteSheet-32x32/tiny_spritesheet_ontology.csv")
    game.populate_sprite_names(game.O)
    game.fps = fps
    game.mainiteration()


def around_pos(pos):
    x, y = pos
    return [
        (x - 1, y - 1), (x - 1, y), (x - 1, y + 1),
        (x, y - 1),                 (x, y + 1),
        (x + 1, y - 1), (x + 1, y), (x + 1, y + 1)
    ]


def get_fiole_type(fiole):
    tid = getattr(fiole, "tileid", None)
    return TILEID_TO_COLOR.get(tid, "yellow")


def resolve_fiole(ftype, t0, t1):
    if ftype == "yellow":
        t0_ok = t0 >= 1
        t1_ok = t1 >= 1

        if t0_ok and t1_ok:
            if t0 > t1:
                return 0
            if t1 > t0:
                return 1
            return None
        if t0_ok:
            return 0
        if t1_ok:
            return 1
        return None

    elif ftype == "red":
        t0_ok = t0 >= 2
        t1_ok = t1 >= 2

        if t0_ok and t1_ok:
            if t0 > t1:
                return 0
            if t1 > t0:
                return 1
            return None
        if t0_ok:
            return 0
        if t1_ok:
            return 1
        return None

    elif ftype == "green":
        total = t0 + t1
        if total < 3:
            return None
        if t0 > t1:
            return 0
        if t1 > t0:
            return 1
        return None

    elif ftype == "blue":
        # règle spéciale
        if t0 == 1 and t1 >= 2:
            return 0
        if t1 == 1 and t0 >= 2:
            return 1

        # sinon comme rouge
        t0_ok = t0 >= 2
        t1_ok = t1 >= 2

        if t0_ok and t1_ok:
            if t0 > t1:
                return 0
            if t1 > t0:
                return 1
            return None
        if t0_ok:
            return 0
        if t1_ok:
            return 1
        return None

    return None


def run_match(strategy0,
              strategy1,
              boardname="mixed-map",
              nb_episodes=3,
              fps=10,
              verbose=True,
              label0="team0",
              label1="team1"):
    global game

    init(boardname, fps)

    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols

    lMin = 2
    lMax = nb_lignes - 2
    cMin = 2
    cMax = nb_cols - 2

    players = [o for o in game.layers["joueur"]]
    items = [o for o in game.layers["ramassable"]]
    


    nb_players = len(players)
    nb_fioles = len(items)

    print("Lecture carte")
    print("-------------------------------------------")
    print("Joueurs :", nb_players)
    print("Fioles  :", nb_fioles)
    print("Lignes  :", nb_lignes)
    print("Colonnes:", nb_cols)
    print("-------------------------------------------")

    rows = sorted(set([p.get_rowcol()[0] for p in players]))
    top_row = rows[0]
    bottom_row = rows[-1]

    team = [[], []]
    for o in players:
        x, y = o.get_rowcol()
        if x == top_row:
            team[0].append(o)
        elif x == bottom_row:
            team[1].append(o)

    assert len(team[0]) == len(team[1]), "Les équipes doivent avoir la même taille"
    nb_players_team = len(team[0])

    init_states = [
        [p.get_rowcol() for p in team[0]],
        [p.get_rowcol() for p in team[1]],
    ]

    strategy0.reset(0, nb_players_team, items)
    strategy1.reset(1, nb_players_team, items)

    scores_totaux = [0, 0]

    history = {
        "episode_scores": [],
        "team_allocations": [[], []],
        "fiole_infos": [],
    }

    def item_states(items_list):
        return [o.get_rowcol() for o in items_list]

    def player_states(players_list):
        return [p.get_rowcol() for p in players_list]

    def legal_position(pos):
        row, col = pos
        return (
            pos not in item_states(items)
            and pos not in player_states(players)
            and row > lMin
            and row < lMax - 1
            and col >= cMin
            and col < cMax
        )

    def around_pos_free(pos):
        return [p for p in around_pos(pos) if legal_position(p)]

    def players_around_item(f):
        count = [0, 0]
        pos = f.get_rowcol()
        neighbours = around_pos(pos)

        for i in [0, 1]:
            for p in team[i]:
                if p.get_rowcol() in neighbours:
                    count[i] += 1
        return count

    def build_grid():
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

    for e in range(nb_episodes):
        print(f"\n========== EPISODE {e+1}/{nb_episodes} ==========")

        alloc0 = strategy0.choose_allocation(history)
        alloc1 = strategy1.choose_allocation(history)

        history["team_allocations"][0].append(alloc0[:])
        history["team_allocations"][1].append(alloc1[:])

        for p in range(nb_players_team):
            if (e + p) % 2 == 0:
                priority = [0, 1]
            else:
                priority = [1, 0]

            for t in priority:
                allocation = alloc0 if t == 0 else alloc1
                target_fiole_idx = allocation[p]
                fiole = items[target_fiole_idx]

                free_positions = around_pos_free(fiole.get_rowcol())

                print(f"\n  -- Joueur {p}, équipe {t} --")

                if not free_positions:
                    print("  Aucune position libre autour de la fiole :", fiole.get_rowcol())
                    continue

                chosen_pos = random.choice(free_positions)
                pos_player = team[t][p].get_rowcol()

                print(f"  Joueur {p} : {pos_player} → fiole {fiole.get_rowcol()} (pos cible {chosen_pos})")

                g = build_grid()
                prob = ProblemeGrid2D(pos_player, chosen_pos, g, "manhattan")
                chemin = probleme.astar(prob, verbose=False)

                for (row, col) in chemin:
                    team[t][p].set_rowcol(row, col)
                    game.mainiteration()

        print(f"\n  -- Résultats épisode {e+1} --")
        scores_episode = [0, 0]
        fiole_infos = []

        for i, fiole in enumerate(items):
            t0, t1 = players_around_item(fiole)
            ftype = get_fiole_type(fiole)
            winner = resolve_fiole(ftype, t0, t1)

            fiole_infos.append({
                "index": i,
                "position": fiole.get_rowcol(),
                "type": ftype,
                "counts": [t0, t1],
                "winner": winner,
            })

            print(f"  Fiole {ftype:6s} {fiole.get_rowcol()} | T0:{t0}  T1:{t1} → ", end="")
            if winner is not None:
                scores_episode[winner] += 1
                print(f"Équipe {winner} marque !")
            else:
                print("Personne ne marque")

        history["episode_scores"].append(scores_episode[:])
        history["fiole_infos"].append(fiole_infos)

        strategy0.update(alloc0, alloc1, fiole_infos, scores_episode, history)
        strategy1.update(alloc1, alloc0, fiole_infos, scores_episode, history)

        scores_totaux[0] += scores_episode[0]
        scores_totaux[1] += scores_episode[1]

        print(f"\n  Score épisode : T0={scores_episode[0]}  T1={scores_episode[1]}")
        print(f"  Score cumulé  : T0={scores_totaux[0]}  T1={scores_totaux[1]}")

        for i in [0, 1]:
            for j, p in enumerate(team[i]):
                x, y = init_states[i][j]
                p.set_rowcol(x, y)
        game.mainiteration()

    print("\n==========================================")
    print("           RÉSULTAT FINAL")
    print("==========================================")
    print(f"  {label0} : {scores_totaux[0]} points")
    print(f"  {label1} : {scores_totaux[1]} points")
    if scores_totaux[0] > scores_totaux[1]:
        print(f"   {label0} gagne !")
    elif scores_totaux[1] > scores_totaux[0]:
        print(f"   {label1} gagne !")
    else:
        print("   Égalité !")
    print("==========================================")

    pygame.quit()
