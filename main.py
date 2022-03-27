import pygame, sys, math

tick = 0
global_dict = {}
mouse_posx = -100000
mouse_posy = -100000
mouse_posx_old = -100000
mouse_posy_old = -100000

mouse_left_button_down = False

offset_x = 0 
offset_y = 0
offset_scale = 8.0

velocity_x = 0
velocity_y = 0

def set_value(key, value):
    global global_dict
    global_dict[key] = value

def get_value(key):
    global global_dict
    return global_dict[key]

def sign(num):
    if num >= 0:
        return 1
    else:
        return -1

set_value("zoom_kinetic_energy",0)  #缩放动能
set_value("zoom_f",10)   #缩放阻尼系数
set_value("drag_kinetic_energy_x",0)  #水平方向拖拽动能
set_value("drag_kinetic_energy_y",0)  #垂直方向拖拽动能
set_value("drag_f",5)   #拖拽阻尼系数

def zoomAnimationUpdate():  #阻尼缩放动画\
    global offset_scale
    zoom_kinetic_energy = get_value("zoom_kinetic_energy")
    zoom_velocity = math.sqrt(2 * math.fabs(zoom_kinetic_energy)) #单位质量
    zoom_force = get_value("zoom_f") * zoom_velocity
    if zoom_kinetic_energy < 0:
        zoom_velocity = -zoom_velocity
    if (math.fabs(zoom_velocity) < 0.2):
        zoom_velocity = 0
        zoom_kinetic_energy = 0
    else:
        offset_scale = offset_scale + (zoom_velocity  * 0.01) * (offset_scale + 1)
        zoom_kinetic_energy = zoom_kinetic_energy - zoom_force * (zoom_velocity)  * 0.01
        if offset_scale > 64:
            offset_scale = 64
        if offset_scale < 0.5:
            offset_scale = 0.5
    
    set_value("zoom_kinetic_energy",zoom_kinetic_energy)

def dragAnimationUpdate():  #阻尼拖拽动画
    global offset_x
    global offset_y
    drag_kinetic_energy_x = get_value("drag_kinetic_energy_x")
    drag_kinetic_energy_y = get_value("drag_kinetic_energy_y")
    drag_velocity_x = math.sqrt(2 * math.fabs(drag_kinetic_energy_x)) #单位质量
    drag_velocity_y = math.sqrt(2 * math.fabs(drag_kinetic_energy_y))

    drag_force_x = get_value("drag_f") * drag_velocity_x #阻尼定义
    drag_force_z = get_value("drag_f") * drag_velocity_y

    if drag_kinetic_energy_x < 0:
        drag_velocity_x = -drag_velocity_x
    if drag_kinetic_energy_y < 0:
        drag_velocity_y = -drag_velocity_y

    if (math.fabs(drag_velocity_x) + math.fabs(drag_velocity_y) < 1):
        drag_velocity_x = 0
        drag_velocity_y = 0
        drag_kinetic_energy_x = 0
        drag_kinetic_energy_y = 0
    
    else:
        offset_x = offset_x - (drag_velocity_x  * 0.01) 
        offset_y = offset_y - (drag_velocity_y  * 0.01) 
        drag_kinetic_energy_x = drag_kinetic_energy_x - drag_force_x * (drag_velocity_x)  * 0.01
        drag_kinetic_energy_y = drag_kinetic_energy_y - drag_force_z * (drag_velocity_y)  * 0.01

    set_value("drag_kinetic_energy_x",drag_kinetic_energy_x)
    set_value("drag_kinetic_energy_y",drag_kinetic_energy_y)

def animationUpdate():
    zoomAnimationUpdate()
    dragAnimationUpdate()

pygame.init()
size = width, height = 960, 540
screen = pygame.display.set_mode(size)
pygame.display.set_caption("garden")
garden = pygame.image.load("garden.jpeg")

def window2World(wind_x,wind_y):
    world_x = wind_x - (width/2 + offset_x)*100/(16*offset_scale)
    world_y = wind_y - (height/2 + offset_y)*100/(16*offset_scale)
    return (world_x, world_y)

def world2Window(world_x , world_y):
    wind_x = world_x + (width/2 + offset_x)*100/(16*offset_scale)
    wind_y = world_y + (height/2 + offset_y)*100/(16*offset_scale)
    return (wind_x, wind_y)

def render():
    delta_scan = 16
    # if offset_scale > 10:
    #     delta_scan = 64
    center_x = math.floor(offset_x / delta_scan)
    center_y = math.floor(offset_y / delta_scan)
    temp_x = center_x * delta_scan
    temp_y = center_y * delta_scan
    posw = world2Window(temp_x,temp_y)
    garden_rend = pygame.transform.scale(garden, (int(7680*8/offset_scale), int(4320*8/offset_scale)))
    # posw = world2Window(-7680, -4320)
    
    screen.blit(garden_rend, posw)

while(True):
    tick = tick + 1
    for event in pygame.event.get():  # 遍历所有事件
        if event.type == pygame.QUIT:  # 如果单击关闭窗口，则退出
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_button_down = True
                velocity_x = 0
                velocity_y = 0
                set_value("drag_kinetic_energy_x",0) #按下键拖拽时立即消除滑动动能
                set_value("drag_kinetic_energy_y",0)
            if event.button == 3:
                offset_x = 0
                offset_y = 0
                offset_scale = 1

            if event.button == 4:
                zoom_kinetic_energy = get_value("zoom_kinetic_energy") - 1
                set_value("zoom_kinetic_energy",zoom_kinetic_energy)
                
            if event.button == 5:
                zoom_kinetic_energy = get_value("zoom_kinetic_energy") + 1  #假设物体“缩放”的质量为1 ，每次滚动给予1焦耳动能
                set_value("zoom_kinetic_energy",zoom_kinetic_energy)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                set_value("drag_kinetic_energy_x", 0.5 * velocity_x * velocity_x * sign(velocity_x) )
                set_value("drag_kinetic_energy_y", 0.5 * velocity_y * velocity_y * sign(velocity_y) )
                mouse_left_button_down = False

        if event.type == pygame.MOUSEMOTION:
            mouse_posx = event.pos[0]
            mouse_posy = event.pos[1]
            if mouse_left_button_down == True:
                dx = mouse_posx - mouse_posx_old
                dy = mouse_posy - mouse_posy_old
                offset_x = offset_x + (dx * 4 * offset_scale / 100 )
                offset_y = offset_y + (dy * 4 * offset_scale / 100 )
                velocity_x = -dx * 3 * offset_scale
                velocity_y = -dy * 3 * offset_scale
            mouse_posx_old = mouse_posx
            mouse_posy_old = mouse_posy
            # mouseMoveHandler(event.pos[0],event.pos[1])

        if event.type == pygame.QUIT:
            sys.exit()
    pygame.draw.rect(screen,(0,0,0,0),((0,0) ,(width, height)),0)
    render()
    animationUpdate()
    pygame.display.update()