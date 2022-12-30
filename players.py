from entities import Entity
import pygame as pg

class Player:
    def __init__(self):
        self.x = 3.5
        self.y = 12.5
        self.rot = 0
        self.roth = 0
        self.vel_x = 0
        self.vel_y = 0
        self.partial_time = 1
        self.total_time = 0
        self.timer = 0
        self.status = 0 # -1 dead, 0 tiny, 1 grown, 2 fireballs
        self.delta = 0.2
        self.lives = 3
        self.star = -20
        self.hit = -5


    def update(self, mapa, jump, entities, GetTile):
        """Update the player's attributes based on input and elapsed time."""

        pressed_keys = pg.key.get_pressed()

        # Update player rotation based on mouse input
        if pg.mouse.get_focused():
            p_mouse = pg.mouse.get_rel()
            if abs(p_mouse[1]) > 1:
                rot = self.rot + min(max((-p_mouse[1])/400, -0.2), .2)
                self.rot = max(min(rot, 1), -1)
            if abs(p_mouse[0]) > 1:
                roth = self.roth + min(max((-p_mouse[0])/400, -0.2), .2)
                self.roth = max(min(roth, 0.5), -0.5)
            # fireballs
            if self.status == 2 and self.total_time - self.timer > 1 and (pressed_keys[ord('f')] or pg.mouse.get_pressed()[0]):
                self.timer = self.total_time
                entities.insert(0, Entity([5, self.x+1, self.y+0.1]))

        # Determine the player's forward velocity based on keyboard input
        forward = pressed_keys[ord('w')] - pressed_keys[ord('s')]       

        # If the player is on the floor, apply friction and increase forward velocity
        if GetTile(self.x, self.y - self.delta-0.01, mapa) > 0:  # Check if there is floor
            self.vel_y = 0
            if forward == 0:
                self.vel_x = self.vel_x - self.elapsed_time*self.vel_x*15
            # Make the player jump if the jump key was pressed
            if pressed_keys[pg.K_SPACE]:
                jump.play()
                self.vel_y = 7
        else:
            self.vel_y -= self.elapsed_time*12 # gravity
       

        if abs(self.vel_y) > 0.001:
            newposy = self.y + self.elapsed_time*self.vel_y*2
            if (GetTile(self.x, newposy - self.delta, mapa) < 1 and GetTile(self.x, newposy + self.delta, mapa) < 1 and
                GetTile(self.x - self.delta, newposy, mapa) < 1 and GetTile(self.x, newposy + self.delta, mapa) != -4):
                self.y = newposy
            else:
                if self.vel_y > 0:
                    self.checkMistery(mapa, entities, GetTile)
                self.vel_y = 0
        else:
            self.vel_y = 0
            if GetTile(self.x, self.y - self.delta, mapa) > 0:
                self.y += self.delta
            elif GetTile(self.x, self.y + self.delta, mapa) > 0:
                self.y -= self.delta

        self.vel_x = min(max(self.vel_x + self.elapsed_time*forward*9, -1.5), 2)
        if abs(self.vel_x) > 0.001:
            newposx = max(0, min(len(mapa) - 1, self.x + self.elapsed_time*self.vel_x*2))

            if (GetTile(newposx - self.delta, self.y, mapa) < 1 and GetTile(newposx + self.delta, self.y, mapa) < 1):
                self.x = newposx
            else:
                self.vel_x *= -0.5
        else:
            self.vel_x = 0
            if GetTile(self.x - self.delta, self.y, mapa) > 0:
                self.x += self.delta
            elif GetTile(self.x + self.delta, self.y, mapa) > 0:
                self.x -= self.delta

    def checkMistery(self, mapa, entities, GetTile):
        if GetTile(self.x, self.y + 1, mapa) in [2, -4]:
            mapa[int(self.x)][int(self.y + 1)] = 9
            if GetTile(self.x, self.y + 2, mapa) == -2:
                mapa[int(self.x)][int(self.y + 2)] = 0
                if self.status == 0:
                    entities.insert(0, Entity([3, self.x, self.y + 2])) # mushroom
                else:
                    entities.insert(0, Entity([4, self.x, self.y + 2])) # flower
            elif GetTile(self.x, self.y + 2, mapa) == -3:
                mapa[int(self.x)][int(self.y + 2)] = 0
                entities.insert(0, Entity([6, self.x, self.y + 2])) # life mushroom
            elif GetTile(self.x, self.y + 2, mapa) == -5:
                mapa[int(self.x)][int(self.y + 2)] = 0
                entities.insert(0, Entity([7, self.x, self.y + 2])) # star
            else:
                print('coin')

        if GetTile(self.x, self.y + 1, mapa) == 3 and self.status > 0:
            mapa[int(self.x)][int(self.y + 1)] = 0
        else:
            print('nothing')

if __name__ == '__main__':
    import main