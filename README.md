# AprilTag ROS2 Node

This ROS2 node uses the AprilTag library to detect AprilTags in images and publish their pose, id and additional metadata.

For more information on AprilTag, the paper and the reference implementation: https://april.eecs.umich.edu/software/apriltag.html

## Topics

### Subscriptions:
The node subscribes via a `image_transport::CameraSubscriber` to rectified images on `/apriltag/image_rect`. The set of topic names depends on the type of image transport (parameter `image_transport`) selected (`raw` or `compressed`):
- `/apriltag/image_rect` (`raw`, type: `sensor_msgs/Image`)
- `/apriltag/image_rect/compressed` (`compressed`, type: `sensor_msgs/CompressedImage`)
- `/apriltag/camera_info` (type: `sensor_msgs/CameraInfo`)

### Publisher:
- `/tf` (type: `tf2_msgs/TFMessage`)
- `/apriltag/detections` (type: `apriltag_msgs/AprilTagDetectionArray`)

The camera intrinsics `P` in `CameraInfo` are used to compute the marker tag pose `T` from the homography `H`. The image and the camera intrinsics need to have the same timestamp.

The tag poses are published on the standard TF topic `/tf` with the header set to the image header and `child_frame_id` set to either `tag<family>:<id>` (e.g. "tag36h11:0") or the frame name selected via configuration file. Additional information about detected tags is published as `AprilTagDetectionArray` message, which contains the original homography  matrix, the `hamming` distance and the `decision_margin` of the detection.

## Configuration

The node is configured via a yaml configurations file. For the complete ROS yaml parameter file syntax, see: https://github.com/ros2/rcl/tree/master/rcl_yaml_param_parser.

The file has the format:
```yaml
apriltag:                   # node name
  ros__parameters:
    # required
    image_transport: raw    # image format: "raw" or "compressed" (default: raw)
    family: <tag family>    # tag family name: 16h5, 25h9, 36h11 (default: 36h11)
    size: <tag edge size>   # tag edge size in meter (default: 2.0)
    z_up: true              # rotate about x-axis to have Z pointing upwards (default: false)

    # (optional) tuning of detection
    max_hamming: 0          # maximum allowed hamming distance (corrected bits)
    decimate: 1.0           # decimate resolution for quad detection
    blur: 0.0               # sigma of Gaussian blur for quad detection
    refine-edges: 1         # snap to strong gradients
    threads: 1              # number of threads
    debug: 0                # write additional debugging images to current working directory

    # (optional) list of tags
    tag_ids: [<id1>, <id2>, ...]            # tag IDs for which to publish transform
    tag_frames: [<frame1>, <frame2>, ...]   # optional frame names
    tag_sizes: [<size1>, <size1>, ...]      # optional tag-specific edge size
```

The parameters `family` and `size` are required. `family` (string) defines the tag family for the detector and must be one of `16h5`, `25h9`, `36h11`, `Circle21h7`, `Circle49h12`, `Custom48h12`, `Standard41h12`, `Standard52h13`. `size` (float) is the tag edge size in meters, assuming square markers.

Instead of publishing all tag poses, the list `tag_ids` can be used to only publish selected tag IDs. Each tag can have an associated child frame name in `tag_frames` and a tag specific size in `tag_sizes`. These lists must either have the same length as `tag_ids` or may be empty. In this case, a default frame name of the form `tag<family>:<id>` and the default tag edge size `size` will be used.

The remaining parameters are set to the their default values from the library. See `apriltag.h` for a more detailed description of their function.

See [tags_16h5_all.yaml](cfg/tags_16h5_all.yaml) for an example configuration that publishes all markers in the 16h5 family and [tags_16h5_filtered.yaml](cfg/tags_16h5_filtered.yaml) for filtering tags.

## Nodes

### Standalone Executable

The `apriltag_node` executable can be launched with topic remappings and a configuration file:
```sh
ros2 run apriltag_ros apriltag_node --ros-args \
    -r /apriltag/image_rect:=/camera/image \
    -r /apriltag/camera_info:=/camera/camera_info \
    --params-file `ros2 pkg prefix apriltag_ros`/share/apriltag_ros/cfg/tags_36h11_all.yaml
```

### Composable Node

For more efficient intraprocess communication, a composable node is provided:
```sh
$ ros2 component types
apriltag_ros
  AprilTagNode
```

This `AprilTagNode` component can be loaded with other nodes into a "container node" process where they used shared-memory communication to prevent unnecessary data copies. The example launch file [tag_36h11_all.launch.py](launch//tag_36h11_all.launch.py) loads the `AprilTagNode` together with the `usb_cam::UsbCamNode` component from the [`usb_cam` package](https://github.com/ros-drivers/usb_cam) (`sudo apt install ros-$ROS_DISTRO-usb-cam`) into one container and enables `use_intra_process_comms` for both:
```sh
ros2 launch apriltag_ros tag_36h11_all.launch.py
```
