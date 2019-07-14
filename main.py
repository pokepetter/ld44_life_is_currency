from ursina import *
# from PIL import Image
# import psd_tools
# from psd_tools import PSDImage
from player import PlayerModel

app = Ursina()

window.title = 'Value of Life'
window.color = color.black
window.exit_button.visible = False
window.fps_counter.visible = False
window.fullscreen = True
mouse.visible = False

bg = Entity(model='quad', scale_x=window.aspect_ratio, texture='climb')
bg.scale *= 2.0
bg.aspect_ratio = bg.scale_x / bg.scale_y

fg = duplicate(bg)
fg.texture = 'climb_fg'
fg.z = -2


player = Entity(
    # model='quad',
    # origin_y=-.5,
    scale=(.06, .06),
    # color=color.orange,
    # texture='player'
    )
player.walk_animation = Animation('player', parent=player, y=.5, fps=6, double_sided=True, enabled=False)
player_idle = Sprite('player_idle', parent=player, y=.5, double_sided=True)
player.followers = list()
player_grid_pos = (0,0)
# player.speed = .00125 * 1.5
player.speed = .001875

collider = Entity(
    parent=bg,
    model='quad',
    z=-.1,
    color=color.clear,
    origin=(-.5, -.5),
    position=(-.5, -.5),
    collider = 'box',
    texture = 'climb_collision',
    # enabled = False,
    )

collider_size = (int(bg.texture.width/16), int(bg.texture.height//16))

if collider.texture == None:
    collider.texture = Texture(Image.new(mode='RGBA', size=collider_size, color=(0,0,0,255)))

collider.texture.filtering = None
collider.color = color.white66
collider.color = color.clear

target_fov = 1.5
camera_target = Entity(model='cube', color=color.clear, z=-1, scale=.1, eternal=True)
camera_target.target = player
max_fov = 2
camera.orthographic = True
# camera.add_script(SmoothFollow(target=camera_target, offset=(0,.25,-50)))
camera.add_script(SmoothFollow(target=camera_target, offset=(0,0,-50)))

def update():
    # collider drawing
    if collider and collider_size and collider.color != color.clear:
        if mouse.left and mouse.hovered_entity == collider:
            grid_position = (
                int(mouse.point[0] * collider_size[0] / 1.5),
                int(mouse.point[1] * collider_size[1] / 1.5),
                )

            if not held_keys['alt']:
                collider.texture.set_pixel(grid_position[0], grid_position[1], color.red)
                collider.texture.apply()
            else:   # erase
                try:
                    for y in range(grid_position[1]-1, grid_position[1]+1):
                        for x in range(grid_position[0]-1, grid_position[0]+1):
                            collider.texture.set_pixel(x, y, color.black)
                    collider.texture.apply()
                except:
                    pass

    # player_movement
    ray = raycast(player.position, (0,0,1), traverse_target=collider, debug=True)
    if ray.hit:
        player_grid_pos = ray.point
    else:
        player_grid_pos = (0,0)

    player_grid_pos = (int(player_grid_pos[0]*collider_size[0]/1.5), int(player_grid_pos[1]*collider_size[1]/1.5))
    free_above = int(collider.texture.get_pixel(player_grid_pos[0], player_grid_pos[1]+1) != (255,0,0,255))

    player.x += held_keys['d'] * player.speed * int(collider.texture.get_pixel(player_grid_pos[0]+1, player_grid_pos[1]+free_above) != (255,0,0,255))
    player.x -= held_keys['a'] * player.speed * int(collider.texture.get_pixel(player_grid_pos[0]-1, player_grid_pos[1]+free_above) != (255,0,0,255))
    player.y += held_keys['w'] * player.speed * free_above
    player.y -= held_keys['s'] * player.speed * int(collider.texture.get_pixel(player_grid_pos[0], player_grid_pos[1]) != (255,0,0,255))

    player.moving = bool(held_keys['w'] + held_keys['a'] + held_keys['s'] + held_keys['d'] > 0)
    player.walk_animation.enabled = player.moving and player.speed != 0
    player_idle.enabled = not player.walk_animation.enabled

    if held_keys['a']:
        player.scale_x = -.06
    if held_keys['d']:
        player.scale_x = .06

    # camera limits
    camera.fov = lerp(camera.fov, target_fov, time.dt * 2)
    camera_target.position = camera_target.target.position
    camera_target.x = clamp(camera_target.x, -(max_fov-camera.fov)/2*bg.aspect_ratio, (max_fov-camera.fov)/2*bg.aspect_ratio)
    camera_target.y = clamp(
        camera_target.y,
        # -((max_fov-camera.fov)/2) - camera.smooth_follow.offset[1],
        # ((max_fov-camera.fov)/2) - camera.smooth_follow.offset[1]
        -((max_fov-camera.fov)/2),
        ((max_fov-camera.fov)/2)
        )


def input(key):
    global target_fov
    global player

    if key == 'c':
        # just change the color so raycast will still hit it
        if not collider.color == color.clear:
            collider.color = color.clear
        else:
            collider.color = color.white66


    if held_keys['control'] and key == 's':
        print('trying to save:', application.asset_folder / 'climb_collision.png')
        collider.texture.save(application.asset_folder / 'climb_collision.png')


        print('trying to save positions:')
        with open('positions.py', 'w') as f:
            print('opened')
            for e in [e for e in scene.entities if isinstance(e, Draggable)]:
                if e in (player, bg, collider, camera_target):
                    continue
                if hasattr(e, 'following') and e.following:
                    print('skip:', e)
                    continue

                print(f'{e.name}.position = ({e.x}, {e.y})')
                f.write(f'{e.name}.position = ({e.x}, {e.y})\n')


        print('saved sucessfully')

    if key == 'tab' or key == 'c':
        camera_target.target = bg
        target_fov = max_fov
    if key == 'tab up' or key == 'c up':
        camera_target.target = player
        target_fov = 1.5

    if key == 'shift':
        player.speed *= 10
    if key == 'shift up':
        player.speed /= 10



from triggers import UseTrigger, Teleporter, CableCar, NPC, TalkativeNPC, ObservatoryDoor, Altar, Sacrifice

player_start = UseTrigger(name='player_start')
door0 = Teleporter(name='door0', player=player)
door1 = Teleporter(name='door1', player=player)
door0.target = door1
door1.target = door0

npc0 = NPC(name='npc0', player=player)
npc1 = NPC(name='npc1', player=player)
npc2 = TalkativeNPC(name='npc2', player=player)

cable_car_0 = CableCar(name='cable_car_0', player=player)
cable_car_1 = CableCar(name='cable_car_1', player=player)
cable_car_0.target = cable_car_1
cable_car_1.target = cable_car_0

altar = Altar(name='altar', player=player) # stop npcs

door2 = Teleporter(name='door2', player=player)
door3 = Teleporter(name='door3', player=player)
door2.target = door3
door3.target = door2

sacrifice_trigger = Sacrifice(name='sacrifice_trigger', player=player, disabled=True)
observatory_door = ObservatoryDoor(name='observatory_door', sacrifice_trigger=sacrifice_trigger, player=player)


# import positions
f = list(application.asset_folder.glob('**/positions.py'))[0]
with open(f, 'r') as f:
    exec(f.read())

player.position = player_start.position
player.z =-1
music = Audio('life_is_currency', pitch=1, loop=True)

input_handler.bind('space', 'e')
input_handler.bind('w', 'arrow up')
input_handler.bind('a', 'arrow left')
input_handler.bind('s', 'arrow down')
input_handler.bind('d', 'arrow right')

app.run()
