from GameManager.util import GameObject, tuple2Vec2
import GameManager.singleton as sing
from GameManager.resources import load_img

from GameExtensions.UI import *
from GameExtensions.locals import *

import pygame
from pygame.math import Vector2

from locals import *

from typing import Union, Any
import pathlib
import os


PAUSE = "pause"


class PauseManager(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "pause_manager")
        self.music_paused = False
        sing.ROOT.set_parameter(PAUSE, False)

    def early_update(self) -> None:
        if pygame.K_ESCAPE in sing.ROOT.key_downs:
            if PAUSE in sing.ROOT.parameters.keys() and sing.ROOT.parameters[PAUSE]:
                self.resume()
                self.music_paused = False
            else:
                sing.ROOT.set_parameter(PAUSE, True)
                self.generate_pause_menu()
                self.music_paused = True
                pygame.mixer.pause()

    def generate_pause_menu(self):
        import main

        pause_panel = BaseUIObject(Vector2(0, 0), 0, pygame.Surface((100, 500)), "pause_panel", anchor=CENTER)
        title_label = TextLabel(Vector2(0, 20), 0, pygame.font.SysFont("Arial", 25), "Pause", (200, 200, 200),
                                "title_label", anchor=N)
        resume_btn = Button(Vector2(0, 0), 0, pygame.Surface((100, 20)), "resume_btn", text="Resume",
                            font=pygame.font.SysFont("Arial", 15), text_color=(200, 200, 200), anchor=CENTER,
                            on_mouse_up_func=self.resume)
        exit_btn = Button(Vector2(0, 30), 0, pygame.Surface((100, 20)), "exit_btn", text="Exit",
                          font=pygame.font.SysFont("Arial", 15), text_color=(200, 200, 200), anchor=CENTER,
                          on_mouse_up_func=main.menu)
        pause_panel.children.add_gameobjects(title_label, resume_btn, exit_btn)
        sing.ROOT.add_gameObject(pause_panel)

    def resume(self):
        sing.ROOT.set_parameter(PAUSE, False)
        sing.ROOT.remove_object(sing.ROOT.game_objects["pause_panel"])
        pygame.mixer.unpause()


class Star(GameObject):
    def __init__(self, pos: Vector2, radius: int, sound: pygame.mixer.Sound, name: str):
        super().__init__(pos, 0, pygame.Surface((0, 0)), name)
        self.radius = radius
        self.note_index = 0

        self.start_time = 0
        self.mov_vec = None
        self.started = False

        self.music = sound

        self.timer = 0

        sing.ROOT.add_gameObject(TextLabel(Vector2(0, 50), 0, pygame.font.SysFont("Arial", 25, bold=True),
                                           "Press space to start", (190, 190, 190), "start_label", anchor=N))

    def early_update(self) -> None:
        if not self.started:
            if pygame.K_SPACE in sing.ROOT.key_downs:
                self.started = True
                sing.ROOT.remove_object(sing.ROOT.game_objects["start_label"])
                self.music.play()
            return
        if PAUSE in sing.ROOT.parameters.keys() and sing.ROOT.parameters[PAUSE]:
            return

        self.timer += sing.ROOT.delta
        cur_time = self.timer
        note_rend: NoteRenderer = sing.ROOT.game_objects["rend"]

        if self.note_index >= len(note_rend.notes):
            return

        if self.mov_vec is None:
            self.new_vec()

        self.translate(self.mov_vec * sing.ROOT.delta)

        if pygame.K_SPACE in sing.ROOT.key_downs:
            print("Pressed")
            print(cur_time, note_rend.notes[self.note_index].timing)
            diff = abs(cur_time - note_rend.notes[self.note_index].timing / 1000)

            if diff <= PERFECT / 1000:
                print("Perfect")
                sing.ROOT.add_gameObject(Assessment(note_rend.notes[self.note_index].pos + Vector2(0, -20),
                                                    PERFECT))
                self.note_index += 1
                self.new_vec()
                note_rend.on_note_destroy()
            elif diff <= OK / 1000:
                print("Ok")
                sing.ROOT.add_gameObject(Assessment(note_rend.notes[self.note_index].pos + Vector2(0, -20),
                                                    OK))
                self.note_index += 1
                self.new_vec()
                note_rend.on_note_destroy()
            else:
                print("Nope")

    def new_vec(self):
        cur_time = self.timer
        note_rend: NoteRenderer = sing.ROOT.game_objects["rend"]
        if self.note_index >= len(note_rend.notes):
            return
        note = note_rend.notes[self.note_index]
        self.mov_vec = (note.pos - self.get_real_pos()) / (abs(cur_time - note.timing / 1000))

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


class ExampleStar(BaseUIObject):
    def __init__(self, image: pygame.Surface, hide_rects: list[pygame.Rect], name: str):
        super().__init__(Vector2(0, 0), 0, image, name)
        self.hide = False
        self.hide_rects = hide_rects

    def early_update(self) -> None:
        mouse_pos = tuple2Vec2(pygame.mouse.get_pos())
        self.translate(mouse_pos, False)
        self.hide = any(map(lambda rct: is_included(mouse_pos, rct), self.hide_rects))
        sing.ROOT.set_parameter("can_place_stars", not self.hide)

    def blit(self, screen: pygame.Surface, apply_alpha=True) -> None:
        if not self.hide:
            super().blit(screen, apply_alpha)


class Map:
    NOTE = 0
    BPM_CH = 1

    def __init__(self, map_name: str, music_path: str):
        self.map_name = map_name
        self.music: str = music_path
        self.bpm: int
        self.speed: int
        self.instructions: list[tuple[int, Any]] = []

    def add_note(self, pos: Vector2):
        self.instructions.append((Map.NOTE, (pos.x, pos.y)))

    def change_bpm(self, new_bpm: int):
        self.instructions.append((Map.BPM_CH, new_bpm))


class MapBuilder(GameObject):
    def __init__(self):
        super().__init__(Vector2(0, 0), 0, pygame.Surface((0, 0)), "map_builder")
        self.map: Map = sing.ROOT.parameters["editing_map"]
        self.star_cnt = 0
        sing.ROOT.set_parameter("can_place_stars", False)

    def early_update(self) -> None:
        if "star_mode" in sing.ROOT.parameters and sing.ROOT.parameters["star_mode"] and\
                sing.ROOT.mouse_downs[MOUSE_LEFT] and sing.ROOT.parameters["can_place_stars"]:
            scrdim = sing.ROOT.screen_dim
            pos = sing.ROOT.camera_pos + tuple2Vec2(pygame.mouse.get_pos()) - Vector2(scrdim[0], scrdim[1]) / 2
            self.map.add_note(pos)
            self.children.add_gameobjects(GameObject(pos, 0, load_img("resources/images/star.png", (32, 32)),
                                                     f"edit_star{self.star_cnt}"))
            self.star_cnt += 1

    def save(self):
        import json
        with open(f"resources/maps/{self.map.map_name}.scr", 'w') as f:
            json.dump(self.map.__dict__, f)


def load_map(path: Union[pathlib.Path, str]) -> list[Note]:
    lst = []
    with open(os.path.join(sing.ROOT.resources_path, path), "r") as f:
        for i, line in enumerate(f.readlines()):
            pos, timing = line.split(";")
            pos = tuple(map(lambda c: int(c), pos.split(",")))
            timing = int(timing)
            lst.append(Note(tuple2Vec2(pos), timing, i))

    return lst





