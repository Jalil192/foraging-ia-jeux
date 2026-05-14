# -*- coding: utf-8 -*-

import random
import numpy as np


TILEID_TO_COLOR = {
    (19, 1): "yellow",   # coins
    (21, 1): "green",    # milieu haut / bas
    (17, 4): "red",      # milieu gauche / droite
    (18, 4): "blue",     # centre
}


def fiole_type_from_item(item):
    tid = getattr(item, "tileid", None)
    return TILEID_TO_COLOR.get(tid, "yellow")


class BaseStrategy:
    def reset(self, team_id, nb_players_team, items):
        self.team_id = team_id
        self.nb_players_team = nb_players_team
        self.items = items
        self.nb_fioles = len(items)

    def choose_allocation(self, history):
        raise NotImplementedError

    def update(self, my_allocation, opp_allocation, fiole_infos, score_episode, history):
        pass


class UniformRandomStrategy(BaseStrategy):
    def choose_allocation(self, history):
        return [random.randint(0, self.nb_fioles - 1) for _ in range(self.nb_players_team)]


class StubbornStrategy(BaseStrategy):
    def __init__(self):
        self.fixed_allocation = None

    def reset(self, team_id, nb_players_team, items):
        super().reset(team_id, nb_players_team, items)
        if self.fixed_allocation is None or len(self.fixed_allocation) != self.nb_players_team:
            self.fixed_allocation = [
                random.randint(0, self.nb_fioles - 1)
                for _ in range(self.nb_players_team)
            ]

    def choose_allocation(self, history):
        return self.fixed_allocation[:]


class ExpertStrategy(BaseStrategy):
    def __init__(self):
        self.experts = []
        self.expert_scores = None
        self.last_expert_idx = None
        self.exploration = 0.15
        self.decay = 0.95

    def reset(self, team_id, nb_players_team, items):
        super().reset(team_id, nb_players_team, items)

        n = self.nb_players_team
        self.experts = []

        yellow_idx = [i for i, f in enumerate(items) if fiole_type_from_item(f) == "yellow"]
        green_idx  = [i for i, f in enumerate(items) if fiole_type_from_item(f) == "green"]
        red_idx    = [i for i, f in enumerate(items) if fiole_type_from_item(f) == "red"]
        blue_idx   = [i for i, f in enumerate(items) if fiole_type_from_item(f) == "blue"]

        def fill_round_robin(indices, total_players):
            if not indices:
                return []
            alloc = []
            for i in range(total_players):
                alloc.append(indices[i % len(indices)])
            return alloc

        def fill_with_caps(priority_groups, caps, total_players):
            alloc = []
            remaining = total_players

            for group in priority_groups:
                for idx in group:
                    if remaining <= 0:
                        break
                    cap = caps.get(idx, 1)
                    take = min(cap, remaining)
                    alloc.extend([idx] * take)
                    remaining -= take
                if remaining <= 0:
                    break

            if remaining > 0:
                all_idx = [i for g in priority_groups for i in g]
                if not all_idx:
                    all_idx = list(range(self.nb_fioles))
                alloc.extend(fill_round_robin(all_idx, remaining))

            return alloc[:total_players]

        caps = {}
        for i in range(self.nb_fioles):
            t = fiole_type_from_item(self.items[i])
            if t == "yellow":
                caps[i] = 2
            elif t == "green":
                caps[i] = 3
            elif t == "red":
                caps[i] = 2
            elif t == "blue":
                caps[i] = 2
            else:
                caps[i] = 2

     
        self.experts.append(
            fill_with_caps([yellow_idx, green_idx, red_idx, blue_idx], caps, n)
        )

     
        useful = yellow_idx + green_idx + red_idx + blue_idx
        if useful:
            self.experts.append(fill_round_robin(useful, n))

      
        alloc = []
        if yellow_idx:
            for i in range(min(len(yellow_idx) * 2, n)):
                alloc.append(yellow_idx[i % len(yellow_idx)])
        remaining = n - len(alloc)
        if remaining > 0 and green_idx:
            alloc.extend(fill_round_robin(green_idx, remaining))
        remaining = n - len(alloc)
        if remaining > 0:
            rest = red_idx + blue_idx + yellow_idx
            alloc.extend(fill_round_robin(rest, remaining))
        self.experts.append(alloc[:n])

        
        center_axis = blue_idx + red_idx + green_idx
        if center_axis:
            self.experts.append(fill_round_robin(center_axis, n))

       
        if yellow_idx:
            self.experts.append(fill_round_robin(yellow_idx, n))

      
        vg = green_idx + yellow_idx
        if vg:
            self.experts.append(fill_round_robin(vg, n))

        # Expert 7 : équilibré avec caps
        balanced_groups = [yellow_idx, green_idx, red_idx, blue_idx]
        self.experts.append(fill_with_caps(balanced_groups, caps, n))

        if self.expert_scores is None or len(self.expert_scores) != len(self.experts):
            self.expert_scores = np.zeros(len(self.experts), dtype=float)
        else:
            self.expert_scores *= self.decay

        self.last_expert_idx = None

    def choose_allocation(self, history):
        if len(self.experts) == 0:
            return [random.randint(0, self.nb_fioles - 1) for _ in range(self.nb_players_team)]

        if random.random() < self.exploration or np.sum(np.maximum(self.expert_scores, 0.0)) == 0:
            idx = random.randint(0, len(self.experts) - 1)
        else:
            scores = np.maximum(self.expert_scores, 0.0) + 1e-6
            probs = scores / scores.sum()
            idx = np.random.choice(len(self.experts), p=probs)

        self.last_expert_idx = idx
        alloc = self.experts[idx][:]

        random.shuffle(alloc)
        return alloc

    def update(self, my_allocation, opp_allocation, fiole_infos, score_episode, history):
        if self.last_expert_idx is None:
            return

        if isinstance(score_episode, (list, tuple, np.ndarray)):
            my_score = score_episode[self.team_id]
        else:
            my_score = score_episode

        self.expert_scores[self.last_expert_idx] += float(my_score)



class CoordinationStrategy(BaseStrategy):
    """
    Version améliorée :
    - choisit plusieurs fioles cibles
    - respecte mieux les tailles de groupe utiles par type
    - évite de tout empiler bêtement sur une seule fiole
    """
    def __init__(self, exploration=0.20):
        self.exploration = exploration

    def _capacity_for_type(self, fiole_index):
        t = fiole_type_from_item(self.items[fiole_index])
        if t == "yellow":
            return 2
        elif t == "red":
            return 3
        elif t == "green":
            return 3
        elif t == "blue":
            return 2
        return 2

    def _priority_for_type(self, fiole_index):
        t = fiole_type_from_item(self.items[fiole_index])
        if t == "yellow":
            return 3.0
        elif t == "red":
            return 2.6
        elif t == "blue":
            return 2.8
        elif t == "green":
            return 2.4
        return 1.0

    def choose_allocation(self, history):
        indices = list(range(self.nb_fioles))

        
        scores = []
        for i in indices:
            score = self._priority_for_type(i)

            
            score += random.random() * self.exploration
            scores.append((score, i))

        scores.sort(reverse=True)
        ordered = [i for _, i in scores]

        
        nb_targets = min(5, self.nb_fioles)
        targets = ordered[:nb_targets]

        allocation = []
        remaining = self.nb_players_team

        
        for f in targets:
            if remaining <= 0:
                break
            cap = self._capacity_for_type(f)
            take = min(cap, remaining)
            allocation.extend([f] * take)
            remaining -= take

        
        idx = 0
        while remaining > 0:
            allocation.append(targets[idx % len(targets)])
            idx += 1
            remaining -= 1

        random.shuffle(allocation)
        return allocation




class FictitiousPlayStrategy(BaseStrategy):
    def reset(self, team_id, nb_players_team, items):
        super().reset(team_id, nb_players_team, items)

      
        self.opp_sum = np.zeros(self.nb_fioles, dtype=float)
        self.nb_updates = 0

        # un peu d'exploration au début
        self.exploration = 0.15
        self.min_exploration = 0.03
        self.decay = 0.97

    def _expected_opponent_counts(self):
        if self.nb_updates == 0:
            # au début on suppose uniforme
            return np.ones(self.nb_fioles, dtype=float) * (
                self.nb_players_team / self.nb_fioles
            )
        return self.opp_sum / self.nb_updates

    def _expected_value(self, fiole_index, my_count, opp_count):
        """
        Renvoie une valeur attendue pour la fiole si on envoie my_count joueurs
        contre opp_count joueurs adverses attendus.
        """
        t = fiole_type_from_item(self.items[fiole_index])

        
        if t == "yellow":
            if my_count <= 0:
                return 0.0
            if my_count > opp_count:
                return 1.0
            elif my_count == opp_count:
                return 0.25
            else:
                return 0.0

        
        elif t == "red":
            if my_count < 2:
                return 0.0
            opp_ok = opp_count >= 2
            if not opp_ok:
                return 1.0
            if my_count > opp_count:
                return 1.0
            elif my_count == opp_count:
                return 0.2
            else:
                return 0.0

        
        elif t == "green":
            total = my_count + opp_count
            if total < 3:
                return 0.0
            if my_count > opp_count:
                return 1.0
            elif my_count == opp_count:
                return 0.2
            else:
                return 0.0

        
        elif t == "blue":
            if my_count == 1 and opp_count >= 2:
                return 1.0
            if my_count >= 2 and opp_count == 1:
                return 0.0

            my_ok = my_count >= 2
            opp_ok = opp_count >= 2

            if my_ok and not opp_ok:
                return 1.0
            if not my_ok and opp_ok:
                return 0.0
            if my_ok and opp_ok:
                if my_count > opp_count:
                    return 1.0
                elif my_count == opp_count:
                    return 0.2
                else:
                    return 0.0
            return 0.0

        return 0.0

    def choose_allocation(self, history):
        opp_expect = self._expected_opponent_counts()

        
        if random.random() < self.exploration:
            return [random.randint(0, self.nb_fioles - 1) for _ in range(self.nb_players_team)]

        allocation = []
        my_counts = np.zeros(self.nb_fioles, dtype=int)

        
        for _ in range(self.nb_players_team):
            best_fiole = None
            best_gain = -10**9

            for f in range(self.nb_fioles):
                current_value = self._expected_value(f, my_counts[f], opp_expect[f])
                new_value = self._expected_value(f, my_counts[f] + 1, opp_expect[f])

                marginal_gain = new_value - current_value

           
                t = fiole_type_from_item(self.items[f])

               
                if t == "yellow":
                    marginal_gain += 0.05

               
                if t == "yellow" and my_counts[f] >= opp_expect[f] + 2:
                    marginal_gain -= 0.15
                elif t == "red" and my_counts[f] >= opp_expect[f] + 2:
                    marginal_gain -= 0.10
                elif t == "green" and my_counts[f] >= opp_expect[f] + 2:
                    marginal_gain -= 0.10
                elif t == "blue" and my_counts[f] >= 2 and opp_expect[f] < 2:
                    marginal_gain -= 0.10

                if marginal_gain > best_gain:
                    best_gain = marginal_gain
                    best_fiole = f

            allocation.append(best_fiole)
            my_counts[best_fiole] += 1

        random.shuffle(allocation)
        return allocation

    def update(self, my_allocation, opp_allocation, fiole_infos, score_episode, history):
        opp_vec = np.zeros(self.nb_fioles, dtype=float)
        for f in opp_allocation:
            opp_vec[f] += 1

        self.opp_sum += opp_vec
        self.nb_updates += 1

        
        self.exploration = max(self.min_exploration, self.exploration * self.decay)


class RegretMatchingStrategy(BaseStrategy):
    def reset(self, team_id, nb_players_team, items):
        super().reset(team_id, nb_players_team, items)
        self.regrets = np.zeros(self.nb_fioles, dtype=float)
        self.exploration = 0.10
        self.decay = 0.97

    def _capacity_for_type(self, fiole_index):
        t = fiole_type_from_item(self.items[fiole_index])
        if t == "yellow":
            return 2
        elif t == "red":
            return 3
        elif t == "green":
            return 3
        elif t == "blue":
            return 2
        return 2

    def choose_allocation(self, history):
        positive_regrets = np.maximum(self.regrets, 0.0)

        if positive_regrets.sum() == 0:
            base_scores = np.ones(self.nb_fioles, dtype=float)
        else:
            base_scores = positive_regrets.copy()

        for i in range(self.nb_fioles):
            t = fiole_type_from_item(self.items[i])
            if t == "yellow":
                base_scores[i] *= 1.15
            elif t == "red":
                base_scores[i] *= 1.05
            elif t == "green":
                base_scores[i] *= 1.10
            elif t == "blue":
                base_scores[i] *= 1.10

        uniform = np.ones(self.nb_fioles, dtype=float)
        base_scores = (1 - self.exploration) * base_scores + self.exploration * uniform

        order = list(np.argsort(-base_scores))

        allocation = []
        remaining = self.nb_players_team

        for f in order:
            if remaining <= 0:
                break
            cap = self._capacity_for_type(f)
            n = min(cap, remaining)
            allocation.extend([int(f)] * n)
            remaining -= n

        idx = 0
        while remaining > 0:
            allocation.append(order[idx % len(order)])
            remaining -= 1
            idx += 1

        random.shuffle(allocation)
        return allocation

    def update(self, my_allocation, opp_allocation, fiole_infos, score_episode, history):
        self.regrets *= self.decay

        my_counts = np.zeros(self.nb_fioles, dtype=int)
        opp_counts = np.zeros(self.nb_fioles, dtype=int)

        for f in my_allocation:
            my_counts[f] += 1
        for f in opp_allocation:
            opp_counts[f] += 1

        def winner_from_counts(fiole_index, my_c, opp_c):
            ftype = fiole_type_from_item(self.items[fiole_index])

            if ftype == "yellow":
                if my_c >= 1 and opp_c >= 1:
                    if my_c > opp_c:
                        return self.team_id
                    elif opp_c > my_c:
                        return 1 - self.team_id
                    return None
                elif my_c >= 1:
                    return self.team_id
                elif opp_c >= 1:
                    return 1 - self.team_id
                return None

            elif ftype == "red":
                my_ok = my_c >= 2
                opp_ok = opp_c >= 2
                if my_ok and opp_ok:
                    if my_c > opp_c:
                        return self.team_id
                    elif opp_c > my_c:
                        return 1 - self.team_id
                    return None
                elif my_ok:
                    return self.team_id
                elif opp_ok:
                    return 1 - self.team_id
                return None

            elif ftype == "green":
                total = my_c + opp_c
                if total < 3:
                    return None
                if my_c > opp_c:
                    return self.team_id
                elif opp_c > my_c:
                    return 1 - self.team_id
                return None

            elif ftype == "blue":
                if my_c == 1 and opp_c >= 2:
                    return self.team_id
                if opp_c == 1 and my_c >= 2:
                    return 1 - self.team_id

                my_ok = my_c >= 2
                opp_ok = opp_c >= 2
                if my_ok and opp_ok:
                    if my_c > opp_c:
                        return self.team_id
                    elif opp_c > my_c:
                        return 1 - self.team_id
                    return None
                elif my_ok:
                    return self.team_id
                elif opp_ok:
                    return 1 - self.team_id
                return None

            return None

        def reward_of_counts(fiole_index, my_c, opp_c):
            w = winner_from_counts(fiole_index, my_c, opp_c)
            return 1.0 if w == self.team_id else 0.0

        for src in range(self.nb_fioles):
            if my_counts[src] == 0:
                continue

            actual_src_reward = reward_of_counts(src, my_counts[src], opp_counts[src])

            for dst in range(self.nb_fioles):
                if src == dst:
                    continue

                new_my = my_counts.copy()
                new_my[src] -= 1
                new_my[dst] += 1

                actual_dst_reward = reward_of_counts(dst, my_counts[dst], opp_counts[dst])
                new_src_reward = reward_of_counts(src, new_my[src], opp_counts[src])
                new_dst_reward = reward_of_counts(dst, new_my[dst], opp_counts[dst])

                actual_total = actual_src_reward + actual_dst_reward
                new_total = new_src_reward + new_dst_reward

                congestion_penalty = 0.0
                if my_counts[src] > self._capacity_for_type(src):
                    congestion_penalty = 0.15

                self.regrets[dst] += (new_total - actual_total + congestion_penalty)
