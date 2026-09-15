"""Small, dependency-free rules engine used for game-rule regression tests."""

SHAPES = {
    "I": [[1, 1, 1, 1]], "O": [[1, 1], [1, 1]], "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]], "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]], "L": [[0, 0, 1], [1, 1, 1]],
}


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


class Board:
    width, height = 10, 20

    def __init__(self):
        self.cells = [[None] * self.width for _ in range(self.height)]

    def collides(self, shape, x, y):
        for row_y, row in enumerate(shape):
            for row_x, value in enumerate(row):
                if value and (x + row_x < 0 or x + row_x >= self.width or y + row_y >= self.height or (y + row_y >= 0 and self.cells[y + row_y][x + row_x])):
                    return True
        return False

    def lock(self, kind, shape, x, y):
        if self.collides(shape, x, y):
            return False
        for row_y, row in enumerate(shape):
            for row_x, value in enumerate(row):
                if value and y + row_y >= 0:
                    self.cells[y + row_y][x + row_x] = kind
        return True

    def clear_lines(self):
        kept = [row for row in self.cells if not all(row)]
        count = self.height - len(kept)
        self.cells = [[None] * self.width for _ in range(count)] + kept
        return count


def score_for_clear(cleared, level):
    return [0, 100, 300, 500, 800][cleared] * level
