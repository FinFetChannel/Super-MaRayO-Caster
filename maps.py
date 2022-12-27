def read_map(image):

    color_map = {
        (185, 122, 87): 1,  # brown -> floor block
        (255, 201, 14): 2,  # gold -> mistery block
        (136, 0, 21): 3,    # dark red -> brick block
        (255, 127, 39): 4,  # orange -> block block
        (181, 230, 29): 5,  # light green -> base pipe block
        (34, 177, 76): 6,   # dark green -> top pipe block
        (127, 127, 127): 7, # gray -> door block
        (163, 73, 164): 8, # purple -> castle block
        (255, 255, 255): -1,# white -> cloud block
        (255, 242, 0): -2,  # yellow -> mushroom
    }

    entity_map = {
        (237, 28, 36): 1,  # red -> goomba
        (255, 174, 201): 2,  # pink -> koopa
        
    }

    # Convert the image to a 2D list of integers using the color map
    map_data = []
    entity_data = []
    height = image.get_height()
    for x in range(image.get_width()):
        map_data.append([])
        for y in range(height):
            pixel_color = image.get_at((x, height - y - 1))
            block_type = color_map.get((pixel_color.r, pixel_color.g, pixel_color.b), 0)
            map_data[x].append(block_type)

            entity_type = entity_map.get((pixel_color.r, pixel_color.g, pixel_color.b), 0)
            if entity_type > 0:
                entity_data.append([entity_type, x, y+1])
                image.set_at((x, height - y - 1), (153, 217, 234)) # set pixel blue for minimap
    
    return map_data, entity_data
