import subprocess

def executar_comando(comando: str) -> None:
    subprocess.run(comando, shell=True, check=True)
