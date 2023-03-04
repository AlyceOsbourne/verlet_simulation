# Particle compatible spatial hash grid for collision detection
import sys
from collections import defaultdict
from math import floor, hypot
from typing import Dict, Iterable, List, Protocol, Set, Tuple, TypeVar

import pygame

Grid = Dict[Tuple[int, int], Set["Particle"]]
Particle = TypeVar("Particle")


def _get_nearby_cells(cell: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
    """Get nearby cells for a given cell"""
    x, y = cell
    return (
            (x - 1, y - 1),
            (x, y - 1),
            (x + 1, y - 1),
            (x - 1, y),
            (x, y),
            (x + 1, y),
            (x - 1, y + 1),
            (x, y + 1),
            (x + 1, y + 1),
    )


def _get_cell(position: Tuple[float, float], cell_size) -> Tuple[int, int]:
    """Get the cell for a given position"""
    return (
            floor(position[0] / cell_size),
            floor(position[1] / cell_size),
    )


class SpatialHashGrid:
    """Spatial hash grid for collision detection"""

    def __init__(self, cell_size: float):
        self.cell_size = cell_size
        self.grid: Grid = defaultdict(set)

    def draw(self, screen: pygame.Surface):
        """Draw the grid"""
        # sell size can be a float, so we need a different way to draw the grid
        # than the one used in the particle system
        for cell in self.grid:
            x, y = cell
            x *= self.cell_size
            y *= self.cell_size
            pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (x, y, self.cell_size, self.cell_size),
                    1,
            )

    def add_particle(self, particle: Particle):
        """Add a particle to the grid"""
        cell = _get_cell(particle.position, self.cell_size)
        self.grid[cell].add(particle)
        particle.properties["cell"] = cell

    def remove_particle(self, particle: Particle):
        """Remove a particle from the grid"""
        self.grid[particle.properties["cell"]].remove(particle)
        particle.properties.pop("cell")

    def update_particle(self, particle: Particle):
        """Update a particle's cell"""
        cell = _get_cell(particle.position, self.cell_size)
        if cell != particle.properties["cell"]:
            self.grid[particle.properties["cell"]].remove(particle)
            self.grid[cell].add(particle)
            particle.properties["cell"] = cell

    def get_nearby_particles(self, particle: Particle) -> Iterable[Particle]:
        cell = particle.properties["cell"]
        for nearby_cell in _get_nearby_cells(cell):
            yield from self.grid[nearby_cell]


    def sweep_empty_cells(self):
        """Remove empty cells from the grid"""
        for cell in list(self.grid):
            if not self.grid[cell]:
                self.grid.pop(cell)
