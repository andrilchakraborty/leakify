````markdown
# Leakify

An async-powered CLI to bulk-download photos and videos from [leakedzone.com](https://leakedzone.com). Leakify crawls a model’s public gallery, grabs full-resolution media URLs, and uses `ffmpeg` under the hood for fast, reliable downloads.

---

## 🚀 Key Features

- **Asynchronous & concurrent** downloading with configurable batch size  
- **Auto-pagination**: crawls all pages of photos and videos  
- **Thumbnail → full-res** URL conversion  
- **HLS & detail-page scraping** for videos  
- **Real-time terminal status** (via `tabulate` + `colorama`)  
- **One-line install** and **one-command** usage  

---

## 📦 Installation

1. Ensure you have:
   - Python 3.7+
   - `ffmpeg` on your `PATH`
2. Install from PyPI:
   ```bash
   pip install leakify
````

---

## 💡 Usage

```bash
leakify -u <MODEL_USERNAME> [options]
```

| Option            | Description                      | Default |
| :---------------- | :------------------------------- | :------ |
| `-u`, `--user`    | **(required)** Model’s username  |         |
| `-p`, `--photos`  | Photos only                      | ✗       |
| `-v`, `--videos`  | Videos only                      | ✗       |
| `-b`, `--batch N` | Max concurrent downloads (1–100) | 10      |
| `-h`, `--help`    | Show help and exit               |         |

### Examples

* **All media** (photos + videos):

  ```bash
  leakify -u jane_doe
  ```
* **Photos only**, batch of 5:

  ```bash
  leakify -u jane_doe --photos -b 5
  ```
* **Videos only**, batch of 20:

  ```bash
  leakify -u jane_doe --videos -b 20
  ```

---

## 📂 Output Layout

Downloads land in a folder named after the model:

```
./jane_doe/
├── photos/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── …
└── videos/
    ├── a1b2c3d4e5f6.mp4
    ├── f6e5d4c3b2a1.mp4
    └── …
```

---

## 🛠 Development

```bash
git clone https://github.com/andrilchakraborty/leakify.git
cd leakify
pip install -e .[test]
pytest
flake8 leakify
```

Feel free to open issues or PRs on the [GitHub repo](https://github.com/andrilchakraborty/leakify).

---
