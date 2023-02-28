# simple pygame verlet simulation
from dataclasses import dataclass

import pygame
import random
import functools
import itertools
from typing import Callable, List, Tuple, NamedTuple

SCREEN_SIZE = (800, 600)
FPS = 20
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
NUM_PARTICLES = 10
DEFAULT_PARTICLE_PROPERTIES = {
        "mass" : 1,
        "radii": 10,
}
DAMPING = 0.97
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

    def apply_constraints(self, constraints: List[Constraint]):
        return functools.reduce(lambda p, c: c(p), constraints, self)


def varlet(
        particles: List[Particle],
        single_pass_constraints: List[Constraint],
        multi_pass_constraints: List[Constraint],
        iterations: int = 1,
) -> List[Particle]:
    for particle in particles:
        particle.update()
        for _ in range(iterations):
            particle.apply_constraints(multi_pass_constraints)
        particle.apply_constraints(single_pass_constraints)
    return particles


def gravity(particle: Particle):
    x, y = particle.old_position
    mass = int(particle.properties.setdefault("mass", 1))
    if not 0 < mass < 100:
        mass = min(max(mass, 0), 100)
    particle.old_position = x, y - (GRAVITY * mass)
    return particle


def constrain_to_circle(center: Position, radius: float):
    def constraint(particle: Particle):
        x, y = particle.position
        cx, cy = center
        dx, dy = x - cx, y - cy
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > radius:
            particle.position = cx + dx / distance * radius, cy + dy / distance * radius
        return particle

    return constraint


def friction(particle: Particle):
    x, y = particle.position
    ox, oy = particle.old_position
    vx, vy = x - ox, y - oy
    friction = particle.properties.setdefault("friction", 0.999)
    particle.old_position = x - vx * friction, y - vy * friction
    return particle


def constrain_particle_collision(particles):
    def constraint(particle: Particle):
        x, y = particle.position
        ox, oy = particle.old_position
        radii = particle.properties.setdefault("radii", 5)
        for other in particles:
            if other is particle:
                continue
            ox, oy = other.position
            oradii = other.properties.setdefault("radii", 5)
            dx, dy = x - ox, y - oy
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < radii + oradii:
                overlap = radii + oradii - distance
                particle.position = x + dx / distance * overlap, y + dy / distance * overlap
        return particle

    return constraint


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    particles = [
            Particle(
                    position = (
                            SCREEN_CENTER[0] + random.randint(-10, 10),
                            SCREEN_CENTER[1] + random.randint(-10, 10),
                    ),
                    old_position = (
                            SCREEN_CENTER[0] + random.randint(-10, 10),
                            SCREEN_CENTER[1] + random.randint(-10, 10),
                    ),
                    **DEFAULT_PARTICLE_PROPERTIES,
            )
            for _ in range(NUM_PARTICLES)
    ]
    single_pass_constraints = [
            gravity,
            friction,
    ]
    multi_pass_constraints = [
            constrain_particle_collision(particles),
            constrain_to_circle(SCREEN_CENTER, SCREEN_SIZE[1] / 3),
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))

        particles = varlet(particles, single_pass_constraints, multi_pass_constraints, iterations = 5)

        for particle in particles:
            radii = particle.properties.setdefault("radii", 5)
            colour = particle.properties.setdefault(
                    "colour",
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            )
            pygame.draw.circle(screen, colour, particle.position, radii)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
