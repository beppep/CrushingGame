import pygame
import time
import random
import os
import math
import pygame_gui

clock = pygame.time.Clock()
#Adam "jag tycker ändå det kan funka med ett cirkelargument."
SOUND_PATH = os.path.join("assets", "sounds")
pygame.init()
pygame.display.init()

infoObject = pygame.display.Info()
SCREENSIZE = (infoObject.current_w, infoObject.current_h)
FRAMERATE = 60
#HEJ = "HJ"

gameDisplay = pygame.display.set_mode(SCREENSIZE)
#gameDisplay = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Fast Game yo")
#pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "puncher", "idle.png")))

managers={
    "menu":pygame_gui.UIManager(SCREENSIZE),
    "level_select":pygame_gui.UIManager(SCREENSIZE),
    "playing":pygame_gui.UIManager(SCREENSIZE),
    "trial_completed":pygame_gui.UIManager(SCREENSIZE),
}

def blitRotate(surf,image, pos, originPos, angle):

    #ifx rad ddeg
    #angle = angle*180/math.pi

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot 
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (int(pos[0] - originPos[0] + min_box[0] - pivot_move[0] + game.currentScreenShake[0]), int(pos[1] - originPos[1] - max_box[1] + pivot_move[1] + game.currentScreenShake[1]))

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    surf.blit(rotated_image, origin)



def loadImage(path):
    image = pygame.image.load(os.path.join("assets", "textures", path))
    
    image = pygame.transform.scale(image, (64, 64))
    return image

def initSound():
    volume = 0.5
    v=volume
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=32)

    Sound.crushSounds = []
    Sound.wallSounds = []
    for i in range(10):
        Sound.crushSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "crush"+str(i+1)+".wav")))
        Sound.crushSounds[-1].set_volume(v*1)
    for i in range(4):
        Sound.wallSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "wall"+str(i+1)+".wav")))
        Sound.wallSounds[-1].set_volume(v*1)
    
    pygame.mixer.music.load(os.path.join(SOUND_PATH, "crushing music.wav")) #must be wav 16bit and stuff?
    pygame.mixer.music.set_volume(v*0.5)
    pygame.mixer.music.play(-1)

def playCrushSound():
    sound = random.choice(Sound.crushSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()
def playWallSound():
    sound = random.choice(Sound.wallSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()

class Sound():
    0

initSound()

class Game():

    def __init__(self):
        self.mode = "menu"
        self.gameMode = "randomized"
        self.level = None
        self.screenshake = 0
        self.currentScreenShake = (0,0)
        self.screenshakeDir = (0,0)
        self.level_over_animation = False
        self.diamonds = 0
        self.time_trial_time = 0

    def exit_level(self):
        if game.level_over_animation:
            Menues.level_buttons[game.level.campaign_level_number+1].enable()
        game.mode = "level_select"

    def start_level(self, lvl = "randomized"):
        self.level = Level(lvl)
        self.level_over_animation = False
        #self.level.start_level(lvl)

    def update_diamond_count(self,d):
        self.diamonds = d
        for i in Menues.diamond_textboxes:
            i.html_text=str(self.diamonds)
            i.rebuild()

    def update(self):

        if self.screenshake>0:
            ampl = 2
            self.currentScreenShake = [(random.random()-0.5)*2*self.screenshake*ampl, ((random.random()-0.5)*2*self.screenshake*ampl)]
            self.currentScreenShake[0] += self.screenshake*ampl*self.screenshakeDir[0]
            self.currentScreenShake[1] += self.screenshake*ampl*self.screenshakeDir[1]
            self.screenshake -= 0.5
        else:
            self.screenshake = 0

        if self.mode == "playing":
            self.level.update()

            if self.gameMode == "time_trial":
                self.time_trial_time += 1
                i = Menues.diamond_textboxes[-1] # hack!!! this is the diamond counter in "playing" mode
                i.html_text=str(round(self.time_trial_time/60,2))
                i.rebuild()

    def draw(self):
        gameDisplay.fill((0,0,0))
        if not (self.gameMode == "time_trial" and self.mode == "playing"):
            gameDisplay.blit(Grid.images["diamond"], (SCREENSIZE[0]-150-64, 50))
        

        if self.mode == "playing":
            self.level.draw()

    def shakeScreen(self, amount, dPos):
        self.screenshake = max(self.screenshake, amount)
        self.screenshakeDir = dPos

    restartTimesForDifferentGamemodes = {"pvp":60, "randomized":15, "campaign":30, "time_trial":1}
    controls = [
        {pygame.K_a : ((-1,0),180), pygame.K_d : ((1,0),0), pygame.K_w : ((0,-1),90), pygame.K_s : ((0,1),270)},
        {pygame.K_LEFT : ((-1,0),180), pygame.K_RIGHT : ((1,0),0), pygame.K_UP : ((0,-1),90), pygame.K_DOWN : ((0,1),270)},
    ]

class Level():

    def __init__(self, lvl = "randomized"):

        self.players = []
        self.particles = []
        self.playerstartpositions = {}
        self.restartTimer = game.restartTimesForDifferentGamemodes[game.gameMode]
        self.start_level(lvl)
        self.campaign_level_number = 0
        self.trials_completed = 0

    def get_topleft(self):
        #level_movement_amount = 0
        return (SCREENSIZE[0]//2 - 64*self.grid.width//2 + game.currentScreenShake[0], SCREENSIZE[1]//2 - 64*self.grid.height//2 + game.currentScreenShake[1])

    def start_level(self, lvl = "randomized"):
        if lvl == "randomized":
            arenasize = (random.randint(5,15),random.randint(3,10))
            self.grid = Grid(arenasize[0], arenasize[1])
            self.playerstartpositions = self.grid.generate_possible()
        elif lvl == "pvp":
            self.grid = Grid(0, 0)
            all_pvp_level_names = os.listdir(path=os.path.join("assets", "pvpLevels"))
            lvlName = random.choice(all_pvp_level_names)
            self.playerstartpositions = self.grid.load_level(os.path.join("pvpLevels", lvlName))
        else:
            self.grid = Grid(0, 0)
            self.playerstartpositions = self.grid.load_level(os.path.join("campaignLevels", lvl))
        self.players = []
        for i in self.playerstartpositions:
            self.players.append(Player(self.playerstartpositions[i], i))
        self.backupsave = Grid(self.grid.width, self.grid.height)
        self.copy_grid(self.grid, self.backupsave)
    
    def copy_grid(self, a, b):
        b.grid = []
        for x in range(a.width):
            b.grid.append([0]*a.height)
            for y in range(a.height):
                b.set_at(x,y, a.get_at(x,y))
        b.diamonds = a.diamonds[:]

    def restart_level(self):
        self.copy_grid(self.backupsave, self.grid)
        self.players = []
        for i in self.playerstartpositions:
            self.players.append(Player(self.playerstartpositions[i], i))

    def update(self):

        #self.grid.update()
        for p in self.particles:
            p.update()
        #if len(self.particles)>10:
        #    self.particles = self.particles[10::]
        self.particles = list(filter(lambda x: (x.lifetime > 0) , self.particles))
        for player in self.players:
            player.update()
        if self.checkCleared():
            self.level_won()
            

    def level_won(self):
        game.level_over_animation = True
        global FRAMERATE
        FRAMERATE = 30
        if self.restartTimer <= 0:
            FRAMERATE = 60
            self.restartTimer = game.restartTimesForDifferentGamemodes[game.gameMode]
            self.level_over()
            game.level_over_animation = False

        else:
            self.restartTimer -= 1
    
    def level_over(self):
        game.update_diamond_count(game.diamonds + self.players[0].diamonds)# problem more than 1 player can take dias??

        if game.gameMode == "randomized":
            self.start_level()

        if game.gameMode == "time_trial":
            self.trials_completed += 1
            if self.trials_completed == 3:
                game.mode = "trial_completed"
                for i in Menues.trial_time_textboxes:
                    i.html_text=str(round(game.time_trial_time/60,2))
                    i.rebuild()
            else:
                random.seed(Menues.seed_textbox.get_text()+str(self.trials_completed))
                self.start_level()

        if game.gameMode == "campaign":
            game.mode = "level_select"
            if len(Menues.level_buttons)-1 >= self.campaign_level_number+1:
                Menues.level_buttons[self.campaign_level_number+1].enable()

        if game.gameMode == "pvp":
            self.start_level("pvp")
            

    def checkCleared(self):
        if game.gameMode == "pvp":
            return len(self.players) == 1
        else:
            for x in range(self.grid.width):
                for y in range(self.grid.height):
                    if self.grid.grid[x][y] in ["rock","wood"]:
                        return False
            return True

    def draw(self):
        self.grid.draw()
        for p in self.particles:
            p.draw()
        for player in self.players:
            player.draw()

class Grid():

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.grid = []
        self.diamonds = []
        for i in range(w):
            self.grid.append([0]*h)
            for j in range(h):
                self.grid[i][j] = "???"


    def draw(self):
        topleft = game.level.get_topleft()

        for x in range(self.width):
            for y in range(self.height):
                image = self.images[self.grid[x][y]]
                #rotated_image = pygame.transform.rotate(image, 0)
                #blitRotate(gameDisplay, image, (topleft[0] + x*64 +32, topleft[1] + y*64 +32), (32,32), 0)
                gameDisplay.blit(image, (topleft[0] + x*64, topleft[1] + y*64))
                if (x,y) in self.diamonds:
                    gameDisplay.blit(self.images["diamond"], (topleft[0] + x*64, topleft[1] + y*64))


    images = {}
    for i in ["sand","wood","rock","obsidian","diamond"]:
        images[i] = loadImage(os.path.join("blocks", i+".png"))

    def load_level(self, path):
        levelFile = open(os.path.join("assets", path), "r")
        lines = levelFile.read().split("\n")
        playerstartpositions = {}
        self.height = len(lines)
        self.width = len(lines[0])
        self.grid = []
        for x in range(self.width):
            self.grid.append([0]*self.height)
            for y in range(self.height):
                if lines[y][x]=="*":
                    playerstartpositions[0] = (x,y)
                    self.set_at(x,y, "sand")
                elif lines[y][x]=="x":
                    playerstartpositions[1] = (x,y)
                    self.set_at(x,y, "sand")
                else:
                    block = ["sand","wood","rock","obsidian"][int(lines[y][x])]
                    self.set_at(x,y, block)
        return playerstartpositions

    def generate_possible(self):
        jump_length_parameter = 0.5 # 0.1 is short. 0.9 is far
        obsidian_density = 1 # 1 or 0.1
        stop_generating_p = 0.001 # low for more lvl
        DIAMOND_CHANCE = 0.1
        rock_chance = 1

        done = False
        x = random.randint(1,self.width-1)
        y = random.randint(1,self.height-1)
        while not done:
            dPos = random.choice([(-1,0), (1,0), (0,1), (0,-1)])
            if self.get_at(x+dPos[0], y+dPos[1]) in ["sand","???"]: # then go that directon
                if not self.get_at(x-dPos[0], y-dPos[1]) == "out_of_bounds" or random.random()<0.5:
                    #leave hittable
                    if self.get_at(x-dPos[0], y-dPos[1]) == "???" and random.random()<obsidian_density:
                        self.grid[x-dPos[0]][y-dPos[1]] = "obsidian"
                    else:
                        self.grid[x][y] = "wood"
                x += dPos[0]
                y += dPos[1]
                self.grid[x][y] = "sand"
                if self.get_at(x+dPos[0], y+dPos[1]) in ["sand","???"] and random.random()<jump_length_parameter:
                    if random.random()<rock_chance:
                        self.set_at(x-dPos[0], y-dPos[1], "rock")
                    x += dPos[0]
                    y += dPos[1]
                    self.grid[x][y] = "sand"
                    while random.random()<jump_length_parameter:
                        if self.get_at(x+dPos[0], y+dPos[1]) in ["sand","???"]:
                            x += dPos[0]
                            y += dPos[1]
                            self.grid[x][y] = "sand"
                        else:
                            break
            elif random.random()<0.01:
                print("done")
                done = True
                break
            else:
                continue
        for a in range(self.width):
            for b in range(self.height):
                if self.get_at(a,b) == "???":
                    block = ["sand","obsidian"][random.random()<obsidian_density]
                    self.set_at(a,b,block)
                if self.get_at(a,b) == "sand" and not (a,b) == (x,y):
                    if random.random()<DIAMOND_CHANCE:
                        self.diamonds.append((a,b))
        playerstartpositions = {}
        playerstartpositions[0] = (x,y)
        return playerstartpositions

    def get_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        else:
            return "out_of_bounds"

    def set_at(self, x, y, val):
        self.grid[x][y] = val

class Player():

    def __init__(self, position, color):
        self.x = position[0]
        self.y = position[1]
        self.angle = 0
        self.color = color
        self.image = self.standingImages[self.color]
        self.diamonds = 0

    def dash(self, dPos, ang):
        self.angle = ang
        stopped = False
        steps_moved = 0
        smokeParticles = []
        while not stopped:
            if 0 <= self.x+dPos[0] < game.level.grid.width and 0 <= self.y+dPos[1] < game.level.grid.height:
                if game.level.grid.grid[self.x+dPos[0]][self.y+dPos[1]] == "obsidian":
                    playWallSound()
                    stopped = True
                elif game.level.grid.grid[self.x+dPos[0]][self.y+dPos[1]] == "rock" and steps_moved==0:
                    playWallSound()
                    stopped = True
                else:
                    trail = Particle(self.x, self.y, self.angle, "smoke", steps_moved//2+4)
                    trail.image = self.trailImages[self.color]
                    game.level.particles.append(trail)
                    smoke = Particle(self.x +dPos[0]*random.random(), self.y +dPos[1]*random.random(), self.angle, "smoke", random.randint(5,15))
                    smoke.xv = (dPos[0] + random.random() -0.5)*0.01
                    smoke.yv = (dPos[1] + random.random() -0.5)*0.01
                    smokeParticles.append(smoke)
                    self.x += dPos[0]
                    self.y += dPos[1]
                    steps_moved += 1
                    if game.level.grid.grid[self.x][self.y] == "rock":
                        self.crushingParticles(dPos, "rocks", 0.15)
                        game.shakeScreen(steps_moved+5, dPos)
                        game.level.grid.grid[self.x][self.y] = "sand"
                        stopped = True
                    elif game.level.grid.grid[self.x][self.y] == "wood":
                        self.crushingParticles(dPos, "planks", 0.2)
                        game.shakeScreen(steps_moved+3, dPos)
                        game.level.grid.grid[self.x][self.y] = "sand"
                        stopped = True
                    else:
                        if (self.x, self.y) in game.level.grid.diamonds:
                            self.diamonds += 1
                            game.level.grid.diamonds.remove((self.x, self.y))
                            self.crushingParticles(dPos, "diamonds", 0.2)
                        for p in game.level.players:
                            if self != p:
                                if p.x == self.x and p.y == self.y:
                                    game.level.players.remove(p)
                                    game.shakeScreen(steps_moved+10, dPos)
                                    stopped = True
                                    game.level.level_won()
            else:
                playWallSound()
                stopped = True
        game.level.particles = smokeParticles + game.level.particles
        game.shakeScreen(steps_moved, dPos)
        if steps_moved:
            self.image = self.dashImages[self.color]
        return steps_moved > 0

    def crushingParticles(self, dPos, particle_name, spd):
        playCrushSound()
        for i in range(random.randint(5,10)):
            particle = Particle(self.x,self.y, random.random()*360, particle_name, random.randint(1,30))
            particle.xv = (random.random()-0.5 + dPos[0])*spd
            particle.yv = (random.random()-0.5 + dPos[1])*spd
            game.level.particles.append(particle)
        for i in range(random.randint(5,10)):
            particle = Particle(self.x,self.y, random.random()*360, "smoke", random.randint(5,30))
            particle.xv = (random.random()-0.5 + dPos[0])*0.05
            particle.yv = (random.random()-0.5 + dPos[1])*0.05
            game.level.particles.append(particle)

    def update(self):
        pass#pressed = pygame.get_pressed()
        if random.random()<0.02:
            self.image = self.standingImages[self.color]

    def draw(self):
        topleft = game.level.get_topleft()
        blitRotate(gameDisplay, self.image, (topleft[0] + self.x*64 +32, topleft[1] + self.y*64 +32), (32,32), self.angle)

    standingImages = [loadImage(os.path.join(p, "player2.png")) for p in ["player","player2"]]
    dashImages = [loadImage(os.path.join(p, "dash.png")) for p in ["player","player2"]]
    trailImages = [loadImage(os.path.join(p, "swoosh.png")) for p in ["player","player2"]]

class Particle():

    def __init__(self, x,y,a, img, lt):
        self.x = x
        self.y = y
        self.xv = 0
        self.yv = 0
        self.angle = a
        self.image = self.images[img]
        self.lifetime = lt

    def update(self):
        self.x += self.xv
        self.y += self.yv
        self.lifetime -= 1

    def draw(self):
        topleft = game.level.get_topleft()
        blitRotate(gameDisplay, self.image, (topleft[0] + self.x*64 +32, topleft[1] + self.y*64 +32), (32,32), self.angle)


    images = {}
    for i in ["rocks","smoke","planks","diamonds"]:
        images[i] = loadImage(os.path.join("particles", i+".png"))


class Menues():
    

    # MAIN MENU

    menu_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Speed Crush Dash <br>yo",manager=managers["menu"])
    diamond_textboxes = [
        pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((SCREENSIZE[0]-100, 50), (50, 50)),html_text=str(0),manager=managers["menu"]),
        pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((SCREENSIZE[0]-100, 50), (50, 50)),html_text=str(0),manager=managers["level_select"]),
        pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((SCREENSIZE[0]-100, 50), (50, 50)),html_text=str(0),manager=managers["playing"]),
    ]
    music_volume_textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((20, 25), (200, 75)),html_text="Speed Crush Dash <br>yo",manager=managers["menu"])
    music_volume_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((SCREENSIZE[0]-300, 200), (200, 50)),start_value=100, value_range=(0,100), manager=managers["menu"])
    music_volume_slider.enable_arrow_buttons=0
    
    level_select_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 200), (300, 200)),text="Puzzle Level Select",manager=managers["menu"])
    play_randomized_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 200), (300, 200)),text="Limitless Mode",manager=managers["menu"])
    play_pvp_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 500), (300, 200)),text="PvP",manager=managers["menu"])
    play_time_trial_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((700, 500), (300, 200)),text="Time Trial",manager=managers["menu"])

    # seed?

    seed_textbox = pygame_gui.elements.UITextEntryLine(pygame.Rect((700,700),(300,50)), manager = managers["menu"])
    trial_time_textboxes = [
        pygame_gui.elements.UITextBox(relative_rect=pygame.Rect((SCREENSIZE[0]//2-50, SCREENSIZE[1]//2-25), (100, 50)),html_text=str(0),manager=managers["trial_completed"]),
    ]



    # LEVEL SELECT
    back_to_menu_buttons = [
        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 100), (100, 50)),text="Back",manager=managers["level_select"]),
        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, 100), (100, 50)),text="Back",manager=managers["playing"]),
        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREENSIZE[0]//2-50, SCREENSIZE[1]//2+50), (100, 50)),text="Continue",manager=managers["trial_completed"]),
    ]

    level_buttons = []
    lvl_list = sorted(os.listdir(path=os.path.join("assets", "campaignLevels")))
    for i in range(len(lvl_list)):
        lvls_per_row = 6
        pos = (200 + (i%lvls_per_row)*200, 200 + (i//lvls_per_row)*150)
        button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(pos, (150, 100)),text='Level '+lvl_list[i], manager=managers["level_select"])
        if i+1>1:
            pass
            button.disable()
        level_buttons.append(button)


game = Game()

jump_out = False
while jump_out == False:
    time_delta = clock.tick(FRAMERATE)/1000.0

    manager=managers[game.mode]
    manager.update(time_delta)
    #pygame.event.get()
    for event in pygame.event.get():
        manager.process_events(event)
        if event.type == pygame.QUIT:
            jump_out = True
        if event.type == pygame.KEYDOWN:
            if game.mode == "playing":
                if not game.level_over_animation:
                    for i in range(len(game.controls)):
                        if event.key in game.controls[i].keys():
                            j = i % len(game.level.players)
                            game.level.players[j].dash(*game.controls[i][event.key])
                            break
                    if event.key == pygame.K_r and not game.gameMode == "pvp":
                        game.level.restart_level()
            if event.key == pygame.K_ESCAPE:
                if game.mode=="playing" and game.gameMode == "campaign":
                    game.exit_level()
                else:
                    game.mode="menu"

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                
                playWallSound()
                #buttons
                if event.ui_element in Menues.level_buttons:
                    game.mode="playing"
                    game.gameMode = "campaign"
                    lvl_nr = Menues.level_buttons.index(event.ui_element)
                    game.start_level(Menues.lvl_list[lvl_nr])
                    game.level.campaign_level_number = lvl_nr
                if event.ui_element == Menues.level_select_button:
                    game.mode="level_select"
                if event.ui_element == Menues.play_randomized_button:
                    game.mode="playing"
                    game.gameMode = "randomized"
                    random.seed()
                    game.start_level()
                if event.ui_element == Menues.play_time_trial_button:
                    game.mode="playing"
                    game.gameMode = "time_trial"
                    random.seed(Menues.seed_textbox.get_text())
                    game.start_level()
                    game.trial_completed = 0
                    game.time_trial_time = 0
                if event.ui_element == Menues.play_pvp_button:
                    game.mode="playing"
                    game.gameMode = "pvp"
                    game.start_level("pvp")
                if event.ui_element in Menues.back_to_menu_buttons:
                    if game.mode=="playing" and game.gameMode == "campaign":
                        game.exit_level()
                    else:
                        game.mode="menu"

    game.update()
    game.draw()
    manager.draw_ui(gameDisplay)
    

    pygame.display.flip()
    
    
pygame.quit()
#quit() #bad for pyinstaller
