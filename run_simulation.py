import random

import pygame

from verlet import circle_constraint, collision_constraint, FPS, friction, gravity, Particle, SCREEN_CENTER, \
    SCREEN_SIZE, varlet


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    particles = [
            Particle(
                    position = (
                            SCREEN_CENTER[0] + random.randint(-200, 200),
                            SCREEN_CENTER[1] + random.randint(-200, 200),
                    ),
                    old_position = (
                            SCREEN_CENTER[0] + random.randint(-100, 100),
                            SCREEN_CENTER[1] + random.randint(-100, 100),
                    ),
                    color = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                    ),
                    radius = random.randint(5, 10),
            )
            for _ in range(80)
    ]
    single_pass_constraints = [
            gravity(acceleration = 3),
    ]
    multi_pass_constraints = [
            collision_constraint(particles),
            circle_constraint(SCREEN_CENTER, 300),
            friction(damping = 0.005),
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
        # draws a circle with the radius of the particle, with transparant background
        self.image = pygame.Surface((particle.properties["radius"] * 2,) * 2, pygame.SRCALPHA)
        radius = particle.properties["radius"]
        pygame.draw.circle(
                self.image,
                particle.properties["color"],
                (radius, radius),
                radius,
        )
        self.rect = self.image.get_rect()
        self.particle = particle

    def update(self):
        self.rect.center = self.particle.position

    def __repr__(self):
        return f"ParticleSprite({self.particle})"


if __name__ == "__main__":
    main()
