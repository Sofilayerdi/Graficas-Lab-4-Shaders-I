import random
import numpy as np
import pygame
from math import sqrt

# Definición de tipos de primitivas
POINTS = 0
LINES = 1
TRIANGLES = 2

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = self.screen.get_rect()

        self.glClearColor(0, 0, 0)  # Color de fondo negro por defecto
        self.glColor(1, 1, 1)       # Color de dibujo blanco por defecto

        self.glClear()

        self.primitiveType = TRIANGLES
        self.models = []
        self.camera = None

        self.activeModelMatrix = None
        self.activeVertexShader = None
        self.activeFragmentShader = None

        # Buffers
        self.frameBuffer = None
        self.zBuffer = None

    def set_camera(self, camera):
        """Asigna una cámara al renderizador"""
        self.camera = camera
        if camera:
            camera.set_viewport(0, 0, self.width, self.height)

    def glClearColor(self, r, g, b):
        """Establece el color de fondo"""
        self.clearColor = [
            min(1, max(0, r)),
            min(1, max(0, g)),
            min(1, max(0, b))
        ]

    def glColor(self, r, g, b):
        """Establece el color de dibujo actual"""
        self.currColor = [
            min(1, max(0, r)),
            min(1, max(0, g)),
            min(1, max(0, b))
        ]

    def glClear(self):
        """Limpia los buffers"""
        color = [int(c * 255) for c in self.clearColor]
        self.screen.fill(color)

        # Inicializar frame buffer
        self.frameBuffer = [
            [color.copy() for _ in range(self.height)] 
            for _ in range(self.width)
        ]

        # Inicializar z-buffer con infinito
        self.zBuffer = [
            [float('inf') for _ in range(self.height)] 
            for _ in range(self.width)
        ]

    def glPoint(self, x, y, color=None, z=0):
        """Dibuja un punto con test de profundidad"""
        x = round(x)
        y = round(y)

        if (0 <= x < self.width) and (0 <= y < self.height):
            # Test de profundidad
            if z < self.zBuffer[x][y]:
                self.zBuffer[x][y] = z

                # Convertir color a 0-255
                final_color = color if color else self.currColor
                pygame_color = [int(c * 255) for c in final_color]

                # Dibujar en pygame y frame buffer
                self.screen.set_at((x, self.height - 1 - y), pygame_color)
                self.frameBuffer[x][y] = pygame_color

    def glLine(self, p0, p1, color=None):
        """Dibuja una línea con interpolación de Z"""
        x0, y0, z0 = p0[0], p0[1], p0[2] if len(p0) > 2 else 0
        x1, y1, z1 = p1[0], p1[1], p1[2] if len(p1) > 2 else 0

        # Si es el mismo punto
        if x0 == x1 and y0 == y1:
            self.glPoint(x0, y0, color, z0)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            z0, z1 = z1, z0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.5
        m = dy / dx
        y = y0

        # Interpolación de Z
        total_distance = sqrt((x1-x0)**2 + (y1-y0)**2)
        
        for x in range(round(x0), round(x1) + 1):
            # Calcular t para interpolación
            if total_distance > 0:
                t = sqrt((x-x0)**2 + (y-y0)**2) / total_distance
            else:
                t = 0
            
            z = z0 + t * (z1 - z0)
            
            if steep:
                self.glPoint(y, x, color, z)
            else:
                self.glPoint(x, y, color, z)

            offset += m
            if offset >= limit:
                y += 1 if y0 < y1 else -1
                limit += 1

    def glTriangle(self, A, B, C, model=None, face_idx=None):
        """Dibuja un triángulo con texturas y z-buffer"""
        # Asegurar coordenadas z
        if len(A) < 3: A = [A[0], A[1], 0]
        if len(B) < 3: B = [B[0], B[1], 0]
        if len(C) < 3: C = [C[0], C[1], 0]
        
        # Bounding box
        min_x = max(0, min(A[0], B[0], C[0]))
        max_x = min(self.width - 1, max(A[0], B[0], C[0]))
        min_y = max(0, min(A[1], B[1], C[1]))
        max_y = min(self.height - 1, max(A[1], B[1], C[1]))
        
        # Función para calcular área (coordenadas baricéntricas)
        def area(p1, p2, p3):
            return abs(p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])) / 2
        
        total_area = area(A, B, C)
        if total_area == 0: return
        
        # Obtener coordenadas UV si hay textura
        uv_a = uv_b = uv_c = None
        if model and hasattr(model, 'texture') and model.texture and face_idx is not None:
            if face_idx < len(model.face_uvs):
                uv_indices = model.face_uvs[face_idx]
                if len(uv_indices) >= 3:
                    uv_a = model.texture_coords[uv_indices[0]] if uv_indices[0] < len(model.texture_coords) else [0, 0]
                    uv_b = model.texture_coords[uv_indices[1]] if uv_indices[1] < len(model.texture_coords) else [0, 0]
                    uv_c = model.texture_coords[uv_indices[2]] if uv_indices[2] < len(model.texture_coords) else [0, 0]
        
        # Rasterización
        for x in range(int(min_x), int(max_x) + 1):
            for y in range(int(min_y), int(max_y) + 1):
                P = [x, y]
                
                # Calcular pesos baricéntricos
                w_A = area(P, B, C) / total_area
                w_B = area(A, P, C) / total_area
                w_C = area(A, B, P) / total_area
                
                if 0 <= w_A <= 1 and 0 <= w_B <= 1 and 0 <= w_C <= 1:
                    # Interpolar Z
                    z = w_A * A[2] + w_B * B[2] + w_C * C[2]
                    
                    # Determinar color
                    color = self.currColor
                    
                    # Textura + iluminación
                    if uv_a and uv_b and uv_c:
                        # Interpolar UVs
                        u = w_A * uv_a[0] + w_B * uv_b[0] + w_C * uv_c[0]
                        v = w_A * uv_a[1] + w_B * uv_b[1] + w_C * uv_c[1]
                        
                        texture_color = model.get_texture_color(u, v)
                        
                        # Combinar con color de iluminación si existe
                        if hasattr(model, 'colors') and face_idx < len(model.colors):
                            lighting_color = model.colors[face_idx]
                            color = [
                                texture_color[0] * lighting_color[0],
                                texture_color[1] * lighting_color[1],
                                texture_color[2] * lighting_color[2]
                            ]
                        else:
                            color = texture_color
                    
                    self.glPoint(x, y, color, z)

    def glRender(self):
        """Renderiza todos los modelos"""
        for model in self.models:
            self.activeModelMatrix = model.GetModelMatrix()
            self.activeVertexShader = model.vertexShader
            self.activeFragmentShader = model.fragmentShader

            vertexBuffer = []
            
            # Procesar vértices con shaders
            for i in range(0, len(model.vertices), 3):
                x, y, z = model.vertices[i], model.vertices[i+1], model.vertices[i+2]
                
                if self.activeVertexShader:
                    kwargs = {"modelMatrix": self.activeModelMatrix}
                    
                    if self.camera:
                        kwargs.update({
                            "viewMatrix": self.camera.get_view_matrix(),
                            "projectionMatrix": self.camera.get_projection_matrix(),
                            "viewportMatrix": self.camera.get_viewport_matrix()
                        })
                    
                    x, y, z = self.activeVertexShader([x, y, z], **kwargs)
                
                vertexBuffer.append([x, y, z])

            # Renderizar según tipo de primitiva
            if hasattr(model, 'faces') and model.faces:
                self.render_with_faces(model, vertexBuffer)
            else:
                self.glDrawPrimitives(vertexBuffer, 3)

    def render_with_faces(self, model, vertexBuffer):
        """Renderiza usando las caras del modelo"""
        for face_idx, face in enumerate(model.faces):
            if len(face) >= 3:
                # Obtener vértices del triángulo
                v1 = vertexBuffer[face[0]]
                v2 = vertexBuffer[face[1]] 
                v3 = vertexBuffer[face[2]]
                
                # Establecer color
                if hasattr(model, 'texture') and model.texture:
                    self.glColor(1, 1, 1)  # Color neutro para texturas
                elif hasattr(model, 'colors') and face_idx < len(model.colors):
                    color = model.colors[face_idx]
                    self.glColor(color[0], color[1], color[2])
                else:
                    self.glColor(1, 1, 1)  # Blanco por defecto
                
                # Renderizar según tipo de primitiva
                if self.primitiveType == TRIANGLES:
                    self.glTriangle(v1, v2, v3, model, face_idx)
                elif self.primitiveType == LINES:
                    self.glLine(v1, v2)
                    self.glLine(v2, v3)
                    self.glLine(v3, v1)
                elif self.primitiveType == POINTS:
                    self.glPoint(v1[0], v1[1], None, v1[2])
                    self.glPoint(v2[0], v2[1], None, v2[2])
                    self.glPoint(v3[0], v3[1], None, v3[2])

    def glDrawPrimitives(self, buffer, vertexOffset):
        """Dibuja primitivas desde un buffer"""
        if self.primitiveType == POINTS:
            for i in range(0, len(buffer), vertexOffset):
                x = buffer[i][0]
                y = buffer[i][1]
                z = buffer[i][2] if len(buffer[i]) > 2 else 0
                self.glPoint(x, y, None, z)

        elif self.primitiveType == LINES:
            for i in range(0, len(buffer), vertexOffset * 3):
                for j in range(3):
                    x0 = buffer[i + vertexOffset * j][0]
                    y0 = buffer[i + vertexOffset * j][1]
                    z0 = buffer[i + vertexOffset * j][2] if len(buffer[i + vertexOffset * j]) > 2 else 0

                    x1 = buffer[i + vertexOffset * ((j + 1) % 3)][0]
                    y1 = buffer[i + vertexOffset * ((j + 1) % 3)][1]
                    z1 = buffer[i + vertexOffset * ((j + 1) % 3)][2] if len(buffer[i + vertexOffset * ((j + 1) % 3)]) > 2 else 0

                    self.glLine([x0, y0, z0], [x1, y1, z1])

        elif self.primitiveType == TRIANGLES:
            for i in range(0, len(buffer), vertexOffset * 3):
                A = buffer[i + vertexOffset * 0]
                B = buffer[i + vertexOffset * 1]
                C = buffer[i + vertexOffset * 2]
                self.glTriangle(A, B, C)

    def glRenderZBuffer(self):
        """Renderiza el z-buffer como imagen en escala de grises"""
        # Encontrar rango de valores z
        min_z = float('inf')
        max_z = float('-inf')
        
        for x in range(self.width):
            for y in range(self.height):
                if self.zBuffer[x][y] != float('inf'):
                    min_z = min(min_z, self.zBuffer[x][y])
                    max_z = max(max_z, self.zBuffer[x][y])
        
        if min_z == float('inf'):
            return  # No hay geometría
        
        z_range = max_z - min_z if max_z != min_z else 1
        
        # Renderizar z-buffer
        for x in range(self.width):
            for y in range(self.height):
                if self.zBuffer[x][y] != float('inf'):
                    normalized_z = (self.zBuffer[x][y] - min_z) / z_range
                    intensity = int(normalized_z * 255)
                    color = [intensity, intensity, intensity]
                    
                    self.screen.set_at((x, self.height - 1 - y), color)
                    self.frameBuffer[x][y] = color