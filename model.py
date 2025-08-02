import random
import numpy as np
from PIL import Image
from MathLib import *
import time
import math

class Model:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.colors = []
        self.texture_coords = []    
        self.texture = None         
        self.face_uvs = []          
        
        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        
        self.vertexShader = None
    
    def GetModelMatrix(self):
        translateMat = TranslationMatrix(self.translation[0], self.translation[1], self.translation[2])
        rotateMat = RotationMatrix(self.rotation[0], self.rotation[1], self.rotation[2])
        scaleMat = ScaleMatrix(self.scale[0], self.scale[1], self.scale[2])
        
        return translateMat * rotateMat * scaleMat
    
    def load_texture(self, filename):
        """Cargar textura desde archivo (BMP, PNG, JPG)"""
        try:
            self.texture = Image.open(filename)
            if self.texture.mode != 'RGB':
                self.texture = self.texture.convert('RGB')
            print(f"Textura cargada: {filename} ({self.texture.width}x{self.texture.height})")
        except Exception as e:
            print(f"Error cargando textura {filename}: {e}")
            self._create_procedural_texture()
    
    def _create_procedural_texture(self, size=512):
        """Crear textura procedural de fallback"""
        self.texture = Image.new('RGB', (size, size))
        pixels = self.texture.load()
        
        # Patrón de ajedrez
        for x in range(size):
            for y in range(size):
                if (x // 32 + y // 32) % 2 == 0:
                    pixels[x, y] = (255, 0, 0)  # Rojo
                else:
                    pixels[x, y] = (255, 255, 255)  # Blanco
        
        print(f"Textura procedural creada: {size}x{size}")
    
    def get_texture_color(self, u, v):
        """Obtener color de la textura en coordenadas UV (0-1)"""
        if not self.texture:
            return [0.8, 0.8, 0.8]  # Gris claro si no hay textura
        
        u = u % 1.0
        v = (1 - v) % 1.0  # Flip vertical
        
        x = int(u * (self.texture.width - 1))
        y = int(v * (self.texture.height - 1))
        
        x = max(0, min(self.texture.width - 1, x))
        y = max(0, min(self.texture.height - 1, y))
        
        r, g, b = self.texture.getpixel((x, y))
        return [r / 255.0, g / 255.0, b / 255.0]
    
    def load_obj(self, filename):
        """Cargar modelo desde archivo .obj"""
        self.vertices = []
        self.faces = []
        self.texture_coords = []
        self.face_uvs = []
        
        vertex_list = []
        uv_list = []
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    if line.startswith('v '):
                        parts = line.split()
                        vertex_list.append([float(parts[1]), float(parts[2]), float(parts[3])])
                        
                    elif line.startswith('vt '):
                        parts = line.split()
                        uv_list.append([float(parts[1]), float(parts[2])])
                        
                    elif line.startswith('f '):
                        face_vertices = []
                        face_uvs = []
                        
                        for vertex in line.split()[1:]:
                            indices = vertex.split('/')
                            vertex_index = int(indices[0]) - 1
                            face_vertices.append(vertex_index)
                            
                            if len(indices) > 1 and indices[1]:
                                uv_index = int(indices[1]) - 1
                                face_uvs.append(uv_index)
                            else:
                                face_uvs.append(0)
                        
                        # Triangular caras con más de 3 vértices
                        for i in range(1, len(face_vertices) - 1):
                            self.faces.append([face_vertices[0], face_vertices[i], face_vertices[i + 1]])
                            self.face_uvs.append([face_uvs[0], face_uvs[i], face_uvs[i + 1]])
            
            # Aplanar vértices
            self.vertices = []
            for vertex in vertex_list:
                self.vertices.extend(vertex)
            
            self.texture_coords = uv_list
            
            # Generar colores aleatorios si no hay textura
            if not self.texture:
                self.colors = []
                for _ in self.faces:
                    self.colors.append([random.random(), random.random(), random.random()])
            
            print(f"Modelo cargado: {filename}")
            print(f"  Vértices: {len(vertex_list)}")
            print(f"  Caras: {len(self.faces)}")
            print(f"  UVs: {len(self.texture_coords)}")
            
        except Exception as e:
            print(f"Error cargando modelo {filename}: {e}")
    
    def scale_to_fit(self, target_size=2.0):
        """Escalar modelo para que quepa en un cubo de tamaño target_size"""
        if not self.vertices:
            return
            
        # Calcular bounding box
        xs = [self.vertices[i] for i in range(0, len(self.vertices), 3)]
        ys = [self.vertices[i + 1] for i in range(0, len(self.vertices), 3)]
        zs = [self.vertices[i + 2] for i in range(0, len(self.vertices), 3)]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        
        max_size = max(size_x, size_y, size_z)
        scale_factor = target_size / max_size if max_size > 0 else 1
        
        self.scale = [scale_factor, scale_factor, scale_factor]
        
        # Centrar en origen
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2
        
        self.translation = [
            -center_x * scale_factor,
            -center_y * scale_factor,
            -center_z * scale_factor
        ]
        
        print(f"Modelo escalado: factor={scale_factor:.2f}")