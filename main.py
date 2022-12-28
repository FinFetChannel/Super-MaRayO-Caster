''' #TODO list
- entities sounds
- entities kill player
- cliffs kill player
- lives system
- lives mushrooms
- coins
- timer
- grow shrink mario animation?
- end game
- flag
- door logic
- enter pipe
- splash
- menu
'''
import asyncio
import pygame as pg
from entities import Entity
from players import Player
from renderer import rayCaster, render2D
from maps import read_map

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((800,600))
clock = pg.time.Clock()
font = pg.font.SysFont("Arial", 20, 1)
pg.mouse.set_visible(False)


async def main():
    running = 1
    player = Player()
    horizontal_res = 200
    vertical_res = int(horizontal_res*0.75)
    frame = pg.Surface([horizontal_res, vertical_res])
    mod = 60/horizontal_res
    step = mod*0.07
    pg.event.set_grab(1)
    pg.mixer.music.load('assets/sounds/mario theme.ogg')
    pg.mixer.music.play(-1)
    jump = pg.mixer.Sound('assets/sounds/jump.wav')
    wall = pg.image.load('assets/textures/wall.jpg').convert()
    floor = pg.image.load('assets/textures/floor.jpg').convert()
    pipe = pg.image.load('assets/textures/pipe.jpg').convert()
    pipetop = pg.image.load('assets/textures/pipetop.jpg').convert()
    pipehole = pg.image.load('assets/textures/pipehole.jpg').convert()
    mistery = pg.image.load('assets/textures/mistery.jpg').convert()
    nomistery = pg.image.load('assets/textures/nomistery.jpg').convert()
    door = pg.image.load('assets/textures/door.jpg').convert()
    castle = pg.image.load('assets/textures/castle.jpg').convert()
    block = pg.image.load('assets/textures/block.jpg').convert()
    cloud = pg.image.load('assets/textures/cloud.png').convert_alpha()
    
    sprites = { 'goomba': [pg.image.load('assets/textures/goomba front.png').convert_alpha(),
                           pg.image.load('assets/textures/goomba back.png').convert_alpha(),
                           pg.image.load('assets/textures/goomba back.png').convert_alpha()],
                'koopa': [pg.image.load('assets/textures/koopa front.png').convert_alpha(),
                          pg.image.load('assets/textures/koopa back.png').convert_alpha(),
                          pg.image.load('assets/textures/koopa slide.png').convert_alpha()], 
                'mushroom': [pg.image.load('assets/textures/mushroom.png').convert_alpha()], 
                'flower': [pg.image.load('assets/textures/flower.png').convert_alpha()], 
                'fireball': [pg.image.load('assets/textures/fireball.png').convert_alpha()]
            }

    sky = pg.transform.scale(pg.image.load('assets/textures/skybox.jpg').convert(), (horizontal_res*2, 6*vertical_res))
    textures = [cloud, floor, mistery, wall, block, pipe, pipetop, door, castle, nomistery, pipehole, cloud]

    map_image = pg.image.load('assets/maps/map1.png').convert()
    mapa, entity_data = read_map(map_image)
    entities = []
    for entity in entity_data:
        entities.append(Entity(entity))

    while True:
        player.elapsed_time = clock.tick(60)/1000
        player.total_time += player.elapsed_time
        # p_mouse, pressed_keys = Inputs()
        player.update(mapa, jump, entities, GetTile)
        frame = rayCaster(player, mapa, frame, horizontal_res, vertical_res, mod, textures, sky, step, GetTile)
        
        for i in range(len(entities)):
            if entities[i].status != 'dead':
                # sprite = entities[i].sprite(sprites, player.total_time)
                entities[i].renderSprite(frame, sprites, player, horizontal_res, vertical_res, mapa)
                entities[i].update(mapa, player, entities, GetTile)
                # soft sort entities for drawing, may take a few frames...
                if i > 0 and entities[i].dist2player > entities[i-1].dist2player:
                    entities[i-1], entities[i] = entities[i], entities[i-1]
            elif entities[i].status == 'dead':
                entities.pop(i)
                break

        if player.y < 0 or player.status < 0:
            player.lives -= 1
            player.x = player.y = 3.5
            player.vel_x = player.vel_y = 0

        
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = 0
        
        render2D(frame, map_image, player, entities) # for debug to see where are player and entities
            
        upscaled = pg.transform.scale(frame, [800,600])
        upscaled.blit(font.render(str(round(clock.get_fps(),1)), 1, [255, 255, 255]), [750,0])
        screen.blit(upscaled, (0,0))

        pg.display.update()

        await asyncio.sleep(0)  # very important, and keep it 0
        if not running:
            pg.quit()
            return

def GetTile(x, y, mapa):
    if x < 0 or y < 0 or x > len(mapa) or y > len(mapa[0]): return 0
    else: return mapa[int(x)][int(y)]

asyncio.run( main() )

# do not add anything from here
# asyncio.run is non block on pg-wasm

