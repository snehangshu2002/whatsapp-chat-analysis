# WhatsApp Chat Analysis

This repository provides tools and scripts for analyzing WhatsApp chat exports. It helps you extract insights, visualize statistics, and understand communication patterns from your WhatsApp chat history.

## Features

- Parse and clean WhatsApp chat text files
- Generate statistics (message count, active times, user activity, etc.)
- Visualize chat data (graphs, word clouds, etc.)
- Support for group and individual chats
- Easily extensible for custom analyses

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

Clone the repository:

```bash
git clone https://github.com/snehangshu2002/whatsapp-chat-analysis.git
cd whatsapp-chat-analysis
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

### Usage

1. Export your WhatsApp chat (with or without media) from your phone.
2. Place the exported `.txt` file in the project directory.
3. Run the analysis script:

```bash
python main.py --chat your_chat_file.txt
```

#### Example command:

```bash
python main.py --chat "WhatsApp Chat with ABC.txt"
```

### Features in detail

- **Message statistics**: Total messages, messages per user, most active dates/times.
- **Visualization**: Pie charts, bar graphs, word clouds, etc.
- **Custom analysis**: Modify or extend scripts to extract specific insights.

## Project Structure

```
whatsapp-chat-analysis/
├── main.py
├── parser.py
├── analysis.py
├── visualizations.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements.

## License

This project is licensed under the MIT License.

## Acknowledgements

- Inspired by various open-source WhatsApp analysis tools.
- Built with Python and popular data science libraries (pandas, matplotlib, wordcloud, etc.).
