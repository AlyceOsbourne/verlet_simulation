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
            'skip_pass',
            'idle_frames',
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
        self.idle_frames = 0

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
        vx, vy = self.velocity
        if all([
                math.isclose(vx, 0, rel_tol=self.properties.get('radius', 0.1)),
                math.isclose(vy, 0, rel_tol=self.properties.get('radius', 0.1)),
        ]):
            self.idle_frames += 1
            if self.idle_frames > 10:
                self.skip_pass = not self.skip_pass
                if self.skip_pass:
                    return self
        else:
            self.idle_frames = 0
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

    @property
    def velocity(self):
        return self.position[0] - self.old_position[0], self.position[1] - self.old_position[1]

    @velocity.setter
    def velocity(self, value):
        self.old_position = self.position[0] - value[0], self.position[1] - value[1]


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
