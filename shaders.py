import numpy as np
import random
import math

def vertexShader(vertex, **kwargs):
    modelMatrix = kwargs["modelMatrix"]
    viewMatrix = kwargs["viewMatrix"] 
    projectionMatrix = kwargs["projectionMatrix"] 
    viewportMatrix = kwargs["viewportMatrix"]

    normal = kwargs.get("normal", [0, 0, 1])  

    vt = [vertex[0],
          vertex[1],
          vertex[2],
          1]
    
    nt = [normal[0],
          normal[1],
          normal[2],
          0]

    vt = viewportMatrix * projectionMatrix * viewMatrix * modelMatrix @ vt
    vt = vt.tolist()[0]

    nt = modelMatrix @ nt
    nt = nt.tolist()[0]

    vt = [vt[0] / vt[3],
          vt[1] / vt[3],
          vt[2] / vt[3]]
    
    nt = [nt[0],
          nt[1],
          nt[2]]

    nt = nt / np.linalg.norm(nt)

    return vt, nt

def fragmentShader(**kwargs):
    r, g , b = kwargs["pixelColor"]
    return [r, g, b]

def flatShader(**kwargs):
    A, B, C = kwargs["verts"]
    r, g , b = kwargs["pixelColor"]
    dirLight = kwargs["dirLight"]

    nA = [A[3], A[4], A[5]]
    nB = [B[3], B[4], B[5]]
    nC = [C[3], C[4], C[5]]

    normal = [(nA[0]+nB[0]+nC[0])/3,
              (nA[1]+nB[1]+nC[1])/3,
              (nA[2]+nB[2]+nC[2])/3]
    
    #intensity = normal DOT -dirLight
    intensity = np.dot(normal, -np.array(dirLight))
    intensity = max(0, intensity)

    r *= intensity
    g *= intensity
    b *= intensity

    return [r, g, b]

def gouradShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    r, g , b = kwargs["pixelColor"]
    dirLight = kwargs["dirLight"]

    nA = [A[3], A[4], A[5]]
    nB = [B[3], B[4], B[5]]
    nC = [C[3], C[4], C[5]]

    normal = [u*nA[0] + v*nB[0] + w*nC[0],
              u*nA[1] + v*nB[1] + w*nC[1],
              u*nA[2] + v*nB[2] + w*nC[2]]
    
    #intensity = normal DOT -dirLight
    intensity = np.dot(normal, -np.array(dirLight))
    intensity = max(0, intensity)

    r *= intensity
    g *= intensity
    b *= intensity

    return [r, g, b]


def RainbowShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    
    pos = (u * 0.3 + v * 0.6 + w * 0.1)
    
    if pos < 0.166:
        r, g, b = 1.0, 0.0, 0.0    # Rojo
    elif pos < 0.333:
        r, g, b = 1.0, 0.5, 0.0    # Naranja
    elif pos < 0.5:
        r, g, b = 1.0, 1.0, 0.0    # Amarillo
    elif pos < 0.666:
        r, g, b = 0.0, 1.0, 0.0    # Verde
    elif pos < 0.833:
        r, g, b = 0.0, 0.0, 1.0    # Azul
    else:
        r, g, b = 0.5, 0.0, 0.5    # Violeta
    
    return [r, g, b]

def oceanShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    
    # Coordenadas de textura simuladas
    tx = u * 10
    ty = v * 10
    
    # Patrón de onda
    wave1 = math.sin(tx * 2 + ty) * 0.5
    wave2 = math.sin(tx * 1.5 - ty * 2) * 0.3
    wave = wave1 + wave2
    
    # Color base azul con variación
    base_blue = 0.6 + wave * 0.2
    r = 0.1
    g = 0.3 + wave * 0.1
    b = min(1.0, base_blue)
    
    # Highlight basado en normales
    nA = [A[3], A[4], A[5]]
    nB = [B[3], B[4], B[5]]
    nC = [C[3], C[4], C[5]]
    normal = [u*nA[0] + v*nB[0] + w*nC[0],
              u*nA[1] + v*nB[1] + w*nC[1],
              u*nA[2] + v*nB[2] + w*nC[2]]
    
    highlight = max(0, np.dot(normal, [0, 1, 0])) ** 2
    r += highlight * 0.5
    g += highlight * 0.3
    b += highlight * 0.1
    
    return [r, g, b]

def discoShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    
    center_u = 1/3
    center_v = 1/3
    center_w = 1/3
    
    dist = math.sqrt((u-center_u)**2 + (v-center_v)**2 + (w-center_w)**2)
    
    rings = math.sin(dist * 50)  
    
    r = abs(math.sin(dist * 20))  #
    g = (rings + 1) / 2          
    b = 1 - dist                 
    
    return [r, g, b]

def fireShader(**kwargs):
    A, B, C = kwargs["verts"]
    u, v, w = kwargs["bCoords"]
    
    # Base de las llamas (zona más caliente)
    flame_base = 1.0 - v  # Más intenso en la parte inferior
    
    # Patrón de llamas con ruido fractal
    noise1 = math.sin(u * 10.0 + v * 20.0) * 0.5
    noise2 = math.sin(u * 7.0 - v * 15.0) * 0.3
    noise3 = math.sin(u * 15.0 + v * 25.0) * 0.2
    combined_noise = (noise1 + noise2 + noise3) * v
    
    # Forma de las llamas
    flame_shape = flame_base * (1.0 + combined_noise)
    
    # Gradiente de color (de amarillo a rojo)
    r = min(1.0, flame_shape * 1.2)  # Componente roja
    g = flame_shape * 0.6             # Componente verde
    b = flame_shape * 0.1             # Componente azul
    
    # Zona más caliente (núcleo de la llama)
    hot_core = max(0.0, flame_shape - 0.7) * 2.0
    r += hot_core * 0.5
    g += hot_core * 0.3
    
    # Efecto de chispas aleatorias
    if random.random() > 0.98:
        r, g, b = 1.0, 1.0, 0.8  # Destellos blancos
    
    return [r, g, b]