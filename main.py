import pygame

from GameExtensions.UI import *

from GameManager.MainLoopManager import GameRoot
import GameManager.singleton as sing
from GameManager.resources import *
from objects import *
from pygame import Vector2

import os
import shutil
import pathlib
import typing


def play(map_data_path: typing.Union[pathlib.Path, str], edit_mode=False):
    if not edit_mode:
        sing.ROOT.clear_objects()
    notes = load_map(map_data_path)
    map_reader = MapReader(notes)
    star = Star(Vector2(0, 0), 10, sing.ROOT.sounds["music"], map_reader, "star")

    sing.ROOT.add_gameObject(star, NoteRenderer(map_reader), PauseManager())


def edit():
    sing.ROOT.clear_objects()
    background = BaseUIObject(Vector2(-120, 0), 0, load_img("resources/UI/background.png", (50, 250)),
                              "menu_background", anchor=E)
    select_img = BaseUIObject(Vector2(0, 40), 0, load_img("resources/UI/edit/select.png"), "select_img", anchor=N)

    def cursor_mode():
        exit_star()
        select_img.translate(cursor_btn.pos, False)

    cursor_btn = Button(Vector2(0, 40), 0, load_img("resources/UI/edit/cursor.png"), "cursor_btn",
                        on_mouse_down_func=cursor_mode, anchor=N)

    def delete_mode():
        exit_star()
        select_img.translate(delete_btn.pos, False)

    delete_btn = Button(Vector2(0, 80), 0, load_img("resources/UI/edit/delete.png"), "delete_btn",
                        on_mouse_down_func=delete_mode, anchor=N)

    def star_mode():
        sing.ROOT.set_parameter("star_mode", True)
        if "example_star" in sing.ROOT.game_objects:
            sing.ROOT.game_objects["example_star"].set_enabled(True)
        else:
            sing.ROOT.add_gameObject(ExampleStar(load_img("resources/images/star.png", (32, 32)),
                                                 [background.image.get_rect(center=background.get_screen_pos())],
                                                 "example_star"))
        select_img.translate(star_btn.pos, False)

    def exit_star():
        sing.ROOT.set_parameter("star_mode", False)
        if "example_star" in sing.ROOT.game_objects:
            sing.ROOT.game_objects["example_star"].set_enabled(False)

    star_btn = Button(Vector2(0, 120), 0, load_img("resources/UI/edit/star.png"), "star_btn",
                      on_mouse_down_func=star_mode, anchor=N)

    def edit_settings():

        def save_modif():
            sing.ROOT.set_parameter("BPM", int(sing.ROOT.game_objects["settings_background"].children["bpm_textbox"].text))
            sing.ROOT.set_parameter("SPD", int(sing.ROOT.game_objects["settings_background"].children["spd_textbox"].text))
            sing.ROOT.parameters["editing_map"].map_name = sing.ROOT.game_objects["settings_background"].children["name_textbox"].text

        if "edit_settings_already_opened" in sing.ROOT.parameters and sing.ROOT.parameters["edit_settings_already_opened"]:
            sing.ROOT.game_objects["settings_background"].set_enabled(True)
        else:
            bc = BaseUIObject(Vector2(0, 0), 0, load_img("resources/UI/background.png", (270, 250)),
                              "settings_background", CENTER)
            close_btn = Button(Vector2(-20, 20), 0, load_img("resources/UI/gen/cross.png"), "close_btn",
                               on_mouse_up_func=lambda: bc.set_enabled(False), on_mouse_down_func=save_modif, anchor=NE)
            bpm_label = TextLabel(Vector2(20, 60), 0, pygame.font.SysFont("Arial", 18), "BPM", (200, 200, 200),
                                  "bpm_label",
                                  anchor=NW)
            bpm_textbox = TextBox(Vector2(120, 60), load_img("resources/UI/gen/textboxbar.png", (60, 16)),
                                  pygame.font.SysFont("Arial", 16), (200, 200, 200), "bpm_textbox",
                                  allowed_chars="0123456789", default_text=str(sing.ROOT.parameters["SPD"]),
                                  anchor=NW)

            spd_label = TextLabel(Vector2(20, 95), 0, pygame.font.SysFont("Arial", 18), "Speed(px/beat)",
                                  (200, 200, 200), "spd_label", anchor=NW)
            spd_textbox = TextBox(Vector2(120, 95), load_img("resources/UI/gen/textboxbar.png", (60, 16)),
                                  pygame.font.SysFont("Arial", 16), (200, 200, 200), "spd_textbox",
                                  allowed_chars="0123456789", default_text=str(sing.ROOT.parameters["SPD"]),
                                  anchor=NW)

            name_label = TextLabel(Vector2(20, 130), 0, pygame.font.SysFont("Arial", 18), "Map name", (200, 200, 200),
                                   "name_label",
                                   anchor=NW)
            name_textbox = TextBox(Vector2(120, 130), load_img("resources/UI/gen/textboxbar.png", (60, 16)),
                                   pygame.font.SysFont("Arial", 16), (200, 200, 200), "name_textbox",
                                   default_text=sing.ROOT.parameters["map_name"], anchor=NW)

            bc.children.add_gameobjects(close_btn, bpm_label, bpm_textbox, name_label, name_textbox, spd_label,
                                        spd_textbox)
            sing.ROOT.add_gameObject(bc)

    settings_btn = Button(Vector2(0, 160), 0, load_img("resources/UI/edit/settings.png"), "settings_btn",
                          on_mouse_down_func=edit_settings, anchor=N)

    def play_mode():
        exit_star()
        background.set_enabled(False)
        sing.ROOT.game_objects["map_builder"].set_enabled(False)
        if "settings_background" in sing.ROOT.game_objects:
            sing.ROOT.game_objects["settings_background"].set_enabled(False)
        export()
        play(sing.ROOT.game_objects["map_builder"].get_path(), edit_mode=True)

    play_btn = Button(Vector2(0, 200), 0, load_img("resources/UI/edit/play.png"), "play_btn",
                      on_mouse_down_func=play_mode, anchor=N)

    def export():
        sing.ROOT.game_objects["map_builder"].save()

    export_btn = Button(Vector2(0, 240), 0, load_img("resources/UI/edit/save.png"), "save_btn",
                        on_mouse_down_func=export, anchor=N)

    title_label = TextLabel(Vector2(0, 50), 0, pygame.font.SysFont("Arial", 35, bold=True), "Edit map",
                            (190, 200, 210), "title_label", anchor=N)
    background.children.add_gameobjects(cursor_btn, delete_btn, star_btn, select_img, settings_btn, play_btn,
                                        export_btn)
    sing.ROOT.add_gameObject(background, title_label, MapBuilder())


def edit_choose_music():
    sing.ROOT.clear_objects()

    choose_panel = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", sing.ROOT.screen_dim), "menu_panel",
                                anchor=CENTER)
    choose_label = TextLabel(Vector2(0, 30), 0, pygame.font.SysFont("Arial", 25), "Choose your music",
                             (200, 200, 200), "choose_label", anchor=N)

    display_path_label = TextLabel(Vector2(0, 20), 0, pygame.font.SysFont("Arial", 20), "",
                                   (200, 200, 200), "display_path_label", anchor=CENTER)
    go_btn = Button(Vector2(0, 140), 0, pygame.Surface((50, 50)), "go_btn",
                    text="Go", font=pygame.font.SysFont("Arial", 20), text_color=(200, 200, 200),
                    on_mouse_up_func=edit, anchor=CENTER)
    go_btn.set_enabled(False)

    def ask_file():
        import tkinter.filedialog
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[("Music file", "*.mp3; *.wav")])
        top.destroy()
        display_path_label.set_text(file_name)
        load_sound(file_name, "edit_music")
        go_btn.set_enabled(True)
        map_def_name = os.path.basename(file_name)
        shutil.copy(file_name, "resources/musics/")
        load_sound(os.path.join("resources/musics/", file_name), "music")
        sing.ROOT.set_parameter("editing_map", Map(map_def_name, os.path.join("resources/musics/", map_def_name)))
        sing.ROOT.set_parameter("BPM", 90)
        sing.ROOT.set_parameter("SPD", 100)
        sing.ROOT.set_parameter("map_name", map_def_name)

    choose_btn = Button(Vector2(0, -20), 0, pygame.Surface((50, 50)), "choose_btn",
                        text="Choose", font=pygame.font.SysFont("Arial", 20), text_color=(200, 200, 200),
                        on_mouse_up_func=ask_file, anchor=CENTER)

    choose_panel.children.add_gameobjects(choose_label, choose_btn, display_path_label, go_btn)
    sing.ROOT.add_gameObject(choose_panel)


def menu():
    sing.ROOT.clear_objects()

    menu_panel = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", sing.ROOT.screen_dim), "menu_panel",
                              anchor=CENTER)
    title_label = TextLabel(Vector2(0, 30), 0, pygame.font.SysFont("Arial", 25), "Interstellar beats",
                            (200, 200, 200), "title_label", anchor=N)

    play_btn = Button(Vector2(0, 0), 0, pygame.Surface((50, 50)), "play_btn", text="Play",
                      font=pygame.font.SysFont("Arial", 20), text_color=(180, 180, 180),
                      on_mouse_down_func=play, anchor=CENTER)
    edit_btn = Button(Vector2(0, 75), 0, pygame.Surface((50, 50)), "edit_btn", text="Edit",
                      font=pygame.font.SysFont("Arial", 20), text_color=(180, 180, 180),
                      on_mouse_down_func=edit_choose_music, anchor=CENTER)

    def quit_game():
        import sys
        pygame.quit()
        sys.exit(0)

    quit_btn = Button(Vector2(0, 150), 0, pygame.Surface((50, 50)), "quit_btn", text="Quit",
                      font=pygame.font.SysFont("Arial", 20), text_color=(180, 180, 180),
                      on_mouse_up_func=quit_game, anchor=CENTER)
    menu_panel.children.add_gameobjects(title_label, play_btn, edit_btn, quit_btn)
    sing.ROOT.add_gameObject(menu_panel)


def main():
    root = GameRoot((1440, 900), (20, 20, 55), "Test", os.path.dirname(os.path.realpath(__file__)),
                    Vector2(0, 0), display_flag=pygame.FULLSCREEN, fps_limit=200)
    menu()

    root.mainloop()


if __name__ == '__main__':
    main()
