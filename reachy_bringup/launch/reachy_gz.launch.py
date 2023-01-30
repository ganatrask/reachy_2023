from launch import LaunchDescription, LaunchContext
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.descriptions import ParameterValue
from launch_ros.actions import Node, SetUseSimTime
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    controllers_file_arg = DeclareLaunchArgument(
        'controllers_file',
        default_value=['reachy_controllers.yaml'],
        description='YAML file with the controllers configuration.',
    )


    start_rviz_arg = DeclareLaunchArgument(
        'start_rviz',
        default_value='false',
        description='Start RViz2 automatically with this launch file.',
    )
    start_rviz = LaunchConfiguration('start_rviz')

    arguments = [
        controllers_file_arg,
        start_rviz_arg,
    ]

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [FindPackageShare('reachy_description'), 'urdf', 'reachy.urdf.xacro']
            ),
            ' ',
            'use_fake_hardware:=true use_gazebo:=true depth_camera:=false',
            ' ',

        ]
    )

    robot_description = {
        'robot_description': ParameterValue(robot_description_content, value_type=str),
    }


    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare('reachy_description'), 'config', 'reachy.rviz']
    )


    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(start_rviz),
    )



    gazebo_state_broadcaster_params = PathJoinSubstitution(
        [FindPackageShare('reachy_gazebo'), 'config', 'gz_state_broadcaster_params.yaml']
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-p',gazebo_state_broadcaster_params,'--controller-manager', '/controller_manager'],
    )

    
    

    neck_forward_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['neck_forward_position_controller', '-c', '/controller_manager'],
    )

    r_arm_forward_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['r_arm_forward_position_controller', '-c', '/controller_manager'],
    )

    l_arm_forward_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['l_arm_forward_position_controller', '-c', '/controller_manager'],
    )

    antenna_forward_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['antenna_forward_position_controller', '-c', '/controller_manager'],
    )

    gripper_forward_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_forward_position_controller', '-c', '/controller_manager'],
    )

    forward_torque_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['forward_torque_controller', '-c', '/controller_manager'],
    )

    forward_torque_limit_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['forward_torque_limit_controller', '-c', '/controller_manager'],
    )

    forward_speed_limit_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['forward_speed_limit_controller', '-c', '/controller_manager'],
    )

    pid_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['pid_controller', '-c', '/controller_manager'],
    )

    forward_fan_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['forward_fan_controller', '-c', '/controller_manager'],
    )

    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        ),
    )

    gazebo_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
                FindPackageShare("reachy_gazebo"), '/launch', '/gazebo.launch.py'])
    )
    #For Gazebo simulation, we should not launch the controller manager (Gazebo does its own stuff)

    delay_robot_controller_spawner_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[
                neck_forward_position_controller_spawner,
                r_arm_forward_position_controller_spawner,
                # l_arm_forward_position_controller_spawner,
                # antenna_forward_position_controller_spawner,
                gripper_forward_position_controller_spawner,
                forward_torque_controller_spawner,
                forward_speed_limit_controller_spawner,
                forward_torque_limit_controller_spawner,
                pid_controller_spawner,
                forward_fan_controller_spawner,
            ],
        ),
    )


    kinematics_node = Node(
        package='reachy_kdl_kinematics',
        executable='reachy_kdl_kinematics',
    )

    return LaunchDescription(arguments + [
        SetUseSimTime(True), #does not seem to work...
        robot_state_publisher_node,
        gazebo_node,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        delay_robot_controller_spawner_after_joint_state_broadcaster_spawner,
        kinematics_node,
    ])
