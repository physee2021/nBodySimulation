import pygame
import random as r
import math as m
import numpy as np
from pygame import gfxdraw
from qtree import Point, Rect, QuadTree
import matplotlib.pyplot as plt
from statistics import stdev
# some colours
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)

#                               PYGAME INITIAL CONDITIONS
#--------------------------------------------------------------------------------------#
pygame.init()

# screen dimensions
width = 700
height = 700

# Generate random colour. Looks pretty and saves time hardcoding stuff idk
def randColour():
    colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return colour

# set screen size & instantiate
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('N-Body Simulation')

# loop until close
done = False

# screen updates (for readability)
clock = pygame.time.Clock()

# Specific Globals
gravitationalConst = 6.67408 * (10**-11)

# for debug
# gravitationalConst = 1
#--------------------------------------------------------------------------------------#
#                                   PYGAME OBJECTS
#--------------------------------------------------------------------------------------#
class Particle():
    def __init__(self, x, y, mass, size, angle=0, speed=0, color=blue):
        self.x = x; self.y = y
        self.mass = mass
        self.size = size
        self.angle = angle
        self.speed = speed
        self.color = color

    def display(self):
        try:
            pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.size, self.color)
        except OverflowError:
            pass

    # Speed is a vector and thus can be represented by its direction, determined by it's angle, and its magnitude, which I call speed for simplicities sake:
    def move(self, other):
        force = self.attract(other)
        self.x += m.sin(self.angle) * self.speed
        self.y -= m.cos(self.angle) * self.speed
        return force

    def attract(self, other):
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist = m.hypot(dx, dy)
            
        # returns angle between two lines in euclidean space
        theta = m.atan2(dy, dx)
        try:
            force = gravitationalConst * self.mass * other.mass / dist**2 +.02
        except ZeroDivisionError:
            force = 0
        self.accelerate((theta - 0.5 * m.pi, force/self.mass))
        other.accelerate((theta + 0.5 * m.pi, force/other.mass))
        return force

    def accelerate(self, vector):
        self.angle, self.speed = addVectors((self.angle, self.speed), vector)
    

#--------------------------------------------------------------------------------------#
#                                DEFINING FUNCTIONS
#--------------------------------------------------------------------------------------#

# Adding angle and length components of vectors together

def addVectors(vector1, vector2):
    a1, l1 = vector1
    a2, l2 = vector2
    x = m.sin(a1) * l1 + m.sin(a2) * l2
    y = m.cos(a1) * l1 + m.cos(a2) * l2
    length = m.hypot(x, y)
    angle = 0.5 * m.pi - m.atan2(y, x)
    return angle, length

# Collision function
def collide(p1, p2):
    # Linear algebra. Who woulda thunk, huh?
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    # math.hypot() is distance
    distance = m.hypot(dx, dy)
    if distance < p1.size + p2.size:
        return True

def calcEnergy(p1, p2):
    r = m.hypot(p1.x - p2.x, p1.y-p2.y) # replace with distance
    kinetic = 0.5 * p1.mass * (p1.speed ** 2)
    try:
        gravitational = 0.5 * gravitationalConst * p1.mass * p2.mass / (r)
    except ZeroDivisionError:
        gravitational = 0
    return kinetic, gravitational
    # under construction

def makeCOM(bodies):
    x = []
    y = []
    totalMass = 0
    for body in bodies:
        x.append(body.x)
        y.append(body.y)
        totalMass += body.mass
    try:
        xAve = sum(x)/len(x)
        yAve = sum(y)/len(y)
        return Particle(xAve, yAve, totalMass, totalMass, 0, 0, red)
    except ZeroDivisionError:
        pass
        return None

#--------------------------------------------------------------------------------------#
#                               OBJECT INSTANTIATION
#--------------------------------------------------------------------------------------#
sprites = []


# sun = Particle(width/2, height/2, mass=333, size=1, angle=0, speed=0)
# earth = Particle(width/2 + 200, height/2, mass=1, size=2, angle=0, speed=0)
# earth.speed = (gravitationalConst*sun.mass)/(m.hypot((sun.x - earth.x), (sun.y - earth.y)))
# print(earth.speed)
# sprites.append(sun); sprites.append(earth)
            

domain = Rect(width/2, height/2, width, height)

paused = False
comshow = False
timer = 0
subtimer = 0

totalKE = []
totalPE = []


grid = plt.GridSpec(1, 1, wspace=0.0, hspace=0.3)
ax1 = plt.subplot(grid[0,0])
# plt.show()

#--------------------------------------------------------------------------------------#
#                                        MAIN
#--------------------------------------------------------------------------------------#

# Main loop
for c in range(5):
    # done = False
    timer = 0
    # sprites = []
    for i in range(100):
        # x, y, mass, size, angle, speed
        body = Particle(r.uniform(0, width), r.uniform(10, height-10), mass=2, size=r.randint(1, 1), angle=r.uniform(0, m.pi), speed=0)
        sprites.append(body)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not paused:
                        paused = True
                    else: 
                        paused = False
                if event.key == pygame.K_EQUALS:
                    if not comshow:
                        comshow = True
                    else:
                        comshow = False

        # Wipes screen every time to avoid clipping and stuff
        qTree = QuadTree(domain, 3)
        screen.fill(white)
        
        for point in sprites:
            qTree.insert(point)
        list_of_nodes = qTree.findNodes(qTree, [])
        
        com = []
        for node in list_of_nodes:
            com.append(makeCOM(node))

        tempKE = []
        tempPE = []
        for sprite in sprites:
            for particle in com:
                if sprite is not particle:
                    if not paused:
                        try:
                            gForce = sprite.move(particle)
                            tempKE.append(calcEnergy(sprite, particle)[0])
                            tempPE.append(calcEnergy(sprite, particle)[1])  
                            
                        except AttributeError:
                            pass
                else: gForce = 0
            sprite.display()
        print(c)
        totalKE.append(sum(tempKE))
        totalPE.append(sum(tempPE))
        subtimer += 1     
        # Display graphics
        qTree.draw()
        del qTree
        pygame.display.flip()

        timer += 1
        # @60fps * seconds = desired time
        if timer > 60*5:
            done = True

        clock.tick(60)

# print(sum(totalKE), sum(totalPE))
# print(sum(totalKE) - sum(totalPE))
print(len(totalKE), len(totalPE), subtimer)

print(sum(totalKE) - sum(totalPE))
print(sum(totalKE), sum(totalPE))

# arrays = [np.array(x) for x in multiple_lists]
# [np.mean(k) for k in zip(*arrays)]

print(stdev([x1 - x2 for (x1, x2) in zip(totalKE, totalPE)]))
plt.sca(ax1)
plt.title("Time Evolution of System Energies for \n n=100 bodies (With softening ε = .2) (Barnes-Hut)")
plt.ylabel("Energy E (J)")
plt.xlabel("Frames Elapsed (60 Frames per Second)")
plt.scatter(range(subtimer), totalKE, color='red', s=1, label='Kinetic Energy')
plt.scatter(range(subtimer), totalPE, color='blue',s=1,label='Potential Energy')
plt.scatter(range(subtimer), [x1 - x2 for (x1, x2) in zip(totalKE, totalPE)], color='black', s=1, label='Total Energy')
plt.legend()
plt.show()
