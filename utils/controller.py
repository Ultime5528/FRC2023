import math

from scipy import optimize
import wpimath.trajectory
from wpimath.geometry import Pose2d



class RearWheelFeedbackController:
    def __init__(self, trajectory: wpimath.trajectory.Trajectory):
        self.states = trajectory.states()
        self.left_speed = 0.0
        self.right_speed = 0.0
        self.current_pose = Pose2d()
        self.current_idx = 1

    def _check_idx(self, idx):
        idx = round(float(idx - 0.5))
        return min(max(idx, 1), len(self.states) - 2)

    def _compute_nearest_point(self):
            def calc_distance(idx, *args):
                idx = self._check_idx(idx)
                x = self.states[idx].pose.X()
                y = self.states[idx].pose.Y()
                current_x = self.current_pose.X()
                current_y = self.current_pose.Y()
                return (x - current_x)**2 + (y - current_y)**2

            def calc_distance_jacobian(idx, *args):
                idx = self._check_idx(idx)
                prev_x = self.states[idx - 1].pose.X()
                prev_y = self.states[idx - 1].pose.Y()
                x = self.states[idx].pose.X()
                y = self.states[idx].pose.Y()
                next_x = self.states[idx + 1].pose.X()
                next_y = self.states[idx + 1].pose.Y()

                dx = next_x - prev_x
                dy = next_y - prev_y

                current_x = self.current_pose.X()
                current_y = self.current_pose.Y()

                return 2 * dx * (x - current_x) + 2 * dy * (y - current_y)

            minimum = optimize.fmin_cg(calc_distance, self.current_idx, calc_distance_jacobian, full_output=True, disp=False)
            idx = minimum[0][0]
            error = minimum[1]

            return idx, error

    def update(self, current_pose: Pose2d):
        self.current_pose = current_pose
        current_idx, error = self._compute_nearest_point()
        self.current_idx = self._check_idx(current_idx)
