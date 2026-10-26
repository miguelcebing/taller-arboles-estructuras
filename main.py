"""Start the Nariño biodiversity explorer with a single command."""

import argparse
import threading
import webbrowser

from src.narino_taxonomy import Explorer
from src.server import make_server


def parse_args():
    parser = argparse.ArgumentParser(
        description="Explorador taxonómico de la biodiversidad de Nariño."
    )
    parser.add_argument("--port", type=int, default=8000, help="Puerto local (por defecto 8000).")
    parser.add_argument("--no-browser", action="store_true", help="No abrir el navegador automáticamente.")
    return parser.parse_args()


def main():
    args = parse_args()
    explorer = Explorer.with_seed_data()
    try:
        server = make_server(args.port, explorer)
    except OSError as exc:
        print(f"No se pudo abrir el puerto {args.port}: {exc}")
        print("Prueba con otro puerto, por ejemplo: python main.py --port 8080")
        return 1

    host, port = server.server_address
    url = f"http://{host}:{port}/"
    print(f"Explorador taxonómico de Nariño en {url}")
    print(f"{len(explorer.registry)} especies cargadas. Ctrl+C para detener.")
    if not args.no_browser:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
