import pygame
import random
import time


class Subject:
    def __init__(self, position, text):
        self.position = position
        self.text = text
        self.percent = 100.
        self.request = False
        self.active = False
        self.inuse = False
        self.start_time = time.monotonic()
        self.duration = random.uniform(0, 1) * 10

    def get_colour(self):
        return (100-self.percent) * 2.55, self.percent * 2.55, 0

    def decrease(self, speed):
        self.percent -= speed
        if self.percent < 0:
            self.percent = 0

    def activate(self, speed):
        self.inuse = True
        if not self.active:
            if not self.request:
                self.start_time = time.monotonic()
                self.duration = random.uniform(0, 1) / speed
                self.request = True

    def update(self, speed):
        if self.request:
            current_time = time.monotonic()
            if current_time > self.start_time + self.duration:
                self.active = True
                self.request = False

        if self.active:
            self.decrease(speed)

    def touch(self):
        self.active = False
        self.percent = 100.
        self.inuse = False


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
                      'gameover': pygame.font.SysFont('Comic Sans MS', 30),
                      'session': pygame.font.SysFont('Comic Sans MS', 30)}
        self.fonts['percents'].set_bold(True)
        self.fonts['gameover'].set_bold(True)
        self.fonts['session'].set_bold(True)

        self.subjects = list()
        self.subjects.append(Subject((44, 35), 'Дифференциальные уравнения'))
        self.subjects.append(Subject((44, 120), 'Математический анализ'))
        self.subjects.append(Subject((44, 205), 'Языки программирования'))
        self.subjects.append(Subject((44, 275), 'Безопасность жизнедеятельности'))
        self.subjects.append(Subject((44, 345), 'Иностранный язык'))
        self.subjects.append(Subject((44, 420), 'Пакеты компьютерной алгебры'))
        self.subjects.append(Subject((44, 495), 'Практикум по ЭВМ'))
        self.subjects.append(Subject((44, 565), 'Философия'))
        self.subjects.append(Subject((44, 625), 'Экономика и право'))

        self.background = pygame.image.load('background.png')
        self.final_screen = pygame.image.load('gameover.jpg')

        self.request = False
        self.action = False
        self.choice = 0
        self.start_time = time.monotonic()
        self.duration = random.uniform(0, 1) * 10
        self.speed = 2.
        self.delta = 0.5
        self.gameover = False

        self.score = 0
        self.progress = 0
        self.progress_speed = 0.4
        self.session = False
        self.session_start = time.monotonic()
        self.session_duration = random.uniform(0, 1) * 100
        self.max_activities = 1

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

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for subject in self.subjects:
                        if subject.active:
                            if (pos[0] - subject.position[0]) ** 2 + (pos[1] - subject.position[1]) ** 2 <= 625:
                                subject.touch()
                                self.score += 1

            if not self.gameover:
                self.update(time)
            self.draw()

        pygame.quit()

    def update(self, time_):
        activities = 0
        for subject in self.subjects:
            if subject.inuse:
                activities += 1
        if activities < self.max_activities:
            activate_speed = self.speed * time_
            if self.session:
                activate_speed /= 2
            random.choice(self.subjects).activate(activate_speed)
            self.speed += self.delta * time_

        for subject in self.subjects:
            subject.update(self.speed * time_)

        if not self.session:
            self.progress += self.progress_speed * time_
            if self.progress >= 100:
                self.progress = 100
                self.session = True
                self.session_start = time.monotonic()
                self.session_duration = random.uniform(0, 1) * 100
                self.max_activities = 3
        else:
            current_time = time.monotonic()
            if current_time > self.session_start + self.session_duration:
                self.session = False
                self.max_activities = 1
                self.progress = 0

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

        pygame.draw.line(self.canvas, (0, 255, 0), (0, self.screen_size[1]-20),
                         (self.progress * self.screen_size[0] / 100, self.screen_size[1]-20), 30)

        if self.session:
            session_text = self.fonts['session'].render('СЕССИЯ!!!', True, (255, 0, 0))
            self.canvas.blit(session_text, (self.screen_size[0] / 2 - 50, self.screen_size[1]-40))

        if self.gameover:
            self.canvas.blit(self.final_screen, (0, 0))
            gameover_text = self.fonts['gameover'].render('ВЫ ОТЧИСЛЕНЫ!', True, (255, 0, 0))
            self.canvas.blit(gameover_text, (270, 300))
            final_score_text = self.fonts['gameover'].render('ДОБОРЫ: ' + str(self.score), True, (255, 0, 0))
            self.canvas.blit(final_score_text, (340, 340))

        self.window.blit(self.canvas, (0, 0))


if __name__ == '__main__':
    game = Game((960, 720), "ЫЫЫЫЫ")
    game.run()
