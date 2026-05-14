# -*- coding: utf-8 -*-

from engine import run_match
from strategies import UniformRandomStrategy

if __name__ == "__main__":
    run_match(
        UniformRandomStrategy(),
        UniformRandomStrategy(),
        boardname="blue-map",
        nb_episodes=8,
        fps=100,
        label0="uniforme",
        label1="uniforme"
    )
