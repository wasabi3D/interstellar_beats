from GameManager.util import GameObject
import GameManager.singleton as sing

from GameExtensions.UI import TextLabel

import pygame
from pygame.math import Vector2

from locals import *


class Star(GameObject):
    def __init__(self, pos: Vector2, radius: int, name: str):
        super().__init__(pos, 0, pygame.Surface((0, 0)), name)
        self.radius = radius
        self.note_index = 0

        self.start_time = pygame.time.get_ticks()
        self.mov_vec = None

    def early_update(self) -> None:
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


class Note:
    def __init__(self, pos: Vector2, timing: float):
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
            pygame.draw.circle(screen, (140, 140, 50), self.get_screen_pos() + n.pos, 5)
            if i < len(lst) - 1:
                # print(self.notes[i + 1 + self.draw_begin].pos, n.pos)
                vec = (lst[i + 1].pos - n.pos).normalize()
                pygame.draw.line(screen, (140, 30, 30), n.pos + self.get_screen_pos(),
                                 self.get_screen_pos() + n.pos + vec * 50, width=1)


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
