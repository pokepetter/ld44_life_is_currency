from ursina import *


class UseTrigger(Draggable):

    use_key = 'space'

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = scene
        self.z = -1
        self.scale = .04
        self.color = color.clear
        self.model = 'sphere'
        self.collision = False

        self.dot = Entity(parent=self, model='sphere', world_scale=.25*.05, y=.5, z=-1, color=color.white66, enabled=False)
        self.radius = self.scale_x
        self.require_key = 'tab'
        self.use_key = UseTrigger.use_key
        self.disabled = False

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        super().update()
        if not hasattr(self, 'player') or not self.player or self.disabled:
            return

        self.dot.enabled = distance_2d(self.world_position, self.player.world_position) < self.radius


    def input(self, key):
        super().input(key)
        if key == 'tab':
            self.color = color.white33
            self.collision = True
        if key == 'tab up':
            self.color = color.clear
            self.collision = False

        if key == self.use_key and self.dot.enabled and hasattr(self, 'use'):
            try:
                self.use()
            except Exception as e:
                print(e)

            if isinstance(self.use, str):
                try:
                    exec(self.use)
                except:
                    print('invalid use string:', self.use)


class Teleporter(UseTrigger):

    def use(self):
        self.player.position = self.target.position
        for f in self.player.followers:
            if f.following:
                f.position = self.player.position
        # camera.overlay.fade_in(.4)
        # invoke(setattr, self.player, 'position', self.target.position, delay=.4)
        # camera.overlay.fade_out(.4, delay=.5)

class CableCar(Teleporter):
    def __init__(self, **kwargs):
        super().__init__()

        self.on_cooldown = False

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        super().update()
        self.disabled = len(self.player.followers) < 3


    def use(self):
        if len(self.player.followers) < 3 or self.on_cooldown:
            return

        camera.overlay.fade_in(duration=.4)

        invoke(setattr, self.player, 'position', self.target.position, delay=.4)
        for f in self.player.followers:
            if f.following:
                invoke(setattr, f, 'position', self.target.position, delay=.4)

        self.target.on_cooldown = True
        invoke(setattr, self.target, 'on_cooldown', False, delay=1)

        camera.overlay.fade_out(duration=.4, delay=.5)


class NPC(UseTrigger):
    def __init__(self, player, **kwargs):
        super().__init__()
        self.player = player
        self.walk_animation = Animation('player_walk', parent=self, y=.5, fps=6, double_sided=True)
        self.player_idle = Sprite('player_idle', parent=self, y=.5, double_sided=True)
        self.scale = player.scale
        self.following = False
        self.i = 0
        self.walk_animation.color = color.color(0, .3, 1)
        self.player_idle.color = color.color(0, .3, 1)

        self.scale = self.player.scale
        self.dot.world_scale = .25*.05

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def update(self):
        super().update()
        self.walk_animation.enabled = self.player.moving and self.following
        self.player_idle.enabled = not self.walk_animation.enabled
        if self.following:
            self.dot.enabled = False

        if self.following and self.player.moving:
            self.scale = self.player.scale
            self.position = lerp(
                self.position,
                Vec3(
                    self.player.x - ((held_keys['d'] - held_keys['a']) * .01*self.i),
                    self.player.y - ((held_keys['w'] - held_keys['s']) * .01*self.i),
                    self.player.z
                    ),
                time.dt * 10
                )
            # self.x = self.player.x - ((held_keys['d'] - held_keys['a']) * .01*self.i)
            # self.y = self.player.y - ((held_keys['w'] - held_keys['s']) * .01*self.i)
            self.z = self.player.z - (held_keys['w'] * .01) + (held_keys['s'] * .01)

        # self.following = held_keys['f']

    def use(self):
        self.player.followers.append(self)
        self.i = len(self.player.followers)
        self.following = True


class TalkativeNPC(NPC):

    def use(self):
        lines = '''
            I've changed my mind,
            I don't want to leave this world.
            <lime>I'm sorry,
            <lime>but there's no going back.
            <lime>We agreed.
            '''.split('\n')
        lines = [l.strip() for l in lines if l != '']
        # print(lines)
        lines = [Text(l, parent=self, position=(.5,1.5), origin=(0,0), enabled=False, world_scale=2) for l in lines]
        for l in lines:
            if hasattr(l, 'raw_text') and l.raw_text.startswith('<lime>'):
                l.parent = self.player
                l.y = -.5
                l.x = -.25

            l.world_parent = scene
            l.enabled = False

        self.seq = Sequence()
        # original_player_speed = self.player.speed
        self.player.speed = 0
        self.disabled = True
        self.dot.enabled = False
        speed = .1

        for l in lines:
            # self.seq.append(Wait(.5))
            self.seq.append(Func(l.appear, speed))
            self.seq.append(Wait((len(l.text) * speed) + 2))
            self.seq.append(Func(setattr, l, 'enabled', False))

        # self.seq.append(Wait(1))
        self.seq.append(Func(super().use))
        self.seq.append(Func(setattr, self.player, 'speed', .001875))

        self.seq.start()

    def input(self, key):
        super().input(key)
        if key == 'escape' and hasattr(self, 'seq'):
            self.seq.finish()


class Altar(UseTrigger):

    def use(self):
        for f in self.player.followers:
            f.following = False

        self.disabled = True


class ObservatoryDoor(UseTrigger):
    def __init__(self, **kwargs):
        super().__init__()

        self.opened_eyes = False
        self.moon_open = Animation('moon', fps=3, parent=camera.ui, scale=(16/9,1), loop=False, enabled=False, autoplay=False)
        self.moon_loop = Animation('moon_loop', fps=3, parent=camera.ui, scale=(16/9,1), loop=True, enabled=False, autoplay=False)

        for key, value in kwargs.items():
            setattr(self, key ,value)


    def use(self):
        # print('use')
        if self.opened_eyes == False:
            print('look at moon')
            camera.overlay.fade_in(duration=.2)
            invoke(setattr, self.moon_open, 'enabled', True, delay=.2)
            camera.overlay.fade_out(duration=.5, delay=.4)
            invoke(self.moon_open.start, delay=.4)
            self.disabled = True
            invoke(self.moon_loop.start, delay=2.4)
            invoke(setattr, self.moon_open, 'enabled', False, delay=2.5)
            invoke(setattr, self, 'disabled', False, delay=2.5)
            self.opened_eyes = True
            self.sacrifice_trigger.disabled = False
            invoke(print, 'look at moon finished', delay=2.5)
            return

        if self.opened_eyes:
            camera.overlay.fade_in(duration=.2)
            invoke(setattr, self.moon_loop, 'enabled', not self.moon_loop.enabled, delay=.2)
            # self.moon_loop.enabled = not self.moon_loop.enabled
            camera.overlay.fade_out(duration=.5, delay=.4)


class Sacrifice(UseTrigger):

    def use(self):
        self.player.speed = 0
        camera.overlay.fade_in(duration=2, delay=1)
        lines = '''
            And so their blood were spilled,
            the beings created from him.
            After sacrificing himself
            three times.
            He was finally able to witness
            <red>The End
            '''.split('\n')
        lines = [l.strip() for l in lines if l != '']
        # print(lines)
        lines = [Text(l, parent=camera.overlay, position=(0,0,-.1), origin=(0,0), enabled=False, world_scale=2) for l in lines]
        for l in lines:
            l.enabled = False
            l.world_scale = 50

        self.seq = Sequence()
        self.seq.append(Wait(3))
        self.seq.append(Wait(.5))
        speed = .05

        for l in lines:
            self.seq.append(Wait(.5))
            self.seq.append(Func(l.appear, speed))
            self.seq.append(Wait((len(l.text) * speed) + 1.5))
            self.seq.append(Func(setattr, l, 'enabled', False))

        self.seq.append(Func(setattr, window.exit_button, 'enabled', True))
        self.seq.append(Func(setattr, window.exit_button, 'position', (0,0)))
        self.seq.append(Func(setattr, window.exit_button.text_entity, 'text', 'exit'))
        self.seq.append(Wait(5))
        self.seq.append(Func(application.quit))

        self.seq.start()

        self.disabled = True

    # def input(self, key):
    #     super().input(key)
    #     if key == 'escape' and hasattr(self, 'seq'):
    #         self.seq.finish()


if __name__ == '__main__':
    app = Ursina()
    # UseTrigger()
    p = Entity(moving=False)
    # NPC(p)
    # TalkativeNPC(p).use()
    # od = ObservatoryDoor()
    # Sacrifice(player=p).use()
    # def input(key):
    #     if key == 'space':
    #         od.use()
    app.run()
