import pygame as pg
import math

types = ['goomba', 'koopa', 'mushroom', 'flower', 'fireball', 'life', 'star', 'pole', 'coin']

class Entity:
    
    def __init__(self, data):
        self.type = types[data[0]-1]
        self.x = data[1]
        self.y = data[2]
        self.vel_x = 0
        self.vel_y = 0
        self.direction = 1
        self.dist2player = 1
        self.status = 'alive'
        self.jump = 0
        self.interact_player = 1
        self.interact_entities = 1
        self.interact_world = 1
        self.falls = 1

        match self.type:
            case 'goomba':
                self.vel_x = 2
                self.direction = -1
                self.falls = 0
            case 'koopa':
                self.vel_x = 2
                self.direction = -1
                self.falls = 0
            case 'mushroom':
                self.vel_x = 3
                self.interact_entities = 0
            case 'flower':
                self.interact_entities = 0
                self.interact_world = 0
            case 'life':
                self.vel_x = 3
                self.interact_entities = 0
            case 'star':
                self.vel_x = 3
                self.vel_y = 1
                self.jump = 1
                self.interact_entities = 0
            case 'fireball':
                self.vel_x = 6
                self.vel_y = 1.5
                self.jump = 1
                self.interact_player = 0
                self.status = 'sliding'
            case 'pole':
                self.interact_entities = 0
                self.interact_world = 0
                if self.y < 10:
                    self.direction = -1
            case 'coin':
                self.interact_entities = 0
                self.interact_world = 0
                self.direction = -1

        
    def update(self, mapa, player, entities, sounds, GetTile):

        if self.dist2player < 14:
            if self.interact_player and self.status != 'dying':                 
                self.playerInteractions(player, GetTile, mapa, sounds)
            
            if self.interact_entities and self.status != 'dying':
                self.entitiesInteractions(entities, player, sounds)
            
            if self.interact_world:
                self.worldInteractions(player, GetTile, mapa, sounds)
        
        elif self.type == 'fireball':
            self.status = 'dying'
            self.timer = player.total_time
            self.direction = -1
    
    def worldInteractions(self, player, GetTile, mapa, sounds):       
        self.vel_y -= player.partial_time*4
        newx = self.x + self.direction*player.partial_time*self.vel_x
        newy = self.y + self.vel_y*player.partial_time*2

        if (GetTile(newx, self.y, mapa) < 1 and 
            (GetTile(newx, self.y-1, mapa) > 0 or self.falls or self.dist2player < 10)):
            self.x = newx
        elif self.type == 'fireball':
            self.status = 'dying'
            self.timer = player.total_time
            self.direction = -1
            sounds['break'].play()
        elif GetTile(newx, self.y-1, mapa) > 0:
            self.direction = -self.direction
        
        if newy - 0.25 < 0: # fell off the cliff
            self.status = 'dead'
            sounds['kill'].play()
        elif GetTile(self.x, newy - 0.25, mapa) < 1:
            self.y = newy
        elif self.jump:
            self.vel_y *= -0.8
        else:
            self.vel_y = 0 
        
        if self.status == 'inshell' and self.timer < player.total_time:
            self.status = 'alive'
            self.vel_x = 2
            self.falls = 0  

    def playerInteractions(self, player, GetTile, mapa, sounds):
        if self.dist2player < 0.75:
            if self.type in ['mushroom', 'flower']:
                self.status = 'dead'
                player.points += 1000
                sounds['powerup'].play()
                if player.status < 2:
                    player.delta_player = 0.5
                    player.status += 1
            elif self.type == 'life':
                self.status = 'dead'
                player.points += 1000
                player.lives += 1
                sounds['powerup'].play()
            elif self.type == 'star':
                player.points += 1000
                self.status = 'dead'
                player.star = player.total_time + 20
                sounds['powerup'].play()
            elif player.total_time < player.star:
                self.status = 'dying'
                self.timer = player.total_time
                sounds['kill'].play()
            elif self.type == 'goomba':
                if player.vel_y < 0 and player.y - 0.2 > self.y:
                    player.vel_y = 4
                    self.status = 'dying'
                    self.timer = player.total_time
                    if GetTile(self.x + 0.5, self.y, mapa) < 1:
                        self.x = self.x + 0.5
                    player.points += 100
                    sounds['kill'].play()
                elif player.total_time - player.hit > 0:
                    player.status -= 1
                    player.hit = player.total_time + 3
                    sounds['die'].play()

            elif self.type == 'koopa':
                if self.status in ['alive', 'sliding'] and (player.vel_y < 0 and player.y - 0.2 > self.y):
                    player.vel_y = 4
                    self.status = 'inshell'
                    self.timer = player.total_time + 5
                    self.falls = 0
                    sounds['kill'].play()
                    self.vel_x = 0
                elif self.status == 'inshell':
                    if self.dist2player < 0.5:
                        sounds['kill'].play()
                        player.vel_y *= -0.5
                        self.status = 'sliding'
                        self.falls = 1
                        self.vel_x = 5
                        if self.x < player.x:
                            self.direction = -1
                        else:
                            self.direction = 1
                        if GetTile(self.x + self.direction*0.5, self.y, mapa) < 1: # initial push
                            self.x = self.x + self.direction*0.5
                    
                elif player.total_time - player.hit > 0 and self.status != 'inshell':
                    player.status -= 1
                    player.hit = player.total_time + 3
                    sounds['die'].play()
            elif self.type == 'coin':
                self.status = 'dead'
                player.points += 200
                player.coin(sounds)
            elif self.type == 'pole':
                player.rot *= 0.5
                if abs(player.x - self.x) > 0.01:
                    sounds['pole'].play()
                if player.y > 4 and player.vel_x >= 0:
                    player.points += 10*int(player.partial_time*100)#int(player.y-2)**2*100
                    player.vel_y = -0.5
                    player.vel_x  = 0
                    player.x = self.x
                else:
                    player.vel_y = 3
                    player.vel_x  = 2
                    player.x = self.x + 1
                    

                
    
    def entitiesInteractions(self, entities, player, sounds):
        for entity in entities:
            if ((self.x != entity.x or self.y != entity.y) and entity.interact_entities and 
                (self.x - entity.x)**2 + (self.y - entity.y)**2 < 0.5):

                if self.status == 'sliding':
                
                    entity.status = 'dying'
                    entity.timer = player.total_time
                    player.points += 100
                    sounds['kill'].play()
                    if self.type == 'fireball':
                        self.status = 'dying'
                        self.timer = player.total_time
                        self.direction = -1
                elif self.type in ['goomba', 'koopa']:
                    if self.x > entity.x:
                        self.direction = 1
                    else:
                        self.direction = -1
                    
    def selectSprite(self, sprites):
        index = self.direction
        if index == -1 or self.type in ['mushroom', 'flower', 'life', 'star']:
            index = 0
        if self.type == 'koopa' and self.status in ['sliding', 'dying', 'inshell']:
            index = 2
        
        return sprites[self.type][index]

    
    def renderSprite(self, frame, sprites, player, horizontal_res, vertical_res, mapa):
        """Draw a sprite on a frame in a 3D perspective view."""

        refx, refy = player.x -0.2, player.y+0.1
        
        enx, eny = self.x, self.y
        
        # Calculate the distance between the player and the sprite
        self.dist2player = math.sqrt((enx-player.x)**2 + (eny-player.y)**2)
        if self.dist2player > 13 or enx < refx:
            return 0
        
        angle = math.atan2(eny-refy, enx-refx) # angle between player and entity
        angle2 = (player.rot-angle)%(2*math.pi) # difference to player angle
        angle2degree = math.degrees(angle2)
        if angle2degree > 180:
            angle2degree = angle2degree - 360
        
        if angle2degree > -25 and angle2degree < 25: # within 45° + 5 vertical FOV
            # Check if there is a clear line of sight between the player and the sprite
            if vision(enx, eny, refx, refy, self.dist2player, mapa):
                
                selected_sprite = self.selectSprite(sprites)
                
                if self.status == 'dying':
                    selected_sprite = pg.transform.flip(selected_sprite, flip_x=False, flip_y=True)
                    if  player.total_time - self.timer > 0.5:
                        self.status = 'dead'

                scale =  min(200, vertical_res/(self.dist2player))#*math.cos(angle2)))
                
                # Calculate screen coordinates of the sprite
                hor_coord = horizontal_res*(0.5 + player.roth) - scale*0.5
                vert_coord = (22.5+angle2degree)*vertical_res/45 - scale*0.5
                
                if self.type == 'pole':
                    scaled_sprite = pg.transform.smoothscale(selected_sprite, (1.5*scale, 1.5*scale))
                    vert_coord -= scale*0.4
                else:
                    scaled_sprite = pg.transform.smoothscale(selected_sprite, (scale, scale))
                
                
                frame.blit(scaled_sprite, (hor_coord, vert_coord))

def vision(posx, posy, enx, eny, dist2player, mapa):
    # Calculate the cosine and sine of the angle between the two points
    cosine, sine = (posx - enx) / dist2player, (posy - eny) / dist2player
    x, y = enx, eny # Set the starting point
    
    # Start a loop to move along the line connecting the two points in small increments
    for i in range(int(dist2player / 0.05)):
        x, y = x + 0.05 * cosine, y + 0.05 * sine        
        
        if x >= 0 and y >= 0 and x < len(mapa) and y < len(mapa[0]) and mapa[int(x - 0.02)][int(y - 0.02)] > 0:
            return False # return false if the ray is blocked
    
    return True

if __name__ == '__main__':
    import main