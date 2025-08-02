import numpy as np

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