import numpy as np

class OBJ:
    def __init__(self, filename):
        self.vertices = []
        self.texcoords = []
        self.normals = []
        self.faces = []  # Cada cara almacenará (v, vt, vn)
        self.load(filename)
        
    def load(self, filename):
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):  # Vértices geométricos
                    vertex = list(map(float, line.strip().split()[1:4]))
                    self.vertices.extend(vertex)
                elif line.startswith('vn '):  # Normales
                    normal = list(map(float, line.strip().split()[1:4]))
                    self.normals.extend(normal)
                elif line.startswith('f '):  # Caras
                    face_vertices = line.strip().split()[1:]
                    if len(face_vertices) == 3:  # Triángulos
                        face = []
                        for v in face_vertices:
                            parts = v.split('/')
                            vertex_index = int(parts[0]) - 1  # v
                            normal_index = int(parts[2]) - 1 if len(parts) > 2 and parts[2] else None  # vn
                            face.append((vertex_index, normal_index))
                        self.faces.append(face)
                    elif len(face_vertices) > 3:  # Polígonos (se triangulan)
                        for i in range(1, len(face_vertices)-1):
                            face = [
                                (int(face_vertices[0].split('/')[0]) - 1, int(face_vertices[0].split('/')[2]) - 1 if len(face_vertices[0].split('/')) > 2 else None),
                                (int(face_vertices[i].split('/')[0]) - 1, int(face_vertices[i].split('/')[2]) - 1 if len(face_vertices[i].split('/')) > 2 else None),
                                (int(face_vertices[i+1].split('/')[0]) - 1, int(face_vertices[i+1].split('/')[2]) - 1 if len(face_vertices[i+1].split('/')) > 2 else None)
                            ]
                            self.faces.append(face)