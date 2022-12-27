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

def drawSprite(frame, sprite, player, enemy, horizontal_res, vertical_res, rot, mapa):
    """Draw a sprite on a frame in a 3D perspective view."""

    refx, refy = player.x -0.2, player.y+0.1
    offset = int(player.roth*horizontal_res)
    enx, eny = enemy.x, enemy.y

    # Calculate the distance between the player and the sprite
    dist2p = math.sqrt((enx-refx)**2+(eny-refy)**2 + 1e-16)
    enemy.dist2player = dist2p
    if dist2p > 12:
        return frame

    # Calculate the angle between the player and the sprite in radians
    angle = angle2p(refx, refy, enx, eny)
    # Calculate the angle of the sprite relative to the player's field of view in radians
    angle2 = (rot-angle)%(2*math.pi)
    # Convert the angle to degrees
    angle2degree = math.degrees(angle2)
    # Adjust the angle to be within the range of -180 to 180 degrees
    if angle2degree > 180:
        angle2degree = angle2degree - 360
    
    
    # Check if the sprite is within the player's field of view
    if angle2 > 10.5*math.pi/6 or angle2 < 1.5*math.pi/6:
        # Check if there is a clear line of sight between the player and the sprite
        if vision(enx, eny, refx, refy, dist2p, mapa):
            # Calculate the scale of the sprite based on its distance and angle
            scale = min(vertical_res, vertical_res/(dist2p*math.cos(angle2)))
            # Scale the sprite to the correct size
            spsurf = pg.transform.smoothscale(sprite, (scale, scale))
            # Calculate the horizontal position of the sprite on the frame
            hor_coord = (horizontal_res-scale)*0.5 + offset
            # Calculate the vertical position of the sprite on the frame
            vert_coord = (22.5+angle2degree)*vertical_res/45 - scale/2 # 45° vertical FOV
            # Draw the sprite onto the frame
            frame.blit(spsurf, (hor_coord, vert_coord))
        
    return frame

def angle2p(posx, posy, enx, eny):
    """Calculate the angle between two points in radians."""
    # Check if the x-coordinates are equal, return pi/2
    if posx == enx:
        return math.pi/2 # assume eny > posx
    # Calculate the angle using math.atan2
    angle = math.atan2(eny-posy, enx-posx)
    # If the angle is negative, add 2*pi to make it positive
    if angle < 0:
        angle += 2*math.pi

    return angle

def vision(posx, posy, enx, eny, dist2p, mapa):
    # Calculate the cosine and sine of the angle between the two points
    cosine, sine = (posx - enx) / dist2p, (posy - eny) / dist2p
    
    # Set the starting point to the second point
    x, y = enx, eny
    
    # Start a loop to move along the line connecting the two points in small increments
    for i in range(int(dist2p / 0.05)):
        # Increment the current position by a small amount in the direction of the first point
        x, y = x + 0.05 * cosine, y + 0.05 * sine
        
        # Check if the map at the current position is blocked
        if x >= 0 and y >= 0 and x < len(mapa) and y < len(mapa[0]) and mapa[int(x - 0.02)][int(y - 0.02)]:
            # If the map is blocked, return False
            return False
    
    # If the loop completes without finding a blocked point, return True
    return True

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