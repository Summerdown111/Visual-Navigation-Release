import tensorflow as tf
import tensorflow.contrib.eager as tfe


class Trajectory(object):
    """
    The base class for the trajectory of a ground vehicle.
    n is the batch size and k is the # of time steps in the trajectory.
    """

    def __init__(self, dt, n, k, position_nk2=None, speed_nk1=None, acceleration_nk1=None, heading_nk1=None,
                 angular_speed_nk1=None, angular_acceleration_nk1=None,
                 dtype=tf.float32, variable=True, direct_init=False):

        # Check dimensions now to make your life easier later
        if position_nk2 is not None:
            assert(n == position_nk2.shape[0])
            assert(k == position_nk2.shape[1])

        # Discretization step
        self.dt = dt

        # Number of timesteps
        self.k = k

        # Batch Size
        self.n = n

        self.vars = []
        # When these are already all tensorflow object use direct-init
        if direct_init:
            self._position_nk2 = position_nk2
            self._speed_nk1 = speed_nk1
            self._acceleration_nk1 = acceleration_nk1
            self._heading_nk1 = heading_nk1
            self._angular_speed_nk1 = angular_speed_nk1
            self._angular_acceleration_nk1 = angular_acceleration_nk1
        else:
            if variable:
                # Translational trajectories
                self._position_nk2 = tfe.Variable(tf.zeros([n, k, 2], dtype=dtype) if position_nk2 is None
                                                  else position_nk2)
                self._speed_nk1 = tfe.Variable(tf.zeros([n, k, 1], dtype=dtype) if speed_nk1 is None
                                               else tf.constant(speed_nk1, dtype=dtype))
                self._acceleration_nk1 = tfe.Variable(tf.zeros([n, k, 1], dtype=dtype) if acceleration_nk1 is None
                                                      else tf.constant(acceleration_nk1, dtype=dtype))

                # Rotational trajectories
                self._heading_nk1 = tfe.Variable(tf.zeros([n, k, 1], dtype=dtype) if heading_nk1 is None
                                                 else tf.constant(heading_nk1, dtype=dtype))
                self._angular_speed_nk1 = tfe.Variable(tf.zeros([n, k, 1], dtype=dtype) if angular_speed_nk1 is None
                                                       else tf.constant(angular_speed_nk1, dtype=dtype))
                self._angular_acceleration_nk1 = tfe.Variable(
                    tf.zeros([n, k, 1], dtype=dtype) if angular_acceleration_nk1 is None
                    else tf.constant(angular_acceleration_nk1, dtype=dtype))

                self.vars = [self._position_nk2, self._speed_nk1,
                             self._acceleration_nk1, self._heading_nk1,
                             self._angular_speed_nk1, self._angular_speed_nk1]
            else:
                # Translational trajectories
                self._position_nk2 = tf.zeros([n, k, 2], dtype=dtype) if position_nk2 is None \
                                                  else tf.constant(position_nk2, dtype=dtype)
                self._speed_nk1 = tf.zeros([n, k, 1], dtype=dtype) if speed_nk1 is None \
                                               else tf.constant(speed_nk1, dtype=dtype)
                self._acceleration_nk1 = tf.zeros([n, k, 1], dtype=dtype) if acceleration_nk1 is None \
                                                      else tf.constant(acceleration_nk1, dtype=dtype)

                # Rotational trajectories
                self._heading_nk1 = tf.zeros([n, k, 1], dtype=dtype) if heading_nk1 is None \
                                                 else tf.constant(heading_nk1, dtype=dtype)
                self._angular_speed_nk1 = tf.zeros([n, k, 1], dtype=dtype) if angular_speed_nk1 is None \
                                                       else tf.constant(angular_speed_nk1, dtype=dtype)
                self._angular_acceleration_nk1 = tf.zeros([n, k, 1], dtype=dtype) if angular_acceleration_nk1 is None \
                    else tf.constant(angular_acceleration_nk1, dtype=dtype)

    @classmethod
    def new_traj_from_batch_idx(cls, traj, batch_idx=0):
        """ A utility function for creating a new trajectory
        object corresponding to the trajectory stored at
        the batch index indicated by batch_idx in traj """
        return cls(dt=traj.dt, n=1, k=traj.k,
                   position_nk2=traj.position_nk2()[batch_idx:batch_idx+1],
                   speed_nk1=traj.speed_nk1()[batch_idx:batch_idx+1],
                   acceleration_nk1=traj.acceleration_nk1()[batch_idx:batch_idx+1],
                   heading_nk1=traj.heading_nk1()[batch_idx:batch_idx+1],
                   angular_speed_nk1=traj.angular_speed_nk1()[batch_idx:batch_idx+1],
                   angular_acceleration_nk1=traj.angular_acceleration_nk1()[batch_idx:batch_idx+1])

    @property
    def trainable_variables(self):
        return self.vars

    @property
    def shape(self):
        return '(%d, %d)'%(self.n, self.k)

    def position_nk2(self):
        return self._position_nk2

    def speed_nk1(self):
        return self._speed_nk1

    def acceleration_nk1(self):
        return self._acceleration_nk1

    def heading_nk1(self):
        return self._heading_nk1

    def angular_speed_nk1(self):
        return self._angular_speed_nk1

    def angular_acceleration_nk1(self):
        return self._angular_acceleration_nk1

    def position_and_heading_nk3(self):
        return tf.concat([self.position_nk2(), self.heading_nk1()], axis=2)

    def speed_and_angular_speed(self):
        return tf.concat([self.speed_nk1(), self.angular_speed_nk1()], axis=2)

    def position_heading_speed_and_angular_speed_nk5(self):
        return tf.concat([self.position_and_heading_nk3(),
                          self.speed_and_angular_speed()], axis=2)

    def append_along_time_axis(self, trajectory):
        """ Utility function to concatenate trajectory
        over time. Useful for assembling an entire
        trajectory from multiple sub-trajectories. """
        self._position_nk2 = tf.concat([self.position_nk2(),
                                        trajectory.position_nk2()],
                                       axis=1)
        self._speed_nk1 = tf.concat([self.speed_nk1(), trajectory.speed_nk1()],
                                    axis=1)
        self._acceleration_nk1 = tf.concat([self.acceleration_nk1(),
                                            trajectory.acceleration_nk1()],
                                           axis=1)
        self._heading_nk1 = tf.concat([self.heading_nk1(),
                                       trajectory.heading_nk1()], axis=1)
        self._angular_speed_nk1 = tf.concat([self.angular_speed_nk1(),
                                             trajectory.angular_speed_nk1()],
                                            axis=1)
        self._angular_acceleration_nk1 = tf.concat([self.angular_acceleration_nk1(),
                                                    trajectory.angular_acceleration_nk1()],
                                                   axis=1)
        self.k = self.k + trajectory.k

    def clip_along_time_axis(self, horizon):
        """ Utility function for clipping a trajectory along
        the time axis. Useful for clipping a trajectory within
        a specified horizon."""
        if self.k == horizon:
            return

        self._position_nk2 = self._position_nk2[:, :horizon]
        self._speed_nk1 = self._speed_nk1[:, :horizon]
        self._acceleration_nk1 = self._acceleration_nk1[:, :horizon]
        self._heading_nk1 = self._heading_nk1[:, :horizon]
        self._angular_speed_nk1 = self._angular_speed_nk1[:, :horizon]
        self._angular_acceleration_nk1 = self._angular_acceleration_nk1[:, :horizon]
        self.k = horizon

    def render(self, ax, batch_idx=0, freq=4):
        xs = self._position_nk2[batch_idx, :, 0]
        ys = self._position_nk2[batch_idx, :, 1]
        thetas = self._heading_nk1[batch_idx]
        ax.plot(xs, ys, 'r-')
        ax.quiver(xs[::freq], ys[::freq],
                  tf.cos(thetas[::freq]), tf.sin(thetas[::freq]))


class State(Trajectory):
    """
    A class representing robot state using a trajectory of
    time duration = 1 step.
    """

    def __init__(self, dt, n, k, position_nk2=None, speed_nk1=None, acceleration_nk1=None, heading_nk1=None,
                 angular_speed_nk1=None, angular_acceleration_nk1=None,
                 dtype=tf.float32, variable=True, direct_init=False):
        assert(k == 1)
        super().__init__(dt, n, k, position_nk2, speed_nk1, acceleration_nk1,
                         heading_nk1, angular_speed_nk1,
                         angular_acceleration_nk1, dtype=tf.float32,
                         variable=variable, direct_init=direct_init)

    @classmethod
    def broadcast_batch_size_to(cls, state, n):
        """ A utility method to create a new
            state object thats broadcasts
            a state of batch size 1 to
            batch size n """
        if state.n == n:
            return state

        assert(state.n == 1 == state.position_nk2().shape[0].value)
        k = state.k
        position_1k2 = state.position_nk2()
        speed_1k1 = state.speed_nk1()
        acceleration_1k1 = state.acceleration_nk1()
        heading_1k1 = state.heading_nk1()
        angular_speed_1k1 = state.angular_speed_nk1()
        angular_acceleration_1k1 = state.angular_acceleration_nk1()
        return cls(dt=state.dt, n=n, k=k,
                   position_nk2=tf.broadcast_to(position_1k2, (n, k, 2)),
                   speed_nk1=tf.broadcast_to(speed_1k1, (n, k, 1)),
                   acceleration_nk1=tf.broadcast_to(acceleration_1k1, (n, k, 1)),
                   heading_nk1=tf.broadcast_to(heading_1k1, (n, k, 1)),
                   angular_speed_nk1=tf.broadcast_to(angular_speed_1k1, (n, k, 1)),
                   angular_acceleration_nk1=tf.broadcast_to(angular_acceleration_1k1, (n, k, 1)))

    @classmethod
    def init_state_from_trajectory_time_index(cls, trajectory, t):
        """ A utility method to initialize a state object
        from a particular timestep of a given trajectory object"""
        position_nk2 = trajectory.position_nk2()
        speed_nk1 = trajectory.speed_nk1()
        acceleration_nk1 = trajectory.acceleration_nk1()
        heading_nk1 = trajectory.heading_nk1()
        angular_speed_nk1 = trajectory.angular_speed_nk1()
        angular_acceleration_nk1 = trajectory.angular_acceleration_nk1()

        if t == -1:
            return cls(dt=trajectory.dt, n=trajectory.n, k=1,
                       position_nk2=position_nk2[:, t:],
                       speed_nk1=speed_nk1[:, t:],
                       acceleration_nk1=acceleration_nk1[:, t:],
                       heading_nk1=heading_nk1[:, t:],
                       angular_speed_nk1=angular_speed_nk1[:, t:],
                       angular_acceleration_nk1=angular_acceleration_nk1[:, t:])

        return cls(dt=trajectory.dt, n=trajectory.n, k=1,
                   position_nk2=position_nk2[:, t:t+1],
                   speed_nk1=speed_nk1[:, t:t+1],
                   acceleration_nk1=acceleration_nk1[:, t:t+1],
                   heading_nk1=heading_nk1[:, t:t+1],
                   angular_speed_nk1=angular_speed_nk1[:, t:t+1],
                   angular_acceleration_nk1=angular_acceleration_nk1[:, t:t+1])
