import numpy as np
import math
import time

def vertexShader(vertex, **kwargs):
    modelMatrix = kwargs["modelMatrix"]
    viewMatrix = kwargs["viewMatrix"]
    projectionMatrix = kwargs["projectionMatrix"]
    viewportMatrix = kwargs["viewportMatrix"]
    
    vt = [vertex[0], vertex[1], vertex[2], 1]
    
    vt = viewportMatrix @ projectionMatrix @ viewMatrix @ modelMatrix @ vt
    
    vt = vt.tolist()[0]
    vt = [vt[0]/vt[3], vt[1]/vt[3], vt[2]/vt[3]]
    
    return vt

def fragmentShader(**kwargs):
    texture = kwargs.get("texture")
    texCoords = kwargs.get("texCoords")
    
    if texture and texCoords:
        return texture.get_color(texCoords[0], texCoords[1])
    else:
        return kwargs.get("color", (1, 1, 1)) 
    
def rainbowFragmentShader(**kwargs):
    texCoords = kwargs.get("texCoords", [0, 0])
    u, v = texCoords[0], texCoords[1]

    current_time = time.time() * 0.5  

  
    hue = (u + v + current_time) % 1.0 
    r = math.sin(hue * 2 * math.pi + 0) * 0.5 + 0.5  
    g = math.sin(hue * 2 * math.pi + 2) * 0.5 + 0.5  
    b = math.sin(hue * 2 * math.pi + 4) * 0.5 + 0.5  

    return (r, g, b)