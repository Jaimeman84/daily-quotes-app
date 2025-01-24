# Daily Quotes App ✨

A Streamlit-powered web application that lets you discover, search, and save inspiring quotes.

## 🌟 Features

- 📖 Get random daily quotes
- 🔍 Search quotes by content
- 👤 Filter quotes by author
- 💾 Save your favorite quotes
- 📱 Responsive design
- 🌐 Uses the Quotable API

## 📦 Project Structure

```
daily-quotes/
├── app.py              # Main application file with Streamlit UI
├── test_app.py        # Unit tests for the application
├── requirements.txt   # Project dependencies
├── quotes.csv        # Local database for saved quotes
└── README.md         # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/daily-quotes-app.git
cd daily-quotes-app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

Launch the application:
```bash
streamlit run app.py
```
The app will open in your default web browser at `http://localhost:8501`

### Running Tests

Execute the test suite:
```bash
pytest test_app.py -v
```

## 🛠️ Technologies Used

- [Streamlit](https://streamlit.io/) - Web framework
- [Quotable API](https://github.com/lukePeavey/quotable) - Quotes database
- [Pandas](https://pandas.pydata.org/) - Data handling
- [Pytest](https://docs.pytest.org/) - Testing framework

## ✨ Features in Detail

### Daily Quote
- Get a new random quote every day
- One-click save functionality
- Automatic refresh option

### Search Functionality
- Search through thousands of quotes
- Filter by specific authors
- Find quotes containing specific words or phrases
- Pagination for large result sets

### Save and Manage
- Save your favorite quotes locally
- View all saved quotes in one place
- Automatic duplicate prevention
- Sort and filter saved quotes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Quotable API](https://github.com/lukePeavey/quotable) for providing the quotes database
- [Streamlit](https://streamlit.io/) for the amazing web framework
- All contributors and users of this application

---
Made with ❤️ by Jaime Mantilla + Ai