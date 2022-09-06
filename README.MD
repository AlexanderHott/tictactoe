# Multiplayer Tic Tac Toe

## Quick Start

```
python main.py host
```

```
python main.py connect
```

## Using a different host or port

```
python main.py host --host 192.168.1.1 --port 8888
```

```
python main.py connect --host 192.168.1.1 --port 8888
```

## Help

```
usage: main.py [-h] [--host HOST] [--port PORT] connection

positional arguments:
  connection   'host' or 'connect'

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  host to connect to
  --port PORT  port to connect to
```
