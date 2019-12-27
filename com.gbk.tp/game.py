import pygame
import random
import time


class Subject:
    def __init__(self, text):
        self.position = (0, 0)
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
                self.duration = random.uniform(0, 1) * 2 / speed
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
                      'session': pygame.font.SysFont('Comic Sans MS', 30),
                      'name': pygame.font.SysFont('Comic Sans MS', 30)}
        self.fonts['percents'].set_bold(True)
        self.fonts['gameover'].set_bold(True)
        self.fonts['session'].set_bold(True)

        self.subjects = list()
        self.subjects.append(Subject('Дифференциальные уравнения'))
        self.subjects.append(Subject('Математический анализ'))
        self.subjects.append(Subject('Языки программирования'))
        self.subjects.append(Subject('Безопасность жизнедеятельности'))
        self.subjects.append(Subject('Иностранный язык'))
        self.subjects.append(Subject('Пакеты компьютерной алгебры'))
        self.subjects.append(Subject('Практикум по ЭВМ'))
        self.subjects.append(Subject('Философия'))
        self.subjects.append(Subject('Экономика и право'))

        for i in range(len(self.subjects)):
            self.subjects[i].position = (44, 35+85*i)

        self.final_screen = pygame.image.load('gameover.jpg')

        self.request = False
        self.action = False
        self.choice = 0
        self.speed = 2.
        self.delta = 0.4
        self.gameover = False

        self.score = 0
        self.progress = 0
        self.progress_speed = 0.2
        self.session = False
        self.session_start = time.monotonic()
        self.session_duration = 20
        self.max_activities = 1
        self.semester = 1
        self.course = 1
        self.killed_by = ''

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.fps)
            time = clock.get_time()
            time = time / 80  # game speed

            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE] or event.type == pygame.QUIT:
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
            random.choice(self.subjects).activate(self.speed * time_ / 2)
            if not self.session:
                self.speed += self.delta * time_
            print(self.speed)

        if not self.session:
            self.progress += self.progress_speed * time_
            if self.progress >= 100:
                self.progress = 100
                self.session = True
                self.session_start = time.monotonic()
                self.max_activities = 3
        else:
            current_time = time.monotonic()
            if current_time > self.session_start + self.session_duration:
                self.session = False
                self.max_activities = 1
                self.progress = 0
                self.speed = 2. + (self.semester + (self.course - 1) * 2) / 5
                self.semester += 1
                if self.semester > 2:
                    self.semester = 1
                    self.course += 1
                print(self.speed)

        for subject in self.subjects:
            subject.update(self.speed * time_)
            if subject.percent <= 0:
                self.gameover = True
                self.killed_by = subject.text

        self.pos = pygame.mouse.get_pos()

    def draw(self):
        pygame.display.update()
        self.canvas.fill((255, 255, 255))

        for subject in self.subjects:
            pygame.draw.circle(self.canvas, subject.get_colour(), subject.position, 25)
            percents_text = self.fonts['percents'].render(str(int(subject.percent)) +'%', True, (255, 255, 255))
            self.canvas.blit(percents_text, (subject.position[0]-22, subject.position[1]-12))
            name_text = self.fonts['name'].render(subject.text, True, (0, 0, 255))
            self.canvas.blit(name_text, (subject.position[0] + 40, subject.position[1] - 25))

        score_text = self.fonts['score'].render('ДОБОРЫ: ' + str(self.score), True, (0, 0, 0))
        self.canvas.blit(score_text, (650, 20))

        course_text = self.fonts['score'].render('КУРС: ' + str(self.course), True, (0, 0, 0))
        self.canvas.blit(course_text, (550, 700))

        semester_text = self.fonts['score'].render('СЕМЕСТР: ' + str(self.semester), True, (0, 0, 0))
        self.canvas.blit(semester_text, (750, 700))

        pygame.draw.line(self.canvas, (0, 255, 0), (0, self.screen_size[1]-20),
                         (self.progress * self.screen_size[0] / 100, self.screen_size[1]-20), 30)

        if self.session:
            session_text = self.fonts['session'].render('СЕССИЯ!!!', True, (255, 0, 0))
            self.canvas.blit(session_text, (self.screen_size[0] / 2 - 50, self.screen_size[1]-40))

        if self.gameover:
            self.canvas.blit(self.final_screen, (0, 0))

            gameover_text = 'ВЫ ОТЧИСЛЕНЫ!'
            gameover_img = self.fonts['gameover'].render(gameover_text, True, (255, 0, 0))
            gameover_size = self.fonts['gameover'].size(gameover_text)
            self.canvas.blit(gameover_img, ((self.screen_size[0] - gameover_size[0]) / 2, 300))

            final_course_text = 'ВЫ ПРОУЧИЛИСЬ: ' + str(self.course) + ' КУРСА  ' + str(self.semester) + ' СЕМЕСТРА'
            final_course_img = self.fonts['gameover'].render(final_course_text, True, (255, 0, 0))
            final_course_size = self.fonts['gameover'].size(final_course_text)
            self.canvas.blit(final_course_img, ((self.screen_size[0] - final_course_size[0]) / 2, 350))

            final_score_text = 'И ПЕРЕЖИЛИ: ' + str(self.score) + ' ДОБОРОВ'
            final_score_img = self.fonts['gameover'].render(final_score_text, True, (255, 0, 0))
            final_score_size = self.fonts['gameover'].size(final_score_text)
            self.canvas.blit(final_score_img, ((self.screen_size[0] - final_score_size[0]) / 2, 400))

            killed_by_text = 'ВАС УБИЛ: ' + self.killed_by
            killed_by_img = self.fonts['gameover'].render(killed_by_text, True, (255, 0, 0))
            killed_by_size = self.fonts['gameover'].size(killed_by_text)
            self.canvas.blit(killed_by_img, ((self.screen_size[0] - killed_by_size[0]) / 2, 450))

        self.window.blit(self.canvas, (0, 0))


if __name__ == '__main__':
    game = Game((960, 800), "МЕХМАТ")
    game.run()
