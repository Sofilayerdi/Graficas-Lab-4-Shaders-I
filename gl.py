from MathLib import barycentricCoords
from math import isclose, tan, pi
import numpy as np
from camera import Camera

POINTS = 0
LINES = 1
TRIANGLES = 2

class Renderer(object):
	def __init__(self, screen):
		self.screen = screen
		_, _, self.width, self.height = self.screen.get_rect()

		self.camera = Camera()
		self.glViewport(0,0, self.width, self.height)
		self.glProjection()

		self.glColor(1,1,1)
		self.glClearColor(0,0,0)

		self.glClear()

		self.primitiveType = TRIANGLES

		self.models = []

		self.activeModelMatrix = None
		self.activeVertexShader = None
		self.activeFragmentShader = None

		self.dirLight = [1,0,0]

	def glViewport(self, x, y, width, height):
		self.vpX = round(x)
		self.vpY = round(y)
		self.vpWidth = width
		self.vpHeight = height

		self.viewportMatrix = np.matrix([[width/2, 0, 0, x+width/2],
								   		[0, height/2, 0, y+height/2],
										[0, 0, 0.5, 0.5],
										[0, 0, 0, 1]])
		
	def glProjection(self, n = 0.1, f = 1000, fov = 60):
		aspectRatio = self.vpWidth / self.vpHeight
		fov *= pi/180 #a radianes
		t = tan(fov/2) * n
		r = t * aspectRatio

		self.projectionMatrix = np.matrix([[n/r, 0, 0, 0],
										 [0, n/t, 0, 0],
										 [0, 0, -(f+n)/(f-n), -2*f*n/(f-n)],
										 [0, 0, -1, 0]])


	def glClearColor(self, r, g, b):
		# 0 - 1
		r = min(1, max(0,r))
		g = min(1, max(0,g))
		b = min(1, max(0,b))

		self.clearColor = [r,g,b]


	def glColor(self, r, g, b):
		# 0 - 1
		r = min(1, max(0,r))
		g = min(1, max(0,g))
		b = min(1, max(0,b))

		self.currColor = [r,g,b]

	def glClear(self):
		color = [int(i * 255) for i in self.clearColor]
		self.screen.fill(color)

		self.frameBuffer = [[color for y in range(self.height)]
							for x in range(self.width)]
		
		self.zBuffer = [[float("inf") for y in range(self.height)]
				  		for x in range(self.width)]
	


	def glPoint(self, x, y, color):
    # Pygame empieza a renderizar desde la esquina
    # superior izquierda, hay que voltear la Y

		x = round(x)
		y = round(y)

		if (0 <= x < self.width) and (0 <= y < self.height):
			if color is None:
				color = self.currColor
			
			# Asegurarse de que el color esté en el formato correcto
			if isinstance(color, (list, tuple)) and len(color) >= 3:
				# Convertir de 0-1 a 0-255 si es necesario
				if all(isinstance(c, (int, float)) and 0 <= c <= 1 for c in color[:3]):
					color = [int(c * 255) for c in color[:3]]
				else:
					color = [int(max(0, min(255, c))) for c in color[:3]]
			else:
				color = [int(i * 255) for i in self.currColor]

			# Asegurar que solo tengamos 3 componentes RGB
			color = color[:3]
			
			self.screen.set_at((x, self.height - 1 - y), color)
			self.frameBuffer[x][y] = color


	def glLine(self, p0, p1, color = None):
		# Algoritmo de Lineas de Bresenham
		# y = mx + b

		x0 = p0[0]
		x1 = p1[0]
		y0 = p0[1]
		y1 = p1[1]

		# Si el punto 0 es igual que el punto 1, solamente dibujar un punto
		if x0 == x1 and y0 == y1:
			self.glPoint(x0, y0)
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

		dy = abs(y1 - y0)
		dx = abs(x1 - x0)

		offset = 0
		limit = 0.75
		m = dy / dx
		y = y0

		for x in range(round(x0), round(x1) + 1):
			if steep:
				self.glPoint(y, x, color or self.currColor)
			else:
				self.glPoint(x, y, color or self.currColor)

			offset += m

			if offset >= limit:
				if y0 < y1:
					y += 1
				else:
					y -= 1

				limit += 1


	def glTriangle(self, A, B, C):
		# Hay que asegurarse que los vertices entran en orden
		# A.y > B.y > C.y
		if A[1] < B[1]:
			A, B = B, A
		if A[1] < C[1]:
			A, C = C, A
		if B[1] < C[1]:
			B, C = C, B


		def flatBottom(vA, vB, vC):

			try:
				mBA = (vB[0] - vA[0]) / (vB[1] - vA[1])
				mCA = (vC[0] - vA[0]) / (vC[1] - vA[1])
			except:
				pass
			else:

				if vB[0] > vC[0]:
					vB, vC = vC, vB
					mBA, mCA = mCA, mBA

				x0 = vB[0]
				x1 = vC[0]

				for y in range(round(vB[1]), round(vA[1] + 1)):
					for x in range(round(x0), round(x1 + 1)):
						vP = [x, y]
						self.glDrawTrianglePoint(vA, vB, vC, vP)

					x0 += mBA
					x1 += mCA

		def flatTop(vA, vB, vC):
			try:
				mCA = (vC[0] - vA[0]) / (vC[1] - vA[1])
				mCB = (vC[0] - vB[0]) / (vC[1] - vB[1])

			except:
				pass
			else:

				if vA[0] > vB[0]:
					vA, vB = vB, vA
					mCA, mCB = mCB, mCA

				x0 = vA[0]
				x1 = vB[0]

				for y in range(round(vA[1]), round(vC[1] - 1), -1):
					for x in range(round(x0), round(x1 + 1)):
						vP = [x, y]
						self.glDrawTrianglePoint(vA, vB, vC, vP)

					x0 -= mCA
					x1 -= mCB


		if B[1] == C[1]:
			# Plano abajo
			flatBottom(A,B,C)

		elif A[1] == B[1]:
			# Plano arriba
			flatTop(A,B,C)

		else:
			# Irregular
			# Hay que dibujar ambos casos
			# Teorema del intercepto

			D = [ A[0] + ((B[1] - A[1]) / (C[1] - A[1])) * (C[0] - A[0]), B[1] ]

			u, v, w = barycentricCoords(A, B, C, D)
			for i in range(2, len(A)):
				D.append(u*A[2] + v*B[2] + w*C[2])

			flatBottom(A, B, D)
			flatTop(B, D, C)

	def glDrawTrianglePoint(self, A, B, C, P):
    
		x = P[0]
		y = P[1]

		# Si el punto no esta dentro de la ventana, lo descartamos
		if not(0 <= x < self.width) or not (0 <= y < self.height):
			return
		
		# Obtenemos las coordenadas baricentricas para el punto P
		bCoords = barycentricCoords(A, B, C, P)

		#Si son coordenadas invalidas, descarto pixel
		if bCoords == None:
			return
		
		u, v, w = bCoords

		if not isclose(u+v+w, 1.0):
			return

		z = u * A[2] + v * B[2] + w * C[2]

		# Si el valor de z para este punto es mayor que 
		# el valor guardado en el zBuffer, el pizel esta mas lejos
		#  entonces descarto el pixel

		if z >= self.zBuffer[x][y]:
			return
		
		self.zBuffer[x][y] = z

		color = None
		if self.activeFragmentShader:
			try:
				color = self.activeFragmentShader(verts = [A, B, C],
												bCoords = [u, v, w],
												pixelColor = self.currColor, 
												dirLight = self.dirLight)
			except Exception as e:
				print(f"Error in fragment shader: {e}")
				print(f"A = {A}, B = {B}, C = {C}")
				color = self.currColor

		# Validar y corregir el color si es necesario
		if color is None:
			color = self.currColor
		elif isinstance(color, (list, tuple)):
			# Asegurar que el color tenga exactamente 3 componentes
			if len(color) < 3:
				color = list(color) + [0] * (3 - len(color))
			elif len(color) > 3:
				color = color[:3]
			
			# Asegurar que los valores estén en rango 0-1
			color = [max(0, min(1, c)) if isinstance(c, (int, float)) else 0 for c in color]
		else:
			color = self.currColor

		self.glPoint(x, y, color)



	def glRender(self):
		for model in self.models:
			self.activeModelMatrix = model.GetModelMatrix()
			self.activeVertexShader = model.vertexShader
			self.activeFragmentShader = model.fragmentShader

			vertexBuffer = []
			triangle_index = 0
			
			# Calcular número de vértices (cada vértice tiene 3 componentes: x, y, z)
			vertex_count = len(model.vertices) // 3
			has_normals = hasattr(model, 'normals') and model.normals and (len(model.normals) >= len(model.vertices))

			# Procesar vértices de 3 en 3 para formar triángulos
			for i in range(0, vertex_count, 3):  
				for j in range(3):  # Para cada vértice del triángulo
					vertex_idx = i + j
					idx = vertex_idx * 3  # Índice en el array de vértices
					
					if idx + 2 >= len(model.vertices): 
						break
						
					# Extraer coordenadas del vértice
					x = model.vertices[idx]
					y = model.vertices[idx + 1]
					z = model.vertices[idx + 2]
					
					# Crear vértice
					vertex = [x, y, z]
					
					# Extraer normal si está disponible
					if has_normals and idx + 2 < len(model.normals):
						nx = model.normals[idx]
						ny = model.normals[idx + 1]
						nz = model.normals[idx + 2]
						normal = [nx, ny, nz]
					else:
						# Normal por defecto
						normal = [0, 0, 1]

					# Aplicar vertex shader si está disponible
					if self.activeVertexShader:
						# El vertex shader retorna (vt, nt) como tupla
						vt, nt = self.activeVertexShader(
							vertex,
							modelMatrix=self.activeModelMatrix,
							triangle_index=triangle_index,
							normal=normal,
							viewMatrix = self.camera.GetViewMatrix(),
							projectionMatrix = self.projectionMatrix,
							viewportMatrix = self.viewportMatrix)
						
						# Combinar posición transformada y normal transformada
						# Convertir nt de numpy array a lista si es necesario
						if hasattr(nt, 'tolist'):
							nt = nt.tolist()
						
						transformed_vertex = vt + nt
						
						for component in transformed_vertex:
							vertexBuffer.append(component)
					else:
						# Si no hay vertex shader, usar vértice original con normal
						vertex_with_normal = vertex + normal
						for component in vertex_with_normal:
							vertexBuffer.append(component)
				
				triangle_index += 1

			
			self.glDrawPrimitives(vertexBuffer, 6)



	def glDrawPrimitives(self, buffer, vertexOffset):
		if self.primitiveType == POINTS:
			for i in range(0, len(buffer), vertexOffset):
				x = buffer[i]
				y = buffer[i + 1]
				self.glPoint(x, y, None)

		elif self.primitiveType == LINES:
			for i in range(0, len(buffer), vertexOffset * 3):
				for j in range(3):
					x0 = buffer[i + vertexOffset * j + 0]
					y0 = buffer[i + vertexOffset * j + 1]
					
					x1 = buffer[i + vertexOffset * ((j + 1) % 3) + 0]
					y1 = buffer[i + vertexOffset * ((j + 1) % 3) + 1]

					self.glLine((x0, y0), (x1, y1))

		elif self.primitiveType == TRIANGLES:
			# Verificar que tenemos suficientes datos para al menos un triángulo
			if len(buffer) < vertexOffset * 3:
				print(f"Warning: Not enough data for triangle. Buffer size: {len(buffer)}, needed: {vertexOffset * 3}")
				return
				
			for i in range(0, len(buffer), vertexOffset * 3):
				# Verificar que no nos salgamos del buffer
				if i + vertexOffset * 3 > len(buffer):
					break
					
				# Extraer los tres vértices del triángulo
				A = [buffer[i + j + vertexOffset * 0] for j in range(vertexOffset)]
				B = [buffer[i + j + vertexOffset * 1] for j in range(vertexOffset)]
				C = [buffer[i + j + vertexOffset * 2] for j in range(vertexOffset)]

				# Validar que los vértices tengan al menos 3 componentes (x, y, z)
				if len(A) >= 3 and len(B) >= 3 and len(C) >= 3:
					self.glTriangle(A, B, C)
				else:
					print(f"Warning: Invalid vertex data. A={len(A)}, B={len(B)}, C={len(C)}")