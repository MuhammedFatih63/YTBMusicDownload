# YouTube Music Downloader

## Overview
YouTube Music Downloader is a Python application that allows users to download audio and video from YouTube. The application provides a user-friendly interface built with PyQt5, enabling users to easily input URLs, select formats, and manage download locations.

## Features
- Download audio in various formats (MP3, MP4, WAV, M4A).
- Support for downloading entire playlists.
- Automatic installation of FFmpeg if not already installed.
- Progress bars to show download status.
- User-friendly interface for easy navigation.

## Requirements
- Python 3.x
- PyQt5
- yt-dlp
- requests
- zipfile
- shutil
- platform

## Installation
1. Clone the repository or download the source code.
2. Install the required packages using pip:
   ```bash
   pip install PyQt5 yt-dlp requests
   ```
3. Ensure you have FFmpeg installed. The application will attempt to install it automatically if it is not found.

## Usage
1. Run the application:
   ```bash
   python musicScript.py
   ```
2. Paste the YouTube music or playlist link into the input field.
3. Select the desired format from the dropdown menu.
4. Choose the download location by clicking the "Browse" button.
5. Click the "Download" button to start the download process.
6. Monitor the progress through the progress bars.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to create a pull request.

## Contact
For any inquiries or issues, please contact [your_email@example.com].
