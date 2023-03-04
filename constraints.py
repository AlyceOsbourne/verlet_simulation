import functools
import math

from particle import Constraint, Particle, Position


def gravity(acceleration: float = 3) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        mass = particle.properties.get(
                "mass", particle.properties.get("radius", 5) * 0.02
        )
        particle.position = x, y + (acceleration * mass)
        return particle

    return constraint


def friction(friction_coefficient = .99) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        vx, vy = particle.velocity
        particle.old_position = x - vx * friction_coefficient, y - vy * friction_coefficient
        return particle
    return constraint


@functools.lru_cache(maxsize = 1000)
def _adjust(other, particle):
    x, y = particle
    ox, oy = other
    dx, dy = x - ox, y - oy
    return dx, dy, ox, oy, x, y


@functools.lru_cache(maxsize = 1000)
def _sum_dist(other_radius, radius):
    return radius + other_radius


@functools.lru_cache(maxsize = 1000)
def _hypot_distance(other_particle, particle_position):
    distance = math.hypot(particle_position[0] - other_particle[0], particle_position[1] - other_particle[1])
    return distance


def collision_constraint_2(grid):
    def constraint(particle):
        radius = particle.properties.get("radius", 5)
        for other in grid.get_nearby_particles(particle):
            if other is particle:
                continue
            distance = _hypot_distance(other.position, particle.position)
            radii_sum = _sum_dist(other.properties.get("radius", 5), radius)
            if distance < radii_sum:
                half_distance = (radii_sum - distance) / 2
                dx, dy, ox, oy, x, y = _adjust(other.position, particle.position)
                if distance == 0:
                    distance = 0.0001
                particle.position = (x + dx / distance * half_distance, y + dy / distance * half_distance)
                other.position = (ox - dx / distance * half_distance, oy - dy / distance * half_distance)
        return particle

    return constraint


def repulsive_force(force, radius, mouse_location_function):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        mx, my = mouse_location_function()
        dx, dy = x - mx, y - my
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < radius:
            particle.position = x + dx / distance * force, y + dy / distance * force
        return particle

    return constraint


def magnetic_force(force, radius, mouse_location_function):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        mx, my = mouse_location_function()
        dx, dy = x - mx, y - my
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < radius:
            particle.position = x - dx / distance * force, y - dy / distance * force
        return particle

    return constraint


def rotational_force(force, drop_off, mouse_location_function, anti_clockwise = True):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        cx, cy = mouse_location_function()
        dx, dy = x - cx, y - cy
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < drop_off:
            if anti_clockwise:
                particle.position = x + dy / distance * force, y - dx / distance * force
            else:
                particle.position = x - dy / distance * force, y + dx / distance * force
        return particle

    return constraint


def circle_constraint(center: Position, radius: float) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        cx, cy = center
        dx, dy = x - cx, y - cy
        distance = (dx ** 2 + dy ** 2) ** 0.5
        radii = particle.properties.get("radius", 5)
        if distance > radius - radii:
            particle.position = cx + dx / distance * (
                    radius - radii
            ), cy + dy / distance * (radius - radii)
        return particle

    return constraint


def screen_constraint(screen_size):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        radius = particle.properties.get("radius", 5)
        if x < radius:
            particle.position = radius, y
        elif x > screen_size[0] - radius:
            particle.position = screen_size[0] - radius, y
        if y < radius:
            particle.position = x, radius
        elif y > screen_size[1] - radius:
            particle.position = x, screen_size[1] - radius
        return particle

    return constraint


def link_constraint(particle_2, distance, rigidity = 1):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        ox, oy = particle.old_position
        dx, dy = x - ox, y - oy
        particle.old_position = x - dx * rigidity, y - dy * rigidity
        x, y = particle.position
        ox, oy = particle_2.position
        dx, dy = x - ox, y - oy
        distance_2 = (dx ** 2 + dy ** 2) ** 0.5
        if distance_2 != 0:
            particle.position = ox + dx / distance_2 * distance, oy + dy / distance_2 * distance
        return particle
    return constraint
