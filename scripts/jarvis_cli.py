"""
J.A.R.V.I.S. — Cliente de terminal.
Conecta con el backend FastAPI para enrutar comandos de voz/texto
a través del sistema de agente con permisos y lista blanca.

Uso:
    python scripts/jarvis_cli.py
    python scripts/jarvis_cli.py --host http://localhost:8000
"""

import sys
import json
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError


DEFAULT_HOST = "http://localhost:8000"


def consultar(mensaje: str, modo: str = "general", host: str = DEFAULT_HOST) -> Optional[str]:
    """Envía mensaje al backend y devuelve la respuesta completa."""
    url = f"{host}/chat"
    payload = json.dumps({"message": mensaje, "mode": modo}).encode()

    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=120) as resp:
            respuesta = ""
            for linea_bytes in resp:
                linea = linea_bytes.decode().strip()
                if linea.startswith("data: "):
                    datos = linea[6:]
                    if datos == "[DONE]":
                        break
                    try:
                        parsed = json.loads(datos)
                        if "token" in parsed:
                            respuesta += parsed["token"]
                        if "error" in parsed:
                            return f"[Error] {parsed['error']}"
                    except json.JSONDecodeError:
                        continue
            return respuesta
    except URLError as e:
        return f"[Error de conexión] ¿El backend está corriendo? Detalle: {e}"
    except Exception as e:
        return f"[Error inesperado] {e}"


def mostrar_banner():
    print("=" * 48)
    print("      SISTEMA J.A.R.V.I.S. - TERMINAL")
    print("=" * 48)
    print("  Escribe 'salir' o 'exit' para terminar.")
    print("  Escribe 'ayuda' o 'qué puedes hacer' para ver comandos.")
    print("  Modo: Chat + Acciones (voz, apps, música)")
    print()


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Terminal")
    parser.add_argument("--host", default=DEFAULT_HOST, help="URL del backend")
    args = parser.parse_args()

    mostrar_banner()

    while True:
        try:
            entrada = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if not entrada:
            continue

        if entrada.lower() in ("salir", "exit", "quit", "q"):
            print("J.A.R.V.I.S. desconectado.")
            break

        resultado = consultar(entrada, host=args.host)
        if resultado:
            print(resultado)
        else:
            print("[Sin respuesta del backend]")


if __name__ == "__main__":
    main()
