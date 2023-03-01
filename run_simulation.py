import random

import pygame

from verlet import (
    circle_constraint,
    collision_constraint,
    friction,
    gravity,
    Particle,
    varlet,
    repulsive_mouse_constraint,
    magnetic_mouse_constraint,
    rotational_force,
)

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
FPS = 30


def main():
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
            radius=random.randint(8, 20),
        )
        for _ in range(100)
    ]
    single_pass_constraints = [
        gravity(1),
        collision_constraint(particles),
    ]
    multi_pass_constraints = [
        circle_constraint(SCREEN_CENTER, 300),
        friction(),
    ]
    iterations = 5
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        for particle in varlet(
            particles, single_pass_constraints, multi_pass_constraints, iterations
        ):
            color = particle.properties.setdefault(
                "color",
                (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
            )
            radius = particle.properties.setdefault("radius", random.randint(5, 10))
            pygame.draw.circle(screen, color, particle.position, radius)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
