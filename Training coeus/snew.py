import  pygame, sys, time, random
import neat,os,pickle
from math import sqrt
difficulty = 99999
difficulty_real = 30
#os.environ["SDL_VIDEODRIVER"] = "dummy"
check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')

frame_size_x = 720
frame_size_y = 480
resume= False
root=""
restore_file="SnakeAiData"
# Initialise game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))

# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

class snake:
    def show_score(self,score,choice, color, font, size,data):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render(data + str(score), True, color)
        score_rect = score_surface.get_rect()
        if choice == 1:
            score_rect.midtop = (frame_size_x/10, 15)
        elif choice ==2:
            score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
        else :
            score_rect.midtop = (frame_size_x/10, frame_size_y/1.5)
        game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

    def __init__(self):
        a=random.randrange(20,700,10)
        k=random.randrange(20,450,10)
        self.snake_pos=[a,k]
        self.snake_body = [[a, k], [a-10, k], [a-(2*10), k]]
        self.closeness=0
        self.snake_alive=True
        self.moves=500

        self.rand_food_pos()

    def rand_food_pos(self):
        self.food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
        self.food_spawn = True
        self.getstartdist()

    def getstartdist(self):
        self.distOrig=abs(self.food_pos[0]-self.snake_pos[0])+abs(self.food_pos[1]-self.snake_pos[1])
        self.closeness=0

    def getdistfit(self,ge):
            a=abs(self.food_pos[0]-self.snake_pos[0])+abs(self.food_pos[1]-self.snake_pos[1])
            if a<=self.distOrig:
                ge.fitness+=1
                self.closeness+=1
            else:
                ge.fitness-=1
                self.closeness-=1
            self.distOrig=a
    direction = 'RIGHT'
    #change_to = direction

    def get1dirinfo(self,x,y,xx,yy,fx,fy):
        global frame_size_x,frame_size_y
        while(x >= 0 and x <= frame_size_x and y >= 0 and y <= frame_size_y):
            x += xx
            y += yy
            if(x==fx and y==fy):
                return int(0)
            else:
                for sx,sy in enumerate(self.snake_body):
                    if x==sx and y==sy:
                        return int(1)
                else:
                    return int(2)

    def getdirinfo(self):
        dir = []
        # 0 food        # 1 body        # 2 boundary
        dir.append(self.get1dirinfo(self.snake_pos[0],self.snake_pos[1],0,-10,self.food_pos[0],self.food_pos[1]))#up
        dir.append(self.get1dirinfo(self.snake_pos[0],self.snake_pos[1],0,10,self.food_pos[0],self.food_pos[1]))#DOWN
        dir.append(self.get1dirinfo(self.snake_pos[0],self.snake_pos[1],-10,0,self.food_pos[0],self.food_pos[1]))#Left
        dir.append(self.get1dirinfo(self.snake_pos[0],self.snake_pos[1],10,0,self.food_pos[0],self.food_pos[1]))#RIGHT
        return dir
    def getquaterinfo(self,food,head):
        qs=[]
        if(head[0]>=food[0] and head[1]<=food[1]): #Q1
            qs.append(1)
        else:
            qs.append(0)
        if(head[0]>=food[0] and head[1]>=food[1]): #Q2
            qs.append(1)
        else:
            qs.append(0)
        if(head[0]<=food[0] and head[1]>=food[1]):#Q3
            qs.append(1)
        else:
            qs.append(0)
        if(head[0]<=food[0] and head[1]<=food[1]):#Q4
            qs.append(1)
        else:
            qs.append(0)
        return qs

    def give_arg(self):
        sx = self.snake_pos[0]
        sy = self.snake_pos[1]
        quaterinfo = self.getquaterinfo(self.food_pos,self.snake_pos)
        dirs = self.getdirinfo()
        return (self.snake_pos[0],self.snake_pos[1],self.food_pos[0],self.food_pos[1],quaterinfo[0],quaterinfo[1],quaterinfo[2],quaterinfo[3],dirs[0],dirs[1],dirs[2],dirs[3])

def play_game(genomes, config):
    fps = pygame.time.Clock()
    gen=0
    for _,ge in genomes:
        net = neat.nn.recurrent.RecurrentNetwork.create(ge, config)
        sn =snake()
        sn.snake_alive = True
        ge.fitness=0
        gen+=1
        while (sn.snake_alive and sn.moves> 0):
            args =  sn.give_arg()
            output = net.activate(args)
            sn.getdistfit(ge)
            ge.fitness+=0.0001
            if(output[0] == max(output) and not sn.direction == 'DOWN'):
                sn.snake_pos[1] -= 10
                sn.direction = 'UP'
            elif(output[1] == max(output) and not sn.direction == 'UP'):
                sn.snake_pos[1] += 10
                sn.direction = 'DOWN'
            elif(output[2] == max(output) and not sn.direction == 'RIGHT'):
                sn.snake_pos[0] -= 10
                sn.direction = 'LEFT'
            elif(output[3] == max(output) and not sn.direction == 'LEFT'):
                sn.snake_pos[0] += 10
                sn.direction = 'RIGHT'
            # Snake body growing mechanism
            sn.snake_body.insert(0, list(sn.snake_pos))
            if sn.snake_pos[0] == sn.food_pos[0] and sn.snake_pos[1] == sn.food_pos[1]:
                ge.fitness += 100
                sn.moves +=  500
                sn.food_spawn = False
            else:
                sn.snake_body.pop()
            # Spawning food on the screen
            if not sn.food_spawn:
                sn.rand_food_pos()
            # GFX
            game_window.fill(black)
            for pos in sn.snake_body:
                # Snake body
                # .draw.rect(play_surface, color, xy-coordinate)
                # xy-coordinate -> .Rect(x, y, size_x, size_y)
                pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

            # Snake food
            pygame.draw.rect(game_window, white, pygame.Rect(sn.food_pos[0], sn.food_pos[1], 10, 10))

            if sn.snake_pos[0] < 0 or sn.snake_pos[0] > frame_size_x-10:
                # game_over
                ge.fitness-=2
                sn.snake_alive = False
                break
            if sn.snake_pos[1] < 0 or sn.snake_pos[1] > frame_size_y-10:
                # game_over
                ge.fitness-=2
                sn.snake_alive = False
                break
            # Touching the snake body
            for block in sn.snake_body[1:]:
                if sn.snake_pos[0] == block[0] and sn.snake_pos[1] == block[1]:
                    # game_over
                    ge.fitness-=2
                    sn.snake_alive = False
                    break
                
            sn.show_score(ge.fitness,1, white, 'consolas', 20,"  Score:")
            sn.show_score(gen,2, white, 'consolas', 20,"Gen :")
            sn.show_score(sn.moves,3, white, 'consolas', 20,"Moves:")
            # Refresh game screen
            pygame.display.update()
            # Refresh rate
            fps.tick(difficulty)
            sn.moves-=1

def gg(conf_f):
    conf = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            conf_f)
    # if resume == True:
    #     p = neat.Checkpointer.restore_checkpoint(restore_file)
    # else:
    p = neat.Population(conf)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(play_game, 300)
    print('Writing Data')
    with open('winner.pkl', 'wb') as output:
        pickle.dump(winner, output, 1)

    # drive.flush_and_unmount()
if __name__ == '__main__':
    conf_file = 'conf.txt'
    gg(conf_file)
