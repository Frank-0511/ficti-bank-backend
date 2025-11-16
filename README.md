# ficti-bank-backend

Backend bancario con FastAPI y SQLAlchemy

## Requisitos previos

- Python 3.12
- MySQL y headers de desarrollo
- pkg-config

### Linux (Ubuntu/Debian)

Instala las dependencias del sistema necesarias para compilar `mysqlclient`:
```bash
sudo apt update
sudo apt install -y pkg-config libmysqlclient-dev python3.12-dev
```

### macOS

- [Homebrew](https://brew.sh/)
- MySQL y pkg-config (para compilar mysqlclient)

Instala Homebrew si no lo tienes:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Instala dependencias nativas:
```bash
brew install pkg-config
brew install mysql
```

## Instalación

1. Clona el repositorio:
	```bash
	git clone https://github.com/w2ria/ficti-bank-backend.git
	cd ficti-bank-backend
	```

2. Crea y activa un entorno virtual:
	```bash
	python3 -m venv app/venv
	source app/venv/bin/activate
	```

3. Instala las dependencias Python:
	```bash
	pip install --upgrade pip
	pip install -r requirements.txt
	```

## Configuración

1. Copia el archivo `.env.example` a `.env` y edítalo con tus credenciales:
	```env
	USER_DB=avnadmin
	PASSWORD_DB=tu_password
	HOST_DB=tu_host
	PORT_DB=tu_puerto
	NAME_DB=tu_base
	SECRET_KEY=clave_secreta
	ALGORITHM=HS256
	ACCESS_TOKEN_EXPIRE_MINUTES=30
	```

2. Si usas conexión directa, asegúrate de que el dialecto en la URL sea correcto:
	```env
	DATABASE_URL=mysql+mysqlclient://usuario:contraseña@host:puerto/base?ssl-mode=REQUIRED
	```

## Ejecución

Desde la raíz del proyecto, ejecuta:
```bash
uvicorn app.main:app --reload
```

## Documentación automática (Swagger)

Con el servidor corriendo, abre en tu navegador:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Notas para macOS

- Los comandos `brew install` y la compilación de `mysqlclient` solo aplican para macOS. No intentes estos pasos en Windows.
- Si tienes errores de compilación con `mysqlclient`, revisa que tengas los headers de MySQL instalados.

## Soporte

Para dudas o problemas, abre un issue en el repositorio.
