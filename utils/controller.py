import math
from typing import Optional

from scipy import optimize
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.trajectory import Trajectory


class RearWheelFeedbackController:
    def __init__(self, trajectory: Trajectory):
        self.trajectory = trajectory
        self.states = trajectory.states()
        self.left_speed = 0.0
        self.right_speed = 0.0
        self.current_pose = Pose2d()
        self.closest_t = 0
        self.closest_sample: Optional[Trajectory.State] = None

    # def _check_idx(self, idx):
    #     idx = round(float(idx - 0.5))
    #     return min(max(idx, 1), len(self.states) - 2)

    def _update_closest(self):
            def calc_distance(t, *args):
                pose = self.trajectory.sample(t).pose
                x = pose.X()
                y = pose.Y()
                current_x = self.current_pose.X()
                current_y = self.current_pose.Y()
                return (x - current_x)**2 + (y - current_y)**2

            # def calc_distance_jacobian(t, *args):
            #     prev_x = self.states[idx - 1].pose.X()
            #     prev_y = self.states[idx - 1].pose.Y()
            #     x = self.states[idx].pose.X()
            #     y = self.states[idx].pose.Y()
            #     next_x = self.states[idx + 1].pose.X()
            #     next_y = self.states[idx + 1].pose.Y()
            #
            #     dx = next_x - prev_x
            #     dy = next_y - prev_y
            #
            #     current_x = self.current_pose.X()
            #     current_y = self.current_pose.Y()
            #
            #     return 2 * dx * (x - current_x) + 2 * dy * (y - current_y)

            # minimum = optimize.fmin_cg(calc_distance, self.closest_t, calc_distance_jacobian, full_output=True, disp=False)
            res = optimize.minimize_scalar(calc_distance, bounds=(0, self.trajectory.totalTime()), tol=1e-3)
            # idx = minimum[0][0]
            # error = minimum[1]
            self.closest_t = res.x
            self.error = res.fun
            self.closest_sample = self.trajectory.sample(self.closest_t)

    def update(self, current_pose: Pose2d):
        self.current_pose = current_pose
        self._update_closest()

        curvature = self.closest_sample.curvature
        target_yaw = self.closest_sample.pose.rotation()
        delta_translation = self.closest_sample.pose.translation() - self.current_pose.translation()
        d_angle = target_yaw - delta_translation.angle() #   Rotation2d(math.at) pi_2_pi( - math.atan2(dyl, dxl))

        if d_angle.radians() < 0:
            self.error *= -1



