import pygame, sys, math, os

def rotate2d(pos,rad):
	x,y=pos
	s,c=math.sin(rad),math.cos(rad)
	return x*c-y*s,y*c+x*s

class Cam(object):
	def __init__(self, pos=(0,0,0), rot=(0,0)):
		self.pos = list(pos)
		self.rot = list(rot)

	def events(self,event):
		if event.type == pygame.MOUSEMOTION:
			x, y = event.rel
			x/=500.0
			y/=500.0
			self.rot[0]+=y
			self.rot[1]+=x

	def update(self, key):
		s = 1

		if key[pygame.K_q]: self.pos[1]+=s
		if key[pygame.K_e]: self.pos[1]-=s

		x,y = s*math.sin(self.rot[1]),s*math.cos(self.rot[1])

		if key[pygame.K_w]: 
			self.pos[0]+=x
			self.pos[2]+=y

		if key[pygame.K_s]:
			self.pos[0]-=x
			self.pos[2]-=y

		if key[pygame.K_a]:
			self.pos[0]-=y
			self.pos[2]+=x
		if key[pygame.K_d]:
			self.pos[0]+=y
			self.pos[2]-=x


class Cube(object):
	vertices = (-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)
	edges = (0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)
	faces = (0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)
	colors = (0,255,255),(255,0,255),(255,0,0),(0,255,0),(0,0,255),(255,255,0)
	center = [0,0,0]

	def __init__(self,pos=(0,0,0)):
		x, y, z = pos
		self.verts = [(x+X/2.0,y+Y/2.0,z+Z/2.0) for X,Y,Z in self.vertices]

		self.initialvert = self.verts

		self.cent = []

		for i in self.center:
			self.cent.append(i+pos[i]/2.0)

	def update(self,key):

		vert_list = []
		vert_list += [list(vert) for vert in self.verts]
		rad = 0.1

		if key[pygame.K_LEFT]:
			self.cent[0] -= 1
			for vert in vert_list:
				vert[0] -= 1

		if key[pygame.K_RIGHT]:
			self.cent[0] += 1
			for vert in vert_list:
				vert[0] += 1

		if key[pygame.K_UP]:
			self.cent[1] -= 1
			for vert in vert_list:
				vert[1] -= 1

		if key[pygame.K_DOWN]:
			self.cent[1] += 1
			for vert in vert_list:
				vert[1] += 1


		if key[pygame.K_m]:

			Xdiff = self.center[0] - self.cent[0]
			Ydiff = self.center[1] - self.cent[1]

			for vert in vert_list:

				x = vert[0] + Xdiff
				y = vert[1] + Ydiff

				vert[0] = self.center[0] + (x-self.center[0])*math.cos(rad) - (y-self.center[1])*math.sin(rad)
				vert[1] = self.center[1] + (x-self.center[0])*math.sin(rad) + (y-self.center[1])*math.cos(rad)

				vert[0] -= Xdiff
				vert[1] -= Ydiff


		self.verts = []
		self.verts += [tuple(vert) for vert in vert_list]

pygame.init()
w, h = 800, 600
cx, cy = w/2.0, h/2.0
os.environ['SDL_VIDEO_CENTERED'] = '1'
fov = min(w,h)
screen = pygame.display.set_mode((w,h))
clock = pygame.time.Clock()
FPS = 30

cubes = [Cube((0,0,0)), Cube((2,0,0)), Cube((-2,0,0))]

cam = Cam((0,0,-5))

pygame.event.get()
pygame.mouse.get_rel()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

while True:

	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			pygame.quit()
			sys.exit()
		cam.events(event)

	screen.fill((0,0,0))

	face_list = []
	face_color = []
	depth = []

	for obj in cubes:

		vert_list = []
		screen_coords = []
		for x,y,z in obj.verts:
			x-=cam.pos[0]
			y-=cam.pos[1]
			z-=cam.pos[2]

			x,z = rotate2d((x,z),cam.rot[1])
			y,z = rotate2d((y,z),cam.rot[0])
			vert_list += [(x,y,z)]

			#perspectiva
			f = fov/float(z)
			x, y = x*f, y*f
			screen_coords+=[(cx+int(x), cy+int(y))]

		for f in range(len(obj.faces)):
			face = obj.faces[f]

			on_screen = False
			for i in face:
				x, y = screen_coords[i]
				if vert_list[i][2]>0 and x>0 and x+w and y>0 and h>y:
					on_screen = True
					break

			if on_screen:
				coords = [screen_coords[i] for i in face]
				face_list += [coords]
				face_color += [obj.colors[f]]

				depth += [sum(sum(vert_list[j][i] for j in face)**2 for i in range(3))]

	order = sorted(range(len(face_list)), key=lambda i: depth[i],reverse=True)

	for i in order:
		try: 
			pygame.draw.polygon(screen,face_color[i],face_list[i])
		except:
			pass

	pygame.display.flip()
	clock.tick(FPS)

	key = pygame.key.get_pressed()
	cam.update(key)
	cubes[0].update(key)