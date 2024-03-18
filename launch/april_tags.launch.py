import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    camera_config_dir = os.path.join(get_package_share_directory('apriltag_ros'), 'config')
    usb_cam_1 = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name="camera_1",
        namespace="camera_1",
        parameters=[os.path.join(camera_config_dir, 'camera_param.yaml'),{'camera_name':'camera_1'},{'frame_id':'camera_1_link'},{'device':'/dev/video0'}],
    )
    usb_cam_2 = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name="camera_2",
        namespace="camera_2",
        parameters=[os.path.join(camera_config_dir, 'camera_2_param.yaml'),{'camera_name':'camera_2'},{'frame_id':'camera_2_link'},{'device':'/dev/video1'}],
    )
    usb_cam_3 = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        name="camera_3",
        namespace="camera_3",
        parameters=[os.path.join(camera_config_dir, 'camera_3_param.yaml'),{'camera_name':'camera_3'},{'frame_id':'camera_3_link'},{'device':'/dev/video2'}],
    )
    april_tags = Node(
        package='apriltag_ros',
        executable='apriltag_node',
        name='apriltag_node',
        output='screen',
        parameters=[os.path.join(camera_config_dir, 'apriltag_params.yaml')],
        arguments=['-r','image_rect:=/camera_1/image_raw','-r','camera_info:=/camera_1/camera_info'],
    )


    return LaunchDescription([
        usb_cam_1,
        # usb_cam_2,
        # usb_cam_3,
        april_tags,
    ])
