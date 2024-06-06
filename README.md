# Simple Django based billing application

This project is currently work in progress and has a long way to go until
it is feature complete. Feel free to look at the source code nonetheless
and use it if you find it useful.


## Development

Is it recommended to use the included VSCode devcontainer.

After loading into the container you need to open an additional terminal to enable tailwind processing / hot-reloading.

Terminal 1:
```sh
python manage.py runserver
```

Terminal 2:
```sh
python manage.py tailwind start
```
Of course, the tailwind server does not need to run when no CSS changes are being made.

## Deployment

Run `docker compose up -d` to spin up the app container and a postgres instance. An S3 bucket is assumed to be running on a public endpoint and needs to be configured by providing the respective ENV variables.

The docker entrypoint runs `migrate` and `collectstatic` every time the container is spun up. So long as .env is configured correctly, deployment is hands-off entirely.

It is recommended to run `python manage.py tailwind build` before deployment to minify CSS for production use.

## App Components

- DRF
- HTMX
- AlpineJS
- TailwindCSS + DaisyUI
