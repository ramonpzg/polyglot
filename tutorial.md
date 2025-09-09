# Tutorials Walk-Through


## Python + JS

```sh
uv init montecurious
```
```sh
cd montecurious
```
```sh
tree .
```
```
.
├── main.py
├── pyproject.toml
└── README.md

1 directory, 3 files
```

```sh
mkdir src src/montecurious src/montecurious/static frontend frontend/src
```
```sh
touch src/montecurious/__init__.py src/montecurious/__main__.py src/montecurious/server.py src/montecurious/monte_carlo.py src/montecurious/static/.gitkeep
```
```sh
touch frontend/package.json frontend/vite.config.js frontend/index.html frontend/src/App.jsx frontend/src/index.js
```


montecurious/
├── pyproject.toml
├── README.md
├── src/
│   └── montecurious/
│       ├── __init__.py
│       ├── __main__.py       # Entry point
│       ├── server.py         # FastAPI server
│       ├── monte_carlo.py    # Core computation
│       └── static/           # Frontend build output
│           └── .gitkeep
└── frontend/                 # SolidJS source
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        └── index.js
