import pygame
from pygame.locals import *
import neat
import sys
from corona.Person import Person
import os
import configparser
import matplotlib.pyplot as plt
import numpy  as np

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 32)

filename = "C:\MSC_lectures\Sem_4\game_agent\Assigment\Agent-based-strategy-to-prevent-virtues-\corona\config.ini"

config = configparser.ConfigParser()
config.read(filename)



win_width= int(config.get('pygame','win_width'))
wind_height = int(config.get('pygame','wind_height'))
FPS = int(config.get('pygame','FPS'))  #frames per second
radius= int( config.get('person','radius'))
initial_population_size=int( config.get('person','initial_population_size'))
search_radiues=int( config.get('person','search_radiues'))

heath_condition_color_dic=eval(config.get('heath_condition','dic'))
air_born_distance = int( config.get('virus','air_born_distance'))
genrations_count=eval(config.get('simulation','genrations_count'))

def plot_summary(total_deaths_list,initial_suspected_or_infected_count_list):
    death_per_infections=[ total_deaths_list[i]/initial_suspected_or_infected_count_list[i] for i in range( len(total_deaths_list))]
    plt.plot(death_per_infections, color='red', label='death_per_infections')
    moving_average_steps=3
    moving_average_list=[]
    moving_average_x=[]
    for i in range(len(death_per_infections)-moving_average_steps):
        moving_average_list.append(np.mean(death_per_infections[i:i+moving_average_steps]))
        moving_average_x.append(i+moving_average_steps)
    plt.plot(moving_average_x,moving_average_list,label='{}_steps_moving_average'.format(moving_average_steps))
    plt.xlabel('Generation')
    plt.ylabel('Number of Deaths')
    plt.legend()
    plt.show()

def angel_quadrant(x1,x2,y1,y2):
    sin=y2-y1
    cos=x2-x1

    if sin>=0 and cos >=0:
        return 'quadrant_1'
    elif sin>=0 and cos <0:
        return 'quadrant_2'
    elif sin<0 and cos <0 :
        return 'quadrant_3'
    else:
        return 'quadrant_4'

def draw_text(win,text,x,y):
    text_font = font.render(text, True, 'black')
    win.blit(text_font, (x,y))

def social_interactions(people_list, radius):
    ''' detec if two people are touching
        if an infected person touches a healthy person , healthy peron becomes a suspected person'''
    for i,person_i in enumerate(people_list):
        person_i.quadrant_agent_count={'quadrant_1': 0, 'quadrant_2': 0, 'quadrant_3': 0, 'quadrant_4': 0}
        for j,person_j in enumerate(people_list):
            if i != j:
                distance=((person_i.x-person_j.x)**2+(person_i.y-person_j.y)**2)**.5
                if air_born_distance:
                    if distance-radius<air_born_distance and person_j.health_condition=='infected' and person_i.health_condition=='healthy' :
                        person_i.health_condition='suspected'
                else:
                    if distance <= radius*2 and person_j.health_condition=='infected' and person_i.health_condition=='healthy' :
                        person_i.health_condition='suspected'

                if person_i.health_condition=='healthy' or  person_j.health_condition =="recovered":
                    if distance <= search_radiues: #if infected or suspected agent located within 4 radiues away
                        if person_j.health_condition =='suspected' or person_j.health_condition =='infected':
                            quadrant=angel_quadrant(person_j.x,person_i.x,person_j.y,person_i.y)
                            person_i.quadrant_agent_count[quadrant]=person_i.quadrant_agent_count[quadrant]+1

                if person_j.health_condition =='suspected' or person_j.health_condition =='infected':
                    if distance <= search_radiues: #if infected or suspected agent located within 4 radiues away
                        if person_j.health_condition =="healthy" or person_j.health_condition =="recovered":
                            quadrant=angel_quadrant(person_j.x,person_i.x,person_j.y,person_i.y)
                            person_i.quadrant_agent_count[quadrant]=person_i.quadrant_agent_count[quadrant]+1


genneration =0
total_deaths_list=[]
initial_suspected_or_infected_count_list=[]
def main(genomes,config_ge):
    ''' main function '''

    global genneration
    death_count = 0
    genneration +=1
    people_list = []
    genome_list=[]
    nets_list=[]

    for _,genome in genomes:

        net=neat.nn.FeedForwardNetwork.create(genome, config_ge)
        nets_list.append(net)

        person = Person()
        person.create_person()
        people_list.append(person)

        genome.fitness=0
        genome_list.append(genome)

    window = pygame.display.set_mode((win_width, wind_height))
    fpsClock = pygame.time.Clock()

    run_simulation=True
    runs_count=0
    while run_simulation:
        runs_count=runs_count+1
        fpsClock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:

                pygame.quit()
                sys.exit()
        window.fill('white')
        social_interactions(people_list, radius)
        infected_or_suspected_people_count=0

        for person_num, person in enumerate(people_list):

            heath_condition = person.update_health_condition()
            if heath_condition != 'dead':
                if heath_condition == 'healthy' or heath_condition=='recovered':
                    output = nets_list[person_num].activate( (person.x,person.y,person.quadrant_agent_count['quadrant_1'],person.quadrant_agent_count['quadrant_2'],person.quadrant_agent_count['quadrant_3'],person.quadrant_agent_count['quadrant_4'],1,0,0))
                elif heath_condition == 'suspected' :
                    output = nets_list[person_num].activate( (person.x,person.y,person.quadrant_agent_count['quadrant_1'],person.quadrant_agent_count['quadrant_2'],person.quadrant_agent_count['quadrant_3'],person.quadrant_agent_count['quadrant_4'],0,1,0))
                elif heath_condition == 'infected':
                    output = nets_list[person_num].activate( (person.x,person.y,person.quadrant_agent_count['quadrant_1'],person.quadrant_agent_count['quadrant_2'],person.quadrant_agent_count['quadrant_3'],person.quadrant_agent_count['quadrant_4'],0,0,1))
                degrees, velocity = output[0]*10, output[1]*10


                person.move(degrees, velocity)

            if heath_condition == 'dead':
                genome_list[person_num].fitness -= 2
                people_list.pop(person_num)
                nets_list.pop(person_num)
                genome_list.pop(person_num)
                death_count = death_count +1

            if heath_condition == 'suspected' or heath_condition == 'infected':
                genome_list[person_num].fitness -= 0.3
                infected_or_suspected_people_count=infected_or_suspected_people_count+1

            if heath_condition == 'healthy':
                genome_list[person_num].fitness += 0.1



            person.draw(window)

        if infected_or_suspected_people_count == 0 or len(people_list) == 0:
            total_deaths_list.append(death_count)
            run_simulation = False
            break

        if runs_count==1:
            initial_suspected_or_infected_count_list.append(infected_or_suspected_people_count)

        average_fitness = sum([genome.fitness for genome in genome_list]) / len(genome_list)

        generation_text='Generation: {}'.format(genneration)
        average_fitness_text='AVG fitness: {:.3f}'.format(average_fitness)
        deaths_count_text = 'Total deaths: {}'.format(death_count)
        draw_text(window,generation_text,5,5)
        draw_text(window, average_fitness_text, 5, 30)
        draw_text(window, deaths_count_text, 5, 55)
        pygame.display.update()



def run(config_path):
    ''' config neat library '''
    config =neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,
                               neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats= neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,genrations_count)

if __name__== "__main__":
    local_dir=os.path.dirname(__file__)
    config_path=os.path.join(local_dir,"C:\MSC_lectures\Sem_4\game_agent\Assigment\Agent-based-strategy-to-prevent-virtues-\corona\config-feedforward.txt")
    run(config_path)
    plot_summary(total_deaths_list, initial_suspected_or_infected_count_list)
