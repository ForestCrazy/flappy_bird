import pygame
from pygame.locals import *
from tkinter import *
from tkinter import messagebox
from tkinter import font
import random
import os.path

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colours
white = (255, 255, 255)
dark = (0, 0, 0)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
font_def = pygame.font.SysFont("Angsana New",24)
player_name = None

#load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def reset_game():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

def text_objects(text, font):
    textSurface = font.render(text, True, dark)
    return textSurface, textSurface.get_rect()

def update_score(player_name, score):
	current_score = 0
	# if os.path.isfile('score.txt'):
	# 	l = open('score.txt')
	# 	open('score.txt', 'w').close()
	# 	with open('score.txt', 'a') as f:
	# 		for line in l:
	# 			if not player_name in line:
	# 				f.write(line)
	# 			else:
	# 				current_score = int(line.split(" ")[1])
	# print(current_score)
	# if score > current_score:
	# 	if os.path.isfile('score.txt'):
	# 		with open('score.txt', 'a') as f:
	# 			f.write(player_name + " " + str(score) + "\n")
	# 	else:
	# 		with open('score.txt', 'w+') as f:
	# 			f.write(player_name + ' ' + str(score) + '\n')
	# else:
	# 	if os.path.isfile('score.txt'):
	# 		with open('score.txt', 'a') as f:
	# 			f.write(player_name + " " + str(current_score) + "\n")
	# 	else:
	# 		with open('score.txt', 'w+') as f:
	# 			f.write(player_name + ' ' + str(current_score) + '\n')
	if os.path.isfile('score.txt'):
		with open('score.txt', 'r', encoding="utf-8") as file:
			# read a list of lines into data
			data = file.readlines()

		open('score.txt', 'w', encoding="utf-8").close()
		with open('score.txt', 'a', encoding="utf-8") as f:
			for line in data:
				if not player_name in line:
					f.write(line)
				else:
					current_score = int(line.split(" ")[1])
		if score > current_score:
			with open('score.txt', 'a', encoding="utf-8") as f:
				f.write(player_name + " " + str(score) + "\n")
		else:
			with open('score.txt', 'a', encoding="utf-8") as f:
				f.write(player_name + " " + str(current_score) + "\n")
	else:
		with open('score.txt', 'w+', encoding="utf-8") as f:
			f.write(player_name + ' ' + str(score) + '\n')

def get_score(player_name):
	with open('score.txt', 'r', encoding="utf-8") as f:
		for line in f:
			if player_name in line:
				return int(line.split(" ")[0])
	return 0

def reset_score():
	if os.path.isfile('score.txt'):
		open('score.txt', 'w', encoding="utf-8").close()

class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range (1, 4):
			img = pygame.image.load(f"img/bird{num}.png")
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False

	def update(self):

		if flying == True:
			#apply gravity
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False:
			#jump
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.vel = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#handle the animation
			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]


			#rotate the bird
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			#point the bird at the ground
			self.image = pygame.transform.rotate(self.images[self.index], -90)



class Pipe(pygame.sprite.Sprite):

	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/pipe.png")
		self.rect = self.image.get_rect()
		#position variable determines if the pipe is coming from the bottom or top
		#position 1 is from the top, -1 is from the bottom
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		elif position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]


	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

class ButtonHome():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font_def.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = font_def.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

#load button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()

#create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)
exit_button_game = ButtonHome(screen_width // 2 - 34, screen_height // 2 - 30, exit_img, 0.33)

run = True
home = True
while run:

	if home:
		#create button instances
		start_button = ButtonHome(screen_width // 2 - 250, screen_height // 2 - 100, start_img, 0.5)
		exit_button = ButtonHome(screen_width // 2 + 100, screen_height // 2 - 100, exit_img, 0.5)
		tx = int(screen_width // 2) - 50
		ty = int(screen_height // 2)
		input_box1 = InputBox(screen_width // 2 - 110, screen_height // 2 - 180, 140, 32)
		input_boxes = [input_box1]
		lvx = int(screen_width // 2) - 72
		lvy = int(screen_height // 2) + 100
		
		#game loop
		while home:

			screen.fill((202, 228, 241))

			if start_button.draw(screen):
				player_name = input_box1.text
				home = False
				game_over = False
				score = reset_game()
			if exit_button.draw(screen):
				exit()
			
			# rendering a text written in
			# this font
			text = pygame.font.SysFont("Angsana New",35).render('วิธีการเล่น', True, white)
			pygame.draw.rect(screen, (170,170,170),[tx - 24,ty + 2,140,40])
			screen.blit(text , (tx,ty))
			listview = pygame.font.SysFont("Angsana New", 35).render('ประวัติการเล่น', True, white)
			pygame.draw.rect(screen, (170,170,170),[lvx - 24,lvy + 2,185,45])
			screen.blit(listview , (lvx,lvy))
			draw_text("รีเซ็ตคะแนน", font_def, dark, lvx + 20, lvy + 50)
			draw_text("Insert Player Name", font_def, dark, screen_width // 2 - 110, screen_height // 2 - 210)
			for box in input_boxes:
				box.update()

			for box in input_boxes:
				box.draw(screen)
			
			#event handler
			for event in pygame.event.get():
				#quit game
				if event.type == pygame.QUIT:
					home = False
					run = False
				if event.type== pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse=pygame.mouse.get_pos()
					if mouse[0]in range ( tx-24,tx+130) and  mouse[1]in range ( ty-2,ty+80):
						master = Tk()

						w = Label(master, text="""> กดปุ่ม คลิ๊กซ้าย เพื่อให้ตัวละครกระโดด \n> คุณได้จะได้ 1 คะแนนต่อการผ่าน 1 ท่อ \n> เกมจะจบลงในเมื่อตัวละครตกพื้น หรือ ชนท่อ""", font=('Arial', 20))
						w.pack()

						mainloop()
				if event.type== pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse=pygame.mouse.get_pos()
					if mouse[0]in range ( lvx-24,lvx+130) and  mouse[1]in range ( lvy-2,lvy+50):
						# root = tk.Tk()
						# mlb = treectrl.MultiListbox(root)
						# mlb.pack(side='top', fill='both', expand=1)
						# tk.Button(root, text='Close', command=root.quit).pack(side='top', pady=5)
						# mlb.focus_set()
						# mlb.configure(selectcmd=select_cmd, selectmode='extended')
						# mlb.config(columns=('Column 1', 'Column 2'))
						# if os.path.isfile('score.txt'):
						# 	with open('score.txt', 'r') as f:
						# 		for line in f:
						# 			mlb.insert('end', line.split(" "))
						root = Tk()
						root.resizable(width=False, height=False)
						root.geometry('{}x{}'.format(150, 400))
						listbox = Listbox(root, width=140, height=400, font=('Angsana New', 20))
						listbox.pack()
						# box = tk.Listbox(root, selectmode=tk.MULTIPLE, height=4)
						header = ["Name", "Score"]
						listbox.insert('end', "{:<8} {:>8}".format(*header, sp=" " * 6))
						if os.path.isfile('score.txt'):
							with open('score.txt', 'r', encoding="utf-8") as f:
								for line in f:
									listbox.insert('end', "{:<8} {:>8}".format(*line.split(" "), sp=" " * 12))
								# box.pack()
						root.mainloop()
					if mouse[0]in range ( lvx+20,lvx+110) and  mouse[1]in range ( lvy+50,lvy+80):
						print("c")
						reset_score()
						
				for box in input_boxes:
					box.handle_event(event)

			pygame.display.update()

	clock.tick(fps)

	#draw background
	screen.blit(bg, (0,0))

	pipe_group.draw(screen)
	bird_group.draw(screen)
	bird_group.update()

	#draw and scroll the ground
	screen.blit(ground_img, (ground_scroll, 768))

	#check the score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False
	draw_text(str(score), font, white, int(screen_width / 2), 20)


	#look for collision
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True
	#once the bird has hit the ground it's game over and no longer flying
	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False


	if flying == True and game_over == False:
		#generate new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-80, 80)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		pipe_group.update()

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0
	

	#check for game over and reset
	if game_over == True:
		if button.draw():
			update_score(player_name, score)
			game_over = False
			score = reset_game()
		if exit_button_game.draw(screen):
			update_score(player_name, score)
			home = True


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

pygame.quit()