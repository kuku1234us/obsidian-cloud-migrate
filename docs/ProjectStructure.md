# Project Structure

This document provides a detailed description of the folder structure and purpose for each folder in the `ObsidianCloudMigrate` project.

```ProjectTree
ObsidianCloudMigrate/
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
│   ├── settings_dialog.py
│   └── file_list_view.py
│
├── core/
│   ├── __init__.py
│   └── uploader.py
│
├── docs/
│   ├── AWS Upload Guide.md
│   ├── ProjectRequirements.md
│   ├── ProjectStructure.md
│   └── ProjectClasses.md
│
├── managers/
│   ├── __init__.py
│   └── config_manager.py
│
├── types/
│   ├── __init__.py
│   └── exceptions.py
│
└── utils/
    ├── __init__.py
    ├── error_handler.py
    └── logger.py
```

## Root Directory

- **.env**: Contains environment variables, including AWS credentials and region settings.
- **.gitignore**: Specifies intentionally untracked files to ignore.
- **README.md**: Provides an overview of the project, setup instructions, and other essential information.
- **config.yaml**: Configuration file for various project settings.
- **poetry.lock** & **pyproject.toml**: Manage project dependencies and configurations.

## Subdirectories

### assets

- Folder for static files like images or other assets used in the project.
- `appicon.png` is in this folder

### components

- **main_window.py**: Represents the main window of the application.
- **settings_dialog.py**: A dialog for configuring settings like AWS credentials, bucket name, and app behavior.
- **file_list_view.py**: Displays the list of media files available for upload.
- Purpose: Contains UI components for the project.

### core

- **main.py**: Main execution script for the project.
- **uploader.py**: Handles the uploading of files to the AWS S3 bucket.
- Purpose: Core logic and main functionalities of the project.

### docs

- **AWS Upload Guide.md**: Documentation for uploading to AWS.
- **ProjectRequirements.md**: Lists the requirements and specifications of the project.
- **ProjectStructure.md**: Describes the project structure.
- **ProjectClasses.md**: Lists the classes and components to be built for the project.

### managers

- **config_manager.py**: Manages configuration settings.
- Purpose: Handles management tasks, especially related to configurations.

### types

- **exceptions.py**: Defines custom exceptions used in the project.
- Purpose: Contains type definitions and custom exceptions.

### utils

- **error_handler.py**: Handles error logging and management.
- **logger.py**: Provides logging functionalities.
- Purpose: Utility functions and helpers for the project.

This structure helps in organizing the project efficiently, making it easier to maintain and scale.
