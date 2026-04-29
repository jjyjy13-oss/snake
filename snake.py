import random
import tkinter as tk


CELL_SIZE = 20
SPEED_MS = 120


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake Game")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda _: self.root.attributes("-fullscreen", False))

        self.window_width = self.root.winfo_screenwidth()
        self.window_height = self.root.winfo_screenheight()
        self.grid_width = self.window_width // CELL_SIZE
        self.grid_height = self.window_height // CELL_SIZE

        self.canvas = tk.Canvas(root, width=self.window_width, height=self.window_height, bg="black")
        self.canvas.pack()

        self.score = 0
        self.score_label = tk.Label(root, text=f"Score: {self.score}", font=("Arial", 14))
        self.score_label.pack(pady=6)

        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.apple = self._spawn_apple()
        self.game_over = False

        self.root.bind("<Up>", lambda _: self._set_direction((0, -1)))
        self.root.bind("<Down>", lambda _: self._set_direction((0, 1)))
        self.root.bind("<Left>", lambda _: self._set_direction((-1, 0)))
        self.root.bind("<Right>", lambda _: self._set_direction((1, 0)))
        self.root.bind("<w>", lambda _: self._set_direction((0, -1)))
        self.root.bind("<s>", lambda _: self._set_direction((0, 1)))
        self.root.bind("<a>", lambda _: self._set_direction((-1, 0)))
        self.root.bind("<d>", lambda _: self._set_direction((1, 0)))
        self.root.bind("<r>", lambda _: self._restart())

        self._draw()
        self._tick()

    def _set_direction(self, new_direction: tuple[int, int]) -> None:
        if self.game_over:
            return
        # 바로 반대 방향으로 꺾으면 자기 몸과 즉시 충돌하므로 무시한다.
        if new_direction[0] == -self.direction[0] and new_direction[1] == -self.direction[1]:
            return
        self.pending_direction = new_direction

    def _spawn_apple(self) -> tuple[int, int]:
        while True:
            pos = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
            if pos not in self.snake:
                return pos

    def _tick(self) -> None:
        if self.game_over:
            return

        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 벽 충돌
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            self._end_game()
            return

        # 몸통 충돌
        if new_head in self.snake:
            self._end_game()
            return

        self.snake.insert(0, new_head)

        # 사과를 먹으면 꼬리를 유지해서 길이가 1 증가한다.
        if new_head == self.apple:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.apple = self._spawn_apple()
        else:
            self.snake.pop()

        self._draw()
        self.root.after(SPEED_MS, self._tick)

    def _draw(self) -> None:
        self.canvas.delete("all")

        # 사과
        self._draw_cell(self.apple, "red")

        # 뱀
        for i, segment in enumerate(self.snake):
            color = "lime" if i == 0 else "green"
            self._draw_cell(segment, color)

    def _draw_cell(self, pos: tuple[int, int], color: str) -> None:
        x, y = pos
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray20")

    def _end_game(self) -> None:
        self.game_over = True
        self.canvas.create_text(
            self.window_width // 2,
            self.window_height // 2,
            text=f"Game Over\nScore: {self.score}\nPress R to Restart",
            fill="white",
            font=("Arial", 20, "bold"),
            justify="center",
        )

    def _restart(self) -> None:
        if not self.game_over:
            return
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.apple = self._spawn_apple()
        self.game_over = False
        self._draw()
        self._tick()


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
