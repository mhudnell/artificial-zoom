# Artificial zoom

![Example output](assets/city_20.gif)

## Usage
```commandline
usage: main.py [-h] --coe COE [--fps FPS] [--zoom-factor ZOOM_FACTOR] [--zoom-length ZOOM_LENGTH] [--zoom-out | --no-zoom-out] [--offset | --no-offset] [--draw-center | --no-draw-center] image_file output_size

Create an artificial zoom video from a single image. Output is .mp4 format.

positional arguments:
  image_file            The image to use.
  output_size           The resolution of the generated output video.

optional arguments:
  -h, --help            show this help message and exit
  --coe COE             Center of expansion (e.g. `--coe=978.76x486.45`). Use --offset if you want this to be interpreted as an offset from the physical center.
  --fps FPS             Frames per second of generated output video.
  --zoom-factor ZOOM_FACTOR
                        The amount to zoom in.
  --zoom-length ZOOM_LENGTH
                        The amount of time the zoom in takes (in seconds). If --zoom-out is true, the total time of the video is 2*ZOOM_LENGTH, since both the zoom-in and zoom-out take ZOOM_LENGTH seconds.
  --zoom-out, --no-zoom-out
                        If true, performs a zoom out after zooming in. (default: True)
  --offset, --no-offset
                        If true, COE is considered an offset from the physical center. (e.g. `--coe=-10.74x5.89 --offset` is 10.74 pixels left, and 5.89 pixels below the physical center) (default: False)
  --draw-center, --no-draw-center
                        If true, draws a crosshair at the center of expansion. (default: False)
```

## Requirements

- Tested in Python 3.9.10
- `pip install -r requirements.txt`

## Examples

```commandline
# describe the articifical center exactly
python main.py test_images/city.jpg 640x360 --coe=1909.26x1085.89 --zoom-factor=7.0 --zoom-length=5.5

# describe the artificial center as an offset from the physical center
python main.py test_images/city.jpg 640x360 --coe=-10.74x5.89 --offset --zoom-factor=7.0 --zoom-length=5.5
python main.py test_images/city.jpg 640x360 --coe=-800.74x500.89 --offset --zoom-factor=7.0 --zoom-length=5.5 --draw-center
```