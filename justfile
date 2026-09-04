set windows-powershell := true

# run dev docker containers
docker:
  docker compose up -d --build

ruff:
    uv run ruff check . --fix
    uv run ruff format .
