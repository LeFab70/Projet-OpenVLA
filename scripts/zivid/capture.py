import zivid
import os
def _main() -> None:
    app = zivid.Application()

    print("Connecting to camera")
    camera = app.connect_camera()

    print("Creating default capture settings")
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )

    print("Capturing frame")

    frame = camera.capture_2d_3d(settings)
    image_rgba = frame.frame_2d().image_rgba_srgb()
    image_file = "ColorImage.png"
    print(f"Saving 2D color image (sRGB color space) to file: {image_file}")
    current_folder=os.path.dirname(os.path.abspath(__file__))
    image_path=os.path.join(current_folder,image_file)
    image_rgba.save(image_path)
    data_file = "Frame.zdf"
    data_path=os.path.join(current_folder,data_file)
    print(f"Saving frame to file: {data_file}")
    frame.save(data_path)

    data_file_ply = "PointCloud.ply"
    
    print(f"Exporting point cloud to file: {data_file_ply}")
    data_path_ply=os.path.join(current_folder,data_file_ply)
    frame.save(data_path_ply)


if __name__ == "__main__":
    _main()