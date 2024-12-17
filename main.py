import pygame
import random
import time

pygame.init()
pygame.font.init()
pygame.mixer.init()

canvas = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Jumpball")
score = 0
hscore = -1
hscoreAck = False  # True when user beats the high score
startTime = time.time()
displayTime = time.time()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
YELLOW = (255, 255, 0)

# Game Over text
font = pygame.font.SysFont('Comic Sans MS', 30)
gameOver = font.render('You hit a pipe! Press Space to restart.', False, (0, 0, 0))
scoreFont = pygame.font.SysFont('Comic Sans MS', 15)
scoreText = None

# Sounds
jumpSound = pygame.mixer.Sound("sounds/jumpSfx.wav")
deathSound = pygame.mixer.Sound("sounds/deathSfx.wav")
scoreSound = pygame.mixer.Sound("sounds/scoreSfx.wav")
bumpSound = pygame.mixer.Sound("sounds/bumpsfx.wav")
pygame.mixer.music.load("sounds/musicLoop.wav")
pygame.mixer.music.play(30, 0)


# Bird class

class Bird:
    def __init__(self):
        self.x = 200  # Initial horizontal position
        self.y = 100  # Initial vertical position
        self.radius = 20
        self.velocity = 0
        self.gravity = 0.0003
        self.jump_strength = -0.2
        self.grace_period = 400  # Frames before collisions are checked

    def move(self):
        if self.grace_period > 0:
            self.grace_period -= 1  # Count down grace period
        self.velocity += self.gravity
        self.y += self.velocity
        if self.y > 500:  # Bounce bird off the bottom
            self.y = 500
            self.velocity = random.choice([-0.1, -0.2, -0.3])
            bumpSound.play()
        if self.y < 0:  # Bounce bird off the top
            self.y = 0
            self.velocity = 0.3
            bumpSound.play()

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, canvas):
        pygame.draw.circle(canvas, YELLOW, (self.x, int(self.y)), self.radius)

    def check_collision(self, pipes):
        if self.grace_period > 0:  # Skip collision checks during grace period
            return False
        for pipe in pipes:
            # print(f"Bird: x={self.x}, y={self.y}, radius={self.radius}")
            # print(f"Pipe: x={pipe.x}, top_height={pipe.top_height}, bottom_height={pipe.bottom_height}")
            if self.x + self.radius > pipe.x and self.x - self.radius < pipe.x + pipe.width:
                if pipe.x + pipe.width < 0:  # Skip pipes that are off-screen
                    continue
                if self.y - self.radius < pipe.top_height or self.y + self.radius > 500 - pipe.bottom_height:
                    print("Collision Detected!")
                    return True
        return False


# Pipe class
class Pipe:

    def __init__(self, x, width, gap_height, canvas_height):
        self.x = x
        self.width = width
        self.gap_height = gap_height
        self.canvas_height = canvas_height
        self.top_height = random.randint(50, self.canvas_height - self.gap_height - 50)
        self.bottom_height = self.canvas_height - self.top_height - self.gap_height
        assert self.bottom_height > 0, "Pipe bottom height must be positive."
        self.speed = 0.2 * ((0.05 * score) + 1)
        self.scored = False
        print(f"Pipe initialized: x={self.x}, top_height={self.top_height}, bottom_height={self.bottom_height}")

    def move(self):
        self.x -= self.speed

    def draw(self, canvas):
        # Draw top pipe
        pygame.draw.rect(canvas, GREEN, (self.x, 0, self.width, self.top_height))
        # Draw bottom pipe
        pygame.draw.rect(canvas, GREEN,
                         (self.x, self.canvas_height - self.bottom_height, self.width, self.bottom_height))


# Reset game function
def reset_game():
    pygame.mixer.music.play(30)
    global bird, pipes, dead, score, hscore, hscoreAck, startTime
    bird = Bird()  # Grace period is reset in the constructor
    pipes = [Pipe(1500, 80, 150, 500)]  # Position first pipe further away
    if score > hscore:
        hscore = score
    score = 0
    hscoreAck = False
    dead = False
    startTime = time.time()


# Game loop
dead = False
exit = False
bird = Bird()
pipes = [Pipe(1500, 80, 150, 500)]

while not exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if dead:
                print("Restart")
                reset_game()
            else:
                print("Jump")
                jumpSound.play()
                bird.jump()

    # Clear the screen
    canvas.fill(WHITE)

    scoreText = scoreFont.render(f"Score: {str(score)}", False, (0, 0, 0))
    canvas.blit(scoreText, (20, 10))
    (hours, _) = divmod(displayTime, 3600)
    (minutes, seconds) = divmod(displayTime, 60)
    timeText = scoreFont.render(f"{hours:02.0f}:{minutes:02.0f}:{seconds:05.2f}", False, (0, 0, 0))
    canvas.blit(timeText, (20, 30))
    if score <= hscore:
        highScoreText = scoreFont.render(f"High Score: {str(hscore)}", False, (0, 0, 0))
        canvas.blit(highScoreText, (20, 50))

    if not dead:
        # Update and draw bird
        bird.move()
        bird.draw(canvas)

        # Update and draw pipes
        for pipe in pipes:
            pipe.move()
            pipe.draw(canvas)
            if not pipe.scored and bird.x - bird.radius > pipe.x + pipe.width:
                pipe.scored = True
                score += 1
                scoreSound.play()

        # Add new pipe when the last pipe is far enough left
        if pipes[-1].x < 300:
            pipes.append(Pipe(1000, 80, 150, 500))

        # Remove pipes that have gone off-screen
        if pipes[0].x + pipes[0].width < 0:
            pipes.pop(0)

        # Check for collisions
        if bird.check_collision(pipes):
            pygame.mixer.music.stop()
            deathSound.play()
            dead = True

        # Check for high score
        if score > hscore and not hscoreAck:
            hscoreAck = True
            pygame.mixer.music.stop()
            pygame.mixer.music.load("sounds/highScoreSfx.wav")
            pygame.mixer.music.play(0, 0, 0)
            pygame.mixer.music.queue("sounds/musicLoop.wav", "wav", 30)

        # Update current time (elapsed stopwatch alive)
        displayTime = time.time() - startTime

    else:
        canvas.blit(gameOver, (250, 200))

    pygame.display.update()

pygame.quit()
