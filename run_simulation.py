import random
import pygame
import asyncio
from verlet import (
    circle_constraint,
    collision_constraint_2,
    friction,
    gravity,
    magnetic_force,
    Particle,
    repulsive_force,
    rotational_force,
    simulate,
)

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
FPS = 60
NUM_PARTICLES = 400
MIN_RADIUS = 4
MAX_RADIUS = 15
ITERATIONS = 3


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
        gravity(1),
    ]
    multi_pass_constraints = [
        friction(0.99),
        collision_constraint_2(particles),
        circle_constraint(SCREEN_CENTER, 250),
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
