# How to run project at Docker

1) Install Docker (on Windows with linux daemon)

2) Clone or download project from https://github.com/piranhaCZ/books

3) Copy and rename `docker-compose.example.yaml` to `docker-compose.yaml`.

4) At new `docker-compose.yaml` file change volumes path (at line 8), etc: `C:\Users\User\PycharmProjects\books:/usr/src/app/`

5) Copy and rename `.env.dev.example` to `.env.dev`.

6) Build image and run container