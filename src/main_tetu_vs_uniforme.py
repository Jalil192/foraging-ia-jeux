# -*- coding: utf-8 -*-

from engine import run_match
from strategies import StubbornStrategy, UniformRandomStrategy

if __name__ == "__main__":
    run_match(
        StubbornStrategy(),
        UniformRandomStrategy(),
        boardname="blue-map",
        nb_episodes=8,
        fps=100,
        label0="tetu",
        label1="uniforme"
    )
