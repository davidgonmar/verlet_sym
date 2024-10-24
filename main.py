import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Falling Particle")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

clock = pygame.time.Clock()


class Vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec2d(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vec2d(self.x / scalar, self.y / scalar)

    def __matmul__(self, other):
        return self.x * other.x + self.y * other.y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def magnitude(self):
        return (self @ self) ** 0.5

    def normalize(self):
        if self.magnitude() == 0:
            return Vec2d(0, 0)
        return self / self.magnitude()


class Particle:
    def __init__(self):
        self.position = Vec2d(0, 0)
        self.prev_position = Vec2d(0, 0)
        self.radius = 10
        self.pinned = False

    def apply_forces(self, force_fns, dt):
        if self.pinned:
            return

        total_force = Vec2d(0, 0)
        for force_fn in force_fns:
            total_force += force_fn(self) * dt
        new_position = (
            self.position + (self.position - self.prev_position) + total_force
        )
        self.prev_position = self.position
        self.position = new_position

    def apply_constraints(self, constraint_fns):
        for constraint_fn in constraint_fns:
            constraint_fn(self)


particles = []
GRID_SIZE_X = 8
GRID_SIZE_Y = 8


def gravity(particle):
    return Vec2d(0, 1)


def in_screen(particle):
    particle.position.x = max(
        particle.radius, min(WIDTH - particle.radius, particle.position.x)
    )
    particle.position.y = max(
        particle.radius, min(HEIGHT - particle.radius, particle.position.y)
    )


class Link:
    def __init__(self, p1, p2, length):
        self.p1 = p1
        self.p2 = p2
        self.length = length


links = []

for i in range(GRID_SIZE_X * GRID_SIZE_Y):
    x = i % GRID_SIZE_X
    y = i // GRID_SIZE_X
    particle = Particle()
    particle.position = Vec2d(x * 50 + 300, y * 50 + 100)
    particle.prev_position = particle.position
    particle.radius = 10
    particles.append(particle)

    if y == 0:
        particle.pinned = True

for i in range(GRID_SIZE_X * GRID_SIZE_Y):
    x = i % GRID_SIZE_X
    y = i // GRID_SIZE_X
    if x < GRID_SIZE_X - 1:
        links.append(
            Link(
                particles[i],
                particles[i + 1],
                (particles[i].position - particles[i + 1].position).magnitude(),
            )
        )
    if y < GRID_SIZE_Y - 1:
        links.append(
            Link(
                particles[i],
                particles[i + GRID_SIZE_X],
                (
                    particles[i].position - particles[i + GRID_SIZE_X].position
                ).magnitude(),
            )
        )

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(WHITE)

    for particle in particles:
        particle.apply_forces([gravity], 1 / 120)

    for link in links:
        delta = link.p2.position - link.p1.position
        distance = delta.magnitude()
        error = distance - link.length
        correction = delta.normalize() * error / 2
        if not link.p1.pinned:
            link.p1.position += correction
        if not link.p2.pinned:
            link.p2.position -= correction

    for particle in particles:
        particle.apply_constraints([in_screen])

    for particle in particles:
        pygame.draw.circle(
            screen,
            RED,
            (int(particle.position.x), int(particle.position.y)),
            int(particle.radius),
        )

    for link in links:
        pygame.draw.line(
            screen,
            RED,
            (int(link.p1.position.x), int(link.p1.position.y)),
            (int(link.p2.position.x), int(link.p2.position.y)),
            1,
        )

    pygame.display.flip()

    mouse_pos = pygame.mouse.get_pos()
    for link in links:
        p1 = (int(link.p1.position.x), int(link.p1.position.y))
        p2 = (int(link.p2.position.x), int(link.p2.position.y))
        if pygame.mouse.get_pressed()[0] and pygame.draw.line(
            screen, RED, p1, p2, 1
        ).collidepoint(mouse_pos):
            links.remove(link)

    clock.tick(120)
