import re
import os
import logging

logger = logging.getLogger('ObsCloudMigrate')

class LinkManager:
    def __init__(self, vault_path):
        """Initialize LinkManager with the path to the Obsidian vault"""
        self.vault_path = vault_path

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
                        logger.info(f"Found link in {rel_path} for file: {filename}")
                        logger.info(f"  Full match: {match_data['full_match']}")
                        logger.info(f"  Position: {match_data['position'][0]}-{match_data['position'][1]}")

            return results

        except Exception as e:
            logger.error(f"Error processing file {markdown_file_path}: {str(e)}")
            return {}

    def scan_vault(self, workload):
        """Scan the vault for markdown files and find links to workload files"""
        logger.info(f"Starting vault scan for {len(workload)} media files in: {self.vault_path}")
        
        # Dictionary to store all results
        all_results = {}
        
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_path = os.path.join(root, file)
                    results = self.find_media_links(markdown_path, workload)
                    if results:
                        all_results[markdown_path] = results

        logger.info(f"Vault scan complete. Found media links in {len(all_results)} markdown files")
        return all_results
