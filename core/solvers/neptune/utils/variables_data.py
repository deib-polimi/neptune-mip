from .variables import *
import numpy as np

def init_mu(data, solver, mu):
    for t in range(len(data.tables)):
        for i in range(len(data.nodes)):
            mu[i, t] = solver.BoolVar(f"mu[{i}][{t}]")


def init_sigma(data, solver, sigma):
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
            sigma[i, t] = solver.BoolVar(f"sigma[{i}][{t}]")


def init_z(data, solver, z):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                for j in range(len(data.nodes)):
                    for k in range(len(data.nodes)):
                        z[f, t, i, j, k] = solver.NumVar(0, 1, f"z[{f}][{t}][{i}][{j}][{k}]")


def init_q(data, solver, q):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                q[i, j, t] = solver.BoolVar(f"q[{i}][{j}][{t}]")


def init_w(data, solver, w):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                for j in range(len(data.nodes)):
                    for k in range(len(data.nodes)):
                        w[f, t, i, j, k] = solver.NumVar(0, 1, f"w[{f}][{t}][{i}][{j}][{k}]")


def init_psi(data, solver, psi):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            for t in range(len(data.tables)):
                psi[i, j, t] = solver.BoolVar(f"psi[{i}][{j}][{t}]")


def init_gmax(data, solver, gmax):
    for t in range(len(data.tables)):
        gmax[t] = solver.NumVar(0, solver.infinity(), f"gmax[{t}]")


def init_y(data, solver, y):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                for j in range(len(data.nodes)):
                    y[f, t, i, j] = solver.BoolVar(f"y[{f}][{t}][{i}][{j}]")


def init_rho(data, solver, rho):
    for i in range(len(data.nodes)):
        for t in range(len(data.tables)):
            rho[i, t] = solver.BoolVar(f"rho[{i}][{t}]")


def init_r(data, solver, r):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            r[f, t] = solver.BoolVar(f"r[{f}][{t}]")


def init_d(data, solver, d):
    for i in range(len(data.nodes)):
        for j in range(len(data.nodes)):
            d[i, j] = solver.BoolVar(f"d[{i}][{j}]")

# Linearization of c * r
def init_cr(data, solver, cr):
    for f in range(len(data.functions)):
        for t in range(len(data.tables)):
            for i in range(len(data.nodes)):
                cr[f, t, i] = solver.BoolVar(f"cr[{f}][{t}][{i}]")