import pygame
from pygame.locals import *
from pygame import mixer
import datetime
import os
import random

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.font.init()

mixer.init()
mixer.music.load(os.path.join('Assets', 'bensound-scifi.ogg'))
mixer.Channel(0).play(pygame.mixer.Sound(os.path.join('Assets', "bensound-scifi.ogg")), (-1))
mixer.Channel(0).set_volume(0.1)
mixer.music.play()

clock = pygame.time.Clock()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT),pygame.RESIZABLE)
pygame.display.set_caption("Space Invaders!")

# load images
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 50,50
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png")), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png")), (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))
PURPLE_SPACE_SHIP =  pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_purple.png")), (300, 300))

# Player ship
PLAYER_WIDTH, PLAYER_HEIGHT = 90, 81
YELLOW_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")), (PLAYER_WIDTH, PLAYER_HEIGHT))

# Lasers
#LASER_WIDTH, LASER_HEIGHT = 9, 40
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER =  pygame.transform.rotate(pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")), 180)
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.transform.rotate(pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")), 90)
PURPLE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-blue.png")), (WIDTH, HEIGHT))

# Load sounds
ENEMY_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Grenade+1.ogg'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Gun+Silencer.ogg'))
BULLET_FIRE_SOUND.set_volume(0.075)
LIVES_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'sfx_shieldDown.ogg'))
BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'bullet_hit.ogg'))
BULLET_HIT_SOUND.set_volume(2)
LEVEL_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'level-up.ogg'))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'explosion.ogg'))
EXPLOSION_SOUND.set_volume(0.5)

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y 
		self.img = img 
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel 

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 0)

	def collision(self, obj):
		return collide(obj, self)

class Ship:
	COOLDOWN = 15

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				BULLET_HIT_SOUND.play()
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter > self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x - 12 + (self.laser_img.get_width() / 2), self.y - self.laser_img.get_height() + 20, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img) #mask is used for collision
		self.max_health = health
		self.score = 0
		self.explosions = []

	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:		
			laser.move(vel)							#if laser exists, move it
			if laser.off_screen(HEIGHT):						#if laser is off screen, remove it
				self.lasers.remove(laser)
			else:
				for obj in objs:								#for each obj in objs list
					if laser.collision(obj):						#if laser collides with an obj, remove the laser
						if obj.color == "purple":
							obj.health -= 10	
							BULLET_HIT_SOUND.play()
							if laser in self.lasers:
								self.lasers.remove(laser)
						else:
							objs.remove(obj)
							EXPLOSION_SOUND.play()
							self.score += 10
							if laser in self.lasers:
								self.lasers.remove(laser)

class Enemy(Ship):
	COLOR_MAP = {
					"red": (RED_SPACE_SHIP, RED_LASER),
					"green": (GREEN_SPACE_SHIP, GREEN_LASER),
					"blue": (BLUE_SPACE_SHIP, BLUE_LASER),
					"purple": (PURPLE_SPACE_SHIP, PURPLE_LASER)
	}

	def __init__(self, x, y, color, health=200):
		super().__init__(x, y, health)
		self.color = color
		self.max_health = health
		self.ship_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel

	def draw(self, window):
		super().draw(window)
		self.healthbar(window)
	
	def shoot(self):
		if self.cool_down_counter == 0:
			if self.color == "purple":
				laser = Laser(random.randrange(self.x, self.x + PURPLE_SPACE_SHIP.get_width()), self.y + PURPLE_SPACE_SHIP.get_height(), self.laser_img)
				self.lasers.append(laser)
				self.cool_down_counter = 1
			else:	
				laser = Laser(self.x - 10 + (self.laser_img.get_width() / 2), self.y + self.laser_img.get_height(), self.laser_img)
				self.lasers.append(laser)
				self.cool_down_counter = 1

	def healthbar(self, window):
		if self.color == "purple":
			pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
			pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

def isprime(num):
    for n in range(2,int(num**0.5)+1):
        if num%n==0:
            return False
    return True

def main():
	run = True
	FPS = 50
	level = 0   #default 0, change for testing purposes
	lives = 5
	main_font = pygame.font.SysFont("console", 40)
	lost_font = pygame.font.SysFont("console", 80)
	
	enemies = []
	wave_length = 5
	boss_wave = 1

	enemy_vel = 1.5
	laser_vel = 10.5
	player_vel = 15
	
	blue_vel = 3.5
	red_vel = 0.75

	player = Player(WIDTH//2 - 70, 500)

	lost = False
	lost_count = 0	

	def redraw_window():
		WIN.blit(BG, (0,0))

		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
		level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
		score_label = main_font.render("Score: "+str(player.score), 1, (255,255,255))

		WIN.blit(lives_label, (20, 20))
		WIN.blit(level_label, (WIDTH - level_label.get_width() -  20, 20))
		WIN.blit(score_label, (WIDTH - score_label.get_width() - 20, level_label.get_height() + 40))

		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("Game Over.", 1, (255,255,255))
			WIN.blit(lost_label, (WIDTH / 2 -lost_label.get_width() / 2, 350))

		pygame.display.update()

	def paused():
		pause = True

		pause_label = main_font.render("Paused. Press P to resume.", 1, (255, 255, 255))
		WIN.blit(pause_label, (WIDTH / 2 - pause_label.get_width() / 2 , 350))
	    
		while pause:
			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					pygame.quit()
					quit()
				elif pygame.key.get_pressed()[pygame.K_p]:
					pause = False
                      

			pygame.display.update()
			clock.tick(15)

	while run == True:
		clock.tick(FPS)
		redraw_window()

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 2:
				run = False
			else:
				continue

		if len(enemies) == 0:
			level += 1
			if level == 1:
				for i in range(wave_length):
					enemy = Enemy(random.randrange(60, WIDTH-60), random.randrange(-1500, -10), "green")
					enemies.append(enemy)
			else:
				LEVEL_SOUND.play()
				if level == 2:
					wave_length += 5
					for i in range(wave_length):
						enemy = Enemy(random.randrange(60, WIDTH-60), random.randrange(-1500, -30), random.choice(["blue", "green"]))
						enemies.append(enemy)
				elif level == 3:
					enemy = Enemy(760, -300, "purple")
					enemies.append(enemy)
				elif level > 3 and isprime(level):
					enemy = Enemy(760, -300, "purple")
					enemies.append(enemy)
					boss_wave += 3
					for i in range(boss_wave):
						enemy = Enemy(random.randrange(60, WIDTH-60), random.randrange(-3000, -50), random.choice(["red", "blue", "green"]))
						enemies.append(enemy)
				else:	
					wave_length += 5
					for i in range(wave_length):
						# spawn enemies in random, offscreen locations
						enemy = Enemy(random.randrange(60, WIDTH-60), random.randrange(-3000, -50), random.choice(["red", "blue", "green"]))
						enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and player.x - player_vel > 0: #left
			player.x -= player_vel
		if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: #right
			player.x += player_vel
		if keys[pygame.K_UP] and player.y - player_vel > 0: # up
			player.y -= player_vel
		if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down + health bar height
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()
			BULLET_FIRE_SOUND.play()
		if keys[pygame.K_ESCAPE]:
			pause = True
			paused()
		if keys[pygame.K_s]:
			d = datetime.datetime.now()
			file_name = f'screenshot_{d:%Y-%m-%d}.png'
			pygame.image.save(WIN, file_name)

		for enemy in enemies[:]:
			if enemy.color == "purple":
				enemy.move(0.4)
				enemy.move_lasers(laser_vel, player)
				if random.randrange(0, 5 - (level//2)) == 1:
					enemy.shoot()
			elif enemy.color == "blue":
				enemy.move(blue_vel)
				enemy.move_lasers(laser_vel, player)
				if random.randrange(0, 180) == 1:
					enemy.shoot()
			elif enemy.color == "red":
				enemy.move(red_vel)
				enemy.move_lasers(laser_vel, player)
				if random.randrange(0, 40) == 1:
					enemy.shoot()
			else:
				enemy.move(enemy_vel)
				enemy.move_lasers(laser_vel, player)
				if random.randrange(0, 100) == 1:
					enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				ENEMY_HIT_SOUND.play()
				if enemy.color != "purple":
					enemies.remove(enemy)
			elif enemy.y + enemy.get_height() > HEIGHT:
				if enemy.color == "purple":
					lives = 0
					LIVES_HIT_SOUND.play()
				else:	
					lives -= 1
					enemies.remove(enemy)
					LIVES_HIT_SOUND.play()
			elif enemy.health == 0:
				player.score += 40
				enemies.remove(enemy)


		player.move_lasers(-laser_vel, enemies)

def main_menu():
	WIDTH, HEIGHT = 1920, 1080
	WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
	pygame.display.set_caption("Space Invaders!")
	BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-blue.png")), (WIDTH, HEIGHT))

	title_font = pygame.font.SysFont("console", 40)
	menu_font = pygame.font.SysFont("console", 70)

	run = True
	while run:
		clock.tick(60)
		WIN.blit(BG, (0,0))
		menu_label = menu_font.render("Start Menu", 1, (255,255,255))
		title_label = title_font.render("Press H to begin or Esc to quit.", 1, (255, 255, 255))
		WIN.blit(menu_label, (WIDTH / 2 - menu_label.get_width() / 2 , 50))
		WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))

		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_h:
					main()
				if event.key == pygame.K_ESCAPE:
					run = False

	pygame.quit()

main_menu()

