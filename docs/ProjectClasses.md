# Proposed Classes and Components for ObsidianCloudMigrate

The following is a list of classes and components that should be implemented to build a complete and functional **ObsidianCloudMigrate** application. These components are designed to modularize the application, improve maintainability, and provide clear separation of concerns.

## 1. Core Classes

### 1.1 `MainApp`

- **Location**: `./main.py`
- **Description**: The main entry point for launching the PyQt6 interface of the application.
- **Responsibilities**:
  - Initialize the application UI.
  - Manage high-level interactions between different components.

### 1.2 `Uploader`

- **Location**: `core/uploader.py`
- **Description**: Handles the uploading of files to the AWS S3 bucket.
- **Responsibilities**:
  - Provide functions to upload files.
  - Track upload progress and handle errors.

## 2. User Interface (UI) Components

### 2.1 `MainWindow`

- **Location**: `components/main_window.py`
- **Description**: Represents the main window of the application.
- **Responsibilities**:
  - Display the UI components for selecting files, viewing logs, and starting uploads.
  - Provide user interaction elements such as buttons and input fields.

### 2.2 `SettingsDialog`

- **Location**: `components/settings_dialog.py`
- **Description**: A dialog for configuring settings like AWS credentials, bucket name, and app behavior.
- **Responsibilities**:
  - Allow users to modify AWS settings and other application configurations.
  - Provide an interface to update configuration values stored in `config.yaml`.

### 2.3 `FileListView`

- **Location**: `components/file_list_view.py`
- **Description**: A component that displays the list of media files available for upload.
- **Responsibilities**:
  - Allow users to view, filter, and select files to upload.

## 3. Managers

### 3.1 `ConfigManager`

- **Location**: `managers/config_manager.py`
- **Description**: Manages application configuration settings.
- **Responsibilities**:
  - Load configuration from `.env` and `config.yaml` files.
  - Provide access to application settings.

### 3.2 `UploadManager`

- **Location**: `managers/upload_manager.py`
- **Description**: Coordinates the upload process.
- **Responsibilities**:
  - Manage batch uploads.
  - Handle retries and error logging.

### 3.3 `LogManager`

- **Location**: `managers/log_manager.py`
- **Description**: Manages logging for the application.
- **Responsibilities**:
  - Provide an interface for logging actions and events.
  - Allow logs to be viewed in the UI.

## 4. Utility Classes

### 4.1 `Logger`

- **Location**: `utils/logger.py`
- **Description**: Centralized logging functionality for the application.
- **Responsibilities**:
  - Log events to both console and file.
  - Rotate log files when they exceed a certain size.

### 4.2 `ErrorHandler`

- **Location**: `utils/error_handler.py`
- **Description**: Centralized error handling functionality.
- **Responsibilities**:
  - Log errors and optionally display error messages to the user.
  - Handle fatal errors gracefully.

### 4.3 `FileUtils`

- **Location**: `utils/file_utils.py`
- **Description**: Helper functions for file operations.
- **Responsibilities**:
  - Provide methods to parse Obsidian vault files, find media files, and manage file paths.

## 5. Types and Data Models

### 5.1 `MediaFile`

- **Location**: `types/media_file.py`
- **Description**: Represents a media file in the Obsidian vault.
- **Responsibilities**:
  - Store metadata about the media file, such as path, size, and upload status.

### 5.2 `Exceptions`

- **Location**: `types/exceptions.py`
- **Description**: Custom exceptions used throughout the application.
- **Responsibilities**:
  - Define specific exceptions for different error cases like configuration errors, upload errors, etc.

## 6. Additional Components

### 6.1 `LinkReplacer`

- **Location**: `core/link_replacer.py`
- **Description**: Handles replacing local media links with cloud-hosted URLs.
- **Responsibilities**:
  - Parse Markdown files and replace local links (`![[filename]]`) with corresponding S3/CloudFront URLs.
  - Ensure a backup of original Markdown files is created before modification.

### 6.2 `BackupManager`

- **Location**: `managers/backup_manager.py`
- **Description**: Handles creating and managing backups of Markdown files.
- **Responsibilities**:
  - Backup original Markdown files before any modifications are made.
  - Provide restore functionality in case of any issues.

## Summary

These classes and components provide a modular and extensible foundation for the **ObsidianCloudMigrate** application. The **Core** components focus on the primary functionality (uploading and link replacement), while the **Managers** provide a layer of control and coordination. The **UI Components** offer a user-friendly interface, and the **Utilities** handle logging, configuration, and error management. The **Types and Data Models** represent the application's data, and additional components like `LinkReplacer` and `BackupManager` add robustness to the application. This approach ensures maintainability and clear separation of responsibilities, making future extensions easier.
