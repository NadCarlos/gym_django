# Checklist CI/CD produccion

Este checklist resume lo que hay que revisar antes de subir y activar el pipeline de GitHub Actions.

## Estado del pipeline

- [ ] El workflow `.github/workflows/deploy-prod.yml` esta commiteado y pusheado.
- [ ] El push a `develop` corre CI: `manage.py check`, tests y build de `Dockerfile.prod`.
- [ ] El push a `production` corre CI y, si pasa, ejecuta deploy por SSH.
- [ ] El deploy solo corre en `production`; `develop` no despliega.
- [ ] `.env.prod` no esta commiteado y queda solo en el servidor.
- [ ] `.dockerignore` esta commiteado para excluir `.env`, `.env.*`, backups y caches del build Docker.

## Secrets de GitHub Actions

Cargar estos secrets en GitHub, en `Settings > Secrets and variables > Actions`:

- [ ] `PROD_HOST`: IP o dominio del servidor de produccion.
- [ ] `PROD_USER`: usuario SSH usado para deploy.
- [ ] `PROD_SSH_KEY`: clave privada SSH para entrar al servidor. Debe incluir el bloque completo `-----BEGIN OPENSSH PRIVATE KEY-----`.
- [ ] `PROD_APP_DIR`: ruta absoluta del repo en el servidor. Ejemplo: `/home/usuario/gym_django`.

Opcionales:

- [ ] `PROD_SSH_PORT`: puerto SSH si no es `22`.
- [ ] `PROD_HEALTHCHECK_URL`: URL que el servidor consulta al final del deploy. Default: `http://localhost:8000/`.

## Pares de keys SSH

El pipeline necesita dos accesos diferentes. Se pueden usar keys separadas o la misma key, pero hay que cargar cada parte en el lugar correcto:

| Acceso | Private key | Public key |
| --- | --- | --- |
| GitHub Actions -> servidor | Va en GitHub Secret `PROD_SSH_KEY` | Va en `~/.ssh/authorized_keys` del usuario `PROD_USER` en el servidor |
| Servidor -> GitHub | Queda en el servidor, por ejemplo `~/.ssh/github_gym_django_deploy` | Va en GitHub `Settings > Deploy keys` del repo |

Si se usa la misma key para ambos accesos:

- [ ] La private key va en GitHub Secret `PROD_SSH_KEY`.
- [ ] Esa misma private key queda guardada en el servidor, por ejemplo `~/.ssh/prod_deploy_key`.
- [ ] La public key va en `~/.ssh/authorized_keys` del usuario `PROD_USER`.
- [ ] Esa misma public key tambien va en GitHub `Settings > Deploy keys` del repo, con permisos read-only.

Si falla `Permission denied (publickey,password)` en el primer `ssh`, revisar el acceso GitHub Actions -> servidor: `PROD_SSH_KEY`, `PROD_USER`, `PROD_HOST`, `PROD_SSH_PORT` y `authorized_keys` del server.

## Servidor de produccion

- [ ] El repo esta clonado en la ruta definida por `PROD_APP_DIR`.
- [ ] La rama `production` existe en el server o puede crearse desde `origin/production`.
- [ ] El archivo `.env.prod` existe en la raiz del repo en el server.
- [ ] Docker esta instalado.
- [ ] Docker Compose plugin funciona con `docker compose version`.
- [ ] El usuario `PROD_USER` puede ejecutar Docker sin `sudo`, o el deploy fallara.
- [ ] El server puede hacer `git fetch origin production` usando su propia credencial Server -> GitHub.
- [ ] Nginx/certbot/volumenes usados por `docker-compose-prod.yaml` existen y tienen permisos correctos.
- [ ] Si se usa `PROD_HEALTHCHECK_URL` con dominio HTTPS, el certificado ya esta vigente.

## Acceso del server a GitHub

El comando remoto `git fetch origin production` usa el acceso servidor -> GitHub. Este acceso debe estar configurado en el servidor.

Si queres reutilizar la misma key que ya usa GitHub Actions -> servidor:

1. En GitHub, agregar la misma public key como Deploy Key del repo: `Settings > Deploy keys > Add deploy key`. Para este pipeline alcanza con permisos de lectura, sin marcar write access.
2. En el servidor, configurar SSH para que `github.com` use esa private key. Reemplazar `~/.ssh/prod_deploy_key` por el path real de la private key que generaste:

```bash
cat >> ~/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/prod_deploy_key
  IdentitiesOnly yes
EOF
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config ~/.ssh/prod_deploy_key
ssh-keyscan github.com >> ~/.ssh/known_hosts
ssh -T git@github.com
cd <PROD_APP_DIR>
git fetch origin production
```

Si preferis separar permisos, generar otra key en el server y cargar su public key como Deploy Key read-only. Alternativa: cambiar el remote del repo en el servidor a HTTPS con un token.

## Checks antes de subir

Ejecutar localmente cuando sea posible:

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-prod.yml')); print('yaml ok')"
git diff --check
docker compose --env-file .env.prod -f docker-compose-prod.yaml config --quiet
docker build -f Dockerfile.prod .
```

Para probar tests de forma equivalente al CI, hace falta MySQL disponible con las variables del workflow. Actualmente el repo no tiene tests efectivos: Django reporta `Found 0 test(s)`, pero el comando de tests ya queda conectado al pipeline.

## Primer deploy

- [ ] Pushear primero a `develop` y confirmar que el workflow pasa.
- [ ] Mergear o pushear a `production` solo despues de CI verde.
- [ ] En GitHub Actions, revisar el run de `production` y confirmar que el job `Deploy` se ejecuta.
- [ ] En el server, verificar contenedores:

```bash
cd <PROD_APP_DIR>
make prod-status
docker logs cermed_web --tail 100
docker logs cermed_nginx --tail 100
```

- [ ] Probar la app desde el dominio real.

## Rollback simple

Si el deploy falla o hay regresion:

```bash
cd <PROD_APP_DIR>
git checkout production
git reset --hard <commit_anterior_estable>
make prod-deploy
make prod-status
```

Despues del rollback, revisar logs y confirmar la app desde el navegador.

## Cosas a tener en cuenta

- El workflow usa MySQL 5.7 en CI para acercarse al stack productivo.
- El build Docker puede mostrar warnings por formato legacy de `ENV` en `Dockerfile.prod`; hoy no bloquean el build.
- Si el smoke test falla por `ALLOWED_HOSTS`, configurar `PROD_HEALTHCHECK_URL` con un host permitido por Django.
- Si `git pull --ff-only` falla en el server, hay cambios locales o divergencia: resolver manualmente antes de redeployar.
- No cargar `.env.prod` como secret completo salvo que se cambie la estrategia; el pipeline actual espera que ya exista en el server.
