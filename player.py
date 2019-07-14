from ursina import *


class PlayerModel(Entity):
    def __init__(self, **kwargs):
        super().__init__(scale=(.04, .08))

        self.e = Entity(parent=self, model='quad', origin_y=-.5, texture='player', double_sided=True)
        self.d = Entity(parent=self.e, model='quad', origin_y=-.5, texture='player', z=.01, rotation_y=30, double_sided=True)
        self.c = Entity(parent=self.e, model='quad', origin_y=-.5, texture='player', z=.01, rotation_y=90, double_sided=True, scale_x=1)
        self.speed = .75

        for key, value in kwargs.items():
            setattr(self, key ,value)



    def step(self, key):
        cur = curve.in_out_sine
        self.e.animate_scale_x(-1, duration=self.speed*.4, curve=cur)
        self.e.animate_scale_x(1, duration=self.speed*.4, curve=cur, delay=self.speed*.4)

        self.e.animate_scale_y(1.05, duration=self.speed*.2, curve=cur)
        self.e.animate_scale_y(1, duration=self.speed*.2, curve=cur, delay=self.speed*.2)
        self.e.animate_scale_y(1.05, duration=self.speed*.2, curve=cur, delay=self.speed*.4)
        self.e.animate_scale_y(1, duration=self.speed*.2, curve=cur, delay=self.speed*.6)
        invoke(self.check_for_hold, key, delay=self.speed*.9)

    def check_for_hold(self, key):
        if held_keys[key]:
            self.step(key)

    def input(self, key):
        if key == 'd':
            self.step(key)
            self.scale_x = .04
        if key == 'a':
            self.step(key)
            self.scale_x = -.04

        if key.endswith(' up'):
            for a in self.animations:
                print(a)
                a.finish()


if __name__ == '__main__':
    app = Ursina()
    camera.fov = 1.5
    PlayerModel()

    app.run()
