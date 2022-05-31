import pygame

from GameExtensions.UI import *

from GameManager.MainLoopManager import GameRoot
import GameManager.singleton as sing
from GameManager.resources import *
from objects import Star, NoteRenderer, load_map, PauseManager
from pygame import Vector2

import os


def play():
    sing.ROOT.clear_objects()
    load_sound("resources/musics/surface.mp3", "music")
    star = Star(Vector2(0, 0), 10, sing.ROOT.sounds["music"], "star")
    notes = load_map("resources/maps/surface.scr")

    sing.ROOT.add_gameObject(star, NoteRenderer(notes), PauseManager())


def edit_settings():
    if "edit_settings_already_opened" in sing.ROOT.parameters and sing.ROOT.parameters["edit_settings_already_opened"]:
        sing.ROOT.game_objects["settings_background"].set_enabled(True)
    else:
        background = BaseUIObject(Vector2(0, 0), 0, load_img("resources/UI/background.png", (200, 250)),
                                  "settings_background", CENTER)
        close_btn = Button(Vector2(-20, 20), 0, load_img("resources/UI/gen/cross.png"), "close_btn",
                           on_mouse_up_func=lambda: background.set_enabled(False), anchor=NE)
        bpm_label = TextLabel(Vector2(20, 60), 0, pygame.font.SysFont("Arial", 18), "BPM", (200, 200, 200), "bpm_label",
                              anchor=NW)
        bpm_textbox = TextBox(Vector2(120, 60), load_img("resources/UI/gen/textboxbar.png", (60, 16)),
                              pygame.font.SysFont("Arial", 16), (200, 200, 200), "bpm_textbox", allowed_chars="0123456789",
                              anchor=NW)
        background.children.add_gameobjects(close_btn, bpm_label, bpm_textbox)
        sing.ROOT.add_gameObject(background)
        sing.ROOT.set_parameter("edit_settings_already_opened", True)


def edit(music: pygame.mixer.Sound):
    sing.ROOT.clear_objects()
    background = BaseUIObject(Vector2(-100, 0), 0, load_img("resources/UI/background.png", (50, 200)),
                              "menu_background", anchor=E)
    cursor_btn = Button(Vector2(0, 40), 0, load_img("resources/UI/edit/cursor.png"), "cursor_btn",
                        on_mouse_down_func=None, anchor=N)
    delete_btn = Button(Vector2(0, 80), 0, load_img("resources/UI/edit/delete.png"), "delete_btn",
                        on_mouse_down_func=None, anchor=N)
    star_btn = Button(Vector2(0, 120), 0, load_img("resources/UI/edit/star.png"), "star_btn",
                      on_mouse_down_func=None, anchor=N)
    settings_btn = Button(Vector2(0, 160), 0, load_img("resources/UI/edit/settings.png"), "settings_btn",
                          on_mouse_down_func=edit_settings, anchor=N)
    select_img = BaseUIObject(Vector2(0, 40), 0, load_img("resources/UI/edit/select.png"), "select_img", anchor=N)

    title_label = TextLabel(Vector2(0, 50), 0, pygame.font.SysFont("Arial", 35, bold=True), "Edit map",
                            (190, 200, 210), "title_label", anchor=N)
    background.children.add_gameobjects(cursor_btn, delete_btn, star_btn, select_img, settings_btn)
    sing.ROOT.add_gameObject(background, title_label)


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
                    on_mouse_up_func=lambda: edit(sing.ROOT.sounds["edit_music"]), anchor=CENTER)
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
