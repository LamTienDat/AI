import argparse
import math
from environment import CarMazeEnv

from queue import PriorityQueue


class State:
    def __init__(self, x, y, d=0, v=0, cur_cost=0, disToG=0, par=None, mode=3):
        self.x = x
        self.y = y
        self.d = d
        self.v = v
        self.cur_cost = cur_cost
        self.disToG = disToG
        self.par = par
        self.mode = mode    #1:ucs  2:bfs(greedy)   3:A*

    def display(self):
        print(self.x, self.y, self.d, self.v, self.cur_cost)

    def __lt__(self, other):
        if other is None:
            return False
        if self.mode == 1:
            return self.cur_cost < other.cur_cost
        elif self.mode == 2:
            return self.disToG < other.disToG
        else:
            return self.disToG + self.cur_cost < other.disToG + other.cur_cost

    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y and self.d == other.d and self.v == other.v

    def xydv(self):
        return (self.x, self.y, self.d, self.v)


def equal(O, G):
    x, y = G
    if O.x == x and O.y == y and O.v == 0:
        return True
    return False


def checkInPriority(tmp, c):
    if tmp is None:
        return False
    return tmp in c.queue


def getPath(O):
    O.display()
    if O.par is not None:
        getPath(O.par)
    else:
        return


def creatPath(S):
    path = dict()
    while S.par is not None:
        path[S.xydv()] = S.par.xydv()
        S = S.par
    path[S.xydv()] = None
    return path


class Solver:
    def __init__(self, env: CarMazeEnv, mode=1) -> None:
        self.Open = PriorityQueue()
        self.Closed = PriorityQueue()
        self.env = env
        self.mode = mode

    def step_fn(self, act, s):
        par_cost = s.cur_cost
        x, y, d, v, cost = act(s.x, s.y, s.d, s.v)

        if x < 0 or y < 0:  # Invalid action
            return None

        tmp = State(x, y, d, v, cost + par_cost, self.manhattan(x, y), s, self.mode)

        ok1 = checkInPriority(tmp, self.Open)
        ok2 = checkInPriority(tmp, self.Closed)

        if not ok1 and not ok2:
            self.Open.put(tmp)

    def manhattan(self, x, y):
        x_, y_ = self.env.goal
        return abs(x-x_) + abs(y-y_)

    def solve(self):
        x0, y0 = self.env.start
        s = State(x0, y0)
        self.Open.put(s)

        while True:
            if (self.Open.empty()):
                print('Tim kiem that bai')
                return -1, None
            s = self.Open.get()
            self.Closed.put(s)
            # print('duyet: ')
            # s.display()
            if equal(s, self.env.goal):
                print('tim kiem thanh cong')
                # getPath(s)
                self.path = creatPath(s)
                return s.cur_cost, (s.xydv())
            v = s.v
            if v == 0:
                self.step_fn(self.env.turn_left, s)
                self.step_fn(self.env.turn_right, s)
                self.step_fn(self.env.speed_up, s)
            else:
                self.step_fn(self.env.no_action, s)
                self.step_fn(self.env.slow_down, s)
                if v < self.env.vmax:
                    self.step_fn(self.env.speed_up, s)
