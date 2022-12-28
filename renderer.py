import math
import pygame as pg

def rayCaster(player, mapa, frame, horizontal_res, vertical_res, mod, textures, sky, step, GetTile):
    """Render a first person view of a 3D world using a ray casting algorithm."""
    # Blit the sky onto the frame
    frame.blit(sky, (-0.5*vertical_res +player.roth*vertical_res, -2*horizontal_res +player.rot*horizontal_res))
    # Set the reference position for the rays to be cast from
    refx, refy = player.x -0.2, player.y+0.1
    # Set the horizontal offset for the frame
    offset = int(player.roth*horizontal_res)

    for i in range(vertical_res): # Iterate over each point on the frame
        # Calculate the direction of the ray for this point
        rot_i = player.rot + math.radians(i*mod - 22.5)
        # Set the initial position of the ray
        x, y = refx, refy 
        # Calculate the step size for the ray
        sin, cos = (step*math.sin(rot_i), step*math.cos(rot_i))
        # Skip the first steps inside the player
        n = 15
        # Update the position of the ray
        x, y = x + cos*n, y + sin*n

        for ray in range(300): # Coarse ray loop
            # Check for collisions with the map and break if a collision is found
            tile = GetTile(x + cos*5, y + sin*5, mapa)
            if tile != 0 and tile >= -1:# or GetTile(x + cos*10, y + sin*10, mapa) != 0:
                break
            # Update the position of the ray
            x, y = (x + cos*5, y + sin*5)
            # Increment the number of steps taken
            n = n+5

        for ray in range(100): # Fine ray loop
            # Update the position and number of steps taken
            x, y, n = x + cos, y + sin, n+1
            
            # Get the block at the current position
            tile = GetTile(x, y, mapa)
            
            # If a block was found, render it on the frame
            if tile != 0 and tile >= -1:
                # Calculate the scale of the block based on its distance from the player
                scale = horizontal_res/(step*n*math.cos(math.radians(i*mod-30)))
                
                # Certain types of blocks are wider
                if tile in [-1, 1, 6, 7, 8]:#== 1 or tile == 6 or tile == -1:
                    scale = scale*1.2
                
                # top of pipes
                if tile == 6 and GetTile(x, y+0.05, mapa) == 0:
                    tile = 10
                
                # Calculate the x-coordinate of the block's texture
                xx = x%1
                if xx < 0.03 or xx > 0.97:xx = 1-y%1

                # Extract a horizontal subsurface of the texture and resize it to the correct scale
                subsurface = pg.Surface.subsurface(textures[tile], (0, int(100*xx), 99, 1))
                resized = pg.transform.scale(subsurface, (scale,1))
                # Blit the resized texture onto the frame
                frame.blit(resized, ((horizontal_res-scale)*0.5 + offset, vertical_res - i -1))

                break

    return frame

def render2D(frame, map_image, player, enemies):
    # Draw the map image as the background of the frame
    frame.blit(map_image, (0, 0))

    # Loop through the enemies and draw a pink pixel on the frame for each alive enemy
    for i in range(len(enemies)):
        # if enemies[i].alive:
        frame.set_at((int(enemies[i].x), int(map_image.get_height() - enemies[i].y)), (255, 0, 255))            

    # Draw the player pixel on the frame
    frame.set_at((int(player.x), int(map_image.get_height() - player.y)), (150, 150, 255))


if __name__ == '__main__':
    import main