''' #TODO list
- entities sounds
- timer
- end game
- flag
- door logic
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
    dark = pg.Surface(frame.get_size())
    dark.fill((0,0,0))
    dark.set_alpha(100)
    mod = 60/horizontal_res
    step = mod*0.07

    pg.event.set_grab(1)
    pg.mixer.music.load('assets/sounds/mario theme.ogg')
    
        
    textures, sprites, misteries, sounds = loadAssets(horizontal_res, vertical_res)
    
    def loadLevel(path):
        map_image = pg.image.load(path).convert()
        mapa, entity_data = read_map(map_image)
        entities = []
        for entity in entity_data:
            entities.append(Entity(entity))
        
        return mapa, entities, map_image

    mapa, entities, map_image = loadLevel('assets/maps/map1.png')
    mapa_bonus, entities_bonus, map_image_bonus = loadLevel('assets/maps/mapA.png')
    mapa = [mapa, mapa_bonus]
    entities = [entities, entities_bonus]
    hud_string = 'MARIO                                                      WORLD                          TIME'
    hud_text = font.render( hud_string, 1, [255, 255, 255])
    world_text = font.render('1-1', 1, [255, 255, 255])
    texts = ['Super MaRayo Caster',
             '',
             'Click to Start']
    await textScreen(screen, font, texts)
    pg.mixer.music.play(-1, 0, 1000)

    while True:
        player.partial_time = min(0.2, clock.tick(60)/1000)
        player.total_time += player.partial_time

        player.update(mapa[player.bonus], entities[player.bonus], sounds, GetTile)
        if player.bonus == 2:
            for i in range(len(mapa[0])):
                if -7 in mapa[0][i]:
                    player.x = i
                    player.y = mapa[0][i].index(-7)-0.5
                    player.rot = 0
                    player.bonus = 0
                    player.enterpipe = -75
                    pg.mixer.music.fadeout(1000)
                    pg.mixer.music.unload()
                    pg.mixer.music.load('assets/sounds/mario theme.ogg')
                    pg.mixer.music.play(-1, 0, 1000)
                    sounds['pipe'].play()
        elif player.bonus == 3:
            texts[1]= 'You finished with '+str(player.points)+ ' points'
            await textScreen(screen, font, texts)
            player = Player()
            mapa, entities, map_image = loadLevel('assets/maps/map1.png')
            mapa_bonus, entities_bonus, map_image_bonus = loadLevel('assets/maps/mapA.png')
            mapa = [mapa, mapa_bonus]
            entities = [entities, entities_bonus]
            pg.mixer.music.play(-1, 0, 1000)

        if player.total_time - player.animation > 0:
            player.animation = player.total_time + 0.2
            textures[2] = misteries[0]
            misteries = misteries[1:] + [misteries[0]]
            for key in sprites:
                if key != 'pole':
                    for i in range(len(sprites[key])):
                        sprites[key][i] = pg.transform.flip(sprites[key][i], flip_x=True, flip_y=False)

        frame = rayCaster(player, mapa[player.bonus], frame, horizontal_res, vertical_res, mod, textures, step, GetTile)
        
        popped = 0
        for i in range(len(entities[player.bonus])):
            index = i + popped
            entity = entities[player.bonus][index]
            if entity.status != 'dead':
                entity.renderSprite(frame, sprites, player, horizontal_res, vertical_res, mapa[player.bonus])
                if entity.status != 'dying':
                    entity.update(mapa[player.bonus], player, entities[player.bonus], sounds, GetTile)
               
                if i > 0 and entity.dist2player > entities[player.bonus][index-1].dist2player:# soft sort entities for drawing
                    entities[player.bonus][index-1], entities[player.bonus][index] = entities[player.bonus][index], entities[player.bonus][index-1] # may take a few frames...
            
            elif entities[player.bonus][index].status == 'dead':
                entities[player.bonus].pop(index) # remove dead
                popped -= 1

        if player.y < 0 or player.status < 0:
            sounds['die'].play()
            player.status = 0
            player.lives -= 1
            player.x = 3.5
            player.y = 12.5
            player.vel_x = player.vel_y = 0
            mapa, entities, map_image = loadLevel('assets/maps/map1.png')
            mapa_bonus, entities_bonus, map_image_bonus = loadLevel('assets/maps/mapA.png')
            mapa = [mapa, mapa_bonus]
            entities = [entities, entities_bonus]

            if player.lives < 1:
                texts[1]= 'You died with '+str(player.points)+ ' points'
                await textScreen(screen, font, texts)
                player = Player()

        
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = 0
        
        if player.bonus:
            frame.blit(dark, (0,0))

        # render2D(frame, map_image, player, entities[player.bonus]) # for debug to see where are player and entities
        
        
        upscaled = pg.transform.scale(frame, [800,600])
        
        upscaled.blit(font.render(str(round(clock.get_fps(),1)), 1, [255, 255, 255]), [750, 5])

        upscaled.blit(hud_text, [50, 5])


        display_points = (6-len(str(player.points)))*'0'+str(player.points)
        display_coins = 'x' + (2-len(str(player.coins)))*'0'+str(player.coins)
        display_timer = str(400 - int(player.total_time*2))
        upscaled.blit(font.render(display_points, 1, [255, 255, 255]), [50,25])
        upscaled.blit(font.render(display_coins, 1, [255, 255, 255]), [300,25])
        upscaled.blit(world_text, [460,25])
        upscaled.blit(font.render(display_timer, 1, [255, 255, 255]), [680,25])
        upscaled.blit(sprites['coin'][1], [270,25])
        
        screen.blit(upscaled, (0,0))
        pg.display.update()

        await asyncio.sleep(0)  # very important, and keep it 0
        if not running:
            pg.quit()
            return

def GetTile(x, y, mapa):
    if x < 0 or y < 0 or x > len(mapa) or y > len(mapa[0]): return 0
    else: return mapa[int(x)][int(y)]

def loadAssets(horizontal_res, vertical_res):
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
                'coin': [pg.image.load('assets/sprites/coin.png').convert_alpha(),
                         pg.image.load('assets/sprites/minicoin.png').convert_alpha()],
                'pole': [pg.image.load('assets/sprites/pole.png').convert_alpha(), 
                         pg.image.load('assets/sprites/poletop.png').convert_alpha()],
            }
    sounds = {  'break': pg.mixer.Sound('assets/sounds/break.ogg'),
                'coin': pg.mixer.Sound('assets/sounds/coin.wav'),
                'die': pg.mixer.Sound('assets/sounds/die.wav'),
                'item': pg.mixer.Sound('assets/sounds/item.wav'),
                'jump': pg.mixer.Sound('assets/sounds/jump.ogg'),
                'kill': pg.mixer.Sound('assets/sounds/kill.wav'),
                'pipe': pg.mixer.Sound('assets/sounds/pipe.ogg'),
                'pole': pg.mixer.Sound('assets/sounds/pole.wav'),
                'powerup': pg.mixer.Sound('assets/sounds/powerup.ogg'),
                'shoot': pg.mixer.Sound('assets/sounds/shoot.ogg'),

            }

    return textures, sprites, misteries, sounds

async def textScreen(screen, font, texts):
    while 1:
        screen.fill((0,0,0))
        y_coord = 100
        for text in texts:
            text_surf = font.render(text, 1, [255, 255, 255])
            screen.blit(text_surf, (100, y_coord))
            y_coord += 100

        mouse_pos = pg.mouse.get_pos()
        pg.draw.polygon(screen, (255,0,0), [mouse_pos, [mouse_pos[0], mouse_pos[1]+15],  [mouse_pos[0] +10, mouse_pos[1]+10]])
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                return 0
        
        await asyncio.sleep(0)

asyncio.run(main())

# do not add anything from here
# asyncio.run is non block on pg-wasm

