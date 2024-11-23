# Project Structure

This document provides a detailed description of the folder structure and purpose for each folder in the `VaultManager` project.

```ProjectTree
VaultManager/
│
├── .env
├── .gitignore
├── README.md
├── config.yaml
├── poetry.lock
├── pyproject.toml
├── main.py
│
├── .git/
├── .venv/
├── .vscode/
│
├── assets/
│   └── appicon.png
│
├── components/
│   ├── __init__.py
│   ├── main_window.py
│   ├── system_tray.py
│   ├── settings_dialog.py
│   ├── file_list_view.py
│   └── work_progress.py
│
├── docs/
│   ├── AWS Upload Guide.md
│   ├── ProjectRequirements.md
│   ├── ProjectStructure.md
│   └── ProjectClasses.md
│
├── managers/
│   ├── __init__.py
│   ├── config_manager.py
│   └── link_manager.py
│   └── upload_manager.py
│
├── types/
│   ├── __init__.py
│   └── exceptions.py
│
└── utils/
    ├── __init__.py
    ├── error_handler.py
    ├── logger.py
    └── singleton.py
```

## Root Directory

- **.env**: Contains environment variables, including AWS credentials and region settings.
- **.gitignore**: Specifies intentionally untracked files to ignore, including test-vault/ for development testing.
- **README.md**: Provides an overview of the project, setup instructions, and other essential information.
- **config.yaml**: Configuration file for various project settings.
- **poetry.lock** & **pyproject.toml**: Manage project dependencies and configurations.
- **main.py**: Main execution script for the project.

## Subdirectories

### assets

- Folder for static files like images or other assets used in the project.
- `appicon.png` is in this folder

### components

- **main_window.py**: Main application window implementing the core functionality:
  - Dark Fusion theme
  - Settings dialog management
  - System tray integration
  - Window state management (show/hide/quit)
  - Comprehensive logging integration
  - Clean process lifecycle management
- **system_tray.py**: System tray implementation with:
  - Proper lifecycle management using QObject parent
  - Context menu with show/hide, settings, and quit actions
  - Left-click activation handling
  - Clean resource cleanup on exit
- **settings_dialog.py**: A dialog for configuring settings like AWS credentials, bucket name, and app behavior.
- **file_list_view.py**: Displays and manages the list of media files with logging for file operations.
- **work_progress.py**: Handles progress tracking and status updates with detailed logging.
- Purpose: Contains UI components with integrated logging, status updates, and proper resource management.

### docs

- **AWS Upload Guide.md**: Documentation for uploading to AWS.
- **ProjectRequirements.md**: Lists the requirements and specifications of the project.
- **ProjectStructure.md**: Describes the project structure.
- **ProjectClasses.md**: Lists the classes and components to be built for the project.

### managers

- **config_manager.py**: Manages configuration settings.
- **upload_manager.py**: Handles the uploading of files to the AWS S3 bucket.
- **link_manager.py**: Handles media link detection and replacement with support for:
  - Multiple link formats (Wikilinks, Markdown)
  - Block references and aliases
  - Relative paths
  - Duplicate detection prevention
- Purpose: Handles management tasks for configuration and link processing.

### types

- **exceptions.py**: Defines custom exceptions used in the project.
- Purpose: Contains type definitions and custom exceptions.

### utils

- **error_handler.py**: Handles error logging and management.
- **logger.py**: Singleton Logger implementation with comprehensive logging levels.
- **singleton.py**: Base singleton metaclass implementation.
- Purpose: Provides utility functions and logging infrastructure.

This structure helps in organizing the project efficiently, making it easier to maintain and scale.
