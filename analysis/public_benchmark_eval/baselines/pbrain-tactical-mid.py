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

def inside(x, y):
    return 0 <= x < size and 0 <= y < size

def play(x, y, p):
    if inside(x, y):
        board[y][x] = p

def legal_moves():
    return [(x, y) for y in range(size) for x in range(size) if board[y][x] == 0]

def nearby_moves(radius=2):
    stones = [(x, y) for y in range(size) for x in range(size) if board[y][x] != 0]
    if not stones:
        c = size // 2
        return [(c, c)]

    s = set()
    for x, y in stones:
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and board[ny][nx] == 0:
                    s.add((nx, ny))
    return list(s) if s else legal_moves()

def line_features_after(x, y, p, dx, dy):
    board[y][x] = p
    try:
        count = 1

        nx, ny = x + dx, y + dy
        while inside(nx, ny) and board[ny][nx] == p:
            count += 1
            nx += dx
            ny += dy
        open1 = inside(nx, ny) and board[ny][nx] == 0

        nx, ny = x - dx, y - dy
        while inside(nx, ny) and board[ny][nx] == p:
            count += 1
            nx -= dx
            ny -= dy
        open2 = inside(nx, ny) and board[ny][nx] == 0

        return count, int(open1) + int(open2)
    finally:
        board[y][x] = 0

def pattern_score_for_player(x, y, p):
    best = 0
    total = 0

    for dx, dy in DIRS:
        count, opens = line_features_after(x, y, p, dx, dy)

        if count >= 5:
            score = 100000000
        elif count == 4 and opens >= 1:
            score = 5000000
        elif count == 3 and opens == 2:
            score = 120000
        elif count == 3 and opens == 1:
            score = 10000
        elif count == 2 and opens == 2:
            score = 1000
        else:
            score = count * 10 + opens * 3

        best = max(best, score)
        total += score

    return best * 3 + total

def move_score(x, y):
    # Weaker than tactical_plus:
    # - still sees immediate wins and simple open-threes
    # - less defensive weighting
    # - no random, deterministic center-biased tie break
    self_score = pattern_score_for_player(x, y, 1)
    opp_score = pattern_score_for_player(x, y, 2)

    c = size // 2
    center_bonus = 30 - (abs(x - c) + abs(y - c))

    return self_score + int(0.75 * opp_score) + center_bonus

def choose_move():
    moves = nearby_moves(radius=2)

    c = size // 2
    best = None
    best_key = None

    for x, y in moves:
        key = (
            move_score(x, y),
            -abs(x - c) - abs(y - c),
            -y,
            -x,
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    return best

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
            print('name="tactical-mid", version="0.1", author="local"', flush=True)

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
