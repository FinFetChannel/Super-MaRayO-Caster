import pygame as pg

class Entity:
    def __init__(self, data):
        self.type = data[0] # 1 goomba, 2 koopa, 3 mushroom, 4 flower
        self.x = data[1]
        self.y = data[2]
        self.vel_y = 0
        self.direction = -1
        self.dist2player = 1
        
        # if data[0] <= 2 :
        self.status = 'walking'
        if self.type > 2:
            self.direction = 1
        if self.type == 4:
            self.status = 'sitting'
        if self.type == 5:
            self.status = 'sliding'
            self.vel_y = 2
        
        
    def update(self, mapa, player, entities, GetTile):

        if self.dist2player < 12:
        
            self.player_interactions(player, GetTile, mapa)
            
            self.vel_y -= player.elapsed_time*4

            newx = self.x
            if self.status == 'walking':
                newx = self.x + self.direction*player.elapsed_time*2
            
            elif self.status == 'sliding':
                newx = self.x + self.direction*player.elapsed_time*5
                self.entities_interactions(entities, player)

            elif self.status == 'sitting' and self.dist2player > 10 and self.type == 2:
                self.status = 'walking'
                
            newy = self.y + self.vel_y*player.elapsed_time*2

            if GetTile(newx, self.y, mapa) < 1:# and (GetTile(newx, self.y-1, mapa) > 0 or self.status == 'sliding'):
                self.x = newx
            elif self.type == 5:
                self.status = 'dead'
            else:
                self.direction = -self.direction
            
            if newy - 0.25 < 0:
                self.status = 'dead'
            elif GetTile(self.x, newy - 0.25, mapa) < 1:
                self.y = newy
            elif self.type == 5:
                self.vel_y *= -0.5
                if abs(self.vel_y) < 0.1:
                    self.status = 'dead'
            else:
                self.vel_y = 0

    def player_interactions(self, player, GetTile, mapa):
        if self.dist2player < 1:
            if self.type == 3 or self.type == 4:
                self.status = 'dead'
                player.status = (1 + self.type)%3
                player.delta_player = 0.5
                player.y += 0.25
            elif (player.vel_y < 0 and player.y - 0.2 > self.y) or (player.vel_y == 0 and self.status == 'sitting'):
                player.vel_y *= -0.5
                if self.type == 1 and self.status != 'dying':
                    self.status = 'dying'
                    self.timer = player.total_time
                    if GetTile(self.x + 0.5, self.y, mapa) < 1:
                        self.x = self.x + 0.5
                    print('Dieeeeeee')
                elif self.type == 2:
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
    
    def entities_interactions(self, entities, player):
        for entity in entities:
            if (self.x != entity.x or self.y != entity.y) and entity.dist2player < 20 and (self.x - entity.x)**2 + (self.y - entity.y)**2 < 0.25:
                entity.status = 'dying'
                entity.timer = player.total_time
                if self.type == 5:
                    self.status = 'dead'
                
        pass
    def sprite(self, sprites, total_time):
        if self.type == 3:
            return sprites[2]
        if self.type == 4:
            return sprites[3]
        direction = self.direction
        if direction == -1:
            direction = 0
        if self.status == 'sliding' or self.status == 'sitting':
            direction = 2
        selected_sprite = sprites[self.type-1][direction]
        if int(total_time*6)%6 < 3 and self.status != 'sitting' and self.status != 'dying': # sprite animation
            selected_sprite = pg.transform.flip(selected_sprite, flip_x=True, flip_y=False)
        if self.status == 'dying':
            new_surf = pg.surface.Surface((100,100), pg.SRCALPHA)
            new_surf.blit(pg.transform.scale(selected_sprite, (100, 50)), (0, 50))
            selected_sprite = new_surf
            if  total_time - self.timer > 0.5:
                self.status = 'dead'
        return selected_sprite

if __name__ == '__main__':
    import main