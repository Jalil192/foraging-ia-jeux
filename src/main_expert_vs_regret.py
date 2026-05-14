# -*- coding: utf-8 -*-

from engine import run_match
from strategies import ExpertStrategy, RegretMatchingStrategy

if __name__ == "__main__":
    run_match(
        ExpertStrategy(),
        RegretMatchingStrategy(),
        boardname="blue-map",
        nb_episodes=8,
        fps=1000,
        label0="expert",
        label1="regret"
    )
