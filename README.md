# ObsidianCloudMigrate

ObsidianCloudMigrate is a Python tool designed to help you manage media files within your Obsidian vault by automating the process of uploading these files to cloud storage, freeing up local space, and replacing local links with external cloud URLs. The current version of the tool supports integration with AWS S3 + CloudFront to minimize storage footprint and ensure efficient content delivery.

## Features

- **Automatic Upload**: Automatically upload local media files to an AWS S3 bucket.
- **Link Replacement**: Replace local Obsidian media links with external cloud URLs after successful uploads.
- **CloudFront Integration**: Utilize AWS CloudFront for efficient content delivery with low latency.

## Prerequisites

- **Python 3.6+**
- **AWS Account** with S3 bucket and CloudFront distribution setup
- **AWS Credentials** (Access Key ID and Secret Access Key)

## Setup Instructions

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/obsidiancloudmigrate.git
cd obsidiancloudmigrate
```

### Step 2: Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

### Step 3: Configure AWS Credentials

Ensure you have your AWS credentials set up. You can configure them using the AWS CLI:

```bash
aws configure
```

Or you can create a `.env` file in the root directory to store your AWS Access Key ID and Secret Access Key:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_aws_region
```

### Step 4: Configure S3 Bucket and CloudFront

Update the configuration in `config.yaml` to specify your S3 bucket name and CloudFront distribution (if applicable):

```yaml
s3_bucket_name: your_bucket_name
cloudfront_distribution_id: your_distribution_id # Optional, if you use CloudFront
```

## Usage

Run the main script to start uploading your media files from the Obsidian vault:

```bash
python obsidiancloudmigrate.py
```

This script will:

1. Scan your Obsidian vault for media files (e.g., images, videos).
2. Upload these files to your configured S3 bucket.
3. Replace the local links in your Markdown files with the corresponding CloudFront or S3 URLs.

## Example

```markdown
Before:
![[JournalsSettings.jpg]]

After:
![JournalsSettings](https://your-bucket.s3.amazonaws.com/JournalsSettings.jpg)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
