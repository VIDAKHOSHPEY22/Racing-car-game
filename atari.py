import pygame as pg

from game.game import Game


def main():
    pg.init()
    pg.mixer.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
