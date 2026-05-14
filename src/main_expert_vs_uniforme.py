# -*- coding: utf-8 -*-

from engine import run_match
from strategies import ExpertStrategy, UniformRandomStrategy

if __name__ == "__main__":
    run_match(
        ExpertStrategy(),
        UniformRandomStrategy(),
        boardname="blue-map",
        nb_episodes=10,
        fps=1000,
        label0="expert",
        label1="uniforme"
    )
