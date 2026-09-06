import tkinter as tk
import random


class SpaceCollectorGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Collector Mini-Game")
        self.root.resizable(False, False)

        # 1. Screen Dimensions
        self.WIDTH = 800
        self.HEIGHT = 600
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg="black", highlightthickness=0)
        self.canvas.pack()

        # 2. Game Variables
        self.score = 0
        self.game_over = False

        # Player (Planet) configuration
        self.player_radius = 25
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 60
        self.player_speed = 15

        # Game objects configuration
        self.crystal_radius = 12
        self.asteroid_radius = 20
        self.asteroids = []  # List of dictionaries to track active asteroids
        self.base_asteroid_speed = 4

        # Track key states for smooth holding/movement
        self.keys = {"Left": False, "Right": False, "Up": False, "Down": False}

        # 3. Bind events and initialize
        self.setup_controls()
        self.start_game()

    def start_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.game_over = False
        self.asteroids.clear()
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 60

        # Draw static star background
        for _ in range(100):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            size = random.randint(1, 3)
            self.canvas.create_oval(x, y, x + size, y + size, fill="white", tags="star")

        # Create player planet sprite
        self.player = self.canvas.create_oval(
            self.player_x - self.player_radius, self.player_y - self.player_radius,
            self.player_x + self.player_radius, self.player_y + self.player_radius,
            fill="#3498db", outline=""
        )

        # Spawn the first crystal
        self.spawn_crystal()

        # Spawn 3 starting asteroids
        for _ in range(3):
            self.spawn_asteroid(initial=True)

        # Draw UI Score text
        self.score_text = self.canvas.create_text(
            60, 25, text=f"Score: {self.score}", fill="white", font=("Arial", 18, "bold")
        )

        # Run the primary game loop
        self.game_loop()

    def setup_controls(self):
        # Track when keys are held down and when they are released
        self.root.bind("<KeyPress-Left>", lambda e: self.set_key("Left", True))
        self.root.bind("<KeyRelease-Left>", lambda e: self.set_key("Left", False))
        self.root.bind("<KeyPress-Right>", lambda e: self.set_key("Right", True))
        self.root.bind("<KeyRelease-Right>", lambda e: self.set_key("Right", False))
        self.root.bind("<KeyPress-Up>", lambda e: self.set_key("Up", True))
        self.root.bind("<KeyRelease-Up>", lambda e: self.set_key("Up", False))
        self.root.bind("<KeyPress-Down>", lambda e: self.set_key("Down", True))
        self.root.bind("<KeyRelease-Down>", lambda e: self.set_key("Down", False))
        self.root.bind("<Return>", self.restart_game)

    def set_key(self, key, value):
        if not self.game_over:
            self.keys[key] = value

    def spawn_crystal(self):
        cx = random.randint(self.crystal_radius, self.WIDTH - self.crystal_radius)
        cy = random.randint(self.crystal_radius, self.HEIGHT - self.crystal_radius)

        # Clear old crystal if it exists
        if hasattr(self, 'crystal'):
            self.canvas.delete(self.crystal)

        self.crystal = self.canvas.create_oval(
            cx - self.crystal_radius, cy - self.crystal_radius,
            cx + self.crystal_radius, cy + self.crystal_radius,
            fill="#2ecc71", outline=""
        )
        self.crystal_x, self.crystal_y = cx, cy

    def spawn_asteroid(self, initial=False):
        ax = random.randint(self.asteroid_radius, self.WIDTH - self.asteroid_radius)
        # Stagger spawn heights on initial load so they don't fall as a single flat wall
        ay = random.randint(-400, -self.asteroid_radius) if initial else -self.asteroid_radius
        speed = random.randint(3, 6) + (self.score // 5)

        asteroid_id = self.canvas.create_oval(
            ax - self.asteroid_radius, ay - self.asteroid_radius,
            ax + self.asteroid_radius, ay + self.asteroid_radius,
            fill="#e74c3c", outline=""
        )
        self.asteroids.append({"id": asteroid_id, "x": ax, "y": ay, "speed": speed})

    def move_player(self):
        if self.keys["Left"]: self.player_x -= self.player_speed
        if self.keys["Right"]: self.player_x += self.player_speed
        if self.keys["Up"]: self.player_y -= self.player_speed
        if self.keys["Down"]: self.player_y += self.player_speed

        # Restrict movement to screen boundaries
        self.player_x = max(self.player_radius, min(self.player_x, self.WIDTH - self.player_radius))
        self.player_y = max(self.player_radius, min(self.player_y, self.HEIGHT - self.player_radius))

        # Update canvas coordinate positioning
        self.canvas.coords(
            self.player,
            self.player_x - self.player_radius, self.player_y - self.player_radius,
            self.player_x + self.player_radius, self.player_y + self.player_radius
        )

    def game_loop(self):
        if self.game_over:
            return

        # 1. Update player physics
        self.move_player()

        # 2. Update asteroids physics and logic
        for ast in list(self.asteroids):
            ast["y"] += ast["speed"]
            self.canvas.coords(
                ast["id"],
                ast["x"] - self.asteroid_radius, ast["y"] - self.asteroid_radius,
                ast["x"] + self.asteroid_radius, ast["y"] + self.asteroid_radius
            )

            # Respawn asteroid if it moves past the bottom of the screen
            if ast["y"] > self.HEIGHT + self.asteroid_radius:
                self.canvas.delete(ast["id"])
                self.asteroids.remove(ast)
                self.spawn_asteroid()

            # Check for radial collision with player planet
            dist = ((self.player_x - ast["x"]) ** 2 + (self.player_y - ast["y"]) ** 2) ** 0.5
            if dist < (self.player_radius + self.asteroid_radius):
                self.trigger_game_over()
                return

        # 3. Check for crystal collection
        c_dist = ((self.player_x - self.crystal_x) ** 2 + (self.player_y - self.crystal_y) ** 2) ** 0.5
        if c_dist < (self.player_radius + self.crystal_radius):
            self.score += 1
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
            self.spawn_crystal()

            # Dynamic difficulty: Add another asteroid every 3 points (Cap at 12)
            if self.score % 3 == 0 and len(self.asteroids) < 12:
                self.spawn_asteroid()

        # Loop roughly every 16ms (~60 Frames Per Second)
        self.root.after(16, self.game_loop)

    def trigger_game_over(self):
        self.game_over = True
        # Clear all input buffers
        self.keys = {k: False for k in self.keys}

        # Display game over text overlay
        self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2 - 40,
            text="GAME OVER", fill="#e74c3c", font=("Arial", 40, "bold")
        )
        self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2 + 10,
            text=f"Your Final Score: {self.score}", fill="white", font=("Arial", 20)
        )
        self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2 + 60,
            text="Press ENTER to Play Again", fill="white", font=("Arial", 16)
        )

    def restart_game(self, event):
        if self.game_over:
            self.start_game()


# Execution entry point
if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceCollectorGame(root)
    root.mainloop()
