import math
import sys
import time
import numpy as np


class Board:
    size = int()

    def __init__(self, size: int = 50):
        Board.size = size
        self.LINE_UP = '\033[1A'
        self.LINE_CLEAR = '\x1b[2K'
        self._board = []
        self.clear()
        sys.stdout.write(f"stty cols {self.size + 2} rows {self.size + 2}{self.LINE_CLEAR}\033[0;0f")
        for line in self._board:
            sys.stdout.write(line)
        self.changed_lines = list()
        self.points = set()

    def clear(self):
        self._board = ["＋" + "－" * self.size + "＋" + '\n'] + \
                      ["｜" + "　" * self.size + "｜" + "\n" for _ in range(self.size)] + \
                      ["＋" + "－" * self.size + "＋" + "\n"]

    def update(self):
        pass

    def place(self, x: int, y: int):
        if 0 <= x < self.size and 0 <= y < self.size:
            self._board[y + 1] = self._board[y + 1][:x + 1] + "＊" + self._board[y + 1][x + 2:]
        self.changed_lines += [y]

    def remove(self, x: int, y: int):
        if 0 <= x < self.size and 0 <= y < self.size:
            self._board[y + 1] = self._board[y + 1][:x + 1] + "　" + self._board[y + 1][x + 2:]
            self.changed_lines += [y]

    def draw(self):
        for _ in range(self.size + 2):
            sys.stdout.write(self.LINE_UP + self.LINE_CLEAR)
        for line in self._board:
            sys.stdout.write(line)


class MovingPoint:
    def __init__(self, board: Board, x0: int, y0: int, angle: int = 0, velocity: int = 1):
        self.x0, self.y0 = x0, y0
        self.coords = np.array([x0, y0], dtype=np.float64)
        self.board = board
        self.angle = angle
        self.velocity = velocity
        self.delta = Board.size
        self.board.place(round(self.coords[0]), round(self.coords[1]))

    def move(self):
        self.board.remove(round(self.coords[0]), round(self.coords[1]))
        dx = self.velocity * math.cos(math.radians(self.angle))
        dy = self.velocity * math.sin(math.radians(self.angle))
        d = np.array([dx, dy], dtype=np.float64)
        self.coords += d
        if self.distance() > (self.delta / 2):
            self.velocity *= -1
            self.coords -= (d * 2)
        self.board.place(round(self.coords[0]), round(self.coords[1]))

    def distance(self, x0=25, y0=25):
        return int(math.sqrt((self.coords[0] - x0) ** 2 + (self.coords[1] - y0) ** 2))


class MultiplePoints:
    def __init__(self, board: Board, points: list, angle: int = 0, velocity: int = 1):
        self.points = []
        self.board = board
        self.angle = angle
        self.velocity = velocity
        for x0, y0 in points:
            self.points.append(MovingPoint(board, x0, y0, angle, velocity))

    def move(self):
        dx = self.velocity * math.cos(math.radians(self.angle))
        dy = self.velocity * math.sin(math.radians(self.angle))
        d = np.array([dx, dy], dtype=np.float64)
        self.velocity *= -1
        for point in self.points:
            point.coords += d
            if point.distance() > (point.delta / 2):
                point.coords -= d
                break
            point.coords -= d
        else:
            self.velocity *= -1
        for point in self.points:
            point.velocity = self.velocity
            point.move()


class MovingCircle(MultiplePoints):
    def __init__(self, board: Board, x0, y0, radius, angle=0, velocity=0):
        points = []
        for x in range(x0 - radius, x0 + radius + 1):  # (x-x0)**2 + (y-y0)**2 = radius**2
            y_delta = round(math.sqrt(radius ** 2 - (x - x0) ** 2))  # abs(y-y0) = sqrt(radius ** 2 - (x-x0) ** 2)
            y1, y2 = y0 + y_delta, y0 - y_delta
            points.append([x, y1])
            if y1 != y2:
                points.append([x, y2])
        super().__init__(board, points, angle, velocity)


b = Board()
circle = MovingCircle(b, 25, 25, 10, velocity=1)
while True:
    try:
        circle.move()
        b.draw()
        time.sleep(.1)
    except KeyboardInterrupt:
        print(Board.size)
        break