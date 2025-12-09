# SumGPT
[![python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3112/)

<a href="https://www.buymeacoffee.com/zekezhang" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>

Achieve detailed summarisation of extensive documents through 🚀ultra-fast parallelised completion with APIs provided by [OpenAI](https://openai.com/).

🌐 Web App: [https://sumgpt.streamlit.app](https://sumgpt.streamlit.app/)

---
*⭐️ Like this repo? Please consider a star!*

*💡As I am not a professional programmer and am fairly new to Python, this project may contain bugs. If you encounter any issues, please suggest them in the [Issues section](https://github.com/sean1832/SumGPT/issues).*

---

### 🌟 Features
- 📄 Summarize document (.txt, .md).
- 🤖 Customizable parameters and bot persona for refined response generation.
- 🚀 Facilitates parallel processing of chunks.
- 💼 Export & import configs for easy sharing and reuse.
- 🌍 Encrypted browser cookies ensure configuration settings are preserved across sessions.
- 🧠 Supports multiple models:
    - `gpt-4o-mini`
    - `gpt-4o`
    - `gpt-4-turbo`
    - `gpt-3.5-turbo`

### 💡 What you need
- 🔑 OpenAI **[API keys](https://platform.openai.com/account/api-keys)**

### 💻 Running Locally
- Make sure you have **[python 3.11](https://www.python.org/downloads)** | [python installation tutorial (YouTube)](https://youtu.be/HBxCHonP6Ro?t=105)
1. Clone the repository
```bash
git clone https://github.com/sean1832/SumGPT
cd SumGPT
```

2. Create a `secrets.toml` file under `.streamlit\` directory. Replace `your_secure_key` with your own password for browser cookie encryption.
```bash
mkdir .streamlit
echo "crypto_key = 'your_secure_key'" > .streamlit/secrets.toml
```

3. Execute `RUN.bat`
```bash
./RUN.bat
```
