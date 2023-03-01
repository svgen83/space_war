import os


def get_rocket_frames():
    path_1 = os.path.join("figures",
                          "rocket_frame_1.txt")
    path_2 = os.path.join("figures",
                          "rocket_frame_2.txt")
    with open(path_1) as f:
        frame1 = f.read()
    with open(path_2) as f:
        frame2 = f.read()
    return frame1, frame2


def get_garbage_frames():
    garbage_frames = []
    garbage_figures = ["duck.txt", "lamp.txt",
                       "hubble.txt", "trash_large.txt",
                       "trash_small.txt", "trash_xl.txt"]
    for figure in garbage_figures:
        path = os.path.join("figures", figure)
        with open(path) as f:
            frame = f.read()
        garbage_frames.append(frame)
    return garbage_frames


def get_game_over_frame():
    path = os.path.join("figures",
                        "game_over.txt")
    with open(path) as f:
        game_over = f.read()
    return game_over
