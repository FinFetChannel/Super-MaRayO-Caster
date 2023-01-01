''' #TODO list
- entities sounds
- underworld
- coins underworld
- timer
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
    # pg.mixer.music.load('assets/sounds/mario theme.ogg')
    # pg.mixer.music.play(-1)
    jump = pg.mixer.Sound('assets/sounds/jump.wav')
        
    textures, sprites, misteries = loadTexturesSprites(horizontal_res, vertical_res)
    
    def loadLevel(path):
        map_image = pg.image.load(path).convert()
        mapa, entity_data = read_map(map_image)
        entities = []
        for entity in entity_data:
            entities.append(Entity(entity))
        
        return mapa, entities, map_image

    mapa, entities, map_image = loadLevel('assets/maps/map1.png')

    while True:
        player.partial_time = clock.tick(60)/1000
        player.total_time += player.partial_time

        player.update(mapa, jump, entities, GetTile)
        if player.total_time - player.animation > 0:
            player.animation = player.total_time + 0.2
            textures[2] = misteries[0]
            misteries = misteries[1:] + [misteries[0]]
            for key in sprites:
                for i in range(len(sprites[key])):
                    if key != 'pole':
                        sprites[key][i] = pg.transform.flip(sprites[key][i], flip_x=True, flip_y=False)

        frame = rayCaster(player, mapa, frame, horizontal_res, vertical_res, mod, textures, step, GetTile)
        
        popped = 0
        for i in range(len(entities)):
            index = i + popped
            entity = entities[index]
            if entity.status != 'dead':
                entity.renderSprite(frame, sprites, player, horizontal_res, vertical_res, mapa)
                if entity.status != 'dying':
                    entity.update(mapa, player, entities, GetTile)
               
                if i > 0 and entity.dist2player > entities[index-1].dist2player:# soft sort entities for drawing
                    entities[index-1], entities[index] = entities[index], entities[index-1] # may take a few frames...
            
            elif entities[index].status == 'dead':
                entities.pop(index) # remove dead
                popped -= 1

        if player.y < 0 or player.status < 0:
            player.status = 0
            player.lives -= 1
            player.x = player.y = 3.5
            player.vel_x = player.vel_y = 0
            mapa, entities, map_image = loadLevel('assets/maps/map1.png')

            if player.lives < 1:
                print('restart game')
                player = Player()

        
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = 0
        
        render2D(frame, map_image, player, entities) # for debug to see where are player and entities
            
        upscaled = pg.transform.scale(frame, [800,600])
        upscaled.blit(font.render(str(round(clock.get_fps(),1)), 1, [255, 255, 255]), [750,0])
        upscaled.blit(font.render(str(player.coins)+' '+str(player.points), 1, [255, 255, 255]), [50,0])
        screen.blit(upscaled, (0,0))

        pg.display.update()

        await asyncio.sleep(0)  # very important, and keep it 0
        if not running:
            pg.quit()
            return

def GetTile(x, y, mapa):
    if x < 0 or y < 0 or x > len(mapa) or y > len(mapa[0]): return 0
    else: return mapa[int(x)][int(y)]

def loadTexturesSprites(horizontal_res, vertical_res):
    wall = pg.image.load('assets/textures/wall.jpg').convert()
    floor = pg.image.load('assets/textures/floor.jpg').convert()
    pipe = pg.image.load('assets/textures/pipe.jpg').convert()
    pipetop = pg.image.load('assets/textures/pipetop.jpg').convert()
    pipehole = pg.image.load('assets/textures/pipehole.jpg').convert()
    mistery = pg.image.load('assets/textures/mistery.jpg').convert()
    mistery2 = pg.image.load('assets/textures/mistery2.jpg').convert()
    mistery3 = pg.image.load('assets/textures/mistery3.jpg').convert()
    nomistery = pg.image.load('assets/textures/nomistery.jpg').convert()
    door = pg.image.load('assets/textures/door.jpg').convert()
    castle = pg.image.load('assets/textures/castle.jpg').convert()
    block = pg.image.load('assets/textures/block.jpg').convert()
    cloud = pg.image.load('assets/textures/cloud.png').convert_alpha()
    sky = pg.transform.scale(pg.image.load('assets/textures/skybox.jpg').convert(), (horizontal_res*2, 6*vertical_res))
    misteries = [mistery, mistery, mistery, mistery2, mistery3, mistery2]
    textures = [sky, floor, mistery, wall, block, pipe, pipetop, door, castle, nomistery, pipehole, cloud]
    
    sprites = { 'goomba': [pg.image.load('assets/sprites/goomba front.png').convert_alpha(),
                           pg.image.load('assets/sprites/goomba back.png').convert_alpha(),
                           pg.image.load('assets/sprites/goomba back.png').convert_alpha()],
                'koopa': [pg.image.load('assets/sprites/koopa front.png').convert_alpha(),
                          pg.image.load('assets/sprites/koopa back.png').convert_alpha(),
                          pg.image.load('assets/sprites/koopa slide.png').convert_alpha()], 
                'mushroom': [pg.image.load('assets/sprites/mushroom.png').convert_alpha()], 
                'flower': [pg.image.load('assets/sprites/flower.png').convert_alpha()], 
                'fireball': [pg.image.load('assets/sprites/explosion.png').convert_alpha(),
                             pg.image.load('assets/sprites/fireball.png').convert_alpha()],
                'life': [pg.image.load('assets/sprites/life.png').convert_alpha()],
                'star': [pg.image.load('assets/sprites/star.png').convert_alpha()],
                'pole': [pg.image.load('assets/sprites/pole.png').convert_alpha(), 
                         pg.image.load('assets/sprites/poletop.png').convert_alpha()],
            }
    return textures, sprites, misteries

asyncio.run(main())

# do not add anything from here
# asyncio.run is non block on pg-wasm

