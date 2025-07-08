# 🎨 Designer Upload Tool – Hot Ink

A simple, styled file uploader built in Flask to route design files directly to Hot Ink's creative team. Users select their designer, submit contact info, upload artwork, and automatically notify the assigned designer via email. All uploads are securely logged and stored on your NAS share.

---

## 🚀 Features

- 🔒 Secure artwork submission with Drag & Drop support via Dropzone.js
- 📧 Auto-email notification to selected designer
- 🗂️ Upload log saved as CSV for tracking
- 📁 Files stored on `/mnt/nas_uploads` (or mounted volume)
- 🎨 Modal-based upload form with themed progress bar
- 🧠 Configurable via `config.py` or Docker environment

---

## 📦 Tech Stack

- **Python 3.10**
- **Flask**
- **Dropzone.js**
- **Bootstrap 5**
- **Docker + Docker Compose**

---

## ⚙️ Setup (Local or Dockerized)

### 🔧 Clone the Repo

```bash
git clone https://github.com/Droid80sa/Designer-Upload.git
cd Designer-Upload
```

### 🔑 Environment Variables

Create a `.env` file with:

```bash
SECRET_KEY=supersecret
MAIL_USERNAME=proofs@hotink.co.za
MAIL_PASSWORD=your_password
```

The `docker-compose.yml` file and `config.py` load these variables when running locally.

## 🧪 Running Tests

Install the dependencies and run the test suite with **pytest**:

```bash
pip install -r requirements.txt pytest
pytest
```
## 📌 Managing Dependencies

All Python packages in `requirements.txt` use pinned versions. To update them:

1. Create a fresh virtual environment and install the project.
2. Run `pip freeze > requirements.txt` to capture working versions.
3. Commit the updated file so builds remain reproducible.
=======
## License

This project is licensed under the [MIT License](LICENSE).

