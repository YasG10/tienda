# Despliegue en Render y GitHub

## 1. Prepara tu repositorio

1. Inicializa git (si no lo has hecho):
   ```sh
   git init
   git add .
   git commit -m "Proyecto inicial listo para Render"
   ```
2. Crea un repositorio en GitHub y sigue las instrucciones para hacer push:
   ```sh
   git remote add origin https://github.com/tuusuario/tu-repo.git
   git branch -M main
   git push -u origin main
   ```

## 2. Archivos importantes
- `.gitignore` (ya configurado)
- `requirements.txt` (ya generado)
- `Procfile` y `render.yaml` (ya generados)

## 3. Configura Render
1. Ve a https://dashboard.render.com y crea un nuevo servicio Web.
2. Conecta tu repo de GitHub.
3. Elige Python 3.11+ y selecciona el directorio raíz del proyecto.
4. Render detectará automáticamente el `Procfile` y `requirements.txt`.
5. En "Environment Variables" agrega:
   - `DJANGO_SECRET_KEY` (elige una secreta)
   - `DJANGO_DEBUG` = `False`
   - `ALLOWED_HOSTS` = `tu-dominio.onrender.com`
   - Cualquier otra variable sensible (tokens, etc)

## 4. Migraciones y archivos estáticos
Render ejecuta automáticamente:
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`

## 5. Endpoint keep-alive
- Render apaga apps gratuitas por inactividad. Usa el endpoint:
  ```
  GET https://<tu-app>.onrender.com/keep-alive/
  ```
  Haz que tu software externo lo consulte cada 5 minutos para evitar que se congele.

## 6. Notas
- Para servir archivos de usuario (media), usa un bucket externo (S3, Cloudinary) en producción.
- Cambia `DEBUG = False` en producción.
- Protege tu `SECRET_KEY` y tokens en variables de entorno.

---

¡Listo para desplegar en Render y mantener activo gratis!
