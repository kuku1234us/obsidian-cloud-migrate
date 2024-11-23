# managers/file_manager.py

import os
import random
import string
from PIL import Image
import ffmpeg
import shutil
from datetime import datetime
from managers.config_manager import ConfigManager
from utils.logger import Logger

class FileManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.logger = Logger()
        self.vault_path = None
        self.image_extensions = [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".heif", ".heic", ".svg"]
        self.video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".m4v", ".webm", ".mpeg", ".3gp", ".ogv"]

    def set_vault_path(self, path):
        """Set the vault path"""
        self.vault_path = path
        self.logger.info(f"Set vault path to: {path}")

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
        self.vault_path = directory  # Update vault path when getting workload
        workload = []

        for root, _, files in os.walk(directory):
            for file in files:
                file_lower = file.lower()
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)

                if any(file_lower.endswith(ext) for ext in self.image_extensions):
                    workload.append({
                        'path': file_path,
                        'original_path': file_path,
                        'filename': file,
                        'filesize': file_size,
                        'type': 'image'
                    })
                elif any(file_lower.endswith(ext) for ext in self.video_extensions):
                    workload.append({
                        'path': file_path,
                        'original_path': file_path,
                        'filename': file,
                        'filesize': file_size,
                        'type': 'video'
                    })

        return workload

    def compress_single_file(self, item):
        """Compress a single media file (image or video)"""
        if item['type'] == 'image':
            self.compress_single_image(item)
        elif item['type'] == 'video':
            self.compress_single_video(item)
        else:
            raise ValueError(f"Unsupported media type: {item['type']}")

    def compress_single_image(self, item, max_dimension=1280, quality=80):
        """Compress a single image file"""
        original_path = item['path']
        self.logger.info(f"Starting to process image: {original_path}")

        new_filename = self.generate_processed_filename(item['filename'], 'jpg')
        new_path = os.path.join(os.path.dirname(original_path), new_filename)

        try:
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
                # Update item with compressed file info
                item['compressed_filename'] = new_filename
                item['processed_path'] = new_path
        except Exception as e:
            # Clean up partially processed file if it exists
            if new_path and os.path.exists(new_path):
                try:
                    os.remove(new_path)
                    self.logger.info(f"Cleaned up partial file: {new_path}")
                except Exception as cleanup_error:
                    self.logger.error(f"Failed to clean up partial file {new_path}: {cleanup_error}")
            raise e

    def compress_single_video(self, item, max_dimension=1080, crf=28):
        """Compress a single video file"""
        original_path = item['path']
        self.logger.info(f"Starting to process video: {original_path}")

        new_filename = self.generate_processed_filename(item['filename'], 'mp4')
        new_path = os.path.join(os.path.dirname(original_path), new_filename)

        try:
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
                                   acodec='aac',
                                   preset='fast',
                                   movflags='+faststart',
                                   threads=0)  # Use all available CPU cores
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            self.logger.info(f"Compressed and saved video: {new_path}")
            # Update item with compressed file info
            item['compressed_filename'] = new_filename
            item['processed_path'] = new_path

        except ffmpeg.Error as e:
            error_message = f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
            # Clean up partially processed file if it exists
            if new_path and os.path.exists(new_path):
                try:
                    os.remove(new_path)
                    self.logger.info(f"Cleaned up partial file: {new_path}")
                except Exception as cleanup_error:
                    self.logger.error(f"Failed to clean up partial file {new_path}: {cleanup_error}")
            raise Exception(error_message)
        except Exception as e:
            # Clean up partially processed file if it exists
            if new_path and os.path.exists(new_path):
                try:
                    os.remove(new_path)
                    self.logger.info(f"Cleaned up partial file: {new_path}")
                except Exception as cleanup_error:
                    self.logger.error(f"Failed to clean up partial file {new_path}: {cleanup_error}")
            raise e

    def create_backup(self, file_path):
        """Create a backup of a file before modifying it"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(self.vault_path, '.backup')
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
        return os.path.relpath(file_path, self.vault_path)

    def get_markdown_files(self):
        """Get all markdown files in the vault"""
        markdown_files = []
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.lower().endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
        self.logger.info(f"Found {len(markdown_files)} markdown files in vault")
        return markdown_files

    def get_file_type(self, file_path):
        """Get the type of file based on extension"""
        file_lower = file_path.lower()
        if any(file_lower.endswith(ext) for ext in self.image_extensions):
            return 'image'
        elif any(file_lower.endswith(ext) for ext in self.video_extensions):
            return 'video'
        elif file_lower.endswith('.md'):
            return 'markdown'
        return 'unknown'

    def read_markdown_file(self, file_path):
        """Read content from a markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return True, f.read()
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def write_markdown_file(self, file_path, content):
        """Write content to a markdown file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Successfully updated file"
        except Exception as e:
            error_msg = f"Error writing file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
