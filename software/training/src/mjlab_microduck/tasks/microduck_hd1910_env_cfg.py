"""Microduck geometry with LuwuDynamics' public 1910 M6 actuator baseline.

Parameters and provenance: robot/hd1910/. This does not replace the robot's
measured mass/inertia, calibration, or runtime gain/IMU integration.
"""

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

from mjlab.envs import ManagerBasedRlEnvCfg

from mjlab_microduck.actuator.feetech_bam import FeetechBamActuatorCfg
from .microduck_standup_env_cfg import (
    MicroduckStandUpRlCfg,
    make_microduck_standup_env_cfg,
)
from .microduck_velstand_env_cfg import (
    MicroduckVelStandRlCfg,
    make_microduck_velstand_env_cfg,
)
from .microduck_velocity_env_cfg import MicroduckRlCfg, make_microduck_velocity_env_cfg


HD1910_M6_JSON = Path(__file__).resolve().parents[1] / "robot" / "hd1910" / "1910_m6.json"


def _with_hd1910_actuator(cfg: ManagerBasedRlEnvCfg) -> ManagerBasedRlEnvCfg:
    """Replace a task's actuator without changing its robot model or contract."""
    # Task factories may retain references to module-level robot configs. Copy
    # before replacing actuators so the original XL330 tasks remain untouched.
    robot = deepcopy(cfg.scene.entities["robot"])
    assert robot.articulation is not None
    robot.articulation.actuators = (
        FeetechBamActuatorCfg(
            json_path=str(HD1910_M6_JSON),
            target_names_expr=(r"^(?!passive_).*",),
            kp_fw=5.0,
            vin_range=(7.4, 8.0),
            vin_drop_gain_range=(0.0, 0.2),
            vin_min=7.0,
            delay_min_lag=3,
            delay_max_lag=6,
        ),
    )
    cfg.scene.entities["robot"] = robot
    return cfg


def make_microduck_hd1910_velocity_env_cfg(
    play: bool = False,
    rough: bool = False,
) -> ManagerBasedRlEnvCfg:
    cfg = make_microduck_velocity_env_cfg(play=play, rough=rough)
    return _with_hd1910_actuator(cfg)


def make_microduck_hd1910_standup_env_cfg(
    play: bool = False,
    rough: bool = False,
) -> ManagerBasedRlEnvCfg:
    """Create the sitting-to-standing task with HD1910 M6 actuators."""
    cfg = make_microduck_standup_env_cfg(play=play, rough=rough)
    return _with_hd1910_actuator(cfg)


def make_microduck_hd1910_velstand_env_cfg(
    play: bool = False,
    rough: bool = False,
) -> ManagerBasedRlEnvCfg:
    """Create walking plus prone/supine recovery with HD1910 actuators."""
    cfg = make_microduck_velstand_env_cfg(play=play, rough=rough)
    return _with_hd1910_actuator(cfg)


MicroduckHD1910RlCfg = replace(
    deepcopy(MicroduckRlCfg),
    experiment_name="microduck_hd1910_velocity",
    run_name="hd1910_m6_luwu",
    logger="tensorboard",
)


MicroduckHD1910StandUpRlCfg = replace(
    deepcopy(MicroduckStandUpRlCfg),
    experiment_name="microduck_hd1910_standup",
    run_name="hd1910_m6_standup",
    logger="tensorboard",
)


MicroduckHD1910VelStandRlCfg = replace(
    deepcopy(MicroduckVelStandRlCfg),
    experiment_name="microduck_hd1910_velstand",
    run_name="hd1910_m6_velstand",
    logger="tensorboard",
)
