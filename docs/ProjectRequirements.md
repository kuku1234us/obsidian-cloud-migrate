# ProjectRequirements for Vault-Manager

This document outlines the required functionalities to be implemented in the **VaultManager** project, which aims to provide an efficient solution for managing media files within an Obsidian vault. The project includes an interface built with **PyQt6** for an intuitive user experience.

## Functional Requirements

### 1. User Interface (UI) with PyQt6

- **Main Window**: Design a main application window using PyQt6.
  - **Title**: Set the title to "VaultManager Tool".
- **Menu Bar**: Include a menu bar with the following menus:
  - **File**: Options to configure settings, save current configuration, and exit the application.
  - **Help**: Provide information about the tool and an option for viewing user documentation.
- **Vault Directory Selector**:
  - Allow the user to select the directory of their Obsidian vault.
- **Media File List**:
  - Display a list of detected media files within the selected vault.
  - Provide a filter or search bar to find specific media files.
- **Upload Controls**:
  - Include a button to initiate the upload process to AWS S3.
  - Show a progress bar to indicate the status of the current upload.
- **Status and Logs**:
  - Display a status area to provide real-time updates, such as files being processed or errors.
  - Include a log viewer to show detailed logs of all upload activities.
- **Settings Page**:
  - Display a list of settings options:
    - **AWS Credentials**:
      - AWS Access Key ID input field (stored in `.env`)
      - AWS Secret Access Key input field (stored in `.env`)
      - AWS Region input field (stored in `.env`)
    - **Cloud Storage Configuration**:
      - S3 Bucket Name input field
      - S3 Subfolder Path input field
      - CloudFront Base URL input field
    - **Security**:
      - Securely store sensitive credentials in `.env` file
      - Provide option to test AWS connectivity

### 2. AWS S3 + CloudFront Integration

- **AWS Configuration**:
  - Allow the user to input AWS credentials manually or load from the `.env` file.
  - Provide a form to input S3 bucket name and CloudFront distribution ID.
- **Upload Logic**:
  - Implement logic to automate the upload of selected media files to AWS S3.
  - Use multi-part upload for larger files to improve reliability.
- **CloudFront Integration**:
  - Use CloudFront to generate URLs if the user has specified a CloudFront distribution.
  - Automatically update media file links in Markdown to reflect the CloudFront URLs.

### 3. Link Replacement in Markdown Files

- **Local Link Parsing**:
  - Parse Markdown files in the selected Obsidian vault to identify links to media files.
  - Detect links of the following formats and replace them with public S3 or CloudFront URLs.

#### **Supported Link Formats:**

1. Obsidian Wikilinks:

   - Basic: ![[filename.extension]]
   - With alias: ![[filename.extension|alias]]
   - With block reference: ![[filename.extension#^blockref]]
   - With path: ![[subfolder/filename.extension]]
   - With relative path: ![[../relative/path/filename.extension]]
   - Non-embedded: [[filename.extension]]
   - Non-embedded with block ref: [[filename.extension#^blockref]]
   - Non-embedded with alias: [[filename.extension|alias]]

2. Markdown Links:
   - Basic: ![alt](filename.extension)
   - With path: ![alt](subfolder/filename.extension)
   - With relative path: ![alt](../relative/path/filename.extension)
   - Non-embedded: [alt](filename.extension)
   - With block reference: ![alt](filename.extension#^blockref)

- **Link Detection Features**:

  - Support for block references (#^blockref) in both Wikilinks and Markdown links
  - Handle relative paths (../ or ./) in both link formats
  - Support for aliases in Wikilinks
  - Preserve original link metadata (block refs, aliases) during replacement
  - Duplicate link detection prevention

- **Backup Functionality**:
  - Before replacing links, create a backup of the original Markdown files.
- **Link Replacement Confirmation**:
  - Provide a preview of the changes, allowing the user to confirm before applying them.

### 4. AWS SDK

- **Boto3**:
  - Use the Boto3 library to interact with AWS services, specifically for uploading files to AWS S3.

### 5. Error Handling and Notifications

- **Connection Errors**: Display informative messages if there are any issues connecting to AWS.
- **File Handling Errors**: Catch and log errors related to missing files or incorrect permissions.
- **Notifications**:
  - Provide notifications on completion of upload and link replacement.
  - Show warnings for files that could not be uploaded or replaced.

### 6. Configuration Management

- **Save Configuration**:
  - Allow users to save their current settings (vault path, AWS credentials, etc.) for later use.
- **Load Configuration**:
  - Provide an option to load a previously saved configuration.

### 7. Logging

- **Log File Generation**:
  - Create a log file for every session to store detailed information regarding the operations performed
  - Use a singleton Logger class for consistent logging across components
  - Include debug, info, warning, and error log levels
  - Log detailed information about link matches including file positions and full match text
- **User Access to Logs**:
  - Provide access to view log files from the UI
  - Display real-time log updates in the UI status area

### 8. Testing and Debugging Tools

- **Test Upload**: Provide a "Test Upload" button to verify if the connection to AWS S3 is working correctly.
- **Verbose Mode**: Add an option to run the tool in verbose mode for more detailed output during debugging.

## Non-Functional Requirements

### 1. Performance

- The application should be able to handle vaults with a large number of media files (e.g., 10,000+ files).
- Use threading or asynchronous programming to prevent UI freezes during long-running operations.

### 2. Usability

- The interface should be intuitive and easy to use, with clear labeling of buttons and options.
- Tooltips should be provided for all major functions to help users understand their purpose.

### 3. Security

- AWS credentials should be handled securely and not stored in plain text after the session.
- Use environment variables or an encrypted configuration file to store sensitive information.

## Future Enhancements

- **Support for Other Cloud Providers**: Extend the tool to support other cloud storage services like Google Cloud Storage, Azure Blob Storage, or Baidu Cloud.
- **Scheduling**: Add a feature to allow scheduled uploads, enabling users to automate the process periodically.
- **Advanced Search**: Provide more advanced filtering options for finding specific media files, such as file type, size, or date modified.

## Summary

This project will build a PyQt6-based application to help Obsidian users efficiently manage their media files by uploading them to AWS S3 and replacing local links with cloud-hosted URLs. The tool will provide an easy-to-use graphical interface, reliable error handling, and seamless integration with AWS services, ensuring a smooth experience for users looking to optimize their Obsidian storage.
