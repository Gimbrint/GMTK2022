import pygame
import pygame.sprite
import os.path as ospath

clock = pygame.time.Clock()

class Object(pygame.sprite.Sprite):
	def __init__(self, sprite : pygame.Surface, xPos : int, yPos : int) -> None:
		self.image = sprite
		self.rect = self.image.get_rect(center = (xPos, yPos))

	def move(self, x : int, y : int):
		self.rect.centerx += x
		self.rect.centery += y

	def draw(self, surf : pygame.Surface):
		surf.blit(source=self.image, dest=self.rect)

def checkCollision(rect1 : pygame.Rect, rect2 : pygame.Rect) -> bool:
	if rect1.top < rect2.bottom:
		if rect1.left < rect2.centerx and rect1.right > rect2.centerx:
			return True

clock = pygame.time.Clock()

def main() -> None:
	pygame.init()

	# Create pygame window
	screen = pygame.display.set_mode((500, 400))
	screenBackground = (100, 100, 100)

	# Bullets
	playerBullets = []
	playerBulletSprite = pygame.image.load('Sprites/Sprite_PlayerBullet.png')
	enemyBullets = []
	player = Object(pygame.image.load('Sprites/Sprite_Turret.png'), screen.get_width() / 2, screen.get_height() - 100)
		
	# Keeps the window from closing
	running = True
	leftEdgeOffset = 50
	rightEdgeOffset = screen.get_width() - leftEdgeOffset

	# Delays for shooting bullets
	# It's there to stop the player from going: "Haha space go brrrrrrrr"
	shootDelay = 0.5
	shootDelayLeft = shootDelay

	while running:
		shootDelayLeft -= 1/60

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
		

		if keys[pygame.K_a]:
			# Move left
			player.move(-3, 0)

			if (player.rect.centerx < leftEdgeOffset):
				player.rect.centerx = leftEdgeOffset
		if keys[pygame.K_d]:
			# Move right
			player.move(3, 0)
			
			if (player.rect.centerx > rightEdgeOffset):
				# Clamp the right edge 
				player.rect.centerx = rightEdgeOffset
				
		# Draw stuff
		screen.fill(screenBackground)
		player.draw(screen)

		# Draw all bullets
		for bullet in playerBullets:
			bullet[1] -= 3

			if (bullet[1] < 0):
				playerBullets.remove(bullet)
				continue

			bulletRect = playerBulletSprite.get_rect(center=(bullet[0], bullet[1]))
			if (checkCollision(bulletRect, player.rect)):
				print("Collided")

			screen.blit(playerBulletSprite, bulletRect)
		
		# Update window
		pygame.display.update()

		clock.tick(60)

if __name__ == '__main__':
	main()