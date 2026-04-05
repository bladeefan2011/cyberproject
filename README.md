# Cyber Security Base project

***Clone the repository to your system***
```bash
git clone https://github.com/bladeefan2011/cyberproject
```

***Move to the directory***
```bash
cd cyberproject
```

***Activate the virtual environment***
```bash
python3 -m venv .venv
source .venv/bin/activate
```

***The program requires Django, install with***
```bash
pip install "Django>=6.0,<6.1"
```

***Initialize the database***
```bash
python3 mysite/manage.py migrate
```

***Create an admin account***
```bash
python3 manage.py createsuperuser
```

***Start the server***
```bash
python3 mysite/manage.py runserver 127.0.0.1:8000
```

***The site can now be found at***
```bash
http://127.0.0.1:8000/
```