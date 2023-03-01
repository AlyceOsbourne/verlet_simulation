import functools
import random
from typing import Callable, List, Tuple

import numpy as np

Position = Tuple[float, float]
Constraint = Callable[["Particle"], "Particle"]
import scipy
import numpy
import itertools
import functools
class Particle:
    __slots__ = ("position", "old_position", "properties")

    def __init__(
            self,
            position: Position,
            old_position: Position,
            **properties):
        self.position = position
        self.old_position = old_position
        self.properties = properties

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


def varlet(
        particles: List[Particle],
        single_pass_constraints: List[Constraint],
        multi_pass_constraints: List[Constraint],
        iterations: int = 5,
) -> List[Particle]:
    for particle in particles:
        update_particle(
                iterations, multi_pass_constraints, particle, single_pass_constraints
        )
    return particles


def update_particle(
        iterations, multi_pass_constraints, particle, single_pass_constraints
):
    particle.update()
    particle.apply_constraints(single_pass_constraints)
    for _ in range(iterations):
        particle.apply_constraints(multi_pass_constraints)


def gravity(acceleration: float = 3) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        x, y = particle.old_position
        mass = particle.properties.get("mass", particle.properties.get("radius", 5) * 0.05)
        particle.old_position = x, y - (acceleration * mass)
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


# constrain inside a circle
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


def get_closest_indices(particles: List[Particle], particle: Particle) -> List[int]:
    tree = scipy.spatial.cKDTree([p.position for p in particles])
    return tree.query_ball_point(
            particle.position,
            particle.properties.get("radius", 5) * 2,
            eps = 0,
            return_sorted = False,
            workers = -1,

    )


# constrain collision between particles
def collision_constraint(particles: List[Particle]) -> Constraint:
    def constraint(particle: Particle) -> Particle:
        radii = particle.properties.get("radius", 5)
        for other in itertools.islice(particles, 0, particles.index(particle)):
            if other is particle:
                continue
            ox, oy = other.position
            x, y = particle.position
            dx, dy = x - ox, y - oy
            radii_sum = radii + other.properties.get("radius", 5)
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance == 0:
                continue
            if distance < radii_sum:
                half_distance = (radii_sum - distance) / 2
                particle.position = (
                        x + dx / distance * half_distance,
                        y + dy / distance * half_distance,
                )
                other.position = (
                        ox - dx / distance * half_distance,
                        oy - dy / distance * half_distance,
                )
        return particle

    return constraint


def repulsive_mouse_constraint(force, radius, mouse_location_function):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        mx, my = mouse_location_function()
        dx, dy = x - mx, y - my
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < radius:
            particle.position = x + dx / distance * force, y + dy / distance * force
        return particle

    return constraint


def magnetic_mouse_constraint(force, radius, mouse_location_function):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        mx, my = mouse_location_function()
        dx, dy = x - mx, y - my
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < radius:
            particle.position = x - dx / distance * force, y - dy / distance * force
        return particle

    return constraint


def rotational_force(force, drop_off, mouse_location_function):
    def constraint(particle: Particle) -> Particle:
        x, y = particle.position
        cx, cy = mouse_location_function()
        dx, dy = x - cx, y - cy
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < drop_off:
            particle.position = x + dy / distance * force, y - dx / distance * force
        return particle

    return constraint
