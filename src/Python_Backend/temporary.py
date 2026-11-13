 def __init__(self, url_status: str, url_back: str, request_timeout: float = 10.0):
        """
        Args:
            url_status: HTTP endpoint to poll Arm1 status (expects JSON with {"status": "..."}).
            url_back: HTTP endpoint to send result back to the laptop server.
            request_timeout: requests timeout seconds.
        """
        self.url_status = url_status
        self.url_back = url_back
        self.request_timeout = request_timeout

        # Create the Arm2 node once and reuse it
        self.arm2 = ARM2_Skills()

    # -------------- Helpers --------------
    
    @staticmethod
    def _to_list(x):
        """Normalize a string or scalar to list; leave list/tuple as-is."""
        if isinstance(x, (list, tuple)):
            return list(x)
        return [x]

    @staticmethod
    def _flatten_pose(coords):
        """
        Accepts either:
          - [x, y, z, rx, ry, rz], or
          - [[x, y, z], [rx, ry, rz]]
        Returns: [x, y, z, rx, ry, rz]
        """
        if not isinstance(coords, (list, tuple)):
            raise ValueError("coords must be a list/tuple")

        # Already flat 6
        if len(coords) == 6 and all(isinstance(v, (int, float)) for v in coords):
            return list(coords)

        # Two triplets
        if (
            len(coords) == 2
            and all(isinstance(c, (list, tuple)) for c in coords)
            and len(coords[0]) == 3
            and len(coords[1]) == 3
        ):
            return list(coords[0]) + list(coords[1])

        raise ValueError(
            "coords must be [x,y,z,rx,ry,rz] or [[x,y,z],[rx,ry,rz]]"
        )

    def _send_data_to_url(self, url: str, data: dict) -> bool:
        """POST JSON to a URL; returns True on 2xx."""
        try:
            resp = requests.post(url, json=data, timeout=self.request_timeout)
            return 200 <= resp.status_code < 300
        except Exception as e:
            print(f"[Arm2Controller] POST to {url} failed: {e}")
            return False

    # -------------- Core methods --------------

    def controller_arm2(
        self,
        subtasks,
        coords_list,
        *,
        approach_z: float = 242.23,
        approach_velocity: float = 4.5,
        work_velocity: float = 1.0,
        tolerance_m: float = 0.01,
        pose_timeout_s: float = 60.0,
        lift_after_mm: float = 100.0,
        settle_after_lock_s: float = 3.0,
        go_home_after_each: bool = True,
    ):
        """
        Execute a sequence of subtasks on Arm2.

        Args:
            subtasks: list like ["lock", ...]
            coords_list: list of poses (each either [x,y,z,rx,ry,rz] or [[x,y,z],[rx,ry,rz]])
            approach_z: initial Z to approach above the target XY.
            approach_velocity: velocity for approach.
            work_velocity: velocity for final reach / lift.
            tolerance_m: pose tolerance in meters for is_pose_ready().
            pose_timeout_s: max seconds to wait for pose readiness.
            lift_after_mm: how much to lift after locking (in mm).
            settle_after_lock_s: wait seconds after lock.
            go_home_after_each: whether to move to home after each subtask.
        """
        arm2 = self.arm2

        for t, task in enumerate(subtasks):
            x, y, z, rx, ry, rz = self._flatten_pose(coords_list[t])

            if task == "lock":
                # 1) XY approach at a safe Z
                arm2.move_to(x, y, approach_z, rx, ry, rz, velocity=approach_velocity)
                # 2) Move down to target
                arm2.move_to(x, y, z, rx, ry, rz, velocity=work_velocity)

                arm2.get_logger().info("Waiting for tool_pose to reach target position...")
                start_wait = time.time()

                # 3) Wait until pose is achieved or timeout
                while rclpy.ok():
                    rclpy.spin_once(arm2)  # process callbacks
                    if arm2.tool_pose and arm2.is_pose_ready(
                        arm2.tool_pose, [x / 1000.0, y / 1000.0, z / 1000.0], tolerance_m
                    ):
                        arm2.get_logger().info("Target reached. Executing lock_screw...")
                        ok = arm2.call_lock_screw()
                        if ok:
                            time.sleep(settle_after_lock_s)
                            arm2.move_to(
                                x,
                                y,
                                z + lift_after_mm,
                                rx,
                                ry,
                                rz,
                                velocity=work_velocity,
                            )
                            arm2.get_logger().info(
                                "Screwdriver task done. Proceeding."
                            )
                            if go_home_after_each:
                                arm2.arm2_home()
                        else:
                            arm2.get_logger().error(
                                "Screwdriver task failed. Halting this subtask."
                            )
                        break

                    if time.time() - start_wait > pose_timeout_s:
                        arm2.get_logger().error(
                            f"Pose wait timeout after {pose_timeout_s} s."
                        )
                        break
            else:
                arm2.get_logger().warn(f"Unsupported subtask: {task}")

    def wait_for_arm1_and_execute_arm2(self, action_2, position_2, poll_interval_s: float = 2.0):
        """
        Block until Arm1 reports status=='completed' (or 'error'),
        then execute Arm2 tasks and send result back.

        Args:
            action_2: str or list[str]
            position_2: str or list[str]
            poll_interval_s: seconds between status polls
        """
        try:
            print("Waiting for Arm1 tasks to complete...")
            while True:
                resp = requests.get(self.url_status, timeout=self.request_timeout)
                if resp.status_code == 200:
                    arm1_status = resp.json()
                    status = arm1_status.get("status", "")
                    if status == "completed":
                        print("Arm1 tasks completed.")
                        break
                    if status == "error":
                        print("Error in Arm1 tasks. Aborting Arm2 execution.")
                        return
                time.sleep(poll_interval_s)

            print("Executing Arm2 tasks...")
            result = self.execute_arm2({"action": action_2, "position": position_2})

            if result:
                print("Arm2 tasks completed.")
                data = {"action": ["home"], "position": ["table"]}
            else:
                print("Arm2 tasks failed.")
                data = {"action": ["fail"], "position": ["table"]}

            time.sleep(5)
            self._send_data_to_url(self.url_back, data)

        except Exception as e:
            print(f"Error while waiting for Arm1 or executing Arm2 tasks: {e}")

    def execute_arm2(self, data: dict) -> bool:
        """
        Route high-level commands to Arm2 skills.

        Expects:
            data = {
              "action": "lock" or ["lock", ...],
              "position": "table" or ["table", ...],
              # Optional:
              # "coords": [[x,y,z,rx,ry,rz], ...] or [[[x,y,z],[rx,ry,rz]], ...]
            }
        """
        success = True
        try:
            actions = self._to_list(data.get("action", []))
            positions = self._to_list(data.get("position", []))
            coords_opt = data.get("coords")  # optional list of poses

            print("Check flow")

            for idx, (action, position) in enumerate(zip(actions, positions)):
                if action == "lock":
                    print("ARM2 move (lock)")

                    # Use provided coords if available; else fallback to your defaults
                    if coords_opt and idx < len(coords_opt):
                        pose = coords_opt[idx]
                    else:
                        # Original snippet had two 3D lists; we accept either form via _flatten_pose
                        pose = [[283.15, -370.72, 242.23], [-179.01, 0.3, 44.17]]

                    self.controller_arm2(
                        subtasks=["lock"],
                        coords_list=[pose],
                    )
                else:
                    print(f"Unsupported task for Arm2: {action}")

        except Exception as e:
            print(f"Error while executing Arm2 tasks: {e}")
            success = False

        return success

    # -------------- Lifecycle --------------

    def shutdown(self):
        """Cleanly destroy the Arm2 node."""
        try:
            if self.arm2 is not None:
                self.arm2.destroy_node()
                self.arm2 = None
        except Exception as e:
            print(f"[Arm2Controller] Error during shutdown: {e}")

    def __del__(self):
        # Best-effort cleanup
        try:
            self.shutdown()
        except Exception:
            pass


# ---------------- Example usage ----------------
# controller = Arm2Controller(
#     url_status="https://<laptop>/arm1_status",
#     url_back="https://<laptop>/arm2_back",
# )
# controller.wait_for_arm1_and_execute_arm2(action_2="lock", position_2="power_supply_5")
# controller.shutdown()
