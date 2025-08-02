class OBJ:
    def __init__(self, filename):
        self.vertices = []
        self.texCoords = []
        self.faces = []
        self.load(filename)
        
    def load(self, filename):
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex = list(map(float, line.strip().split()[1:4]))
                    self.vertices.extend(vertex)
                elif line.startswith('vt '):
                    texCoord = list(map(float, line.strip().split()[1:3]))
                    self.texCoords.extend(texCoord)
                elif line.startswith('f '):
                    face_vertices = line.strip().split()[1:]
                    if len(face_vertices) == 3: 
                        face = []
                        tex_face = []
                        for v in face_vertices:
                            parts = v.split('/')
                            vertex_index = int(parts[0]) - 1
                            tex_index = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1
                            face.append(vertex_index)
                            tex_face.append(tex_index)
                        self.faces.append((face, tex_face))
                    elif len(face_vertices) > 3: 
                        for i in range(1, len(face_vertices)-1):
                            face = []
                            tex_face = []
                            for idx in [0, i, i+1]:
                                parts = face_vertices[idx].split('/')
                                vertex_index = int(parts[0]) - 1
                                tex_index = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else -1
                                face.append(vertex_index)
                                tex_face.append(tex_index)
                            self.faces.append((face, tex_face))