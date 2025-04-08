# README

## Running the application

In backend:
```bash
$ USER_DATABASE_STRING="user:test user2:test2" JWT_SECRET_KEY="test_key" uv run uvicorn backend.main:app --reload
```

In frontend:
```bash
$ npm run dev
```

## Misc

* API docs: http://127.0.0.1:8000/docs