---
title: AetherGrid
emoji: ⚡
colorFrom: blue
colorTo: pink
sdk: static
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# AetherGrid — Quantum Power Matrix Controller

A CLI application simulating a futuristic energy hub. It processes
power node telemetry, verifies security credentials, manages system
funds, and computes harmonic wave decay — all from the terminal.

## Overview

AetherGrid is a command-line tool built entirely with the Python
standard library. It models hardware power nodes as a polymorphic
class hierarchy, processes raw telemetry through a functional
pipeline (`map`, `filter`, `reduce`), retains internal state through
closures, and dispatches commands by parsing `sys.argv` manually.

Every failure path is handled with domain-specific exceptions, so
the terminal never crashes — bad input, missing files, and wrong
passwords all produce a single clean error line.

## Features

- Polymorphic node hierarchy (`BaseNode`, `QuantumNode`)
- Operator overloading for combining nodes via `+`
- Domain-specific exception hierarchy
- Functional telemetry pipeline with no `for`/`while` loops for
  filtering, cleaning, or summing
- Closure-based fund manager with private state
- Diagnostic logging decorator applied to pipeline entry points
- Recursive harmonic wave decay with three modes
- Salted SHA-256 credential hashing with constant-time comparison
- Safe file I/O using `with` context managers
- Manual `sys.argv` CLI dispatch with usage text
- Full test suite with pytest and coverage reporting

## Project Structure
