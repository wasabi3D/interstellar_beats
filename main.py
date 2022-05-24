import pygame

from GameExtensions.UI import *

from GameManager.MainLoopManager import GameRoot
import GameManager.singleton as sing
from objects import Star, NoteRenderer, load_map
from pygame import Vector2

import os


def play():
    sing.ROOT.clear_objects()
    star = Star(Vector2(0, 0), 10, pygame.mixer.Sound("resources/musics/surface.mp3"), "star")
    notes = load_map("resources/maps/surface.scr")

    sing.ROOT.add_gameObject(star, NoteRenderer(notes))


def edit():
    sing.ROOT.clear_objects()

    choose_panel = BaseUIObject(Vector2(0, 0), 0, load_img("resources/blank.png", sing.ROOT.screen_dim), "menu_panel",
                                anchor=CENTER)
    choose_label = TextLabel(Vector2(0, 30), 0, pygame.font.SysFont("Arial", 25), "Choose your music",
                             (200, 200, 200), "choose_label", anchor=N)

    display_path_label = TextLabel(Vector2(0, 20), 0, pygame.font.SysFont("Arial", 20), "",
                                   (200, 200, 200), "display_path_label", anchor=CENTER)

    def ask_file():
        import tkinter.filedialog
        top = tkinter.Tk()
        top.withdraw()
        file_name = tkinter.filedialog.askopenfilename(parent=top, filetypes=[("Music file", "*.mp3", "*.wav")])
        top.destroy()
        display_path_label.set_text(file_name)
    choose_btn = Button(Vector2(0, -20), 0, pygame.Surface((50, 50)), "choose_btn",
                        text="Choose", font=pygame.font.SysFont("Arial", 20), text_color=(200, 200, 200),
                        on_mouse_up_func=ask_file, anchor=CENTER)

    choose_panel.children.add_gameobjects(choose_label, choose_btn, display_path_label)
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
                      on_mouse_down_func=edit, anchor=CENTER)

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
                    Vector2(0, 0), display_flag=pygame.FULLSCREEN)
    menu()

    root.mainloop()


if __name__ == '__main__':
    main()
