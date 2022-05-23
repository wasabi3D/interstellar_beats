import pygame

from GameManager.MainLoopManager import GameRoot
from objects import Star, NoteRenderer, Note
from pygame import Vector2

import random


def main():
    root = GameRoot((1440, 900), (20, 20, 55), "Test", "~/", Vector2(0, 0), display_flag=pygame.FULLSCREEN)

    star = Star(Vector2(10, 0), 10, "star")
    notes = [Note(Vector2(50, 100), 800)]

    for i in range(80):
        notes.append(Note(notes[-1].pos + Vector2(random.randint(-300, 300), random.randint(-300, 300)), notes[-1].timing + random.randint(700, 1000)))

    root.add_gameObject(star, NoteRenderer(notes))

    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
