# managers/file_manager.py

import os
import random
import string
from PIL import Image
from utils.logger import Logger
import ffmpeg
import shutil
from datetime import datetime
from managers.config_manager import ConfigManager

class FileManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = Logger()

    def generate_processed_filename(self, original_filename, new_extension):
        """
        Generate a new filename for processed media files.
        
        Args:
            original_filename (str): The original filename
            new_extension (str): The new file extension (without dot)
            
        Returns:
            str: New filename with random prefix and spaces replaced with underscores
        """
        # Generate random prefix
        random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        
        # Replace spaces with underscores and extract base filename without extension
        base_filename = original_filename.rsplit('.', 1)[0].replace(' ', '_')
        
        # Create new filename with specified extension
        return f"{random_prefix}_{base_filename}.{new_extension}"

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

                new_filename = self.generate_processed_filename(item['filename'], 'jpg')
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
                    # Store the compressed filename in the workload item
                    item['compressed_filename'] = new_filename
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

                new_filename = self.generate_processed_filename(item['filename'], 'mp4')
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

                # Store the compressed filename in the workload item
                item['compressed_filename'] = new_filename
                self.logger.info(f"Compressed and saved video: {new_path}")
                if progress_callback:
                    progress_callback(item, status="complete")

            except Exception as e:
                error_message = f"Failed to process video {original_path}: {e}"
                self.logger.error(error_message)
                if progress_callback:
                    progress_callback(None, error_message=error_message)

    def create_backup(self, file_path):
        """Create a backup of a file before modifying it"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(self.config_manager.get_vault_path(), '.backup')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(file_path)
            backup_name = f"{filename}_{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Create backup
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup of {filename} at {backup_path}")
            return True, backup_path
            
        except Exception as e:
            error_msg = f"Error creating backup of {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def save_file_content(self, file_path, content, create_backup=True):
        """Save content to a file with optional backup"""
        try:
            # Create backup if requested
            if create_backup:
                backup_success, backup_result = self.create_backup(file_path)
                if not backup_success:
                    return False, f"Failed to create backup: {backup_result}"
            
            # Save the new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Successfully saved changes to {file_path}")
            return True, file_path
            
        except Exception as e:
            error_msg = f"Error saving changes to {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_relative_path(self, file_path):
        """Get the path of a file relative to the vault root"""
        return os.path.relpath(file_path, self.config_manager.get_vault_path())
