````markdown
# Leakify

[![PyPI version](https://badge.fury.io/py/leakify.svg)](https://badge.fury.io/py/leakify)  
[![Build Status](https://github.com/yourusername/leakify/actions/workflows/python.yml/badge.svg)](https://github.com/yourusername/leakify/actions)  
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A simple, async-powered CLI tool to bulk-download photos and videos from [leakedzone.com](https://leakedzone.com). Leakify crawls a model’s public gallery, extracts full-resolution media URLs, and uses `ffmpeg` under the hood for fast, reliable downloads.

---

## 🚀 Features

- **Async & concurrent** downloads with configurable batch size  
- Auto-pagination: fetches all pages of photos and videos  
- Thumbnail → full-resolution URL conversion  
- HLS playlist & detail-page scraping for videos  
- Real-time status table in your terminal (powered by `tabulate` + `colorama`)  
- Easy install via `pip` and one-command usage  

---

## 📦 Installation

```bash
pip install leakify
````

> **Requirements:**
>
> * Python 3.7+
> * `ffmpeg` available on your `PATH`
> * Internet connection

---

## 💡 Usage

```bash
leakify -u <MODEL_USERNAME> [options]
```

### Options

| Flag             | Description                            | Default |
| :--------------- | :------------------------------------- | :------ |
| `-u`, `--user`   | **(required)** Target model’s username |         |
| `-p`, `--photos` | Only download photos                   | ✗       |
| `-v`, `--videos` | Only download videos                   | ✗       |
| `-b`, `--batch`  | Max concurrent downloads (1–100)       | 10      |
| `-h`, `--help`   | Show help message and exit             |         |

### Examples

* Download **all** media (photos + videos):

  ```bash
  leakify -u jane_doe
  ```

* Download **photos only** (up to 5 at a time):

  ```bash
  leakify -u jane_doe --photos -b 5
  ```

* Download **videos only**, with higher concurrency:

  ```bash
  leakify -u jane_doe --videos -b 20
  ```

---

## 📂 Output

All downloaded files go into a folder named after the model:

```
./jane_doe/
├── photos/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── …
└── videos/
    ├── 9f2c1b7d8a3e4f5.mp4
    ├── 4a7d6c5b8e2f1d0.mp4
    └── …
```

---

## 🛠️ Development

1. **Clone** the repo:

   ```bash
   git clone https://github.com/yourusername/leakify.git
   cd leakify
   ```
2. **Install** dev dependencies:

   ```bash
   pip install -e .[test]
   ```
3. **Run tests**:

   ```bash
   pytest
   ```
4. **Lint** with `flake8`:

   ```bash
   flake8 leakify
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m "Add awesome feature"`)
4. Push to your branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.
