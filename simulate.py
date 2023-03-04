import random

from particle import (
    Particle,
    gravity,
    friction,
    circle_constraint,
    collision_constraint_2,
    screen_constraint,
    repulsive_force,
    magnetic_force,
    rotational_force
)
from spatial_hash_grid import SpatialHashGrid
import pygame

SCREEN_SIZE = (800, 600)
BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_RADIUS = 6
PARTICLE_FRICTION = 0.95
PARTICLE_GRAVITY = .5
PARTICLE_COUNT = 10000
CELL_SIZE = PARTICLE_RADIUS * 2
MULTI_PASS_PASSES = 2
FPS = 999


def position_function():
    if not pygame.mouse.get_focused():
        return SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2
    return pygame.mouse.get_pos()

def add_particle(particles, grid):
    particle = Particle(
            # distribute particles evenly over the space
            position = (
                    SCREEN_SIZE[0] // 2 + random.randint(-1, 1),
                    (SCREEN_SIZE[1] // 10)
            ),
            old_position = (
                    SCREEN_SIZE[0] // 2 + random.randint(-1, 1),
                    (SCREEN_SIZE[1] // 10)
            ),
            radius = PARTICLE_RADIUS,
            color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
            ),
    )
    particles.append(particle)
    grid.add_particle(particle)

def main():
    grid = SpatialHashGrid(CELL_SIZE)
    particles = []
    single_pass_constraints = [
            gravity(PARTICLE_GRAVITY),
    ]
    multi_pass_constraints = [
            screen_constraint(SCREEN_SIZE),
            friction(PARTICLE_FRICTION),
            collision_constraint_2(grid),
    ]
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    running = True
    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(BACKGROUND_COLOR)
        grid.draw(screen)
        for particle in particles:
            grid.update_particle(
                    particle.simulate(
                            MULTI_PASS_PASSES, single_pass_constraints, multi_pass_constraints
                    )
            )
            x, y = particle.position
            radius = particle.properties.setdefault("radius", PARTICLE_RADIUS)
            color = particle.properties.get("color", (255, 255, 255))
            pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        # show the number of particles, and the number of cells, and the fps
        text = font.render(
                f"Particles: {len(particles)} FPS: {clock.get_fps():.2f}",
                True,
                (255, 255, 255),
        )
        screen.blit(text, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        if i & 10 == 0 and len(particles) < PARTICLE_COUNT:
            add_particle(particles, grid)
        if i % 600 == 0:
            grid.sweep_empty_cells()
            i = 0
        else:
            i += 1

    pygame.quit()


if __name__ == "__main__":
    main()
