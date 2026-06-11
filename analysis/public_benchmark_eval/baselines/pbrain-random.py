#!/usr/bin/env python3
import random
import sys

size = 15
board = []

def reset(n):
    global size, board
    size = n
    board = [[0 for _ in range(size)] for _ in range(size)]

def play(x, y, p):
    if 0 <= x < size and 0 <= y < size:
        board[y][x] = p

def choose_move():
    legal = [(x, y) for y in range(size) for x in range(size) if board[y][x] == 0]
    if not legal:
        return None
    # deterministic-ish center preference on first move, random after that
    c = size // 2
    if board[c][c] == 0:
        return (c, c)
    return random.choice(legal)

def output_move():
    mv = choose_move()
    if mv is None:
        print("0,0", flush=True)
        return
    x, y = mv
    play(x, y, 1)
    print(f"{x},{y}", flush=True)

reset(size)

for raw in sys.stdin:
    line = raw.strip()
    if not line:
        continue
    parts = line.split()
    cmd = parts[0].upper()

    try:
        if cmd == "ABOUT":
            print('name="random-baseline", version="0.1", author="local"', flush=True)

        elif cmd == "START":
            n = int(parts[1])
            reset(n)
            print("OK", flush=True)

        elif cmd == "RESTART":
            reset(size)
            print("OK", flush=True)

        elif cmd == "BEGIN":
            output_move()

        elif cmd == "TURN":
            x, y = map(int, parts[1].split(","))
            play(x, y, 2)
            output_move()

        elif cmd == "BOARD":
            reset(size)
            for raw2 in sys.stdin:
                row = raw2.strip()
                if row.upper() == "DONE":
                    break
                x, y, p = map(int, row.split(","))
                play(x, y, p)
            output_move()

        elif cmd == "INFO":
            pass

        elif cmd == "END":
            break

        else:
            pass
    except Exception as e:
        print(f"ERROR {e}", flush=True)
