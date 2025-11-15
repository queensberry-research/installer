set dotenv-load := true
set positional-arguments := true

install *args:
  uv run python3 -m installer.main "$@"
