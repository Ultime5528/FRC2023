import math
from typing import Optional

from scipy import optimize
from wpimath.geometry import Pose2d
from wpimath.trajectory import Trajectory

from utils.property import autoproperty


class RearWheelFeedbackController:
    """
    Adapted from: https://github.com/AtsushiSakai/PythonRobotics/blob/master/PathTracking/rear_wheel_feedback/rear_wheel_feedback.py
    """

    def __init__(self, trajectory: Trajectory, angle_factor=2.5, track_error_factor=30.0):
        self.trajectory = trajectory
        self.current_pose = Pose2d()
        self.closest_t = 0
        self.closest_sample: Optional[Trajectory.State] = None
        self.angle_factor = angle_factor
        self.track_error_factor = track_error_factor

    def _update_closest(self):
            def calc_distance(t, *args):
                pose = self.trajectory.sample(t).pose
                x = pose.X()
                y = pose.Y()
                current_x = self.current_pose.X()
                current_y = self.current_pose.Y()
                return (x - current_x)**2 + (y - current_y)**2

            res = optimize.minimize_scalar(calc_distance, bounds=(0, self.trajectory.totalTime()))

            self.closest_t = res.x
            self.error = res.fun
            self.closest_sample = self.trajectory.sample(self.closest_t)

    def update(self, current_pose: Pose2d, angle_factor: Optional[float] = None, track_error_factor: Optional[float] = None):
        if angle_factor is not None:
            self.angle_factor = angle_factor

        if track_error_factor is not None:
            self.track_error_factor = track_error_factor

        self.current_pose = current_pose
        self._update_closest()

        curvature = self.closest_sample.curvature
        target_yaw = self.closest_sample.pose.rotation()
        delta_translation = self.closest_sample.pose.translation() - self.current_pose.translation()
        d_angle = target_yaw - delta_translation.angle()

        if d_angle.radians() < 0:
            self.error *= -1

        angle_error = self.current_pose.rotation() - self.closest_sample.pose.rotation()

        omega = curvature * angle_error.cos() / (1.0 - curvature * self.error)
        omega -= self.angle_factor * angle_error.radians()
        omega -= self.track_error_factor * angle_error.sin() * self.error / angle_error.radians()

        if angle_error.radians() == 0.0 or omega == 0.0:
            delta = 0
        else:
            delta = math.atan2(omega, 1.0)

        return delta
