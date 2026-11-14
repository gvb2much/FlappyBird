
from drafter import *
from dataclasses import dataclass, field
import random


# SECOND DATACLASS
@dataclass
class Pipe:
    x: int
    gap_y: int
    passed: bool


# MAIN STATE DATACLASS
@dataclass
class State:
    score: int = 0
    bird_height: int = 8
    bird_velocity: int = 0
    pipes: list[Pipe] = field(default_factory=list)
    game_over: bool = False
    player_name: str = "Player"
    difficulty: str = "Normal"
    show_stats: bool = True
    high_score: int = 0
    high_score_name: str = "Nobody"


# RESET GAME
def reset_game(state: State):
    state.score = 0
    state.bird_height = 8
    state.bird_velocity = 0
    state.game_over = False

    state.pipes = [
        Pipe(6, random.randint(4, 11), False),
        Pipe(12, random.randint(4, 11), False)
    ]


# ROUTE 1: HOME PAGE
@route
def index(state: State) -> Page:
    return Page(state, [
        Header("🐦 FLAPPY BIRD"),
        "Welcome to Flappy Bird!",
        LineBreak(),
        "Fly through the pipes and earn points!",
        LineBreak(),

        Header("🎮 Game Setup"),

        "Enter your player name:",
        TextBox("name", state.player_name),
        LineBreak(),

        "Choose your difficulty:",
        SelectBox(
            "difficulty",
            ["Easy", "Normal", "Hard"],
            state.difficulty
        ),
        LineBreak(),

        "Show game statistics:",
        CheckBox("show_stats", state.show_stats),
        LineBreak(),

        Button("▶️ START GAME", "start_game"),
        Button("📖 Instructions", "instructions"),
        Button("🏆 High Scores", "high_scores")
    ])


# ROUTE 2: INSTRUCTIONS
@route
def instructions(state: State) -> Page:
    return Page(state, [
        Header("📖 HOW TO PLAY"),
        "Welcome to Flappy Bird!",
        LineBreak(),

        "🐦 Keep your bird flying!",
        LineBreak(),

        "⬆️ Press FLAP to jump upward.",
        LineBreak(),

        "⏳ Press WAIT to move forward.",
        LineBreak(),

        "🟩 Avoid hitting the green pipes.",
        LineBreak(),

        "🏆 Earn points by passing pipes.",
        LineBreak(),

        "💥 Falling or hitting a pipe ends the game.",
        LineBreak(),

        Button("🏠 Home", "index"),
        Button("▶️ Play", "start_game")
    ])


# ROUTE 3: START GAME
@route
def start_game(state: State,
               name: str = "",
               difficulty: str = "",
               show_stats: bool = True) -> Page:

    if name.strip() != "":
        state.player_name = name.strip()

    if difficulty in ["Easy", "Normal", "Hard"]:
        state.difficulty = difficulty

    state.show_stats = show_stats

    reset_game(state)
    return game_screen(state)


# ROUTE 4: GAME SCREEN
@route
def game_screen(state: State) -> Page:

    if state.game_over:
        return game_over(state)

    game_visual = []

    # DRAW GAME FROM TOP TO BOTTOM
    for height in range(15, -1, -1):

        row = ""

        # DRAW BIRD
        if height == state.bird_height:
            row += "🐦"
        else:
            row += "  "

        # DRAW MULTIPLE PIPES
        previous_x = 0

        for pipe in state.pipes:

            spaces = max(0, pipe.x - previous_x)
            row += "   " * spaces

            if abs(height - pipe.gap_y) > 2:
                row += "🟩"
            else:
                row += "  "

            previous_x = pipe.x

        game_visual.append(Text(row))

    # FIND NEXT PIPE
    next_pipe = None

    for pipe in state.pipes:
        if pipe.x > 0:
            if next_pipe is None or pipe.x < next_pipe.x:
                next_pipe = pipe

    # GET PIPE INFORMATION
    if next_pipe is not None:
        pipe_distance = next_pipe.x
        pipe_hole_height = next_pipe.gap_y
    else:
        pipe_distance = 0
        pipe_hole_height = 0

    content = [
        Header("🐦 FLAPPY BIRD"),

        "Player: " + state.player_name,
        LineBreak(),

        "Score: " + str(state.score),
        LineBreak(),

        "Pipe Distance: " + str(pipe_distance),
        LineBreak(),

        "Pipe Hole Height: " + str(pipe_hole_height),
        LineBreak()
    ]

    if state.show_stats:
        content.extend([
            "Bird Height: " + str(state.bird_height),
            LineBreak(),

            "Difficulty: " + state.difficulty,
            LineBreak()
        ])

    content.extend([
        Div(game_visual),
        LineBreak(),

        Button("⬆️ FLAP", "flap"),
        Button("⏳ WAIT", "wait"),
        LineBreak(),

        Button("🏠 Home", "index")
    ])

    return Page(state, content)


# ROUTE 5: FLAP
@route
def flap(state: State) -> Page:

    if not state.game_over:
        state.bird_velocity = 2
        state.bird_height += state.bird_velocity

        if state.bird_height > 15:
            state.bird_height = 15

        return advance(state)

    return game_over(state)


# ROUTE 6: WAIT
@route
def wait(state: State) -> Page:

    if not state.game_over:
        state.bird_velocity = 0
        return advance(state)

    return game_over(state)


# UPDATE GAME LOGIC
def advance(state: State) -> Page:

    # GRAVITY
    state.bird_height -= 1

    if state.bird_height < 0:
        state.game_over = True
        return game_over(state)

    # DIFFICULTY CONTROLS PIPE SPEED
    speed = 1

    if state.difficulty == "Hard":
        speed = 2

    # MOVE ALL PIPES
    for pipe in state.pipes:
        pipe.x -= speed

        # CHECK COLLISION
        if pipe.x <= 0 and not pipe.passed:

            if abs(state.bird_height - pipe.gap_y) <= 2:
                state.score += 1
                pipe.passed = True

            else:
                state.game_over = True
                return game_over(state)

    # REMOVE PIPES THAT HAVE PASSED
    state.pipes = [
        pipe for pipe in state.pipes
        if pipe.x > 0
    ]

    # ADD NEW PIPES
    while len(state.pipes) < 2:

        if len(state.pipes) > 0:
            next_x = state.pipes[-1].x + 6
        else:
            next_x = 6

        state.pipes.append(
            Pipe(
                next_x,
                random.randint(4, 11),
                False
            )
        )

    return game_screen(state)


# ROUTE 7: GAME OVER
@route
def game_over(state: State) -> Page:

    state.game_over = True

    if state.score > state.high_score:
        state.high_score = state.score
        state.high_score_name = state.player_name

    return Page(state, [
        Header("💥 GAME OVER"),

        "Player: " + state.player_name,
        LineBreak(),

        "Final Score: " + str(state.score),
        LineBreak(),

        "Best Score: " + str(state.high_score),
        LineBreak(),

        Button("🔄 Restart", "restart"),
        Button("🏆 High Scores", "high_scores"),
        Button("🏠 Home", "index")
    ])


# ROUTE 8: HIGH SCORES
@route
def high_scores(state: State) -> Page:

    return Page(state, [
        Header("🏆 HIGH SCORES"),

        "Best Player: " + state.high_score_name,
        LineBreak(),

        "Highest Score: " + str(state.high_score),
        LineBreak(),

        "Try to beat the record!",
        LineBreak(),

        Button("🏠 Home", "index"),
        Button("▶️ Play Again", "restart")
    ])


# ROUTE 9: RESTART
@route
def restart(state: State) -> Page:

    reset_game(state)
    return game_screen(state)


# START WEBSITE
start_server(State(), site_title="Flappy Bird")
