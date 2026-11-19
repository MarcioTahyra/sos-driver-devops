import subprocess


def executar_comando(argumentos: list[str]) -> None:
    subprocess.run(argumentos, shell=False, check=True)
