import pygame
from pygame.locals import *
import sys
import random
import math
import configparser
filename = "C:\MSC_lectures\Sem_4\game_agent\Assigment\Agent-based-strategy-to-prevent-virtues-\corona\config.ini"
config = configparser.ConfigParser()
config.read(filename)

wind_width= int(config.get('pygame','win_width'))
wind_height = int(config.get('pygame','wind_height'))
FPS = int(config.get('pygame','FPS'))  #frames per second

radius= int( config.get('person','radius'))
velocity= int( config.get('person','velocity'))
search_radiues=int( config.get('person','search_radiues'))

suspected_to_infection_rate=int( config.get('virus','suspected_to_infection_rate'))
infected_to_death_rate=int( config.get('virus','infected_to_death_rate'))
initial_healthy_population=int( config.get('virus','initial_healthy_population'))
initial_infected_population=int( config.get('virus','initial_infected_population'))
air_born_distance = int( config.get('virus','air_born_distance'))

heath_condition_color_dic=eval(config.get('heath_condition','dic'))


class Person:
    ''' Person is an agent. Each person can be healthy, suspected or healthy '''
    def __init__(self):
       #self.x=x
       #self.y=y

        self.radius = radius
        self.color='green'
        self.suspected_to_infection_rate=suspected_to_infection_rate
        self.suspected_tick=0
        self.search_radiues=search_radiues
        self.infected_to_death_rate = infected_to_death_rate
        self.inflected_tick = 0
        self.quadrant_agent_count={'quadrant_1':0,'quadrant_2':0,'quadrant_3':0,'quadrant_4':0}


    def draw(self,win):
        ''' update person's color and draw on the display  '''

        self.color = heath_condition_color_dic.get(self.health_condition)
        pygame.draw.circle(win, 'black',(self.x, self.y), self.search_radiues, width=1)
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
        if air_born_distance and self.health_condition=='infected' :
            pygame.draw.circle(win, 'red', (self.x, self.y), air_born_distance, width=1)


    def create_person(self):
        ''' determin initial position of the person '''
        self.x = random.randint(0, wind_width)
        self.y= random.randint(0, wind_height)

        ''' determine the initial health condition of the person  '''
        health_condition_int = random.randint(0, 100)

        if health_condition_int<= initial_healthy_population:
            self.health_condition= 'healthy'
            self.color=heath_condition_color_dic.get(self.health_condition)
        elif health_condition_int >= 100-initial_infected_population:
            self.health_condition = 'infected'
            self.color = heath_condition_color_dic.get(self.health_condition)
        else:
            self.health_condition = 'suspected'
            self.color = heath_condition_color_dic.get(self.health_condition)

    def update_health_condition(self):
        ''' suspected person can get infected
          , infected person can die or recover'''

        # determine if infected person recovered or dead
        if self.health_condition =='infected':
            self.inflected_tick = self.inflected_tick + 1

            if self.inflected_tick >= 25:
                is_dead = random.randint(0, 100)
                if is_dead>self.infected_to_death_rate:
                        self.health_condition ='dead'
                else:
                    self.health_condition = 'recovered'

        # determine if suspected person is infected or healthy
        elif self.health_condition =='suspected':
            self.suspected_tick = self.suspected_tick + 1

            if self.suspected_tick >= 25:
                is_infected = random.randint(0, 100)
                if is_infected>self.suspected_to_infection_rate:
                        self.health_condition ='infected'
                else:
                    self.health_condition = 'healthy'

        return self.health_condition




    def move(self,degrees,velocity):
        ''' move person '''

        sin = math.sin(degrees)
        cos = math.cos(degrees)

        # setting up the nex x,y position of the person
        new_y=self.y + velocity*sin
        new_x=self.x + velocity*cos

        # stop person from crossing the display boundary
        if new_y<wind_height-self.radius-1 and new_y>self.radius+1:
            self.y =new_y

        if new_x<wind_width-self.radius-1 and new_x>self.radius+1:
            self.x =new_x
