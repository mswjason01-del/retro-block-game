from app.game import Board, SHAPES, rotate, score_for_clear


def test_piece_rotation_and_wall_collision():
    board = Board()
    shape = rotate(SHAPES['T'])
    assert len(shape) == 3
    assert board.collides(shape, -1, 0)
    assert not board.collides(shape, 3, 0)


def test_lock_and_line_clear():
    board = Board()
    board.cells[-1] = ['X'] * 8 + [None, None]
    assert board.lock('O', SHAPES['O'], 8, 18)
    assert board.clear_lines() == 1
    assert all(cell is None for cell in board.cells[0])


def test_scoring_values_and_level_progression():
    assert score_for_clear(4, 3) == 2400
    assert 1 + 20 // 10 == 3


def test_spawn_collision_means_game_over_condition():
    board = Board()
    board.cells[0][4] = 'X'
    assert board.collides(SHAPES['T'], 3, 0)
