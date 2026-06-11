#!/usr/bin/env python3
import random
import sys

size = 15
board = []

DIRS = [(1,0), (0,1), (1,1), (1,-1)]

def reset(n):
    global size, board
    size = n
    board = [[0 for _ in range(size)] for _ in range(size)]

def play(x, y, p):
    if 0 <= x < size and 0 <= y < size:
        board[y][x] = p

def inside(x, y):
    return 0 <= x < size and 0 <= y < size

def legal_moves():
    return [(x, y) for y in range(size) for x in range(size) if board[y][x] == 0]

def would_win(x, y, p):
    board[y][x] = p
    try:
        for dx, dy in DIRS:
            count = 1

            nx, ny = x + dx, y + dy
            while inside(nx, ny) and board[ny][nx] == p:
                count += 1
                nx += dx
                ny += dy

            nx, ny = x - dx, y - dy
            while inside(nx, ny) and board[ny][nx] == p:
                count += 1
                nx -= dx
                ny -= dy

            if count >= 5:
                return True
        return False
    finally:
        board[y][x] = 0

def nearby_moves():
    stones = [(x, y) for y in range(size) for x in range(size) if board[y][x] != 0]
    if not stones:
        c = size // 2
        return [(c, c)]

    s = set()
    for x, y in stones:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and board[ny][nx] == 0:
                    s.add((nx, ny))
    return list(s) if s else legal_moves()

def choose_move():
    moves = nearby_moves()

    # self immediate win
    for x, y in moves:
        if would_win(x, y, 1):
            return x, y

    # block opponent immediate win
    for x, y in moves:
        if would_win(x, y, 2):
            return x, y

    # center-biased random
    c = size // 2
    moves.sort(key=lambda m: abs(m[0] - c) + abs(m[1] - c))
    top = moves[: min(12, len(moves))]
    return random.choice(top)

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
            print('name="tactical-lite", version="0.1", author="local"', flush=True)

        elif cmd == "START":
            reset(int(parts[1]))
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

    except Exception as e:
        print(f"ERROR {e}", flush=True)
