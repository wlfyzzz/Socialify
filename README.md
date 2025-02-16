```
 ____             _       _ _  __       
/ ___|  ___   ___(_) __ _| (_)/ _|_   _ 
\___ \ / _ \ / __| |/ _` | | | |_| | | |
 ___) | (_) | (__| | (_| | | |  _| |_| |
|____/ \___/ \___|_|\__,_|_|_|_|  \__, |
                                  |___/
```

## Overview

Socialify is a powerful and flexible open-source Discord bot designed to enhance server engagement and communication. It provides features similar to Pingcord.gg, allowing you to create custom announcements when your favorite creators go live. Built with a focus on customization and community contribution, Socialify aims to be a valuable tool for Discord server administrators and community managers.

## Features

*   **Custom Announcements:** Create visually appealing and informative announcements with rich text formatting, embedded images, and interactive elements.
*   **Highly Customizable:** Tailor the bot's behavior and appearance to match your server's unique identity.
*   **Open-Source & Community-Driven:** Contribute to the project, suggest new features, and help shape the future of Socialify.

## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   pip (Python package installer)
*   A Discord bot 

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/wlfyzzz/socialify
    cd socialify
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install flask twikit nextcord
    ```

4.  **Configure the bot:**

    *   Edit both configurations in `/Backend/config.json` and `/Bot/config.json` and fill it with the required information it needs .
5. **Start up flaresolver for kick notifications**
   ```bash
    docker run -d \
   --name=flaresolverr \
   -p 8191:8191 \
   -e LOG_LEVEL=info \
   --restart unless-stopped \
   ghcr.io/flaresolverr/flaresolverr:latest```

7.  **Run the backend service:**

    ```bash
    cd Backend
    python3 backend.py
    ```
8.  **Run the Bot:**

    ```bash
    cd Bot
    python3 main.py
    ```

### Invite the Bot to Your Server

1.  Generate an invite link with the appropriate permissions. You can use a Discord permission calculator to help with this.
2.  Use the generated link to invite the bot to your Discord server.

## Usage

Detailed documentation on how to use Socialify's features will be available soon. In the meantime, you can use the `/help` command in your Discord server to see a list of available commands.

## Contributing

We welcome contributions from the community! If you'd like to contribute to Socialify, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear, concise messages.
4.  Submit a pull request to the `main` branch.

Please adhere to the project's coding style and guidelines.

## Support

If you encounter any issues or have questions about Socialify, please:

*   Check the [Issues](https://github.com/wlfyzzz/Socialify/issues) section of the repository.
*   Join our [Discord server](https://discord.gg/XCbnnexRr6) for community support.

## License

This project is licensed under the [MIT License](https://github.com/wlfyzzz/Socialify/blob/main/LICENSE).

## Acknowledgements

*   This project was inspired by Pingcord.gg.
*   We would like to thank all the contributors who have helped make Socialify a better project.
