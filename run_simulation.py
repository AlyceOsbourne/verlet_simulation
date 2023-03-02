import random

import pygame

from verlet import (
    circle_constraint,
    collision_constraint,
    friction,
    gravity,
    magnetic_mouse_constraint,
    Particle,
    repulsive_mouse_constraint,
    rotational_force,
    simulate,
)

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
FPS = 60
NUM_PARTICLES = 300
MIN_RADIUS = 5
MAX_RADIUS = 15
ITERATIONS = 10


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
            radius=random.randint(MIN_RADIUS, MAX_RADIUS),
        )
    ]
    single_pass_constraints = [
        gravity(0.3),
        rotational_force(0.1, 200, pygame.mouse.get_pos),
        magnetic_mouse_constraint(1, 200, pygame.mouse.get_pos),
        repulsive_mouse_constraint(3, 140, pygame.mouse.get_pos),
        magnetic_mouse_constraint(5, 120, pygame.mouse.get_pos),
        repulsive_mouse_constraint(6, 100, pygame.mouse.get_pos),
        magnetic_mouse_constraint(7, 80, pygame.mouse.get_pos),
        repulsive_mouse_constraint(9, 60, pygame.mouse.get_pos),
        magnetic_mouse_constraint(10, 50, pygame.mouse.get_pos),
        collision_constraint(particles),
    ]
    multi_pass_constraints = [
        friction(0.99),
        circle_constraint(SCREEN_CENTER, 300),
    ]
    i = 0
    font = pygame.font.SysFont("Arial", 20)
    while True:
        if len(particles) < NUM_PARTICLES:
            if i % 5 == 0:
                particles.append(
                    Particle(
                        position=(
                            SCREEN_CENTER[0],
                            SCREEN_CENTER[1] - 30,
                        ),
                        old_position=(
                            SCREEN_CENTER[0] + random.randint(-5, 5),
                            SCREEN_CENTER[1] + random.randint(-5, 5),
                        ),
                        radius=random.randint(MIN_RADIUS, MAX_RADIUS),
                    )
                )
            i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        for particle in simulate(
            particles, single_pass_constraints, multi_pass_constraints, ITERATIONS
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
        # print num particles and fps
        text = font.render(
            f"Particles: {len(particles)} FPS: {int(clock.get_fps())}",
            True,
            (255, 255, 255),
        )
        screen.blit(text, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
