PORT ?= 8010

.PHONY: run stop restart

run:
	uvicorn backend.app.main:app --reload --port=$(PORT)

stop:
	@fuser -k $(PORT)/tcp || true

restart: stop run




make run       # runs on default 8010
make stop      # kills whatever is on 8010
make restart   # cleans & restarts
