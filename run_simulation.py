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
    rotational_force
)

SCREEN_SIZE = (800, 600)
SCREEN_CENTER = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2)
FPS = 30


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    mouse_location_function = pygame.mouse.get_pos
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
            radius=random.randint(5, 10),
        )
        for _ in range(100)
    ]
    single_pass_constraints = [
        magnetic_mouse_constraint(1, 200, mouse_location_function),
        repulsive_mouse_constraint(3, 140, mouse_location_function),
        magnetic_mouse_constraint(5, 120, mouse_location_function),
        repulsive_mouse_constraint(6, 100, mouse_location_function),
        magnetic_mouse_constraint(7, 80, mouse_location_function),
        repulsive_mouse_constraint(9, 60, mouse_location_function),
        magnetic_mouse_constraint(10, 50, mouse_location_function),
        rotational_force( 0.1, 200, mouse_location_function),
        gravity(0.1),
    ]
    multi_pass_constraints = [
        collision_constraint(particles),
        circle_constraint(SCREEN_CENTER, 300),
        friction,
    ]
    particle_sprite_group = pygame.sprite.Group(
        [ParticleSprite(particle) for particle in particles]
    )
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill((0, 0, 0))
        particle_sprite_group.update()
        particle_sprite_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        varlet(particles, single_pass_constraints, multi_pass_constraints)


class ParticleSprite(pygame.sprite.Sprite):
    def __init__(self, particle: Particle):
        super().__init__()
        self.image = pygame.Surface(
            (particle.properties["radius"] * 2,) * 2, pygame.SRCALPHA
        )
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.particle = particle

    def update(self):
        radius = self.particle.properties.setdefault("radius", 5)

        pygame.draw.circle(
            self.image,
            self.particle.properties.setdefault(
                "color",
                (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                ),
            ),
            (radius, radius),
            radius,
        )
        self.rect.center = self.particle.position

    def __repr__(self):
        return f"ParticleSprite({self.particle})"


if __name__ == "__main__":
    main()
