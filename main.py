import random
import pygame
import pygame.sprite

clock = pygame.time.Clock()

global screen
global leftEdgeOffset
global rightEdgeOffset
global enemyBullets
global enemies

class Object(pygame.sprite.Sprite):
	def __init__(self, sprite : pygame.Surface, xPos : int, yPos : int) -> None:
		self.image = sprite
		self.xPos = xPos
		self.yPos = yPos
		self.rect = self.image.get_rect(center = (xPos, yPos))

	def move(self, x : int, y : int) -> None:
		# I discovered a bug where the rect floors the number.
		# Lets say the player moves right (speed=1.5) and lets say the rect position is 100
		# When the player moves, the new position would be 101.5, but because the rect floors the number, it becomes 101
		# If the speed is -1.5, then 101 - 1.5 would be 99.5, but becouse the rect floors the number, it becomes 99
		#
		# .i.e: Player moves faster left than right
		#
		# fix: Don't use rect's to store position. Instead use variables. Becouse somebody at pygame though flooring it would be a good idea

		self.xPos += x
		self.yPos += y
		self.rect.centerx = self.xPos
		self.rect.centery = self.yPos

	def draw(self, surf : pygame.Surface) -> None:
		surf.blit(source=self.image, dest=self.rect)

class Enemy(Object):
	xspeed = 120
	yspeed = 120

	def __init__(self, sprite: pygame.Surface, xPos: int, yPos: int) -> None:
		super().__init__(sprite, xPos, yPos)

		# Starting direction
		if random.randint(0, 1) == 0:
			self.xdirection = -1
		else:
			self.xdirection = 1
		if random.randint(0, 1) == 0:
			self.ydirection = -1
		else:
			self.ydirection = 1

		# Enemies can only move x tiles around the point where they spawned
		#
		# |             |
		# |--E----      |
		# |             |
		clampSize = 75
		self.leftClamp = xPos - clampSize
		self.rightClamp = xPos + clampSize
		self.topClamp = 0
		self.bottomClamp = 300
		

		global leftEdgeOffset
		global rightEdgeOffset
		global screen
		if self.leftClamp < leftEdgeOffset:
			self.leftClamp = leftEdgeOffset
		elif self.rightClamp > rightEdgeOffset:
			self.rightClamp = rightEdgeOffset

		# Add the enemy in a list for collision detection, drawing and movement
		global enemies
		enemies.append(self)

	def Remove(self) -> None:
		global enemies
		enemies.remove(self)

	def move(self, dt) -> None:
		super().move(self.xdirection * self.xspeed * dt, self.ydirection * self.yspeed * dt)

		# Boundaries, aka bouncing.
		# this made them move like pong, for some reason
		if self.rect.centerx <= self.leftClamp:
			self.rect.centerx = self.leftClamp
			self.xdirection = 1
			self.xspeed = self.getSpeed()
		elif self.rect.centerx >= self.rightClamp:
			self.rect.centerx = self.rightClamp
			self.xdirection = -1
			self.xspeed = self.getSpeed()
		if self.rect.centery <= self.topClamp:
			self.rect.centery = self.topClamp
			self.ydirection = 1
			self.yspeed = self.getSpeed()
		elif self.rect.centery >= self.bottomClamp:
			self.rect.centery = self.bottomClamp
			self.ydirection = -1
			self.yspeed = self.getSpeed()

	def getSpeed(self) -> float:
		range = 30
		x = 120 + random.randrange(-range, range, 1)
		print(x)
		return x

	def fire(self) -> None:
		# Spawns enemy bullet
		global enemyBullets
		
		enemyBullets.append([self.rect.centerx, self.rect.bottom])

def checkCollision(rect1 : pygame.Rect, rect2 : pygame.Rect) -> bool:
	if rect1.top < rect2.bottom:
		if rect1.left < rect2.centerx and rect1.right > rect2.centerx:
			return True

clock = pygame.time.Clock()

def main() -> None:
	pygame.init()

	# Create pygame window
	global screen
	screen = pygame.display.set_mode((500, 600))
	screenBackground = (100, 100, 100)

	# Clamps player and enemy xPos between these 2 values
	global leftEdgeOffset
	leftEdgeOffset = 50
	global rightEdgeOffset
	rightEdgeOffset = screen.get_width() - leftEdgeOffset

	# Objects
	playerBullets = []
	playerBulletSprite = pygame.image.load('Sprites/Sprite_PlayerBullet.png')
	global enemyBullets
	enemyBullets = []
	enemyBulletSprite = pygame.image.load('Sprites/Sprite_EnemyBullet.png')
	maxEnemies = 3
	global enemies
	enemies = []
	enemySprite = pygame.image.load('Sprites/Sprite_Enemy.png')
	player = Object(pygame.image.load('Sprites/Sprite_Turret.png'), screen.get_width() / 2, screen.get_height() - 100)
	Enemy(enemySprite, 100, 100)
		
	# Keeps the window from closing
	running = True
	
	# Delays for shooting bullets
	# It's there to stop the player from going: "Haha space go brrrrrrrr"
	shootDelay = 0.5
	shootDelayLeft = shootDelay

	while running:
		# Delta Time
		dt = clock.tick(clock.get_fps())/1000

		# Decrement the delay by the deltatime
		shootDelayLeft -= dt

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and shootDelayLeft <= 0:
					# Create bullet position
					playerBullets.append([player.rect.centerx, player.rect.top])
					shootDelayLeft = shootDelay
			if event.type == pygame.QUIT:
				running = False
				return

		# Inputs
		keys = pygame.key.get_pressed()

		speed = 200 * dt
		if keys[pygame.K_a]:
			# Move left
			player.move(-speed, 0)

			if (player.rect.centerx < leftEdgeOffset):
				player.rect.centerx = leftEdgeOffset
		if keys[pygame.K_d]:
			# Move right
			player.move(speed, 0)
			
			if (player.rect.centerx > rightEdgeOffset):
				# Clamp the right edge 
				player.rect.centerx = rightEdgeOffset
				
		# Player and Background
		screen.fill(screenBackground)
		player.draw(screen)

		# Draw enemies and move them
		for enemy in enemies:
			enemy.move(dt)
			enemy.draw(screen)

		# Draw all bullets
		bulletsToRemove = []
		bulletSpeed = 300 * dt

		for bullet in playerBullets:
			bullet[1] -= bulletSpeed

			if (bullet[1] < 0):
				bulletsToRemove.append(bullet)
				continue

			bulletRect = playerBulletSprite.get_rect(center=(bullet[0], bullet[1]))
			if (checkCollision(bulletRect, player.rect)):
				print("Collided")

			screen.blit(playerBulletSprite, bulletRect)

		# Remove bullets that are gone, yes i know it's bad, it's there because when you remove an entry from an array,
		# it moves all entries above it down, and so it skips an entry
		for bullet in bulletsToRemove:
			playerBullets.remove(bullet)
		bulletsToRemove.clear()
		
		# Update window
		pygame.display.update()

		clock.tick(120)

if __name__ == '__main__':
	main()