import pygame
import random
import time


class Subject:
    def __init__(self, position):
        self.position = position
        self.percent = 100.

    def get_colour(self):
        return ((100-self.percent) * 2.55, self.percent * 2.55, 0)

    def decrease(self, speed, time_):
        self.percent -= speed * time_
        if self.percent < 0:
            self.percent = 0


class Game:
    def __init__(self, screen_size, title):
        self.screen_size = screen_size
        self.title = title
        self.fps = 60

        pygame.init()
        pygame.font.init()
        self.window = pygame.display.set_mode(screen_size,
                                              pygame.HWSURFACE | pygame.DOUBLEBUF)  # only for draw the canvas
        self.canvas = self.window.copy()  # used to draw

        pygame.display.set_caption(title)

        self.fonts = {'score': pygame.font.SysFont('Comic Sans MS', 30),
                      'percents': pygame.font.SysFont('Times New Roman', 18),
                      'gameover': pygame.font.SysFont('Comic Sans MS', 30)}
        self.fonts['percents'].set_bold(True)
        self.fonts['gameover'].set_bold(True)

        self.subjects = list()
        self.subjects.append(Subject((44, 35)))
        self.subjects.append(Subject((44, 120)))
        self.subjects.append(Subject((44, 205)))
        self.subjects.append(Subject((44, 275)))
        self.subjects.append(Subject((44, 345)))
        self.subjects.append(Subject((44, 420)))
        self.subjects.append(Subject((44, 495)))
        self.subjects.append(Subject((44, 565)))

        self.background = pygame.image.load('brs.png')
        self.final_screen = pygame.image.load('gameover.jpg')

        self.request = False
        self.action = False
        self.choice = 0
        self.start_time = time.monotonic()
        self.duration = random.uniform(0, 1) * 10
        self.speed = 2.
        self.delta = 0.3
        self.gameover = False

        self.score = 0

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.fps)
            time = clock.get_time()
            time = time / 80  # game speed

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if self.action:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if (pos[0] - self.subjects[self.choice].position[0]) ** 2 + \
                                        (pos[1] - self.subjects[self.choice].position[1]) ** 2 <= 25 ** 2:
                            self.action = False
                            self.subjects[self.choice].percent = 100.
                            self.score += 1

            if not self.gameover:
                self.update(time)
            self.draw()

        pygame.quit()

    def update(self, time_):
        if not self.action:
            if not self.request:
                self.choice = int(random.uniform(0, 1) * len(self.subjects))
                self.start_time = time.monotonic()
                self.duration = random.uniform(0, 1) * 10 / self.speed
                self.request = True
                self.speed += self.delta
            else:
                current_time = time.monotonic()
                if (current_time > self.start_time + self.duration):
                    self.action = True
                    self.request = False
        else:
            self.subjects[self.choice].decrease(self.speed, time_)

            if self.subjects[self.choice].percent <= 0:
                self.gameover = True

        self.pos = pygame.mouse.get_pos()

    def draw(self):
        pygame.display.update()
        self.canvas.fill((0, 0, 0))

        self.canvas.blit(self.background, (0, 0))
        for subject in self.subjects:
            pygame.draw.circle(self.canvas, subject.get_colour(), subject.position, 25)
            percents_text = self.fonts['percents'].render(str(int(subject.percent)) +'%', True, (255, 255, 255))
            self.canvas.blit(percents_text, (subject.position[0]-22, subject.position[1]-12))

        score_text = self.fonts['score'].render('ДОБОРЫ: ' + str(self.score), True, (0, 0, 0))
        self.canvas.blit(score_text, (600, 0))


        if self.gameover:
            self.canvas.blit(self.final_screen, (0, 0))
            gameover_text = self.fonts['gameover'].render('ВЫ ОТЧИСЛЕНЫ!', True, (255, 0, 0))
            self.canvas.blit(gameover_text, (270, 300))
            final_score_text = self.fonts['gameover'].render('ДОБОРЫ: ' + str(self.score), True, (255, 0, 0))
            self.canvas.blit(final_score_text, (340, 340))

        self.window.blit(self.canvas, (0, 0))


if __name__ == '__main__':
    game = Game((800, 600), "ЫЫЫЫЫ")
    game.run()
