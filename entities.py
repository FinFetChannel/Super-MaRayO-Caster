import pygame as pg
import math

types = ['goomba', 'koopa', 'mushroom', 'flower', 'fireball', 'life', 'star']

class Entity:
    
    def __init__(self, data):
        self.type = types[data[0]-1]
        self.x = data[1]
        self.y = data[2]
        self.vel_y = 0
        self.direction = -1
        self.dist2player = 1
        self.status = 'walking'

        if self.type in ['mushroom', 'fireball', 'life', 'star']:
            self.direction = 1
            
        if self.type == 'flower':
            self.status = 'sitting'
        if self.type == 'fireball':
            self.status = 'sliding'
            self.vel_y = 1
        if self.type == 'star':
            self.vel_y = 4

        # print('creating', self.type)
        
    def update(self, mapa, player, entities, GetTile):

        if self.dist2player < 14:
                             
            self.player_interactions(player, GetTile, mapa)
            
            self.vel_y -= player.elapsed_time*4

            newx = self.x
            if self.status == 'walking':
                if self.dist2player < 3 and self.type in  ['goomba', 'koopa']:
                    self.direction = int(math.copysign(1, player.x - self.x))
                newx = self.x + self.direction*player.elapsed_time*2
            
            elif self.status == 'sliding':
                newx = self.x + self.direction*player.elapsed_time*5
                self.entities_interactions(entities, player)

            elif self.status == 'sitting' and self.dist2player > 10 and self.type == 'koopa':
                self.status = 'walking'
                
            newy = self.y + self.vel_y*player.elapsed_time*2

            if (GetTile(newx, self.y, mapa) < 1 and (GetTile(newx, self.y-1, mapa) > 0 or
                self.status == 'sliding' or self.dist2player < 10 or self.type == 'mushroom')):
                self.x = newx
            elif self.type == 'fireball':
                self.status = 'dead'
            elif GetTile(newx, self.y-1, mapa) > 0:
                self.direction = -self.direction
            
            if newy - 0.25 < 0:
                self.status = 'dead'
            elif GetTile(self.x, newy - 0.25, mapa) < 1:
                self.y = newy
            elif self.type in ['fireball', 'star']:
                self.vel_y *= -0.5
                if abs(self.vel_y) < 0.1 and self.type == 'fireball':
                    self.status = 'dead'
            else:
                self.vel_y = 0
        elif self.type == 'fireball':
            self.status = 'dead'

    def player_interactions(self, player, GetTile, mapa):
        if self.dist2player < 1:
            if self.type in ['mushroom', 'flower']:
                self.status = 'dead'
                if player.status < 2:
                    player.delta_player = 0.5
                    player.status += 1
                else:
                    player.lives += 1
            elif self.type == 'life':
                self.status = 'dead'
                player.lives += 1
            elif self.type == 'star':
                self.status = 'dead'
                player.star = player.total_time
            elif player.total_time - player.star < 20:
                self.status = 'dying'
                self.timer = player.total_time
            elif (player.vel_y < 0 and player.y - 0.2 > self.y) or (player.vel_y == 0 and self.status == 'sitting'):
                player.vel_y *= -0.5
                if self.type == 'goomba' and self.status != 'dying':
                    self.status = 'dying'
                    self.timer = player.total_time
                    if GetTile(self.x + 0.5, self.y, mapa) < 1:
                        self.x = self.x + 0.5
                    print('Dieeeeeee')
                elif self.type == 'koopa':
                    if self.status == 'walking' or self.status == 'sitting':
                        self.status = 'sliding'
                        if self.x > player.x:
                            self.direction = 1
                        else:
                            self.direction = -1
                        if GetTile(self.x + self.direction*0.5, self.y, mapa) < 1:
                            self.x = self.x + self.direction*0.5
                        print('koopa slide')
                    elif self.status == 'sliding':
                        self.status = 'sitting'
                        print('koopa sit')
            elif player.total_time - player.hit > 5:
                player.status -= 1
                player.hit = player.total_time
                print(player.status, player.lives)
    
    def entities_interactions(self, entities, player):
        for entity in entities:
            if ((self.x != entity.x or self.y != entity.y) and entity.dist2player < 20 and
                entity.type != 'fireball' and (self.x - entity.x)**2 + (self.y - entity.y)**2 < 0.5):
                
                entity.status = 'dying'
                entity.timer = player.total_time
                if self.type == 'fireball':
                    self.status = 'dead'
                    
    def selectSprite(self, sprites):
        index = self.direction
        if index == -1 or self.type in ['mushroom', 'flower', 'fireball', 'life', 'star']:
            index = 0
        if self.type == 'koopa' and self.status in ['sliding', 'dying', 'sitting']:
            index = 2
        
        return sprites[self.type][index]

    
    def renderSprite(self, frame, sprites, player, horizontal_res, vertical_res, mapa):
        """Draw a sprite on a frame in a 3D perspective view."""

        refx, refy = player.x -0.2, player.y+0.1
        
        enx, eny = self.x, self.y

        # Calculate the distance between the player and the sprite
        dist2p = math.sqrt((enx-refx)**2+(eny-refy)**2 + 1e-16)
        self.dist2player = dist2p
        if dist2p > 13:
            return 0
        
        angle = math.atan2(eny-refy, enx-refx) # angle between player and entity
        angle2 = (player.rot-angle)%(2*math.pi) # difference to player angle
        angle2degree = math.degrees(angle2)
        if angle2degree > 180:
            angle2degree = angle2degree - 360
        
        if angle2degree > -25 and angle2degree < 25: # within 45° + 5 vertical FOV
            # Check if there is a clear line of sight between the player and the sprite
            if vision(enx, eny, refx, refy, dist2p, mapa):
                
                selected_sprite = self.selectSprite(sprites)
                
                if self.status == 'dying':
                    selected_sprite = pg.transform.flip(selected_sprite, flip_x=False, flip_y=True)
                    if  player.total_time - self.timer > 0.5:
                        self.status = 'dead'
                elif int(player.total_time*4)%4 < 2 and self.status != 'dying': # sprite "animation"
                    selected_sprite = pg.transform.flip(selected_sprite, flip_x=True, flip_y=False)

                scale =  vertical_res/(dist2p)#*math.cos(angle2)))
                scaled_sprite = pg.transform.smoothscale(selected_sprite, (scale, scale))
                
                # Calculate screen coordinates of the sprite
                hor_coord = horizontal_res*(0.5 + player.roth) - scale*0.5
                vert_coord = (22.5+angle2degree)*vertical_res/45 - scale*0.5
                frame.blit(scaled_sprite, (hor_coord, vert_coord))

def vision(posx, posy, enx, eny, dist2p, mapa):
    # Calculate the cosine and sine of the angle between the two points
    cosine, sine = (posx - enx) / dist2p, (posy - eny) / dist2p
    x, y = enx, eny # Set the starting point
    
    # Start a loop to move along the line connecting the two points in small increments
    for i in range(int(dist2p / 0.05)):
        x, y = x + 0.05 * cosine, y + 0.05 * sine        
        
        if x >= 0 and y >= 0 and x < len(mapa) and y < len(mapa[0]) and mapa[int(x - 0.02)][int(y - 0.02)]:
            return False # return false if the ray is blocked
    
    return True

if __name__ == '__main__':
    import main