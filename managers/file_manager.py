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

    def get_media_workload(self, directory):
        """Get list of all media files with their information"""
        workload = []
        image_extensions = [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg"]
        video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".m4v", ".webm", ".mpeg", ".3gp", ".ogv"]

        for root, _, files in os.walk(directory):
            for file in files:
                file_lower = file.lower()
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)

                if any(file_lower.endswith(ext) for ext in image_extensions):
                    workload.append({
                        'path': file_path,
                        'filename': file,
                        'filesize': file_size,
                        'type': 'image'
                    })
                elif any(file_lower.endswith(ext) for ext in video_extensions):
                    workload.append({
                        'path': file_path,
                        'filename': file,
                        'filesize': file_size,
                        'type': 'video'
                    })

        return workload

    def compress_images_in_directory(self, workload, max_dimension=1280, quality=80, progress_callback=None):
        """Compress images from workload array"""
        for item in workload:
            if item['type'] != 'image':
                continue

            try:
                original_path = item['path']
                self.logger.info(f"Starting to process image: {original_path}")
                if progress_callback:
                    progress_callback(item, status="start")

                random_prefix = self.generate_random_prefix()
                new_filename = f"{random_prefix}_{item['filename'].rsplit('.', 1)[0]}.jpg"
                new_path = os.path.join(os.path.dirname(original_path), new_filename)

                with Image.open(original_path) as img:
                    # Check if resizing is needed
                    width, height = img.size
                    if width > max_dimension or height > max_dimension:
                        aspect_ratio = width / height
                        if width > height:
                            new_width = max_dimension
                            new_height = int(new_width / aspect_ratio)
                        else:
                            new_height = max_dimension
                            new_width = int(new_height * aspect_ratio)
                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    else:
                        img_resized = img

                    img_resized = img_resized.convert('RGB')
                    img_resized.save(new_path, 'JPEG', quality=quality)
                    self.logger.info(f"Compressed and saved image: {new_path}")
                    
                    if progress_callback:
                        progress_callback(item, status="complete")

            except Exception as e:
                error_message = f"Failed to process image {original_path}: {e}"
                self.logger.error(error_message)
                if progress_callback:
                    progress_callback(None, error_message=error_message)

    def compress_videos_in_directory(self, workload, max_dimension=1080, crf=28, progress_callback=None):
        """Compress videos from workload array"""
        for item in workload:
            if item['type'] != 'video':
                continue

            try:
                original_path = item['path']
                self.logger.info(f"Starting to process video: {original_path}")
                if progress_callback:
                    progress_callback(item, status="start")

                random_prefix = self.generate_random_prefix()
                new_filename = f"{random_prefix}_{item['filename'].rsplit('.', 1)[0]}.mp4"
                new_path = os.path.join(os.path.dirname(original_path), new_filename)

                # Get video dimensions
                probe = ffmpeg.probe(original_path)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream is None:
                    raise ValueError("No video stream found")

                width = int(video_stream['width'])
                height = int(video_stream['height'])

                # Calculate new dimensions
                if width > max_dimension or height > max_dimension:
                    if width > height:
                        new_width = max_dimension
                        new_height = int(height * (max_dimension / width))
                    else:
                        new_height = max_dimension
                        new_width = int(width * (max_dimension / height))

                    # Ensure dimensions are even
                    new_width = new_width + (new_width % 2)
                    new_height = new_height + (new_height % 2)
                else:
                    new_width = width + (width % 2)
                    new_height = height + (height % 2)

                # Compress video
                stream = ffmpeg.input(original_path)
                stream = ffmpeg.output(stream, new_path,
                                    vf=f'scale={new_width}:{new_height}',
                                    vcodec='libx264',
                                    crf=str(crf),
                                    acodec='aac')
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

                self.logger.info(f"Compressed and saved video: {new_path}")
                if progress_callback:
                    progress_callback(item, status="complete")

            except Exception as e:
                error_message = f"Failed to process video {original_path}: {e}"
                self.logger.error(error_message)
                if progress_callback:
                    progress_callback(None, error_message=error_message)
