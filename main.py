import pygame

running = True

def main() -> None:
	pygame.init()

	createWindow(name='Game', width=500, height=400)

# Creates new pygame window
def createWindow(name : str, width : int, height : int) -> pygame.Surface:
	surface = pygame.display.set_mode((width, height))
	pygame.display.flip()
	pygame.display.set_caption(name)

	return surface

if __name__ == '__main__':
	main()

# Keeps the window from closing
while running:
	for event in pygame.event.get():
		if (event.type == pygame.QUIT):
			running = False