from scripts.settings import * 

def get_image(path: str, scale: list):
    image: pg.image = pg.image.load(path)
    image = pg.transform.scale(image, (scale[0], scale[1]))
    return image

def render_text(surf, text: str, pos: vec2, offset: vec2, size: int, italic: bool, rgb: tuple, font='arial', bold=True):
    font = pg.font.SysFont(font, size, bold, italic)
    text_surface = font.render(text, False, rgb)
    surf.blit(text_surface, (pos.x + offset.x, pos.y + offset.y))
    return text_surface   

def text_surface(text: str, size: int, italic: bool, rgb: tuple, font='arial', bold=True):
    font = pg.font.SysFont(font, size, bold, italic)
    text_surface = font.render(text, False, rgb)    
    return text_surface

def render_text_box(surf, pos: vec2, size: list[int], color: tuple, hollow: int = 0):
    pg.draw.rect(surf, color, (pos.x, pos.y, size[0], size[1]), hollow)

def mask_collision(mask1, pos1, mask2, pos2): return mask2.overlap(mask1, (pos1.x - pos2.x, pos1.y - pos2.y))

def check_circle_collision(circle1, circle2):
    dist = math.sqrt( math.pow(circle1[0] - circle2[0], 2) + math.pow(circle1[1] - circle2[1], 2) )
    if dist < circle1[2] + circle2[2]: return True
    return False

def distance(px1, px2, py1, py2): return math.sqrt(pow(px1 - px2, 2) + pow(py1 - py2, 2))

def boxes_colliding(box_1, box_2):
    normal: vec2 = vec2(0)
    depth: float = inf

    vertices_1: list[vec2] = box_1.vertices
    vertices_2: list[vec2] = box_2.vertices
    for i in range(len(vertices_1)):
        vertex_a: vec2 = vertices_1[i]
        vertex_b: vec2 = vertices_1[(i + 1) % len(vertices_1)]

        edge: vec2 = vertex_b - vertex_a
        axis: vec2 = vec2(-edge.y, edge.x)

        mn_1, mx_1 = project_vertices(vertices_1, axis)
        mn_2, mx_2 = project_vertices(vertices_2, axis)

        if mn_1 >= mx_2 or mn_2 >= mx_1:
            return vec2(0), 0, false
        axis_depth: float = min(mx_2 - mn_1, mx_1 - mn_2)
        if axis_depth < depth:
            depth = axis_depth
            normal = axis
        
    for i in range(len(vertices_2)):
        vertex_a: vec2 = vertices_2[i]
        vertex_b: vec2 = vertices_2[(i + 1) % len(vertices_2)]

        edge: vec2 = vertex_b - vertex_a
        axis: vec2 = vec2(-edge.y, edge.x)

        mn_1, mx_1 = project_vertices(vertices_1, axis)
        mn_2, mx_2 = project_vertices(vertices_2, axis)

        if mn_1 >= mx_2 or mn_2 >= mx_1:
            return vec2(0), 0, false
        axis_depth: float = min(mx_2 - mn_1, mx_1 - mn_2)
        if axis_depth < depth:
            depth = axis_depth
            normal = axis

    center_1: vec2 = get_mean(vertices_1)
    center_2: vec2 = get_mean(vertices_2)
    direction: vec2 = center_2 - center_1
    if direction.dot(normal) < 0: normal = -normal

    depth /= normal.length()
    normal = normal.normalize() 
    return normal, depth, true

def get_mean(vertices: list[vec2]):
    total_x: float = 0
    total_y: float = 0
    N: int = len(vertices)
    for i in range(N):
        total_x += vertices[i].x
        total_y += vertices[i].y
    return vec2(total_x / float(N), total_y / float(N))

def project_vertices(vertices: list[vec2], axis: vec2):
    mn = inf
    mx = n_inf
    for i in range(len(vertices)):
        vertex: vec2 = vertices[i]
        projection: vec2 = vertex.dot(axis)
        if projection < mn: mn = projection
        if projection > mx: mx = projection
    return mn, mx
