
GAS_DENSITY = 2.858
ONE_MPH = 0.44704

MAX_SPEED_MPH = 40.0

class Controller(object):
    def __init__(self, *args, **kwargs):
        # TODO: Implement
        self.throttle_pid = PID(kwargs['throttle_gains'])
        self.yaw_control = YawController(kwargs['wheel_base'], kwargs['steer_ratio'],
                                         kwargs['min_speed'], kwargs['max_lat_accel'],
                                         kwargs['max_steer_angle'],
                                         kwargs['steering_gains']
                                         )
        self.last_t = None
        self.accel_limit = kwargs['accel_limit']
        self.decel_limit = kwargs['decel_limit']
        self.filter = LowPassFilter(0.2,0.1)

    def control(self, *args, **kwargs):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
         Get throttle value from controller
        if self.last_t is None or not dbw_enabled:
            self.last_t = rospy.get_time()
            return 0.0, 0.0, 0.0

        dt = rospy.get_time() - self.last_t

        error_v = min(target_v.x, MAX_SPEED_MPH*ONE_MPH) - current_v.x
        error_v = max(self.decel_limit*dt, min(self.accel_limit*dt, error_v))
        throttle = self.throttle_pid.step(error_v, dt)
        throttle = max(0.0, min(1.0, throttle))
        if error_v < 0:
            brake = -15.0*error_v   # Proportional braking
            brake = max(brake, 1.0)
            throttle = 0.0
        else:
            brake = 0.0

        # # Special case for stopping
        if abs(target_v.x) < 0.1:
            brake = 12.0

        steer = self.yaw_control.get_steering(target_v.x, target_w.z, current_v.x)
        steer = self.filter.filt(steer)
        self.last_t = time.time()
        return throttle, brake, steer
