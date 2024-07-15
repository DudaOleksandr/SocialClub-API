# Social Club API Scraper

## Fork from
- GitHub: [SocialClub-API](https://github.com/Alex-MHR/SocialClub-API)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction
This **Social Club API Scraper** is a tool that allows you to scrape Rockstar Social Club data to convert player names to their corresponding Rockstar IDs (Rid). This project is useful for developers who need to interface with Social Club data programmatically.

## Features
- Convert player names to Rockstar IDs
- Lightweight and fast
- Easy to configure and extend
- Supports bulk scraping

## Installation
To get started with the Social Club API NameToRid Scraper, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Alex-MHR/SocialClub-API.git
    cd SocialClub-API
    ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Here's a basic example of how to use the scraper :

```python
from Rockstar.RID import RockstarClient

# Constants
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']
TARGET = "TARGET" # The username of the player whose RID you want
SILENT = False

# Main script to retrieve RID and avatar URL
client = RockstarClient(EMAIL, PASSWORD, SILENT)
client.Startup(force_renewing=True)
(rid, avatar_url), state = client.RetrieveRID(TARGET)

# Results
if state == 1:
    print(f"RID of player {TARGET} is {rid}.\nAvatar URL : {avatar_url}")
else:
    print(f"An error occured while retriving the Rockstar ID of player {TARGET}.")
```

## Configuration
You can configure the scraper by creating env file. Here is configuration structure :

```python
EMAIL="my-email@my-host.com" # Your SocialClub E-Mail
PASSWORD="MyStrongPassword" # Your SocialClub Password
SILENT=False # Mostly for Debug
```

## Contributing
Contributions are welcome ! To contribute to this project, follow these steps :

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions, feel free to me reach out at :

- GitHub: [Alex-MHR](https://github.com/Alex-MHR)
- Discord: `wagner.50hz`