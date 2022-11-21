import time
import multiplayer
from board import Board

FRAMERATE = 60

def start():
    print("Welcome to Connect4 Online!")
    global connection
    connection = multiplayer.start(data_received)

    global board
    board = Board()
    is_my_turn = connection.is_server
    if is_my_turn:
        play()
    else:
        print(f"{connection.their_name} is playing...")


def try_input(answer):
    try:
        column = int(answer) - 1 
    except ValueError:
        return False, f"{answer} is not a valid number"
    if column < 0 or column > 6:
        return False, f"{answer} is not between 1 and 7"
    valid_column = board.try_input(column)
    if not valid_column:
        return False, f"Column {column + 1} is full"
    return True, ""

def play():
    print("Your turn:")
    board.print()
    while True:
        answer = input("Enter column number (1 to 7), 'q' to quit: ")
        if answer == "q":
            connection.close()
            exit()
        valid_input, error = try_input(answer)
        if not valid_input:
            print(error)
            continue
        break

    if board.check_win():
        board.print()
        print(f"You won!")
    connection.send(answer)

    print()
    print("Their turn:")
    board.print()
    print(f"{connection.their_name} is playing...")
    print()

def they_play(position):
    valid_input, error = try_input(position)
    if not valid_input:
        print(f"{connection.their_name} sent an invalid input:")
        print(f"Received {position} but {error}")
        exit()

    if board.check_win():
        board.print()
        print(f"{connection.their_name} won!")
    
    play()

def update():
    connection.poll()

def data_received(data):
    they_play(data)

if __name__ == "__main__":
    start()
    while True:
        update()
        time.sleep(1/FRAMERATE)