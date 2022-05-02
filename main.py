import argparse
import itertools
import pathlib

import cv2
import numpy as np


def resolution(input_string: str):
    arr = input_string.split('x')
    if len(arr) != 2:
        raise ValueError('Invalid resolution format.')
    arr = [int(x) for x in arr]
    return arr


def point(input_string: str):
    arr = input_string.split('x')
    if len(arr) != 2:
        raise ValueError('Invalid point format.')
    arr = [float(x) for x in arr]
    return np.array(arr)


def create_artificial_zoom_video(full_res_image, output_filename: str, output_size: tuple[int, int],
                                 coe: tuple[float, float], zoom_factor: float, zoom_length: float, zoom_out: bool,
                                 fps: float, draw_center: bool):
    """
    :param full_res_image: Full resolution image, already loaded with OpenCV.
    :param output_filename: The name of the generated output video file.
    :param output_size: The resolution of the generated output video.
    :param coe: Center of expansion (c_x, c_y).
    :param zoom_factor: The amount to zoom.
    :param zoom_length: The length of zoom in seconds.
    :param zoom_out: Whether to zoom out after zooming in.
    :param fps: Frames per second of the generated output video.
    :param draw_center: Whether to draw a crosshair at the `coe`.
    :return:
    """

    # full_res_image = cv2.imread(image_path)
    original_resolution = np.flip(np.array(full_res_image.shape[:2]))  # [width, height]
    coe_complement = original_resolution - coe

    # set output vid settings
    codec = cv2.VideoWriter.fourcc(*'mp4v')
    vid_writer = cv2.VideoWriter(output_filename + '.mp4', codec, fps, output_size)

    # loop to create vid frame-by-frame
    total_frames = round(zoom_length * fps)
    zoom_base = (zoom_factor - 1.0) ** (1.0 / total_frames)
    frame_range = range(total_frames)
    if zoom_out:
        frame_range = itertools.chain(frame_range, reversed(frame_range))
    for i in frame_range:

        # crop
        x_left = round(coe[0] - coe[0] / zoom_factor)
        x_right = round(coe[0] + coe_complement[0] / zoom_factor)
        y_top = round(coe[1] - coe[1] / zoom_factor)
        y_bottom = round(coe[1] + coe_complement[1] / zoom_factor)
        cropped = full_res_image[y_top:y_bottom, x_left:x_right]

        # scale to output resolution
        cropped_and_scaled = cv2.resize(cropped, output_size)

        # draw crosshair at center for sanity check
        if draw_center:
            scaled_artificial_center = coe * (output_size / original_resolution)
            pt1 = np.rint(scaled_artificial_center - np.array([10, 0])).astype(int)
            pt2 = np.rint(scaled_artificial_center + np.array([10, 0])).astype(int)
            cv2.line(cropped_and_scaled, pt1, pt2, (0, 0, 255), thickness=2)
            pt1 = np.rint(scaled_artificial_center - np.array([0, 10])).astype(int)
            pt2 = np.rint(scaled_artificial_center + np.array([0, 10])).astype(int)
            cv2.line(cropped_and_scaled, pt1, pt2, (0, 0, 255), thickness=2)

        # add image to video
        vid_writer.write(cropped_and_scaled)

        zoom_factor = zoom_base ** i


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an artificial zoom video from a single image. Output is .mp4 format.')
    parser.add_argument('image_file', type=str, help='The image to use.')
    parser.add_argument('output_size', type=resolution, help='The resolution of the generated output video.')
    parser.add_argument('--coe', type=point, required=True, help='The center of expansion at the original video resolution. Use --offset if you want this to be interpreted as an offset from the physical center. (e.g. `--coe=978.76x486.45`, `--coe=-10.74x5.89 --offset`)')
    parser.add_argument('--fps', type=float, default=30.0, help='Frames per second of generated output video.')
    parser.add_argument('--zoom-factor', type=float, default=6.0, help='The amount to zoom in.')
    parser.add_argument('--zoom-length', type=float, default=5.0,
                        help='The amount of time the zoom in takes (in seconds). If --zoom-out is true, the total time of the video is 2*ZOOM_LENGTH, since both the zoom-in and zoom-out take ZOOM_LENGTH seconds.')
    parser.add_argument('--zoom-out', action=argparse.BooleanOptionalAction, default=True,
                        help='If true, performs a zoom out after zooming in.')
    parser.add_argument('--offset', action=argparse.BooleanOptionalAction, default=False,
                        help='If true, COE is considered an offset from the physical center. (e.g. `--coe=-10.74x5.89 --offset` is 10.74 pixels left, and 5.89 pixels below the physical center)')
    parser.add_argument('--draw-center', action=argparse.BooleanOptionalAction, default=False,
                        help='If true, draws a crosshair at the center of expansion.')
    args = parser.parse_args()

    # check file exists
    resolved_path = pathlib.Path(args.image_file).resolve()
    if not resolved_path.exists():
        raise ValueError(f'File ({resolved_path}) does not exist.')
    output_filename = resolved_path.stem

    # load the image
    full_res_image = cv2.imread(args.image_file)
    if full_res_image is None:
        raise ValueError('Error loading image.')

    # determine the center of expansion
    coe = args.coe
    original_resolution = np.flip(np.array(full_res_image.shape[:2]))  # [width, height]

    if args.offset:  # use offset from physical center
        physical_center = np.array([original_resolution[0] / 2, original_resolution[1] / 2])
        coe = physical_center + coe

    scale_factors = args.output_size / original_resolution
    coe_scaled = coe * scale_factors
    print(f'Using center of expansion: \n' \
          f'    - full resolution: ({coe[0]:.2f}, {coe[1]:.2f})\n' \
          f'    - output resolution: ({coe_scaled[0]:.2f}, {coe_scaled[1]:.2f})'
    )

    create_artificial_zoom_video(full_res_image, output_filename, args.output_size, coe, args.zoom_factor,
                                 args.zoom_length, args.zoom_out, args.fps, args.draw_center)

    print('Done!')
