import pygame
import random
from gl import *
from BMP_Writer import GenerateBMP
from model import Model
from shaders import *
from OBJLoader import OBJ

width = 800
height = 600

screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()

rend = Renderer(screen)

rend.primitiveType = TRIANGLES

obj_model = OBJ("Penguin.obj")

model = Model()
model.vertices = []
model.normals = []

# Cargar vértices y normales por cada cara
for face in obj_model.faces:
    for vertex_index, normal_index in face:
        # Añadir vértices (x, y, z)
        model.vertices.extend(obj_model.vertices[vertex_index*3 : vertex_index*3+3])
        
        # Añadir normales (nx, ny, nz) si existen
        if normal_index is not None and obj_model.normals:
            model.normals.extend(obj_model.normals[normal_index*3 : normal_index*3+3])

# Configurar transformación y shaders
#model.translation[0] = width / 2
#model.translation[1] = height / 3
model.translation[2] = -5
model.scale = [(i*2) for i in model.scale]
model.vertexShader = vertexShader
model.fragmentShader = fireShader
#model.rotation[1] = 180

rend.models.append(model)

#rend.glColor(0,0,1)

#rend.glRender()

isRunning = True
while isRunning:
    deltaTime = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                rend.primitiveType = POINTS
            elif event.key == pygame.K_2:
                rend.primitiveType = LINES
            elif event.key == pygame.K_3:
                rend.primitiveType = TRIANGLES
            elif event.key == pygame.K_4:
                model.fragmentShader = fragmentShader
            elif event.key == pygame.K_5:
                model.fragmentShader = flatShader
            elif event.key == pygame.K_6:
                model.fragmentShader = gouradShader
            elif event.key == pygame.K_7:
                model.fragmentShader = RainbowShader
            elif event.key == pygame.K_8:
                model.fragmentShader = oceanShader
            elif event.key == pygame.K_9:
                model.fragmentShader = discoShader
            elif event.key == pygame.K_0:
                model.fragmentShader = fireShader

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        rend.camera.translation[0] += 20 
    if keys[pygame.K_LEFT]:
        rend.camera.translation[0] -= 20
    if keys[pygame.K_UP]:
        rend.camera.translation[1] += 20
    if keys[pygame.K_DOWN]:
        rend.camera.translation[1] -= 20
    if keys[pygame.K_d]:
        model.rotation[1] += 45 * deltaTime  # Rotación Y (horizontal)
    if keys[pygame.K_a]:
        model.rotation[1] -= 45 * deltaTime  # Rotación Y (horizontal)
    if keys[pygame.K_w]:
        model.rotation[0] += 45 * deltaTime  # Rotación X (vertical)
    if keys[pygame.K_s]:
        model.rotation[0] -= 45 * deltaTime  # Rotación X (vertical)
    if keys[pygame.K_q]:
        model.rotation[2] += 45 * deltaTime  # Rotación Z (roll)
    if keys[pygame.K_e]:
        model.rotation[2] -= 45 * deltaTime  # Rotación Z (roll)
    if keys[pygame.K_z]:
        model.scale = [(i + deltaTime) for i in model.scale]
    if keys[pygame.K_x]:
        model.scale = [(max(0.1, i - deltaTime)) for i in model.scale]

    

    rend.glClear()
    rend.glRender()
    pygame.display.flip()

rend.glClear()
GenerateBMP("output.bmp", width, height, 3, rend.frameBuffer)
pygame.quit()