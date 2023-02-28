# simple pygame verlet simulation
from dataclasses import dataclass

import pygame
import random
import functools
import itertools
from typing import Callable, List, Tuple, NamedTuple

Position = Tuple[float, float]
Constraint = Callable[[Position], Position]


class Particle:
    def __init__(self, position: Position, old_position: Position):
        self.position = position
        self.old_position = old_position

    def __repr__(self):
        return f"Particle(position={self.position}, old_position={self.old_position})"


def apply_constraints_to_particle(
    position: Position, constraints: List[Constraint]
) -> Position:
    return functools.reduce(lambda p, c: c(p), constraints, position)


def apply_constraints_to_particles(
    particles: List[Particle], constraints: List[Constraint]
) -> List[Particle]:
    return [
        Particle(apply_constraints_to_particle(p.position, constraints), p.old_position)
        for p in particles
    ]


def update_particle(particle: Particle):
    x, y = particle.position
    ox, oy = particle.old_position
    vx, vy = x - ox, y - oy
    particle.old_position = particle.position
    particle.position = x + vx, y + vy
    return particle


def update_particles(particles: List[Particle]):
    return [update_particle(p) for p in particles]


def verlet(
    particles: List[Particle],
    single_pass_constraints: List[Constraint],
    multi_pass_constraints: List[Constraint],
    iterations: int = 1,
) -> List[Particle]:
    for particle in particles:
        particle.position = apply_constraints_to_particle(
            particle.position, single_pass_constraints
        )
        for _ in range(iterations):
            particle.position = apply_constraints_to_particle(
                particle.position, multi_pass_constraints
            )
        update_particle(particle)
    return particles


def constrain_to_bounds(bounds: Tuple[Position, Position]):
    def constraint(position: Position):
        x, y = position
        min_x, min_y = bounds[0]
        max_x, max_y = bounds[1]
        return max(min_x, min(x, max_x)), max(min_y, min(y, max_y))

    return constraint


def constrain_to_circle(center: Position, radius: float):
    def constraint(position: Position):
        x, y = position
        cx, cy = center
        dx, dy = x - cx, y - cy
        d = (dx**2 + dy**2) ** 0.5
        if d > radius:
            return cx + dx / d * radius, cy + dy / d * radius
        return x, y

    return constraint


# gravity
def apply_gravity(gravity: float):
    def constraint(position: Position):
        x, y = position
        return x, y + gravity

    return constraint


# collision
def apply_collision(particles: List[Particle], radius: float):
    def constraint(position: Position):
        x, y = position
        for p in particles:
            px, py = p.position
            dx, dy = x - px, y - py
            d = (dx**2 + dy**2) ** 0.5
            if d < radius:
                try:
                    return px + dx / d * radius, py + dy / d * radius
                except ZeroDivisionError:
                    return px, py
        return x, y

    return constraint


def apply_damping(damping: float):
    def constraint(position: Position):
        # get the velocity from the old and new position
        x, y = position
        ox, oy = position
        vx, vy = x - ox, y - oy
        return x + vx * damping, y + vy * damping

    return constraint


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    running = True
    particles = [
        Particle((random.randint(0, 800), random.randint(0, 600)), (0, 0))
        for _ in range(100)
    ]
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        particles = verlet(
            particles,
            [constrain_to_circle((400, 300), 200), apply_gravity(0.2)],
            [apply_collision(particles, 10), apply_damping(0.80)],
            3,
        )
        for particle in particles:
            pygame.draw.circle(screen, (255, 255, 255), particle.position, 5)
        pygame.display.flip()
        clock.tick(60)
