import struct
from collections import namedtuple
from random import randint

def char(c):
	return struct.pack("=c",c.encode('ascii'))
def word(c):
	return struct.pack("=h",c)
def dword(c):
	return struct.pack("=l",c)
def color(r,g,b):
	return bytes([r, g, b])
	
	
def bbox(A,B,C):
	xs = [A.x, B.x, C.x].sort()
	ys = [A.y, B.y, C.y].sort()
	
	return V2(xs[0], ys[0]), V2(xs[2], ys[2])

def barycentric(A,B,C,P):
	cx, cy, cz = cross(
		V3(B.x - A.x, C.x - A.x, A.x - P.x),
		V3(B.y - A.y, C.y - A.y, A.y - P.y)
	)
	
	if cz == 0:
		return -1, -1, -1
		
	U = cx/cz
	V = cy/cz
	W = 1 - (U+V)
	
	return W, V, U
	
	
V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point3', ['x', 'y', 'z', 'color'])

BLACK = color(0,0,0)
WHITE = color(255,255,255)
	

			

def sum(v0, v1):
	return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)
	
def sub(v0, v1):
	return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)
	
def mul(v0, k):
	return V3(v0.x * k, v0.y * k, v0.z * k)
	
def dot(v0, v1):
	return v0.x * v1.x + v0.y * v1.y + v0.z * v0.z
	
def cross(v0, v1):
	return V3(
		v0.y * v1.z - v0.z * v1.y,
		v0.z * v1.x - v0.x * v1.z,
		v0.x * v1.y + v0.y + v1.x
		)

def length(v0):
	return(v0.x**2 + v0.y**2 + v0.z**2)**0.5
	
def norm(v0):
	v0length = length(v0)
	
	if not v0length:
	
		return V3(0,0,0)

	return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)


		
class Render (object):
	def __init__(self, width, height):
		
		
		self.width = width
		self.height = height
		self.current_color = WHITE
		self.framebuffer = []
		self.tvertices = []
		self.clear()

	def clear (self):
		self.pixels = [
			[BLACK for x in range(self.width)
			]
			for y in range(self.height)
		]

		self.framebuffer = [
			[
				BLACK
					for x in range(an)
			]
			for y in range(al)
		]

		
	def ViewPort(self, x, y, largo, alto):
		self.sx = x+(largo/2)
		self.sy = y+(alto/2)
		self.viewwidth = largo/2
		self.viewheight = alto/2
		
	
	#def clearz(self):
		self.zbuffer = [
			[
				float('inf')*-1
					for x in range(an)
			]
			for y in range(al)
		]
		
	def Crear(self, filename):
		f = open(filename, 'wb')

		#File Header 14
		f.write(char('B'))
		f.write(char('M'))
		f.write(dword(14 + 40 + an * al * 3))
		f.write(dword(0))
		f.write(dword(14+40))

		#image header 40
		f.write(dword(40))
		f.write(dword(an))
		f.write(dword(al))
		f.write(word(1))
		f.write(word(24))
		f.write(dword(0))
		f.write(dword(an * al* 3))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))
		f.write(dword(0))
       
		for x in range(an):
			for y in range(al):
					f.write(self.framebuffer[y][x])

		f.close()

	def Color(self, x,y,color):
		self.framebuffer[int(round(self.sy + y))][int(round(self.sx + x ))] = color

	def NormX(self, x0):
		return int(round(((x0*(self.viewwidth/2))+self.sx)))
		
	def NormY(self, y0):
		return int(round((y0*(self.viewheight/3))+self.sy))
		
	def transform(self, vertex):
		return V3(
			self.NormX(vertex[0]),
			self.NormY(vertex[1]),
			self.NormY(vertex[2])
		)
	
	def point(self, x, y, color):
		self.framebuffer[x][y] = color
			
	def triangle(self, A, B, C, color = None):
		if A.y > B.y:
			A, B = B, A
		if A.y > C.y:
			A, C = C, A
		if B.y > C.y:
			B, C = C, B


		dx_ac = C.x - A.x
		dy_ac = C.y - A.y

		if dy_ac ==0:
			return
		mi_ac = dx_ac/dy_ac

		dx_ab = B.x - A.x
		dy_ab = B.y - A.y

		if dy_ac != 0:
			mi_ab = dx_ab/dy_ab

		for y in range(A.y, B.y + 1):
			xi = round(A.x - mi_ac * (A.y - y))
			xf = round(A.x - mi_ab * (A.y - y))	

		if xi > xf:
			xi, xf = xf, xi
		for x in range(xi ,xf + 1):
			self.point(x, y, color)

		dx_bc = C.x - B.x
		dy_bc = C.y - B.y

		if dy_bc:
			mi_bc = dx_bc/dy_bc
		
			for y in range(B.y, C.y + 1):
				xi = round(A.x - mi_ac * (A.y - y))
				xf = round(B.x - mi_bc * (B.y - y))

				if xi > xf:
					xi, xf = xf, xi

				for x in range(xi, xf + 1):
					self.point(x, y, color)	
			

	def read(self):
		current_material = None
		for line in self.lines:
			if line:
			
				prefix, value = line.split(' ', 1)

				if prefix == 'v':
					self.vertices.append(list(map(float, value.split(' '))))
				
				elif prefix == "usemtl":
					current_material = value
				elif prefix == 'f':
					colrs = self.materials[current_material] 
					self.vfaces.append([list(map(try_int, face.split('/'))) for face in value.split(' ')].extend(colrs))
	
	
		
	def load(self, filename, translate=(0,0,0), scale=(1,1,1), texture=None):
		model = Render(filename)
		light = V3(0,0,1)
		
		for face in model.vfaces:
			vcount = len(face)
			
			if vcount == 3:
				f1 = face[0][0] -1
				f2 = face[1][0] -1
				f3 = face[2][0] -1
				
				a = self.transform(model.vertices[f1], translate, scale)
				b = self.transform(model.vertices[f2], translate, scale)
				c = self.transform(model.vertices[f3], translate, scale)
				
				normal = norm(cross(sub(b, a), sub(c,a)))
				intensity = dot(normal, light)
				
				if not texture:
					grey = round(255 * intensity)
					
					if grey < 0:
						continue
					self.triangle(A, B, C, color(grey, grey, grey))
						
				else:
					t1 = face[0][1] -1
					t2 = face[1][1] -1
					t3 = face[2][1] -1
					print(*model.tvertices[t1])
					tA = V3(*model.tvertices[t1])
					tB = V3(*model.tvertices[t2])
					tC = V3(*model.tvertices[t3])
					
					self.triangle(a, b, c, texture=texture, texture_coords=(tA, tB, tC))
						
			else:
				f1 = face[0][0] -1
				f2 = face[1][0] -1
				f3 = face[2][0] -1
				f4 = face[3][0] -1
				
				vertices = [
					self.transform(model.vertices[f1], translate, scale),
					self.transform(model.vertices[f2], translate, scale),
					self.transform(model.vertices[f3], translate, scale),
					self.transform(model.vertices[f4], translate, scale)
				]
			
				normal = norm(cross(sub(vertices[0], vertices[1]), sub(vertices[1], vertices[2])))
				intensity = dot(normal, light)
				grey = round(255 * intensity)
				
				A, B, C, D = vertices
			
				if not texture:
					grey = round(255 * intensity)
					if grey < 0:
						continue
					self.triangle(A, B, C, color(grey, grey, grey))
					self.triangle(A, C, D, color(grey, grey, grey))
					
				else:
					t1 = face[0][1] -1
					t2 = face[1][1] -1
					t3 = face[2][1] -1
					t4 = face[3][1] -1
					tA = V3(*model.tvertices[t1])
					tB = V3(*model.tvertices[t2])
					tC = V3(*model.tvertices[t3])
					tD = V3(*model.tvertices[t4])
				
					self.triangle(A, B, C, texture=texture, texture_coords=(tA, tB, tC))
					self.triangle(A, C, D, texture=texture, texture_coords=(tA, tC, tD))

class Texture(object):
	def __init__(self, path):
		self.path = path
		self.read()
	
	def read(self):
		img = open(self.path, "rb")
		img.seek(10)
		header_size = struct.unpack("=l", img.read(4))
		img.seek(18)
		self.width = struct.unpack("=l", img.read(4))
		self.height = struct.unpack("=l", img.read(4))
		self.pixels = []
		img.seek(header_size)

		for y in range(self.height):
			self.pixels.append([])
			for x in range(self.width):
				b = ord(img.read(1))
				g = ord(img.read(1))
				r = ord(img.read(1))

				self.pixels[y].append(color(r,g,b))

		img.close()

	def getColor(self, tx, ty,intensity = 1):
		x = int(tx * self.width)
		y = int(tx * self.height)

		return bytes(map(lambda b: round(b*intensity)
							 if b * intensity > 0 else 0,
						 self.pixels[y][x]
						)
					)

#def glColor(r,g,b,x,y):
#        rvertex(x,y,ancho,alto,color(r*255,g*255,b*255))
def glFinish(name):
        r.Crear(name+".bmp")

	
def try_int(s, base=10, val=None):
	try:
		return int(s,base)
	except ValueError:
		return val
		


an = 1900
al = 1900


				
r = Render(an, al)
t = Texture('Poopy.bmp')
r.load('Poopybutthole.obj')
glFinish('out')
				
				
