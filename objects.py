from GameManager.util import GameObject, tuple2Vec2
import GameManager.singleton as sing
from GameManager.resources import load_img

from GameExtensions.UI import TextLabel
from GameExtensions.locals import *

import pygame
from pygame.math import Vector2

from locals import *

from typing import Union
import pathlib
import os


class Star(GameObject):
    def __init__(self, pos: Vector2, radius: int, sound: pygame.mixer.Sound, name: str):
        super().__init__(pos, 0, pygame.Surface((0, 0)), name)
        self.radius = radius
        self.note_index = 0

        self.start_time = 0
        self.mov_vec = None
        self.started = False

        self.music = sound

        sing.ROOT.add_gameObject(TextLabel(Vector2(0, 50), 0, pygame.font.SysFont("Arial", 25, bold=True),
                                           "Press space to start", (190, 190, 190), "start_label", anchor=N))

    def early_update(self) -> None:
        if not self.started:
            if pygame.K_SPACE in sing.ROOT.key_downs:
                self.start_time = pygame.time.get_ticks()
                self.started = True
                sing.ROOT.remove_object(sing.ROOT.game_objects["start_label"])
                self.music.play()
            return
        cur_time = pygame.time.get_ticks() - self.start_time
        note_rend: NoteRenderer = sing.ROOT.game_objects["rend"]

        if self.note_index > len(note_rend.notes):
            return

        if self.mov_vec is None:
            self.new_vec()

        self.translate(self.mov_vec * sing.ROOT.delta)

        if pygame.K_SPACE in sing.ROOT.key_downs:
            print("Pressed")
            print(cur_time, note_rend.notes[self.note_index].timing)
            diff = abs(cur_time - note_rend.notes[self.note_index].timing)

            if diff <= PERFECT:
                print("Perfect")
                sing.ROOT.add_gameObject(Assessment(note_rend.notes[self.note_index].pos + Vector2(0, -20),
                                                    PERFECT))
                self.note_index += 1
                self.new_vec()
                note_rend.on_note_destroy()
            elif diff <= OK:
                print("Ok")
                sing.ROOT.add_gameObject(Assessment(note_rend.notes[self.note_index].pos + Vector2(0, -20),
                                                    OK))
                self.note_index += 1
                self.new_vec()
                note_rend.on_note_destroy()
            else:
                print("Nope")

    def new_vec(self):
        cur_time = pygame.time.get_ticks() - self.start_time
        note_rend: NoteRenderer = sing.ROOT.game_objects["rend"]
        if self.note_index >= len(note_rend.notes):
            return
        note = note_rend.notes[self.note_index]
        self.mov_vec = (note.pos - self.get_real_pos()) / (abs(cur_time - note.timing) / 1000)

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        sing.ROOT.camera_pos = self.get_real_pos()
        pygame.draw.circle(screen, (150, 150, 150), self.get_screen_pos(), self.radius, width=2)


class Note(GameObject):
    def __init__(self, pos: Vector2, timing: float, sid: int):
        super().__init__(pos, 0, load_img("resources/images/star.png", (32, 32)), f"star{sid}")
        self.pos = pos
        self.timing = timing


class NoteRenderer(GameObject):
    def __init__(self, notes: list[Note]):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "rend")
        self.notes = notes
        self.draw_begin = 0
        self.draw_end = 3

    def on_note_destroy(self):
        self.draw_begin += 1
        self.draw_end += 1

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        lst = self.notes[self.draw_begin:min(self.draw_end, len(self.notes))]
        for i, n in enumerate(lst):
            # pygame.draw.circle(screen, (140, 140, 50), self.get_screen_pos() + n.pos, 5)
            if i < len(lst) - 1:
                vec = (lst[i + 1].pos - n.pos).normalize()
                pygame.draw.line(screen, (140, 30, 30), n.pos + self.get_screen_pos(),
                                 self.get_screen_pos() + n.pos + vec * 50, width=1)
            n.blit(screen, apply_alpha)


class Assessment(TextLabel):
    def __init__(self, pos: Vector2, assessment):
        if assessment == PERFECT:
            txt = "Perfect"
            col = (30, 120, 30)
        elif assessment == OK:
            txt = "OK"
            col = (150, 80, 120)

        super().__init__(pos, 0, pygame.font.SysFont("Arial", 15), txt, col, f"{pygame.time.get_ticks()}")
        self.global_cords = True
        self.spawn_time = pygame.time.get_ticks()

    def early_update(self) -> None:
        if pygame.time.get_ticks() - self.spawn_time > 500:
            sing.ROOT.remove_object(self)


def load_map(path: Union[pathlib.Path, str]) -> list[Note]:
    lst = []
    with open(os.path.join(sing.ROOT.resources_path, path), "r") as f:
        for i, line in enumerate(f.readlines()):
            pos, timing = line.split(";")
            pos = tuple(map(lambda c: int(c), pos.split(",")))
            timing = int(timing)
            lst.append(Note(tuple2Vec2(pos), timing, i))

    return lst


