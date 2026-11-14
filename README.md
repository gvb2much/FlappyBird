from drafter import *
from dataclasses import dataclass
import random


@dataclass
class State:
    score: int
    bird_height: int
    pipe_distance: int
    pipe_gap: int
    game_over: bool


@route
def index(state: State) -> Page:

    if state.game_over:
        return Page(
            state,
            [
                Header("💥 GAME OVER"),
                "Final Score: " + str(state.score),
                LineBreak(),
                Button("🔄 Restart", "restart")
            ]
        )

    game_visual = []

    # HEIGHTS 15 DOWN TO 0
    for height in range(15, -1, -1):

        row = ""

        # BIRD
        if height == state.bird_height:
            row += "🐦"
        else:
            row += " "

        # DISTANCE TO PIPE
        row += " " * (state.pipe_distance * 8)

        # PIPE
        # Gap is 5 spaces tall
        if abs(height - state.pipe_gap) > 2:
            row += "🟩"
        else:
            row += " "

        game_visual.append(Text(row))

    return Page(
        state,
        [
            Header("🐦 Flappy Bird"),

            "Score: " + str(state.score),
            LineBreak(),

            "Bird Height: " + str(state.bird_height),
            LineBreak(),

            "Pipe Distance: " + str(state.pipe_distance),
            LineBreak(),

            Div(game_visual),

            LineBreak(),

            Button("⬆️ FLAP", "flap"),
            Button("⏳ WAIT", "wait")
        ]
    )


@route
def flap(state: State) -> Page:

    state.bird_height += 2

    if state.bird_height > 15:
        state.bird_height = 15

    return advance(state)


@route
def wait(state: State) -> Page:
    return advance(state)


def advance(state: State) -> Page:

    # Gravity
    state.bird_height -= 1

    if state.bird_height < 0:
        state.game_over = True
        return index(state)

    # Move pipe
    state.pipe_distance -= 1

    if state.pipe_distance <= 0:

        # Bird must be inside gap
        if abs(state.bird_height - state.pipe_gap) <= 2:

            state.score += 1

            # Next pipe
            state.pipe_distance = 6

            # New random gap
            state.pipe_gap = random.randint(4, 11)

        else:

            state.game_over = True

    return index(state)


@route
def restart(state: State) -> Page:

    state.score = 0
    state.bird_height = 8
    state.pipe_distance = 6
    state.pipe_gap = random.randint(4, 11)
    state.game_over = False

    return index(state)


start_server(
    State(
        0,                      # score
        8,                      # bird height
        6,                      # pipe distance
        random.randint(4, 11),  # pipe gap
        False                   # game over
    )
)


