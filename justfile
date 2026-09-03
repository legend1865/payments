set windows-powershell := true

# run dev docker containers
docker:
  docker-compose -f docker-compose-dev.yml up -d --build

ruff:
    uv run ruff check . --fix
    uv run ruff format .