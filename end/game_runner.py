import time
from copy import deepcopy
from math import floor

from pygame_utils import *
from important_variables import *


class Game:
    # The padding between the board element (circle or X) and the board
    square_right_padding = 35
    square_bottom_padding = 35
    square_left_padding = 15
    square_top_padding = 15

    # Alterable numbers
    board_line_length = 15
    board_padding = 40  # Padding between the board and the screen
    circle_outline_length = 15

    # Miscellaneous
    X = 1
    CIRCLE = -1
    EMPTY = 0
    is_player1_turn = True
    squares = []
    board = []
    game_is_done = False
    player1_color = [0, 0, 255]
    player2_color = [255, 0, 0]
    moves_left = 9
    square_length = (screen_length - board_line_length * 2) / 3
    square_height = (screen_height - board_line_length * 2) / 3
    dummy_draw_victory_line_function = lambda unused: 0  # Doesn't do anything- the default function if nothing should be drawn
    game_is_paused = True

    # AI Stuff:
    is_single_player = True
    ai_starts = True
    big_number = 10_000  # So that it is guaranteed that the first value is taken because no number will be bigger/smaller than it
    ai_type = CIRCLE
    human_type = X

    def draw_row_victory_line(self, index):
        offset = (self.square_height + self.board_line_length) * index
        draw_line(0, screen_length, offset + self.square_height / 2, offset + self.square_height / 2, self.victory_line_color, 15)

    def draw_column_victory_line(self, index):
        offset = (self.square_length + self.board_line_length) * index
        draw_line(offset + self.square_length / 2, offset + self.square_length / 2, 0, screen_height, self.victory_line_color, 15)

    def draw_diagonal_victory_line(self, index):
        start_left_edge, end_left_edge = 0, screen_length
        start_top_edge, end_top_edge = [0, screen_height] if index == 0 else [screen_height, 0]
        draw_line(start_left_edge, end_left_edge, start_top_edge, end_top_edge, self.victory_line_color, 15)

    def get_all_board_types(self, game_board):
        """returns: [rows, columns, diagonals]"""
        return [game_board[0] + game_board[1] + game_board[2],
                [game_board[i][j] for j in range(3) for i in range(3)],
                [game_board[i][i] for i in range(3)] + [game_board[i][2 - i] for i in range(3)]]

    @property
    def victory_line_color(self):
        return self.player1_color if self.is_player1_turn else self.player2_color

    def __init__(self):
        self.reset_board_elements(False)

    def get_square(self, row, column):
        left_edge = column * (self.square_length + self.board_line_length) + self.square_left_padding
        top_edge = row * (self.square_height + self.board_line_length) + self.square_top_padding
        length = self.square_length - self.square_right_padding
        height = self.square_height - self.square_bottom_padding

        return [left_edge, top_edge, length, height,
                left_edge + length, top_edge + height]

    def draw_x(self, row, column):
        left_edge, top_edge, length, height, right_edge, bottom_edge = self.get_square(row, column)

        draw_line(left_edge, right_edge, top_edge, bottom_edge, self.player1_color, self.circle_outline_length)
        draw_line(left_edge, right_edge, bottom_edge, top_edge, self.player1_color, self.circle_outline_length)

    def draw_circle(self, row, column):
        left_edge, top_edge, length, height, right_edge, bottom_edge = self.get_square(row, column)

        draw_circle(left_edge, top_edge, length, height, self.player2_color, self.circle_outline_length)

    def draw_board_line(self, is_horizontal, square_number):
        square_size = self.square_height if is_horizontal else self.square_length
        offset = square_number * (square_size + self.board_line_length) + square_size

        y1, y2 = [offset] * 2 if is_horizontal else [self.board_padding, screen_height - self.board_padding]
        x1, x2 = [offset] * 2 if not is_horizontal else [self.board_padding, screen_length - self.board_padding]
        draw_line(x1, x2, y1, y2, [0, 255, 0], self.board_line_length)

    def draw_board(self):
        for x in range(2):
            self.draw_board_line(True, x)
            self.draw_board_line(False, x)

    def run_human_player_turns(self):
        mouse_left_edge, mouse_top_edge = get_mouse_position()
        column_length = screen_length / 3
        row_height = screen_height / 3

        row = floor(mouse_top_edge / row_height)
        column = floor(mouse_left_edge / column_length)

        if mouse_was_pressed() and self.board[row][column] == self.EMPTY:
            self.play_move(row, column)

    def get_victory_line_indexes(self, board):
        """returns [index of draw_function, number that draw_function needs]"""

        return_value = [-1, -1]
        all_board_types = self.get_all_board_types(board)

        for i in range(len(all_board_types)):
            board_type = all_board_types[i]

            for j in range(len(board_type) // 3):
                start_index = j * 3
                current_elements = board_type[start_index: start_index + 3]
                player_has_won = abs(sum(current_elements)) == 3

                if player_has_won:
                    return_value = [i, j]
        return return_value

    def player_has_won(self, board):
        return self.get_victory_line_indexes(board)[0] != -1

    def play_move(self, row, column):
        self.board[row][column] = self.X if self.is_player1_turn else self.CIRCLE
        self.moves_left -= 1

        function = self.draw_x if self.is_player1_turn else self.draw_circle
        function(row, column)
        update_display()

        if self.player_has_won(self.board):
            draw_functions = [self.draw_row_victory_line, self.draw_column_victory_line, self.draw_diagonal_victory_line]
            draw_function_index, draw_function_data = self.get_victory_line_indexes(self.board)
            draw_functions[draw_function_index](draw_function_data)
            update_display()

        self.is_player1_turn = not self.is_player1_turn

        if self.player_has_won(self.board) or self.moves_left <= 0:
            pause_game(1)
            self.game_is_paused = True

    def run_game(self):
        if self.game_is_paused:
            self.game_is_paused = False
            self.reset_board_elements(self.is_player1_turn)

        if self.is_player1_turn:
            self.run_human_player_turns()

        else:
            self.play_ai_move()

    def reset_board_elements(self, player1_has_won):
        self.board = [[self.EMPTY, self.EMPTY, self.EMPTY], [self.EMPTY, self.EMPTY, self.EMPTY], [self.EMPTY, self.EMPTY, self.EMPTY]]

        self.is_player1_turn = not player1_has_won
        self.game_is_done = False
        self.moves_left = 9
        clear_screen()
        self.draw_board()
        update_display()

    # AI Stuff
    def get_valid_actions(self, board):
        valid_actions = []

        for row in range(3):
            for column in range(3):
                if board[row][column] == self.EMPTY:
                    valid_actions.append([row, column])

        return valid_actions

    def play_middle_if_applicable(self, best_play, valid_actions):
        # The middle should be played if the AI goes first, and it is available the second turn (guarantees a win) or
        # If the AI goes second, and it is available the first turn (guarantees a tie)
        should_play_middle_if_available = len(valid_actions) == 8 or len(valid_actions) == 7
        middle_is_available = self.board[1][1] == self.EMPTY
        middle_is_playable = middle_is_available and should_play_middle_if_available

        if middle_is_playable:
            best_play[0], best_play[1] = 1, 1

    def play_ai_move(self):
        best_score = -self.big_number
        best_play = []
        valid_actions = self.get_valid_actions(self.board)

        for row, column in self.get_valid_actions(self.board):
            self.board[row][column] = self.ai_type
            score = self.minimax(self.board, 1, True)

            self.board[row][column] = self.EMPTY

            if score > best_score:
                best_score = score
                best_play = [row, column]

        self.play_middle_if_applicable(best_play, valid_actions)
        self.play_move(best_play[0], best_play[1])

    def get_ai_start_data(self, is_maximizing):
        """returns: [beginning_best_score, play_type]; The starting values for the ai best_score and play_type"""

        # The big number is for guaranteeing that the first value is replaced
        return [self.big_number, self.human_type] if is_maximizing else [-self.big_number, self.ai_type]

    def minimax(self, board, depth, is_maximizing):
        valid_actions = self.get_valid_actions(board)

        if self.player_has_won(board):
            number = 100 if is_maximizing else -100
            return number / depth

        elif len(valid_actions) == 0 or depth >= 4:
            return 0

        best_score, play_type = self.get_ai_start_data(is_maximizing)

        for row, column in valid_actions:
            new_board = deepcopy(board)
            new_board[row][column] = play_type

            score = self.minimax(new_board, depth + 1, not is_maximizing)

            # We want a big number if we are maximizing, but a small number if we aren't
            condition = score < best_score if is_maximizing else score > best_score

            if condition:
                best_score = score

        return best_score

call_every_cycle(Game().run_game)