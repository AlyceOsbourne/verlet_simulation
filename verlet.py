# simple pygame verlet simulation
from dataclasses import dataclass

import pygame
import random
import functools
import itertools
from typing import Callable, List, Tuple, NamedTuple

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
FPS = 60

Position = Tuple[float, float]
Constraint = Callable[["Particle"], "Particle"]


class Particle:
    def __init__(self, position: Position, old_position: Position, **properties):
        self.position = position
        self.old_position = old_position
        self.properties = properties

    def __repr__(self):
        return f"Particle(position={self.position}, old_position={self.old_position})"

    def update(self):
        x, y = self.position
        ox, oy = self.old_position
        vx, vy = x - ox, y - oy
        self.old_position = x, y
        self.position = x + vx, y + vy
        return self

    def apply_constraints(self, constraints: List[Constraint]):
        return functools.reduce(lambda p, c: c(p), constraints, self)


def varlet(
    particles: List[Particle],
    single_pass_constraints: List[Constraint],
    multi_pass_constraints: List[Constraint],
    iterations: int = 5,
) -> List[Particle]:
    for particle in particles:
        particle.update()
        particle.apply_constraints(single_pass_constraints)
        for _ in range(iterations):
            particle.apply_constraints(multi_pass_constraints)
    return particles


def gravity(acceleration: float = 10) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.old_position
        particle.position = x, y + acceleration
        return particle

    return constraint


# constrain inside a circle
def circle_constraint(center: Position, radius: float) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        cx, cy = center
        dx, dy = x - cx, y - cy
        distance = (dx**2 + dy**2) ** 0.5
        radii = particle.properties.get("radius", 5)
        if distance > radius - radii:
            particle.position = cx + dx / distance * (
                radius - radii
            ), cy + dy / distance * (radius - radii)
        return particle

    return constraint


# constrain collision between particles
def collision_constraint(particles: List[Particle]) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        radii = particle.properties.get("radius", 5)
        for other in particles:
            if other is particle:
                continue
            ox, oy = other.position
            x, y = particle.position
            dx, dy = x - ox, y - oy
            radii_sum = radii + other.properties.get("radius", 5)
            distance = (dx**2 + dy**2) ** 0.5
            if distance == 0:
                distance = 0.0001
            if distance < radii_sum:
                half_distance = (radii_sum - distance) / 2
                particle.position = (
                    x + dx / distance * half_distance,
                    y + dy / distance * half_distance,
                )
                other.position = (
                    ox - dx / distance * half_distance,
                    oy - dy / distance * half_distance,
                )
        return particle

    return constraint


def damping(damping: float = 0.2) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        ox, oy = particle.old_position
        vx, vy = x - ox, y - oy
        particle.old_position = x - vx * damping, y - vy * damping
        return particle

    return constraint


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    particles = [
        Particle(
            position=(
                SCREEN_CENTER[0] + random.randint(-200, 200),
                SCREEN_CENTER[1] + random.randint(-200, 200),
            ),
            old_position=(
                SCREEN_CENTER[0] + random.randint(-100, 100),
                SCREEN_CENTER[1] + random.randint(-100, 100),
            ),
            color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            radius=random.randint(5, 10),
        )
        for _ in range(50)
    ]
    single_pass_constraints = [
        gravity(
            acceleration=3
        ),
    ]
    multi_pass_constraints = [
        collision_constraint(particles),
        circle_constraint(SCREEN_CENTER, 200),
        damping(
            damping=0.0001
        ),
    ]

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        varlet(particles, single_pass_constraints, multi_pass_constraints)
        for particle in particles:
            pygame.draw.circle(
                screen,
                particle.properties["color"],
                particle.position,
                particle.properties["radius"],
            )
        pygame.display.flip()
        clock.tick(FPS)
