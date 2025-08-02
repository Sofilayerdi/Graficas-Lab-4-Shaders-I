import pygame
from gl import Renderer, POINTS, LINES, TRIANGLES
from model import Model
from shaders import rainbowFragmentShader, vertexShader, fragmentShader
from Camera import Camera

class GraphicsEngine:
    def __init__(self, width=800, height=600):
        # Inicialización de pygame
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
        pygame.display.set_caption("3D Renderer")
        self.clock = pygame.time.Clock()
        
        # Configuración del renderizador
        self.renderer = Renderer(self.screen)
        self.renderer.primitiveType = TRIANGLES
        
        # Configuración de cámara
        self.camera = Camera(width, height)
        self.renderer.set_camera(self.camera)
        
        # Modelo 3D
        self.model = Model()
        self.load_model("Penguin.obj", "PenguinTex.bmp")
        
        # Configuración inicial del modelo
        self.model.translation = [0, -1, 0]
        self.model.scale = [0.5, 0.5, 0.5]
        self.model.vertexShader = vertexShader
        self.model.fragmentShader = rainbowFragmentShader  
        
        self.renderer.models.append(self.model)
        
        self.renderer.models.append(self.model)
        
        # Control de tiempo
        self.deltaTime = 0
        self.isRunning = True
    
    def load_model(self, obj_file, texture_file):
        """Carga un modelo OBJ y su textura"""
        try:
            # Cargar modelo (versión simplificada)
            with open(obj_file) as f:
                vertices = []
                tex_coords = []
                faces = []
                
                for line in f:
                    if line.startswith('v '):
                        vertices.extend([float(x) for x in line.strip().split()[1:]])
                    elif line.startswith('vt '):
                        tex_coords.extend([float(x) for x in line.strip().split()[1:]])
                    elif line.startswith('f '):
                        face_data = [x.split('/') for x in line.strip().split()[1:]]
                        faces.append((
                            [int(x[0])-1 for x in face_data],  # Índices de vértices
                            [int(x[1])-1 if len(x) > 1 and x[1] else -1 for x in face_data]  # Índices de textura
                        ))
                
                # Procesar caras y convertir a triángulos
                for face, tex_face in faces:
                    for i in range(1, len(face)-1):
                        # Triángulo 0, i, i+1
                        for idx in [0, i, i+1]:
                            self.model.vertices.extend(vertices[face[idx]*3 : face[idx]*3+3])
                            if tex_face[idx] != -1 and tex_face[idx] < len(tex_coords)//2:
                                self.model.texCoords.extend(tex_coords[tex_face[idx]*2 : tex_face[idx]*2+2])
                            else:
                                self.model.texCoords.extend([0, 0])
            
            # Cargar textura
            self.model.load_texture(texture_file)
            
            print(f"Modelo cargado: {len(self.model.vertices)//3} vértices, {len(faces)} caras")
            
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            # Crear un cubo simple como fallback
            self.create_fallback_model()
    
    def create_fallback_model(self):
        """Crea un modelo simple en caso de error"""
        # Vértices de un cubo
        vertices = [
            -1,-1,-1, 1,-1,-1, 1,1,-1, -1,1,-1,
            -1,-1,1, 1,-1,1, 1,1,1, -1,1,1
        ]
        
        # Caras (triángulos)
        faces = [
            [0,1,2], [0,2,3], [4,5,6], [4,6,7],
            [0,4,7], [0,7,3], [1,5,6], [1,6,2],
            [0,1,5], [0,5,4], [3,2,6], [3,6,7]
        ]
        
        # Coordenadas de textura simples
        tex_coords = [0,0, 1,0, 1,1, 0,1] * 6
        
        self.model.vertices = []
        self.model.texCoords = []
        
        for face in faces:
            for idx in face:
                self.model.vertices.extend(vertices[idx*3 : idx*3+3])
                self.model.texCoords.extend(tex_coords[idx*2 : idx*2+2])
        
        # Textura procedural
        self.model.load_texture(None)
    
    def handle_events(self):
        """Maneja los eventos de entrada"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.renderer.primitiveType = POINTS
                    print("Modo: Puntos")
                elif event.key == pygame.K_2:
                    self.renderer.primitiveType = LINES
                    print("Modo: Líneas")
                elif event.key == pygame.K_3:
                    self.renderer.primitiveType = TRIANGLES
                    print("Modo: Triángulos")
                elif event.key == pygame.K_ESCAPE:
                    self.isRunning = False
    
    def update(self):
        """Actualiza la lógica del juego"""
        keys = pygame.key.get_pressed()
        
        # Movimiento de cámara
        move_speed = 3 * self.deltaTime
        if keys[pygame.K_w]:
            self.camera.move_forward(move_speed)
        if keys[pygame.K_s]:
            self.camera.move_forward(-move_speed)
        if keys[pygame.K_a]:
            self.camera.move_right(-move_speed)
        if keys[pygame.K_d]:
            self.camera.move_right(move_speed)
        if keys[pygame.K_q]:
            self.camera.move_up(move_speed)
        if keys[pygame.K_e]:
            self.camera.move_up(-move_speed)
        
        # Rotación del modelo
        rotate_speed = 45 * self.deltaTime
        if keys[pygame.K_LEFT]:
            self.model.rotation[1] -= rotate_speed
        if keys[pygame.K_RIGHT]:
            self.model.rotation[1] += rotate_speed
    
    def render(self):
        """Renderiza la escena"""
        self.renderer.glClear()
        self.renderer.glRender()
        pygame.display.flip()

    
    def run(self):
        """Bucle principal"""
        while self.isRunning:
            self.deltaTime = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update()
            self.render()
        
        pygame.quit()

if __name__ == "__main__":
    engine = GraphicsEngine()
    engine.run()