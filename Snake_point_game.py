import tkinter as tk
import random
import os
game_over_text = None
replay_btn = None


# ---------------- SOUND ----------------
try:
    import winsound
    def eat_sound():
        winsound.Beep(800, 100)
    def game_over_sound():
        winsound.Beep(300, 500)
except:
    def eat_sound():
        root.bell()
    def game_over_sound():
        root.bell()

# ---------------- GAME SETTINGS ----------------
WIDTH = 500
HEIGHT = 500
SIZE = 20
SPEED = 120

paused = False
game_running = True
score = 0

# ---------------- LEADERBOARD ----------------
FILE = "leaderboard.txt"

def load_scores():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return [int(x.strip()) for x in f.readlines() if x.strip().isdigit()]

def save_score(new_score):
    scores = load_scores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]
    with open(FILE, "w") as f:
        for s in scores:
            f.write(str(s) + "\n")
    return scores

leaderboard = load_scores()

# ---------------- WINDOW ----------------
root = tk.Tk()
root.title("🐍 Snake Game with Leaderboard")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

score_label = tk.Label(
    root,
    text="Score: 0",
    font=("Arial", 14)
)
score_label.pack()

status_label = tk.Label(root, text="Running ▶️", font=("Arial", 12))
status_label.pack()

leaderboard_label = tk.Label(
    root,
    text="🏆 Leaderboard\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(leaderboard)]),
    font=("Arial", 12),
    fg="blue"
)
leaderboard_label.pack(pady=5)

# ---------------- SNAKE ----------------
snake = [(100, 100), (80, 100), (60, 100)]
direction = "Right"

# ---------------- FOOD ----------------
food_x = random.randint(0, (WIDTH - SIZE)//SIZE) * SIZE
food_y = random.randint(0, (HEIGHT - SIZE)//SIZE) * SIZE
food = canvas.create_oval(food_x, food_y, food_x+SIZE, food_y+SIZE, fill="red")

# ---------------- DRAW SNAKE ----------------
def draw_snake():
    canvas.delete("snake")
    for x, y in snake:
        canvas.create_rectangle(
            x, y, x+SIZE, y+SIZE,
            fill="green", tag="snake"
        )

# ---------------- MOVE SNAKE ----------------
def move_snake():
    global food_x, food_y, score, game_running

    if not game_running or paused:
        root.after(SPEED, move_snake)
        return

    head_x, head_y = snake[0]

    if direction == "Up":
        new_head = (head_x, head_y - SIZE)
    elif direction == "Down":
        new_head = (head_x, head_y + SIZE)
    elif direction == "Left":
        new_head = (head_x - SIZE, head_y)
    else:
        new_head = (head_x + SIZE, head_y)

    # Wall collision
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        game_over()
        return

    # Self collision
    if new_head in snake:
        game_over()
        return

    snake.insert(0, new_head)

    # Eat food
    if new_head == (food_x, food_y):
        score += 10
        eat_sound()

        food_x = random.randint(0, (WIDTH - SIZE)//SIZE) * SIZE
        food_y = random.randint(0, (HEIGHT - SIZE)//SIZE) * SIZE
        canvas.coords(food, food_x, food_y, food_x+SIZE, food_y+SIZE)
    else:
        snake.pop()

    score_label.config(text=f"Score: {score}")
    draw_snake()
    root.after(SPEED, move_snake)

# ---------------- GAME OVER ----------------
def game_over():
    global game_running, leaderboard, game_over_text, replay_btn

    game_running = False
    game_over_sound()
    status_label.config(text="Game Over ❌")

    leaderboard = save_score(score)

    leaderboard_label.config(
        text="🏆 Leaderboard\n" +
        "\n".join([f"{i+1}. {s}" for i, s in enumerate(leaderboard)])
    )

    game_over_text = canvas.create_text(
        WIDTH//2, HEIGHT//2 - 40,
        text="GAME OVER",
        fill="white",
        font=("Arial", 28, "bold")
    )

    replay_btn = tk.Button(
        root,
        text="🔁 Replay",
        font=("Arial", 14, "bold"),
        bg="green",
        fg="white",
        command=reset_game
    )
    replay_btn.pack(pady=10)


# ---------------- CONTROLS ----------------
def change_direction(event):
    global direction

    if event.keysym == "Up" and direction != "Down":
        direction = "Up"
    elif event.keysym == "Down" and direction != "Up":
        direction = "Down"
    elif event.keysym == "Left" and direction != "Right":
        direction = "Left"
    elif event.keysym == "Right" and direction != "Left":
        direction = "Right"
    elif event.keysym.lower() == "p":
        pause_game()
    elif event.keysym.lower() == "r":
        resume_game()
    elif event.keysym == "Return" and not game_running:
       reset_game()


def pause_game():
    global paused
    paused = True
    status_label.config(text="Paused ⏸️")

def resume_game():
    global paused
    paused = False
    status_label.config(text="Running ▶️")

root.bind("<KeyPress>", change_direction)

def reset_game():
    global snake, direction, score, game_running, paused
    global food_x, food_y, game_over_text, replay_btn

    # Clear canvas
    canvas.delete("all")

    # Reset values
    snake = [(100, 100), (80, 100), (60, 100)]
    direction = "Right"
    score = 0
    game_running = True
    paused = False

    # Redraw food
    food_x = random.randint(0, (WIDTH - SIZE)//SIZE) * SIZE
    food_y = random.randint(0, (HEIGHT - SIZE)//SIZE) * SIZE
    canvas.create_oval(food_x, food_y, food_x+SIZE, food_y+SIZE, fill="red")

    score_label.config(text="Score: 0")
    status_label.config(text="Running ▶️")

    # Remove replay button if exists
    if replay_btn:
        replay_btn.destroy()

    draw_snake()
    move_snake()


# ---------------- START GAME ----------------
draw_snake()
move_snake()

root.mainloop()
