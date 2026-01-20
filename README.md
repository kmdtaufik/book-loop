# BookLoop 📚

A desktop application for managing book exchanges and swaps. Built with Python, featuring a modern GUI powered by CustomTkinter and a FastAPI backend.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Ubuntu%20%7C%20Arch-lightgrey.svg)

## ✨ Features

- 🔐 **Secure Authentication** - User registration and login with password hashing
- 📖 **Book Management** - Upload, browse, and manage your book collection
- 🔄 **Book Swaps** - Request and manage book exchanges with other users
- 💾 **Session Management** - Automatic session persistence using system keyring
- 🎨 **Modern UI** - Dark mode interface with CustomTkinter
- 🌐 **Cloud Backend** - FastAPI backend hosted on Render

## 🖥️ Desktop Client

### Installation

#### Windows
Download and run the latest installer:
```
BookLoop-Setup-Windows-x64.exe
```
The installer will create desktop shortcuts and start menu entries.

#### Ubuntu/Debian
Download and install the .deb package:
```bash
sudo dpkg -i bookloop_0.1.0_amd64.deb
```

#### Arch Linux
Download and install the package:
```bash
sudo pacman -U bookloop-0.1.0-1-x86_64.pkg.tar.zst
```

### Latest Releases
Get the latest builds from the [Releases](https://github.com/kdx/book-loop/releases) page.

## 🚀 Development Setup

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database (for backend)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/kdx/book-loop.git
cd book-loop
```

2. **Install dependencies**
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

3. **Configure environment**
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost/bookloop
SECRET_KEY=your-secret-key-here
API_URL=http://localhost:8000
```

4. **Initialize database**
```bash
python reset_db.py
```

5. **Run the backend**
```bash
uvicorn app.main:app --reload
```

6. **Run the desktop client**
```bash
uv run python client/main.py
```

## 📦 Project Structure

```
book-loop/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   └── schemas/           # Pydantic schemas
├── client/                # Desktop client
│   ├── ui/                # UI screens
│   ├── api_client.py      # API client wrapper
│   └── main.py            # Application entry point
├── .github/
│   └── workflows/         # CI/CD workflows
│       └── build.yml      # Build installers for all platforms
├── pyproject.toml         # Project dependencies
└── README.md
```

## 🔨 Building from Source

### Build all platforms
The GitHub Actions workflow automatically builds installers for Windows, Ubuntu, and Arch Linux on every push.

### Manual build
```bash
# Install PyInstaller
uv pip install pyinstaller

# Build executable
pyinstaller --noconsole --onefile \
  --add-data "client/ui:client/ui" \
  --add-data "icon.ico:." \
  --hidden-import=api_client \
  --hidden-import=ui.dashboard_screen \
  --hidden-import=ui.login_screen \
  --hidden-import=ui.register_screen \
  --hidden-import=ui.swaps_screen \
  --hidden-import=ui.upload_dialog \
  --hidden-import=ui.swap_dialog \
  --paths=client \
  --name BookLoop \
  --icon icon.ico \
  client/main.py
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Database
- **Pydantic** - Data validation
- **JWT** - Authentication tokens

### Desktop Client
- **CustomTkinter** - Modern GUI framework
- **Requests/httpx** - HTTP client
- **Keyring** - Secure credential storage
- **Pillow** - Image handling

## 📝 API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `GET /books` - List all books
- `POST /books` - Upload a book
- `GET /transactions` - Get user's transactions
- `POST /transactions` - Create swap request

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- **Backend API**: https://bookloop-api.onrender.com
- **Documentation**: Coming soon
- **Issues**: [GitHub Issues](https://github.com/kdx/book-loop/issues)

## 💡 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)
- Package management with [uv](https://github.com/astral-sh/uv)
