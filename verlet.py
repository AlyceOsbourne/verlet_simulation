# simple pygame verlet simulation
from dataclasses import dataclass

import pygame
import random
import functools
import itertools
from typing import Callable, List, Tuple, NamedTuple

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
NUM_PARTICLES = 100
DEFAULT_PARTICLE_PROPERTIES = {
    "mass": 1,
    "radii": 20,
}
DAMPING = 0.3
GRAVITY = 10

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
        self.old_position = self.position
        self.position = x + vx, y + vy
        return self

    def draw(self, screen):
        radii = self.properties.setdefault("radii", 5)
        colour = self.properties.setdefault(
            "colour",
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
        pygame.draw.circle(screen, colour, self.position, radii)

    def apply_constraints(self, constraints: List[Constraint]):
        return functools.reduce(lambda p, c: c(p), constraints, self)


def varlet(
    particles: List[Particle],
    single_pass_constraints: List[Constraint],
    multi_pass_constraints: List[Constraint],
    iterations: int = 1,
) -> List[Particle]:
    for particle in particles:
        particle = particle.apply_constraints(single_pass_constraints)
        for _ in range(iterations):
            particle = particle.apply_constraints(multi_pass_constraints)
        particle.update()

    return particles


def apply_gravity(gravity: float):
    def constraint(particle: Particle):
        x, y = particle.old_position
        mass = particle.properties.setdefault("mass", 1)
        particle.old_position = x, y + (gravity * mass)
        return particle

    return constraint


def constrain_to_circle(center: Position, radius: float):
    def constraint(particle: Particle):
        x, y = particle.position
        cx, cy = center
        dx, dy = x - cx, y - cy
        distance = (dx**2 + dy**2) ** 0.5
        if distance > radius:
            particle.position = cx + dx / distance * radius, cy + dy / distance * radius
        return particle

    return constraint


def constrain_damping(damping: float):
    def constraint(particle: Particle):
        x, y = particle.position
        ox, oy = particle.old_position
        if damping < 1:
            particle.old_position = x + (x - ox) * damping, y + (y - oy) * damping
        return particle

    return constraint


def constrain_particle_collision(particles):
    def constraint(particle: Particle):
        x, y = particle.old_position
        for p in particles:
            px, py = p.old_position
            dx, dy = x - px, y - py
            radius = particle.properties.setdefault("radii", 5)
            pradius = p.properties.setdefault("radii", 5)
            distance = (dx**2 + dy**2) ** 0.5
            if distance < radius + pradius:
                if distance == 0 or distance > radius + pradius:
                    distance = radius + pradius
                particle.old_position = px + dx / distance * (
                    radius + pradius
                ), py + dy / distance * (radius + pradius)
                p.old_position = x - dx / distance * (
                    radius + pradius
                ), y - dy / distance * (radius + pradius)
        return particle

    return constraint


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    particles = [
            Particle(
                    position = (
                            random.randint(0, SCREEN_SIZE[0]),
                            random.randint(0, SCREEN_SIZE[1]),
                    ),
                    old_position = (
                            random.randint(0, SCREEN_SIZE[0]),
                            random.randint(0, SCREEN_SIZE[1]),
                    ),
                    **DEFAULT_PARTICLE_PROPERTIES,
            )
            for _ in range(NUM_PARTICLES)
    ]
    single_pass_constraints = [
            apply_gravity(GRAVITY),
    ]
    multi_pass_constraints = [
            constrain_to_circle(SCREEN_CENTER, SCREEN_SIZE[0] / 3),
            constrain_particle_collision(particles),
            constrain_damping(DAMPING),
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))

        particles = varlet(particles, single_pass_constraints, multi_pass_constraints)

        for particle in particles:
            particle.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
