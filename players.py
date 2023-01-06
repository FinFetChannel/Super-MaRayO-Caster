from entities import Entity
import pygame as pg

class Player:
    def __init__(self):
        self.x = 1.5
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
        self.star = 0
        self.hit = 0
        self.points = 0
        self.coins = 0
        self.animation = 0
        self.bonus = 0
        self.enterpipe = 0

    def update(self, mapa, entities, sounds, GetTile):
        """Update the player's attributes based on input and elapsed time."""

        if self.enterpipe > 0:
            self.y -= 0.01
            self.enterpipe -= 1
            if self.enterpipe == 0:
                self.bonus = 1
                pg.mixer.music.fadeout(1000)
                pg.mixer.music.unload()
                pg.mixer.music.load('assets/sounds/under theme.ogg')
                pg.mixer.music.play(-1, 0, 1000)
                self.x = 1.5
                self.y = 12.5
            return 0
        elif self.enterpipe < 0:
            self.y += 0.01
            self.enterpipe += 1
            return 0

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
                sounds['shoot'].play()

        # Determine the player's forward velocity based on keyboard input
        forward = pressed_keys[ord('w')] - pressed_keys[ord('s')]       

        if GetTile(self.x, self.y - self.delta-0.05, mapa) > 0:  # Check if there is floor
            self.vel_y = 0
            if forward == 0:
                self.vel_x = self.vel_x - self.partial_time*self.vel_x*15

            if pressed_keys[pg.K_SPACE]:
                sounds['jump'].play()
                self.vel_y = 7
            if pressed_keys[pg.K_LCTRL] and GetTile(self.x, self.y, mapa) == -6:
                self.enterpipe = 100
                sounds['pipe'].play()
                return 0
        else:
            self.vel_y -= self.partial_time*12 # gravity
       

        if abs(self.vel_y) > 0.001:
            newposy = self.y + self.partial_time*self.vel_y*2
            if (GetTile(self.x, newposy - self.delta, mapa) < 1 and GetTile(self.x, newposy + self.delta, mapa) < 1 and
                GetTile(self.x - self.delta, newposy, mapa) < 1 and (self.vel_y < 0 or GetTile(self.x, newposy + self.delta, mapa) != -4)):
                self.y = newposy
            else:
                if self.vel_y > 0:
                    self.checkMistery(mapa, entities, sounds, GetTile)
                self.vel_y = 0
        else:
            self.vel_y = 0
            if GetTile(self.x, self.y - self.delta, mapa) > 0:
                self.y += self.delta
            elif GetTile(self.x, self.y + self.delta, mapa) > 0:
                self.y -= self.delta

        self.vel_x = min(max(self.vel_x + self.partial_time*forward*9, -2), 3)
        if abs(self.vel_x) > 0.01:
            newposx = max(0, min(len(mapa) - 1, self.x + self.partial_time*self.vel_x*2))

            if (GetTile(newposx - self.delta, self.y, mapa) < 1 and GetTile(newposx + self.delta, self.y, mapa) < 1):
                self.x = newposx
            else:
                self.vel_x *= -0.5
        else:
            self.vel_x = 0
            if GetTile(self.x + 1.5, self.y, mapa) == 7:
                self.bonus = 3
                sounds['pipe'].play()
                return 0
            if GetTile(self.x + 1.5, self.y, mapa) == 10:
                self.bonus = 2
                sounds['pipe'].play()
                return 0
            if GetTile(self.x - self.delta, self.y, mapa) > 0:
                self.x += self.delta
            elif GetTile(self.x + self.delta, self.y, mapa) > 0:
                self.x -= self.delta

    def checkMistery(self, mapa, entities, sounds, GetTile):
        if GetTile(self.x, self.y + 1, mapa) in [2, -4]:
            mapa[int(self.x)][int(self.y + 1)] = 9
            if GetTile(self.x, self.y + 2, mapa) == -2:
                mapa[int(self.x)][int(self.y + 2)] = 0
                sounds['item'].play()
                if self.status == 0:
                    entities.insert(0, Entity([3, int(self.x)+0.5, int(self.y) + 2.35])) # mushroom
                else: # elif self.status == 1:
                    entities.insert(0, Entity([4, int(self.x)+0.5, int(self.y) + 2.35])) # flower
                # else:
                #     entities.insert(0, Entity([6, int(self.x)+0.5, int(self.y) + 2.35])) # life mushroom
            elif GetTile(self.x, self.y + 2, mapa) == -3:
                mapa[int(self.x)][int(self.y + 2)] = 0
                entities.insert(0, Entity([6, int(self.x)+0.5, int(self.y) + 2.35])) # life mushroom
                sounds['item'].play()
            elif GetTile(self.x, self.y + 2, mapa) == -5:
                mapa[int(self.x)][int(self.y + 2)] = 0
                entities.insert(0, Entity([7,  int(self.x)+0.5, int(self.y) + 2.35])) # star
                sounds['item'].play()
            else:
                self.coin(sounds)
                self.points += 200
        elif GetTile(self.x, self.y + 2, mapa) < -10:
            self.coin(sounds)
            self.points += 200
            mapa[int(self.x)][int(self.y + 2)] += 1
            if mapa[int(self.x)][int(self.y + 2)] == -10:
                mapa[int(self.x)][int(self.y + 1)] = 9
                mapa[int(self.x)][int(self.y + 2)] = 0
        elif GetTile(self.x, self.y + 1, mapa) == 3 and self.status > 0:
            mapa[int(self.x)][int(self.y + 1)] = 0
            sounds['break'].play()
    
    def coin(self, sounds):
        self.coins += 1
        sounds['coin'].play()
        if self.coins > 99:
            self.coins = 0
            self.lives += 1
            sounds['powerup'].play()

if __name__ == '__main__':
    import main