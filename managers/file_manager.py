# managers/file_manager.py

import os
import random
import string
from PIL import Image
from utils.logger import Logger
import ffmpeg

class FileManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = Logger()

    def generate_random_prefix(self, length=20):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def compress_images_in_directory(self, directory, max_dimension=1280, quality=80, progress_callback=None):
        supported_extensions = [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg"]

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    original_path = os.path.join(root, file)
                    random_prefix = self.generate_random_prefix()
                    new_filename = f"{random_prefix}_{file.rsplit('.', 1)[0]}.jpg"
                    new_path = os.path.join(root, new_filename)

                    try:
                        with Image.open(original_path) as img:
                            # Check if resizing is needed
                            width, height = img.size
                            if width > max_dimension or height > max_dimension:
                                # Calculate the new size while preserving the aspect ratio
                                aspect_ratio = width / height
                                if width > height:
                                    new_width = max_dimension
                                    new_height = int(new_width / aspect_ratio)
                                else:
                                    new_height = max_dimension
                                    new_width = int(new_height * aspect_ratio)

                                # Resize the image
                                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            else:
                                # No resizing needed, use the original image
                                img_resized = img

                            img_resized = img_resized.convert('RGB')  # Ensure compatibility with JPEG format

                            # Save the image with a new name
                            img_resized.save(new_path, 'JPEG', quality=quality)
                            self.logger.info(f"Compressed and saved image: {new_path}")
                            if progress_callback:
                                progress_callback(f"Compressed and saved image: {new_path}")

                    except Exception as e:
                        error_message = f"Failed to process image {original_path}: {e}"
                        self.logger.error(error_message)
                        if progress_callback:
                            progress_callback(error_message)

    def compress_videos_in_directory(self, directory, max_dimension=1080, crf=28, progress_callback=None):
        supported_extensions = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".m4v", ".webm", ".mpeg", ".3gp", ".ogv"]

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    original_path = os.path.join(root, file)
                    random_prefix = self.generate_random_prefix()
                    new_filename = f"{random_prefix}_{file.rsplit('.', 1)[0]}.mp4"
                    new_path = os.path.join(root, new_filename)

                    try:
                        # Determine the new dimensions while maintaining aspect ratio, without scaling up
                        probe = ffmpeg.probe(original_path)
                        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                        if video_stream is None:
                            raise ValueError("No video stream found")

                        width = int(video_stream['width'])
                        height = int(video_stream['height'])

                        if width > max_dimension or height > max_dimension:
                            if width > height:
                                new_width = max_dimension
                                new_height = int(height * (max_dimension / width))
                            else:
                                new_height = max_dimension
                                new_width = int(width * (max_dimension / height))

                            # Ensure the height is divisible by 2 (required by libx264)
                            if new_height % 2 != 0:
                                new_height += 1
                            if new_width % 2 != 0:
                                new_width += 1
                        else:
                            new_width = width
                            new_height = height

                        self.logger.info(f"Compressing video {original_path} with new dimensions: {new_width}x{new_height}")
                        if progress_callback:
                            progress_callback(f"Compressing video {original_path} with new dimensions: {new_width}x{new_height}")

                        # Use ffmpeg to compress the video, retaining audio
                        vid_stream = ffmpeg.input(original_path).video.filter('scale', new_width, new_height)
                        audio_stream = ffmpeg.input(original_path).audio

                        (
                            ffmpeg
                            .output(vid_stream, audio_stream, new_path, vcodec='libx264', acodec='aac', crf=crf, audio_bitrate='192k')
                            .run()
                        )
                        self.logger.info(f"Compressed and saved video: {new_path}")
                        if progress_callback:
                            progress_callback(f"Compressed and saved video: {new_path}")

                    except ffmpeg.Error as e:
                        error_message = f"Failed to process video {original_path}: {e.stderr.decode('utf-8')}"
                        self.logger.error(error_message)
                        if progress_callback:
                            progress_callback(error_message)
                    except Exception as e:
                        error_message = f"Failed to process video {original_path}: {e}"
                        self.logger.error(error_message)
                        if progress_callback:
                            progress_callback(error_message)
