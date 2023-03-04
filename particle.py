import functools
import itertools
import math
from typing import Callable, List, Tuple

Position = Tuple[float, float]
Constraint = Callable[["Particle"], "Particle"]


class Particle:
    __slots__ = (
            "position",
            "old_position",
            "properties",
            "single_pass_constraints",
            "multi_pass_constraints",
            "num_iterations",
            'skip_pass'
    )

    def __init__(
            self,
            position: Position,
            old_position: Position,
            single_pass_constraints: List[Constraint] = None,
            multi_pass_constraints: List[Constraint] = None,
            num_iterations: int = 0,
            **properties,
    ):
        self.position = position
        self.old_position = old_position
        self.properties = properties
        self.single_pass_constraints = single_pass_constraints or []
        self.multi_pass_constraints = multi_pass_constraints or []
        self.num_iterations = num_iterations
        self.skip_pass = False

    def __repr__(self):
        return f"Particle(position={self.position}, old_position={self.old_position})"

    def update(self: "Particle") -> "Particle":
        x, y = self.position
        ox, oy = self.old_position
        vx, vy = x - ox, y - oy
        self.old_position = x, y
        self.position = x + vx, y + vy
        return self

    def apply_constraints(self, constraints: List[Constraint]):
        return functools.reduce(lambda p, c: c(p), constraints, self)

    def simulate(
            self,
            iterations,
            single_pass_constraints,
            multi_pass_constraints,
    ):
        # if the particle has barely moved, don't bother simulating it
        # if the difference between its old position and its current position is less than 1
        # then we can assume that it hasn't moved much
        if math.hypot(*self.position) - math.hypot(*self.old_position) < 1:
            self.skip_pass = not self.skip_pass
            if self.skip_pass:
                return self
        self.update()
        self.apply_constraints(single_pass_constraints)
        self.apply_constraints(self.single_pass_constraints)
        itertools.repeat(self.apply_constraints(multi_pass_constraints), iterations)
        itertools.repeat(
                self.apply_constraints(self.multi_pass_constraints), self.num_iterations
        )
        return self

    def __hash__(self):
        return id(self)


def simulate(
        particles: List[Particle],
        single_pass_constraints: List[Constraint],
        multi_pass_constraints: List[Constraint],
        iterations: int = 5,
) -> List[Particle]:
    yield from (
            particle.simulate(iterations, single_pass_constraints, multi_pass_constraints)
            for particle in particles
    )


# Forces
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
        ox, oy = particle.old_position
        vx, vy = x - ox, y - oy
        particle.old_position = x - vx * friction_coefficient, y - vy * friction_coefficient
        return particle

    return constraint
def get_nearby_particles(particle, particles):
    _range = particle.properties.get("radius", 5) + 30
    for other in itertools.islice(particles, 0, particles.index(particle) + 1):
        dist_x = abs(particle.position[0] - other.position[0])
        if dist_x > _range:
            continue
        dist_y = abs(particle.position[1] - other.position[1])
        if dist_y > _range:
            continue
        if dist_x < _range and dist_y < _range:
            yield other


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
def _hypot_distance(other, particle):
    distance = math.hypot(particle[0] - other[0], particle[1] - other[1])
    return distance


def collision_constraint(particles):
    def constraint(particle):
        radius = particle.properties.get("radius", 5)
        for other in get_nearby_particles(particle, particles):
            if other is particle:
                continue
            distance = _hypot_distance(other.position, particle.position)
            radii_sum = _sum_dist(other.properties.get("radius", 5), radius)
            if distance < radii_sum:
                half_distance = (radii_sum - distance) / 2
                dx, dy, ox, oy, x, y = _adjust(other.position, particle.position)
                particle.position = (x + dx / distance * half_distance, y + dy / distance * half_distance)
                other.position = (ox - dx / distance * half_distance, oy - dy / distance * half_distance)
        return particle

    return constraint


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
                if distance== 0:
                    distance = 0.0001
                particle.position = (x + dx / distance * half_distance, y + dy / distance * half_distance)
                other.position = (ox - dx / distance * half_distance, oy - dy / distance * half_distance)
        return particle

    return constraint


# Effectors
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
