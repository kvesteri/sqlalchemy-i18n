

## Quickstart

In this directory
- `pip install -r requirements.txt`
- `pip install -e ../`

In [strive-rails-backend](github.com/rune-labs/strive-rails-backend/), do the "bootstrapping" section in order to create a local, seeded DB

Run `PGPASSWORD={your-password} FLASK_APP=app.py python -m flask run`


### vscode launch.json

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "PGPASSWORD": "your-password"
            },
            "args": [
                "run",
                "--no-debugger"
            ],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```