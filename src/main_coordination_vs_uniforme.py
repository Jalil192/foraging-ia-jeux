# -*- coding: utf-8 -*-

from engine import run_match
from strategies import CoordinationStrategy, UniformRandomStrategy

if __name__ == "__main__":
    run_match(
        CoordinationStrategy(),
        UniformRandomStrategy(),
        boardname="blue-map",
        nb_episodes=8,
        fps=1000,
        label0="coordination",
        label1="uniforme"
    )
