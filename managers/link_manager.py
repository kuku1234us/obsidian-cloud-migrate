import re
import os
from utils.logger import Logger
from managers.config_manager import ConfigManager

class LinkManager:
    def __init__(self, vault_path):
        """Initialize LinkManager with the path to the Obsidian vault"""
        self.vault_path = vault_path
        self.config_manager = ConfigManager()
        self.logger = Logger()

    def create_pattern_for_file(self, filename):
        """Create regex patterns for a specific filename in all supported link formats"""
        # Escape special characters in filename while preserving dots
        escaped_filename = re.escape(filename).replace(r'\.', '.')
        
        # Create patterns for both wikilinks and standard markdown links
        # Allow for optional path components before the filename
        path_component = r'(?:[^]\[/\\]+/)*'  # Matches any path segments before filename
        block_ref = r'(?:#\^[a-zA-Z0-9-_]+)?'  # Optional block reference
        
        patterns = [
            # Obsidian wikilinks with optional path, alias, and block reference
            f"!?\\[\\[{path_component}{escaped_filename}{block_ref}(?:\\|[^\\]]*)?\\]\\]",
            
            # Markdown image/link with optional path
            f"!?\\[[^\\]]*\\]\\({path_component}{escaped_filename}{block_ref}\\)",
            
            # Handle relative path references (../ or ./)
            f"!?\\[\\[(?:\\.\\./)*{path_component}{escaped_filename}{block_ref}(?:\\|[^\\]]*)?\\]\\]",
            f"!?\\[[^\\]]*\\]\\((?:\\.\\./)*{path_component}{escaped_filename}{block_ref}\\)"
        ]
        
        # Combine patterns with OR operator
        combined_pattern = '|'.join(f"(?:{pattern})" for pattern in patterns)
        return re.compile(combined_pattern)

    def find_media_links(self, markdown_file_path, workload):
        """Find all media links in a markdown file that match files in the workload"""
        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a dictionary to store results for each file
            results = {}
            
            # For each file in workload, find all its occurrences in the markdown
            for item in workload:
                filename = os.path.basename(item['path'])
                pattern = self.create_pattern_for_file(filename)
                
                # Use a set to track unique positions to avoid duplicates
                unique_matches = {}
                
                for match in pattern.finditer(content):
                    # Create a unique key based on the start and end position
                    pos_key = (match.start(), match.end())
                    if pos_key not in unique_matches:
                        unique_matches[pos_key] = {
                            'full_match': match.group(0),
                            'position': pos_key,
                            'original_path': item['path']
                        }
                
                if unique_matches:
                    results[filename] = {
                        'matches': list(unique_matches.values())
                    }
                    
                    # Log each unique match with relative path info
                    rel_path = os.path.relpath(markdown_file_path, self.vault_path)
                    for match_data in unique_matches.values():
                        self.logger.info(f"Found link in {rel_path} for file: {filename}")
                        self.logger.info(f"  Full match: {match_data['full_match']}")
                        self.logger.info(f"  Position: {match_data['position'][0]}-{match_data['position'][1]}")

            return results

        except Exception as e:
            self.logger.error(f"Error processing file {markdown_file_path}: {str(e)}")
            return {}

    def scan_vault(self, workload):
        """Scan the vault for markdown files and find links to workload files"""
        self.logger.info(f"Starting vault scan for {len(workload)} media files in: {self.vault_path}")
        
        # Dictionary to store all results
        all_results = {}
        
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_path = os.path.join(root, file)
                    results = self.find_media_links(markdown_path, workload)
                    if results:
                        all_results[markdown_path] = results

        self.logger.info(f"Vault scan complete. Found media links in {len(all_results)} markdown files")
        return all_results

    def create_external_url(self, compressed_filename):
        """Create the external URL for a compressed media file"""
        base_url = self.config_manager.get('cloudfront_base_url', '').rstrip('/')
        subfolder = self.config_manager.get('s3_subfolder', '').strip('/')
        
        # Ensure we have proper path separators
        if subfolder:
            subfolder = f"{subfolder}/"
            
        return f"{base_url}/{subfolder}{compressed_filename}"

    def replace_link_in_content(self, content, original_filename, compressed_filename):
        """Replace all occurrences of a media file link in the content with its external URL"""
        pattern = self.create_pattern_for_file(original_filename)
        external_url = self.create_external_url(compressed_filename)
        
        def replace_match(match):
            full_match = match.group(0)
            
            # Extract block reference if present
            block_ref = ""
            block_ref_match = re.search(r'(#\^[a-zA-Z0-9-_]+)', full_match)
            if block_ref_match:
                block_ref = block_ref_match.group(1)
            
            # Extract alias if present
            alias = ""
            alias_match = re.search(r'\|(.*?)(?:\#|\])', full_match)
            if alias_match:
                alias = f"|{alias_match.group(1)}"
            
            # Handle different link formats
            if full_match.startswith('![['):
                # Obsidian wikilink with image embed
                return f"![[{external_url}{block_ref}{alias}]]"
            elif full_match.startswith('[['):
                # Obsidian wikilink without image embed
                return f"[[{external_url}{block_ref}{alias}]]"
            elif full_match.startswith('!['):
                # Markdown image link
                alt_text = re.search(r'!\[(.*?)\]', full_match).group(1)
                return f"![{alt_text}]({external_url}{block_ref})"
            else:
                # Regular Markdown link
                alt_text = re.search(r'\[(.*?)\]', full_match).group(1)
                return f"[{alt_text}]({external_url}{block_ref})"
        
        # Replace all occurrences while preserving the link format
        new_content = pattern.sub(replace_match, content)
        return new_content

    def replace_media_links(self, markdown_file_path, media_mapping):
        """
        Replace all media links in a markdown file with their external URLs
        
        Args:
            markdown_file_path (str): Path to the markdown file
            media_mapping (dict): Dictionary mapping original filenames to their compressed versions
                                Format: {'original.jpg': 'compressed_original.jpg'}
        
        Returns:
            tuple: (bool, str) - (Success status, Updated content or error message)
        """
        try:
            # Read the markdown file
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Keep track of changes
            original_content = content
            
            # Replace each media file link
            for original_file, compressed_file in media_mapping.items():
                content = self.replace_link_in_content(content, original_file, compressed_file)
            
            # Check if any changes were made
            if content == original_content:
                return True, "No changes needed"  # No changes needed
            
            # Write the updated content back to the file
            with open(markdown_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "Successfully updated file"
            
        except Exception as e:
            error_msg = f"Error replacing links in {markdown_file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
