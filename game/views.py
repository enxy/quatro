# -*- coding: utf-8 -*-
from game import app, mysql, bdp
from flask import render_template, session, request, redirect, url_for, flash, make_response
#from flask.ext.bcrypt import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt
import pickle, copy, os
from pymysql import IntegrityError

match = 4
bcrypt = Bcrypt(app)

def validation(cursor, connect, name, login, password, re_password, pw_hash ):
        try:
            if len(name) < 3 or len(login) < 3: raise NameError
            if password != re_password: raise ValueError
            cursor.execute("INSERT INTO users(login, password, name) VALUES(%s, %s, %s)",
                           (login, pw_hash, name))
        except IntegrityError:
            flash('Login already occupied. Try again.')
            connect.rollback()
        except ValueError:
            flash('Wrong password')
            connect.rollback()
        except NameError:
            flash('Login or name should have at least 3 chars')
            connect.rollback()
        else:
            connect.commit()
            cursor.close()
            flash('Congratulations! You have been correctly registered.')
            return redirect(url_for('quatro'))


@app.route('/quatro')
def quatro():

    user = session['user'] if 'user' in session else None

    return render_template('index.html', user=user)

@app.route('/quatro/players')
def players():
    if 'user' not in session:
        flash('Quatro game is available only for registered users! Login or register first.')
        return redirect(url_for('login'))

    return render_template('players.html', user = session['user'])

@app.route('/quatro/previous')
def previous():
    lista = []
    if 'repeat' in session:
        content = next(iter(session['repeat']))
        z = content.split(' ')
        for item in z: lista.append(item.split(':'))

    return render_template('games.html', content = lista)

@app.route('/games')
def activeGames():
    user_id = request.cookies.get('Player')

    listOfGames = []
    for file in os.listdir("games/"):
        listOfGames.append(file)

    return render_template('online.html', games=listOfGames, user_id = user_id)

@app.route('/quatro/start', methods=['POST'])
def start():
    from game import quatro

    game = quatro.Game()
    pickle.dump(game, open(game.file_obj, 'wb'))

    session['player2'], session['game_turn'] = game.set_turn()

    if session['player2'] == 'computer':
        player = quatro.Computer(game.figures)
        session['file'] = "slot.html"
    else:
        player = quatro.Player(game.figures)
        session['file'] = "figure.html"

    if next(iter(session['game_turn'])) == 'player2':
        player.turn = 1
        player.change_flag()
    else:
        player.turn = 2
        session['file'] = "figure.html"

    pickle.dump(player, open(player.file_player, 'wb'))
    session['player2'], session['game_turn'] = game.set_turn()
    response = make_response(redirect(url_for('play')))
    response.set_cookie('Game', game.file_obj)
    response.set_cookie('Player', player.file_player)
    return response


@app.route('/quatro/play')
def play():
    from game import quatro
    game = pickle.load(open(request.cookies.get('Game'), 'rb'))
    player = pickle.load(open(request.cookies.get('Player'), 'rb'))

    figure, file, message, symbols, winner, user, player2 = game.session_manager(session, player.flag)
    if isinstance(player, quatro.Computer):
        figure = game.select_from_figures(player.user_f)
    if figure:
        player.user_f = copy.deepcopy(figure)
    if not figure:
        figure = player.user_f

    game.save_settings(game.current_board())
    current_board2 = game.read_settings(game.file_name)
    current_board = sorted(list(current_board2))
    name = session['user'] if player.flag else session['player2']
    if len(player.current_figures) == 0:
        session[message] = 'No one has win'
    if winner:
        game.save_winner(winner)
        del game

    return render_template('board2.html', board2 = current_board2, board =  current_board, figures = player.current_figures, symbols = symbols,
                           figure=figure, file = file, message = message, winner = winner, name = name, user=session['user'])


@app.route('/quatro/set_figure', methods=['GET','POST'])
def set_figure():
    game_file = request.cookies.get('Game')
    player_file = request.cookies.get('Player')
    game = pickle.load(open(game_file, 'rb'))
    player = pickle.load(open(player_file, 'rb'))

    board = game.current_board()
    symbol = game.get_symbol()
    if not symbol:
        symbol = request.form['figure']
        if not player.check_exists(symbol):
            message = 'Please select figure from figures available!'
            session['message'] = message
            session['file'] = "figure.html"
            return redirect(url_for('play'))

    if session['player2'] == 'computer':
        figure2 = player.select_from_figures(symbol, game.figures)
        features_figure2 = player.check_features(figure2)
        result = player.search_slot(match, board, features_figure2, game.figures, figure2)
        player.place_on_board(result, board, figure2)
        player.user_f = result[1]
    else:
        session['figure'] = symbol

    session['file'] = "slot.html"
    pickle.dump(game, open(game_file, 'wb'))
    pickle.dump(player, open(player_file, 'wb'))

    return redirect(url_for('play'))

@app.route('/quatro/set_slot', methods=['POST'])
def set_slot():
    game_file = request.cookies.get('Game')
    player_file = request.cookies.get('Player')
    game = pickle.load(open(game_file, 'rb'))
    player = pickle.load(open(player_file, 'rb'))

    player.change_flag()
    board = game.current_board()
    slot = request.form['slot']
    symbol = request.form['symbol']
    player.delete_figure(symbol)
    board[slot] = symbol
    session['file'] = "figure.html"
    pickle.dump(game, open(game_file, 'wb'))
    pickle.dump(player, open(player_file, 'wb'))

    return redirect(url_for('play'))

@app.route('/quatro/check', methods=['GET','POST'])
def check():
    game_file = request.cookies.get('Game')
    player_file = request.cookies.get('Player')
    game = pickle.load(open(game_file, 'rb'))
    player = pickle.load(open(player_file, 'rb'))

    board = game.current_board()
    symbols = player.check_quatro(board)
    if symbols:
        row_features = player.check_row_features(symbols, game.figures)
        result = player.fours_logic(row_features, symbols)
        if result:
            session['quatro'] = result[1]
            file = open(game.file_name, 'r')
            user_game = file.readlines()
            session['repeat'] = user_game
            print(session['reapeat'])
        else:
            symbols = None
    if not symbols:
        if session['player2'] == 'computer':
            figure = player.search_figure(game.figures, board, game.current_figures())
            session['symbol'] = figure.get_name()
            return redirect(url_for('set_figure'))
        else:
            session['file'] = 'figure.html'
            name = session['user'] if player.flag else session['player2']
            session['message'] = 'Error no Quatro found ' + name +' can select figure and place it on the board.'
    pickle.dump(game, open(game_file, 'wb'))
    pickle.dump(player, open(player_file, 'wb'))
    return redirect(url_for('play'))

@app.route('/quatro/login',  methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        connect = mysql.connect()
        cursor = connect.cursor()
        login = request.form['login']
        password = request.form['password']

        if request.form['submit'] == 'Register':
            name = request.form['name']
            re_password = request.form['re_password']
            pw_hash = bcrypt.generate_password_hash(password)
            validation(cursor,connect, name, login, password, re_password, pw_hash)
        elif request.form['submit'] == 'Login':
            cursor.execute("SELECT password FROM users WHERE login='" + login + "'")
            user_data = cursor.fetchall()
            if not user_data:
                error = 'Invalid login. Try again.'
            elif not bcrypt.check_password_hash(user_data[0][0], password):
                error = 'Invalid login/password. Try again.'
            else:
                session['user'] = login
                return redirect(url_for('players'))

    return render_template('login.html', error = error)


@app.route('/quatro/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('quatro'))


@app.route('/quatro/rules')
def rules():
    return render_template('rules.html')


if __name__ == "__main__":
    app.run()