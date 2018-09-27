# -*- coding: utf-8 -*-
from flask import session, request, flash, redirect, url_for
from game import bdp, mysql
import random, uuid, copy, os, pickle


class Game:
    def __init__(self):
        self.file_obj = 'games/' + str(uuid.uuid4()) + '.txt'
        self.file_name = 'results/' + str(uuid.uuid4()) + '.txt'
        self.figures = bdp.figures
        self.board = dict()
        self.create_board()

    def save_object(self, object):
        file = open(self.file_obj, 'wb')
        pickle.dump(object, file)
        file.close()

    def get_object(self, file):
        file = open(file, 'rb')
        game = pickle.load(file)
        file.close()
        return game

    def create_board(self):
        for i in range(1, 5):
            for j in range(1, 5):
                self.board['s' + str(i) + str(j)] = '0'
        self.save_settings(self.board)

    def save_settings(self, content):
        file = open(self.file_name, 'a')
        for key, value in content.items():
            file.write("%s:%s " % (key, value))
        file.write("\n")
        file.close()

    def save_winner(self, winner):
        winner2 = session['user'] if session['user'] != winner else session['player2']
        connect = mysql.connect()
        cursor = connect.cursor()
        cursor.execute("INSERT INTO game(player1, player2, winner) VALUES(%s, %s, %s)", (winner, winner2, winner))
        connect.commit()
        cursor.close()
        os.remove(self.file_name)

    def set_winner(self, flag):
        if flag:
            winner = session['player2']
        else:
            winner = session['user']
        return winner

    def read_settings(self, file_name):
        file = open(file_name)
        items=[]
        lines = file.readlines()
        current_line = lines[-1]
        positions = current_line.split(' ')
        del(positions[-1])
        for position in positions:
            items.append( position.split(':'))
        items = sorted(items)
        file.close()
        return self.convert_board(items)

    def convert_board(self, items):
        current_board = dict()
        for item in items:
            current_board[item[0]] = item[1]
        return current_board

    def current_board(self):
        return self.board

    def select_from_figures(self, symbol):
        for figure in self.figures:
            if symbol == figure.get_name(): return figure
        return 0

    def current_figures(self):
        current_board = self.read_settings(self.file_name)
        figures_used = set()
        for item in current_board:
            if current_board[item] != '0':
                figures_used.add(current_board[item])
        figures_names = set()
        for figure in self.figures:
            figures_names.add(figure.get_name())
        symbols = figures_names.difference(figures_used)
        current_figures = []
        for symbol in symbols:
            figure = self.select_from_figures(symbol)
            current_figures.append(figure)
        return current_figures

    def random_figure(self):
        figures = self.current_figures()
        aval_figures = []
        for figure in figures:
            aval_figures.append(figure.get_name())
        symbol = random.choice(aval_figures)
        figure = self.select_from_figures(symbol)
        return figure

    def session_manager(self, session, flag):
        if 'figure' in session:
            symbol = session['figure']
            figure = self.select_from_figures(symbol)
            session.pop('figure', None)
        else:
            figure = None

        if 'file' in session:
            file = session['file']
            session.pop('figure', None)
        else:
            file = None

        if 'message' in session:
            message = session['message']
            session.pop('message', None)
        else:
            message = None
        if 'quatro' in session:
            symbols = session['quatro']
            winner = self.set_winner(flag)
            session.pop('quatro', None)
        else:
            symbols = None
            winner = None
        user = session['user']
        player2 = session['player2']

        return (figure, file, message, symbols, winner, user, player2)

    def get_symbol(self):
        symbol = None
        if 'symbol' in session:
            symbol = session['symbol']
            session.pop('symbol', None)
            session['message'] = 'You are wrong. Computer gained extra move!'
        return symbol

    def set_turn(self):
        player2 = request.form['player']
        if player2 != 'computer':
            nickname = request.form['nickname']
            player2 = nickname
        who_starts = request.form['turn']
        if who_starts == 'player2': game_turn = {'player2': 1, 'player1': 2}
        else: game_turn = {'player1': 1, 'player2': 2}
        return (player2, game_turn)

class Player:

    def __init__(self, figures):
        self.current_figures = copy.deepcopy(figures)
        self.file_player = 'games/' + str(uuid.uuid4()) + '.txt'
        self.user_f = 0
        self.turn = 0
        self.flag = 0

    def change_flag(self):
        if not self.flag:
            self.flag = 1
        else:
            self.flag = 0

    def get_flag(self):
        return self.flag

    def check_exists(self, symbol):
        for figure in self.current_figures:
            if figure.get_name() == symbol:
                return 1

    def delete_figure(self, symbol):
        for figure in self.current_figures:
            if figure.get_name() == symbol:
                self.current_figures.remove(figure)

    def check_row_x(self, row_x, match, board):
        symbols = []
        for i in range(1, 5):
            if board['s' + str(row_x) + str(i)] != '0':
                symbols.append(board['s' + str(row_x) + str(i)])
        if match == len(symbols):
            return symbols

    def check_row_y(self, row_y, match, board):
        symbols = []
        for i in range(1, 5):
            if board['s' + str(i) + str(row_y)] != '0':
                symbols.append(board['s' + str(i) + str(row_y)])
        if match == len(symbols):
            return symbols

    def check_across_xy(self, match, board):
        symbols = []
        for i in range(1, 5):
            if board['s' + str(i) + str(i)] != '0':
                symbols.append(board['s' + str(i) + str(i)])
        if len(symbols) == match:
            return symbols

    def check_across_yx(self, match, board):
        symbols = []
        for i in range(1, 5):
            if board['s' + str(i) + str(5 - i)] != '0':
                symbols.append(board['s' + str(i) + str(5 - i)])
        if len(symbols) == match:
            return symbols

    def fours_logic(self, row_features, symbols):
        common_features = row_features[0] & row_features[1] & row_features[2] & row_features[3]
        if common_features:
            return (4, symbols)
        return 0

    def check_quatro(self, board):
        symbols = []
        for row_num in range(1, 5):
            symbols = self.check_row_x(row_num, 4, board)
            if symbols: break
            symbols = self.check_row_y(row_num, 4, board)
            if symbols: break
        if not symbols:
            symbols = self.check_across_yx(4, board)
            if symbols:
                return symbols
            symbols = self.check_across_xy(4, board)
            if symbols:
                return symbols
        return symbols

    def check_features(self, figure):
        features = set([figure.get_size(), figure.get_color(), figure.get_shape(), figure.get_full()])
        return features

    def check_row_features(self, symbols, figures):
        row_features = []
        for symbol in symbols:
            figure = self.select_from_figures(symbol, figures)
            features = self.check_features(figure)
            row_features.append(features)
        return row_features


    def select_from_figures(self, symbol, figures):
        for figure in figures:
            if figure.get_name() == symbol:
                self.delete_figure(symbol)
                break
        return figure


class Computer(Player):
    def __init__(self, figures):
        Player.__init__(self, figures)
        self.user_f = 0

    def select_slot(self, board, figures):
        slots = []
        for slot, value in board.items():
            if board[slot] == '0':
                slots.append(slot)
        selected_slot = random.choice(slots)
        figure = random.choice(self.current_figures)
        return (selected_slot, figure.get_name())

    def random_figure(self, figures):
        aval_figures = []
        for figure in figures:
            aval_figures.append(figure.get_name())
        symbol = random.choice(aval_figures)
        figure = self.select_from_figures(symbol, figures)
        return figure.get_name()

    def random_in_row(self, row, board):
        seq = []
        for i in range(1, 5):
            if board['s' + str(row) + str(i)] == '0':
                seq.append('s' + str(row) + str(i))
        if seq:
            slot = random.choice(seq)
        return slot

    def cases(self, row_x, row_y, x, y, board, row):
        for i in range(1, 5):
            if row_x:
                if board['s' + str(row) + str(i)] == '0':
                    slot = 's' + str(row) + str(i)
                    return slot
            if row_y:
                if board['s' + str(i) + str(row)] == '0':
                    slot = 's' + str(i) + str(row)
                    return slot
            if x:
                if board['s' + str(i) + str(i)] == '0':
                    slot = 's' + str(i) + str(i)
                    return slot
            if y:
                if board['s' + str(i) + str(5 - i)] == '0':
                    slot = 's' + str(i) + str(5 - i)
                    return slot

    def threes_logic(self, row_features, figure_features, row_x, row_y, x, y, row, board, symbols):
        common_features = row_features[0] & row_features[1] & row_features[2] & figure_features
        if common_features:
            slot = self.cases(row_x, row_y, x, y, board, row)
            return (slot, symbols)
        return 0

    def twos_logic(self, row_features, figure_features, row_x, row_y, x, y, row, board, figures_available):
        common_features = row_features[0] & row_features[1] & figure_features
        #user_figures = copy.deepcopy(self.current_figures)
        if common_features:
            for user_figure in self.current_figures:
                features = self.check_features(user_figure)
                if not common_features & features:
                    slot = self.cases(row_x, row_y, x, y, board, row)
                    return slot, user_figure.get_name()
        return 0

    def ones_logic(self, row_features, features_figure2, row, board, figures_available):
        slot = 0
        common_features = row_features[0] & features_figure2
        if common_features:
            slot = self.random_in_row(row, board)
            for user_figure in self.current_figures:
                features = self.check_features(user_figure)
                if common_features & features:
                    return (slot, user_figure.get_name())
        return slot

    def single_figure(self, board, figures):
        cross = set()
        board_set = set()
        x, y, slot = 0, 0, 0
        for i in range(1, 5):
            for j in range(1, 5):
                board_set.add('s' + str(i) + str(j))
                if board['s' + str(i) + str(j)] != '0':
                    x, y = i, j
                    break
        if x & y:
            for i in range(1, 5):
                cross.add('s' + str(x) + str(i))
                cross.add('s' + str(i) + str(y))
            slot = random.sample(board_set - cross, 1)
            figure = self.random_figure(figures)
            return (slot[0], figure)
        return slot

    def check_rows(self, row_x, row_y, x, y, match, board, features_figure2, figures, figure2):
        result, row = 0, 1
        symbols = []
        while row != 5:
            if row_x:
                symbols = self.check_row_x(row, match, board)
            if row_y:
                symbols = self.check_row_y(row, match, board)
            if x:
                symbols = self.check_across_xy(match, board)
            if y:
                symbols = self.check_across_yx(match, board)
            if symbols:
                row_features = self.check_row_features(symbols, figures)
                if match == 4:
                    result = self.fours_logic(row_features, symbols)
                    if result:
                        break
                if match == 3:
                    result = self.threes_logic(row_features, features_figure2, row_x, row_y, x, y, row, board, symbols)
                    if result:
                        break
                if match == 2:
                    result = self.twos_logic(row_features, features_figure2, row_x, row_y, x, y, row, board, figures)
                    if result:
                        board[result[0]] = figure2.get_name()
                        user_fig = self.user_figure(board, figures)
                        for fi in board: print(fi)
                        print(user_fig)
                        if user_fig:
                            result = list(result)
                            result[1] = user_fig.get_name()
                            result = tuple(result)
                        break
                if match == 1:
                    result = self.single_figure(board, figures)
                    if result:
                        break
            row += 1
        return result


    def search_slot(self, match, board, features_figure2, figures, figure2):
        self.change_flag()
        options = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        for i in range(1, 5):
            for option in options:
                row_x, row_y, x, y = option
                slot = self.check_rows(row_x, row_y, x, y, match, board, features_figure2, figures, figure2)
                if slot: return slot
            match -= 1
            if match == 0:
                slot = self.single_figure(board, figures)
                if not slot:
                    slot = self.select_slot(board, figures)
        return slot

    def place_on_board(self, result, board, figure_to_place):
        if result[0] == 4:
            session['quatro'] = result[1]
        else:
            if type(result[1]) == list:
                result[1].append(figure_to_place.get_name())
                session['quatro'] = result[1]
        slot = result[0]
        session['figure'] = result[1]
        if slot != 4:
            board[slot] = figure_to_place.get_name()

    def search_figure(self, figures, board, cur_fig):
        match = 4
        options = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        figure = 0
        for num in range(1, 5):
            for option in options:
                row_x, row_y, x, y = option
                if row_x:
                    symbols = self.check_row_x(num, match, board)
                if row_y:
                    symbols = self.check_row_y(num, match, board)
                if x:
                    symbols = self.check_across_xy(match, board)
                if y:
                    symbols = self.check_across_yx(match, board)
                if symbols:
                    features = self.check_row_features(symbols, figures)
                    for figure in cur_fig:
                         figure_features = self.check_features(figure)
                         if features and figure_features:
                             return figure
            match -= 1
            if match == 0:
                figure = random.choice(board)
        return figure

    def candidates(self, figures, common):
        i = 0
        while(i < len(figures)):
            features = self.check_features(figures[i])
            if common & features:
                figures.remove(figures[i])
                i -= 1
            i += 1
        return figures

    def user_figures(self, symbols, figures):
        user_figures = copy.deepcopy(self.current_figures)
        feat_fig = self.check_row_features(symbols, figures)
        feat = set.intersection(*feat_fig)
        user_figures = self.candidates(user_figures, feat)
        return user_figures

    def user_figure(self, board, figures):
        figure, user_figures = None, None
        for row_num in range(1,5):
            symbols = self.check_row_x(row_num, 3, board)
            if symbols:
                user_figures = self.user_figures(symbols, figures)
            symbols = self.check_row_y(row_num, 3, board)
            if symbols:
                user_figures = self.user_figures(symbols, figures)
        symbols = self.check_across_yx(3, board)
        if symbols:
            user_figures = self.user_figures(symbols, figures)
        symbols = self.check_across_xy(3, board)
        if symbols:
            user_figures = self.user_figures(symbols, figures)
        if user_figures:
            figure = random.choice(user_figures)
            for fi in user_figures:print(fi.get_name())
        return figure












