# 🎨 Designer Upload Tool – Hot Ink

A simple, styled file uploader built in Flask to route design files directly to Hot Ink's creative team. Users select their designer, submit contact info, upload artwork, and automatically notify the assigned designer via email. All uploads are securely logged and stored on your NAS share.

---

## 🚀 Features

- 🔒 Secure artwork submission with Drag & Drop support via Dropzone.js
- 📧 Auto-email notification to selected designer
- 🗂️ Upload log saved as CSV for tracking
- 📁 Files stored on `/mnt/nas_uploads` (or mounted volume)
- 🎨 Full-page upload interface with themed progress bar
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

### Docker Volumes

`docker-compose.yml` mounts a `designer_data` directory so designer avatars and
`designers.json` remain available between container restarts:

```yaml
volumes:
  - ./designer_data:/app/static/images/designers
  - ./designer_data/designers.json:/app/designers.json
```

Create this folder next to `docker-compose.yml` before running `docker compose up`.
Any avatars uploaded through the admin dashboard will then persist even if the container is rebuilt or restarted.


## 🧪 Running Tests

Install the dependencies and run the test suite with **pytest**:

```bash
pip install -r requirements.txt pytest
pytest
```

## 🛠️ Admin Dashboard

An authenticated admin area lets you upload designer avatars and change theme
colors defined in `static/css/dashboard.css`. Set `ADMIN_PASSWORD` in your
environment, visit `/admin`, and log in. The avatar form saves images to
`static/images/designers` and updates `designers.json`. The theme form edits CSS
variables directly in the stylesheet.
## 📌 Managing Dependencies

All Python packages in `requirements.txt` use pinned versions. To update them:

1. Create a fresh virtual environment and install the project.
2. Run `pip freeze > requirements.txt` to capture working versions.
3. Commit the updated file so builds remain reproducible.
## License

This project is licensed under the [MIT License](LICENSE).

