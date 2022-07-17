import enum
import random
import pygame
import pygame.sprite
import math

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

	shootDelay = 1.5
	shootDelayLeft = 0

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
		return 120 + random.randrange(-range, range, 1)

	def fire(self) -> None:
		# Spawns enemy bullet
		global enemyBullets
		enemyBullets = spawnBullets(enemyBullets, (self.rect.centerx, self.rect.bottom), random.randint(1, 3), 25, 180)

def spawnBullets(bullets : list(), basePos : tuple(), numBullets : int, rotationStep : int, baseRotation : int) -> list():
	totalRotation = numBullets * rotationStep

	for x in range(0, numBullets):
		rotation = x / numBullets * totalRotation - (totalRotation - rotationStep) / 2 + baseRotation

		bullets.append([basePos[0], basePos[1], rotation])

	return bullets

def checkCollision(rect1 : pygame.Rect, rect2 : pygame.Rect) -> bool:
	if rect1.top <= rect2.bottom and rect1.bottom >= rect2.top:
		if rect1.left <= rect2.right and rect1.right >= rect2.left:
			return True

clock = pygame.time.Clock()

def main() -> None:
	pygame.init()

	# Window size
	screenSize = [500, 600]

	# Create pygame window
	global screen
	screen = pygame.display.set_mode(screenSize)

	# Set the gameState to 'game'.
	# The gameState 'game' means that the game is playing, 'lose' means that the player has died
	currentState = gameState.game

	# Clamps player and enemy xPos between these 2 values
	global leftEdgeOffset
	leftEdgeOffset = 50
	global rightEdgeOffset
	rightEdgeOffset = screenSize[0] - leftEdgeOffset

	# Sprites
	playerBulletSprite = pygame.image.load('Sprites/Sprite_PlayerBullet.png')
	enemyBulletSprite = pygame.image.load('Sprites/Sprite_EnemyBullet.png')
	enemySprite = pygame.image.load('Sprites/Sprite_Enemy.png')
	playerSprite = pygame.image.load('Sprites/Sprite_Turret.png')
	backgroundImage = pygame.image.load('Sprites/Sprite_SpaceBackground.jpg')

	# Objects
	playerBullets = []
	global enemyBullets
	enemyBullets = []
	maxEnemies = 3
	global enemies
	enemies = []
	player = Object(playerSprite, screenSize[0] / 2, screenSize[1] - 100)
	
	# Score
	score = 0
		
	# Keeps the window from closing
	running = True
	
	# Delays for shooting bullets
	# It's there to stop the player from going: "Haha space go brrrrrrrr"
	shootDelay = 0.5
	shootDelayLeft = shootDelay
	spawnDelay = 2.5
	minSpawnDelay = 0.5
	spawnDelayLeft = spawnDelay

	while running:
		# Delta Time
		dt = clock.tick(clock.get_fps())/1000

		# Decrement delays by deltatime
		shootDelayLeft -= dt

		# General inputs
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if currentState == gameState.game:
					if event.key == pygame.K_SPACE and shootDelayLeft <= 0:
						playerBullets = spawnBullets(playerBullets, (player.rect.centerx, player.rect.top), random.randint(1, 3), 20, 0)
						shootDelayLeft = shootDelay
				else:
					if event.key == pygame.K_r:
						# Reset game
						score = 0
						player.xPos = screenSize[0] / 2
						player.yPos = screenSize[1] - 100
						player.rect.centerx = screenSize[0] / 2
						player.rect.centery = screenSize[1] - 100
						playerBullets = []
						enemyBullets = []
						enemies = []

						currentState = gameState.game
			if event.type == pygame.QUIT:
				running = False
				return

		# MAIN GAME
		if currentState == gameState.game:
			# Inputs
			keys = pygame.key.get_pressed()

			speed = 300 * dt
			if keys[pygame.K_a]:
				# Move left
				player.move(-speed, 0)

				# Clamps
				if player.xPos < leftEdgeOffset:
					player.xPos = leftEdgeOffset
					player.rect.centerx = leftEdgeOffset
			if keys[pygame.K_d]:
				# Move right
				player.move(speed, 0)
				
				if player.xPos > rightEdgeOffset:
					player.xPos = rightEdgeOffset
					player.rect.centerx = rightEdgeOffset
					
			# Player and Background
			screen.fill((0, 0, 0))
			screen.blit(backgroundImage, (0, 0))
			player.draw(screen)

			# Spawn enemies
			if spawnDelayLeft <= 0 and len(enemies) < maxEnemies:
				spawnDelayLeft = spawnDelay

				spawnOffset = 100
				enemies.append(Enemy(enemySprite, random.randint(spawnOffset, screenSize[0] - spawnOffset), 150))

				if (spawnDelay > minSpawnDelay):
					spawnDelay -= 0.05
				else:
					spawnDelay = minSpawnDelay
			else:
				spawnDelayLeft -= dt

			# Draw enemies and move them
			for enemy in enemies:
				# Shooting
				if enemy.shootDelayLeft <= 0:
					enemy.shootDelayLeft = enemy.shootDelay

					enemy.fire()
				else:
					enemy.shootDelayLeft -= dt

				enemy.move(dt)
				enemy.draw(screen)

			# Store bullets and enemies
			playerBulletsToRemove = []
			enemyBulletsToRemove = []
			enemiesToRemove = []
			bulletSpeed = 300 * dt

			# Draw all player bullets
			for bullet in playerBullets:
				x = bulletSpeed * math.cos(math.radians(bullet[2] + 90))
				y = bulletSpeed * math.sin(math.radians(bullet[2] + 90))
				bullet[0] += x
				bullet[1] -= y

				if (bullet[1] < 0):
					playerBulletsToRemove.append(bullet)
					continue

				bulletRect = playerBulletSprite.get_rect(center=(bullet[0], bullet[1]))
				# Collision detection, yes i know it's really bad, i don't have time and experience to implement more complex stuff
				for enemy in enemies:		
					if checkCollision(bulletRect, enemy.rect) and enemiesToRemove.count(enemy) < 1:
						enemiesToRemove.append(enemy)
						playerBulletsToRemove.append(bullet)
						break

				rotatedBulletSprite = pygame.transform.rotate(playerBulletSprite, bullet[2])
				screen.blit(rotatedBulletSprite, bulletRect)

			# Draw all enemy bullets
			for bullet in enemyBullets:
				x = bulletSpeed * math.cos(math.radians(bullet[2] + 90))
				y = bulletSpeed * math.sin(math.radians(bullet[2] + 90))
				bullet[0] += x
				bullet[1] -= y

				if (bullet[1] > screenSize[0]):
					enemyBulletsToRemove.append(bullet)
					continue

				bulletRect = enemyBulletSprite.get_rect(center=(bullet[0], bullet[1]))
				# Collision detection with the player
				if (checkCollision(bulletRect, player.rect)):
					currentState = gameState.lose
					enemyBulletsToRemove.append(bullet)

				screen.blit(enemyBulletSprite, bulletRect)

			# Remove bullets that are gone, yes i know it's bad, it's there because when you remove an entry from an array,
			# it moves all entries above it down, and so it skips an entry
			for bullet in playerBulletsToRemove:
				playerBullets.remove(bullet)
			playerBulletsToRemove.clear()
			
			for bullet in enemyBulletsToRemove:
				enemyBullets.remove(bullet)
			enemyBulletsToRemove.clear()

			# The same for enemies
			for enemy in enemiesToRemove:
				enemies.remove(enemy)
				score += 1
			enemiesToRemove.clear()
			
			# Score text
			font = pygame.font.SysFont(None, 48)
			img = font.render('score: ' + score.__str__(), True, (255, 255, 255))
			screen.blit(img, (20, 20))
		# LOSE SCREEN
		else:
			# Clear Screen
			screen.fill((70, 70, 70))
			
			# Lose text
			font = pygame.font.SysFont(None, 96)
			text = 'You died!'
			fontSize = font.size(text)
			img = font.render(text, True, (255, 255, 255))
			screen.blit(img, (screenSize[0] / 2 - fontSize[0] / 2, screenSize[1] / 2 - fontSize[1] / 2 - 200))
			
			# Score text
			font = pygame.font.SysFont(None, 48)
			text = 'You got a score of: ' + score.__str__()
			fontSize = font.size(text)
			img = font.render(text, True, (255, 255, 255))
			screen.blit(img, (screenSize[0] / 2 - fontSize[0] / 2, screenSize[1] / 2 - fontSize[1] / 2))
		
			# Reset text
			font = pygame.font.SysFont(None, 48)
			text = "Play again by pressing 'r'"
			fontSize = font.size(text)
			img = font.render(text, True, (255, 255, 255))
			screen.blit(img, (screenSize[0] / 2 - fontSize[0] / 2, screenSize[1] / 2 - fontSize[1] / 2 + 100))

		# Update window
		pygame.display.update()

		clock.tick(120)

class gameState(enum.Enum):
	game = 0
	lose = 1

if __name__ == '__main__':
	main()