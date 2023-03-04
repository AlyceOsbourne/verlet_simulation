import random

from particle import (
    Particle,
)
from constraints import (
    circle_constraint,
    collision_constraint_2,
    friction,
    gravity,
    magnetic_force,
    repulsive_force,
    rotational_force,
    screen_constraint,
)
from spatial_hash_grid import SpatialHashGrid
import pygame

SCREEN_SIZE = (800, 600)
BACKGROUND_COLOR = (0, 0, 0)
PARTICLE_RADIUS = 5
PARTICLE_FRICTION = 0.99
PARTICLE_GRAVITY = 0.2
PARTICLE_COUNT = 5000
CELL_SIZE = PARTICLE_RADIUS * 2
MULTI_PASS_PASSES = 3
FPS = 60

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)


def position_function():
    if not pygame.mouse.get_focused():
        return SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2
    return pygame.mouse.get_pos()


class ParticleSprite(pygame.sprite.Sprite):
    # us ised to render the particles, but instead of reblitting cirles, we just move the rect
    def __init__(self, particle):
        super().__init__()
        self.particle = particle
        self.radius = particle.properties.get("radius", PARTICLE_RADIUS)
        self.color = particle.properties.get("color", (255, 255, 255))
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = particle.position
        pygame.draw.circle(
            self.image,
            self.color,
            (self.rect.width // 2, self.rect.height // 2),
            self.radius,
        )

    def update(self):
        self.rect.center = self.particle.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def add_particle(particles, grid, sprite_group):
    particle = Particle(
        # distribute particles evenly over the space
        position=(SCREEN_SIZE[0] // 2 + random.randint(-2, 2), (SCREEN_SIZE[1] // 10)),
        old_position=(
            SCREEN_SIZE[0] // 2 + random.randint(-2, 2),
            (SCREEN_SIZE[1] // 10),
        ),
        radius=PARTICLE_RADIUS,
        color=(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ),
    )
    particles.append(particle)
    grid.add_particle(particle)
    sprite_group.add(ParticleSprite(particle))


def main(render_grid=False, render_particles=True, cull_grid=False):

    grid = SpatialHashGrid(CELL_SIZE)
    particles = []
    sprite_group = pygame.sprite.Group()
    single_pass_constraints = [
        gravity(PARTICLE_GRAVITY),
        circle_constraint((SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2), 300),
        rotational_force(0.1, 200, position_function),
        magnetic_force(0.1, 300, position_function),
        repulsive_force(0.3, 100, position_function),
    ]
    multi_pass_constraints = [
        friction(PARTICLE_FRICTION),
        collision_constraint_2(grid),
    ]
    running = True
    i = 0

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for particle in particles:
            grid.update_particle(
                particle.simulate(
                    MULTI_PASS_PASSES, single_pass_constraints, multi_pass_constraints
                )
            )
        screen.fill(BACKGROUND_COLOR)
        if render_grid:
            grid.draw(screen)
        if render_particles:
            sprite_group.update()
            sprite_group.draw(screen)
        text = font.render(
            f"Particles: {len(particles)} FPS: {clock.get_fps():.2f}",
            True,
            (255, 255, 255),
        )
        screen.blit(text, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        if i & 10 == 0 and len(particles) < PARTICLE_COUNT:
            add_particle(particles, grid, sprite_group)
        if i % 30000 == 0:
            if cull_grid:
                grid.sweep_empty_cells()
            i = 0
        else:
            i += 1

    pygame.quit()


if __name__ == "__main__":
    profile = False
    if profile:
        import cProfile
        import pstats

        def filter_builtins(stats):
            for stat in stats:
                if stat[0].startswith("builtins"):
                    continue
                yield stat

        cProfile.run(
            "main(render_grid=False, render_particles=False, cull_grid=True)", "stats"
        )
        stats = pstats.Stats("stats")
        stats.strip_dirs()
        stats.sort_stats("time")
        stats.print_stats(20)
        stats.sort_stats("calls")
        stats.print_stats(20)

    else:
        main(render_grid=False, render_particles=True, cull_grid=True)
