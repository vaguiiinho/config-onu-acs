#!/usr/bin/env python3
import pexpect
import sys
import re
import time
from dotenv import load_dotenv
import os


load_dotenv()

# Configurações
HOST = os.getenv("DEVICE_HOST")
USER = os.getenv("DEVICE_USER")
PASSWORD = os.getenv("DEVICE_PASSWORD")
ENABLE_PASSWORD = os.getenv("DEVICE_PASSWORD")
TIMEOUT = 60

# Argumento: aplicar ou somente exibir
MODO_APLICAR = len(sys.argv) > 1 and sys.argv[1] == "--aplicar"

# Comandos
CMD_ENTER_ONU = "cd onu"
CMD_LIST_ONU = "show authorization slot 4 p 3"
CMD_LIST_CONFIG_WAN = "show startup-config module onu_wan"
CMD_WAN_CFG = (
    "set wancfg sl {slot} {pon} {onu} ind 1 mode inter ty r 3800 0 nat en qos dis dsp pppoe pro dis "
    "emr_aroeiras_fib@tubaron.net key:khl1k+3& null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5"
)

CMD_TR069 = (
    "set remote_manage_cfg slot {slot} pon {pon} onu {onu} tr069 enable "
    "acs_url http://acs.ixc.tubaron.net/tr069 acl_user admin acl_pswd 7W9wqMdIeIPnxIsWZeeA "
    "inform enable interval 200 port 7545 user IXCSoft pswd 7W9wqMdIeIPnxIsWZeeA"
)
COMPATIBLE_ONUS = ["HG6145E", "5506-04-FA"]

# --------------------------------------------------------------------
def conectar(host, user, password, enable_password):
    print(f"Tentando conectar a {host}...")
    try:
        session = pexpect.spawn(f"telnet {host}", encoding="utf-8", timeout=TIMEOUT)

        session.expect("Login:")
        session.sendline(user)

        session.expect("Password:")
        session.sendline(password)

        session.expect("User>")
        session.sendline("en")

        session.expect("Password:")
        session.sendline(enable_password)

        session.expect("#")
        print("✅ Conectado com sucesso!\n")
        return session
    except pexpect.exceptions.TIMEOUT as e:
        print(f"❌ Erro de timeout ao conectar: {e}")
        sys.exit(1)

# --------------------------------------------------------------------
def get_full_output(session, stop_patterns=None, more_pattern=r"--Press any key to continue|Ctrl\+c to stop", timeout=60):
    """
    Captura toda a saída de um comando, tratando paginação.
    Retorna o texto completo.
    """
    if stop_patterns is None:
        stop_patterns = [r"Command execute success\.", r"[>#]"]

    output = ""
    while True:
        idx = session.expect([more_pattern] + stop_patterns, timeout=timeout)
        output += session.before.replace("\x00", "")
        if idx == 0:
            # Paginando → envia Enter
            session.send("\r")
            continue
        else:
            # Encontrou padrão final
            break

    return output.strip()

# --------------------------------------------------------------------
def send_command(session, command, force=False):
    print(f"[CMD] Executando: {command}")
    session.sendline(command)
    time.sleep(1)

# --------------------------------------------------------------------
def listar_onus(session):
    send_command(session, CMD_ENTER_ONU, force=True)
    session.expect(r"onu#")
    
    send_command(session, CMD_LIST_ONU)
    output = get_full_output(session)

    print("\n📋 Saída completa do comando:\n")
    print(output)

    # Filtrar ONUs compatíveis
    onus_compat = []
    for line in output.splitlines():
        match = re.search(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+([^\s]+)", line)
        if match:
            slot, pon, onu, onutype = match.groups()
            if onutype in COMPATIBLE_ONUS:
                onus_compat.append((slot, pon, onu, onutype))
                print(f"✅ Compatível: Slot {slot}, PON {pon}, ONU {onu}, Tipo {onutype}")

    print(f"\n📊 Total ONUs compatíveis: {len(onus_compat)}")
    return onus_compat

import re

import re

def listar_wan_cfg(session, onus_compat, timeout=60):
    """
    Lista a configuração WAN apenas das ONUs compatíveis.
    onus_compat: lista de tuplas (slot, pon, onu, onutype)
    """
    send_command(session, "cd ..", force=True)
    send_command(session, CMD_LIST_CONFIG_WAN, force=True)
    
    output = ""
    while True:
        try:
            chunk = session.read_nonblocking(size=4096, timeout=1)
        except Exception:
            chunk = b""
        
        if not chunk:
            continue
        
        if isinstance(chunk, bytes):
            chunk = chunk.decode(errors="ignore")
        
        output += chunk.replace("\x00", "")
        
        # paginação
        if "--Press any key to continue" in chunk:
            session.send(" ")  # envia espaço para continuar
        
        # prompt final
        if re.search(r"#\s*$", chunk):
            break

    # Limpa linhas vazias e espaços extras
    output = "\n".join([line.strip() for line in output.splitlines() if line.strip()])
    
    # Extrai só as linhas compatíveis
    filtered_lines = []
    for line in output.splitlines():
        match = re.search(r"set wancfg sl (\d+) (\d+) (\d+) ", line)
        if match:
            slot, pon, onu = match.groups()
            if (slot, pon, onu, None) in [(s, p, o, None) for s, p, o, t in onus_compat]:
                filtered_lines.append(line)
    
    print("\n📋 Config WAN das ONUs compatíveis:\n")
    for l in filtered_lines:
        print(l)
    
    return filtered_lines

# --------------------------------------------------------------------
def mostrar_tr069_e_wan(session, onus):
    # print(onus)
    # print("\n🔍 Exibindo TR-069 e WAN CFG (modo teste)...\n")
    for slot, pon, onu, onutype in onus:
        print(CMD_TR069.format(slot=slot, pon=pon, onu=onu))
    #     print(f"\n=== ONU {onu} ({onutype}) ===")
    #     print(f"[Simulação] Executando: {CMD_WAN_CFG} para Slot {slot}, PON {pon}")
    #     print("[TR069] http://acs.exemplo.com:7547")
    #     print("[WAN CFG] PPPoE usuário: cliente123 senha: ****")
    #     time.sleep(0.5)

    print(CMD_WAN_CFG.format(slot=slot, pon=pon, onu=onu))
    # print(CMD_LIST_CONFIG_WAN)

# --------------------------------------------------------------------
if __name__ == "__main__":
    session = conectar(HOST, USER, PASSWORD, ENABLE_PASSWORD)
    onus_compat = listar_onus(session)
    # mostrar_tr069_e_wan(session, onus_compat)
    listar_wan_cfg(session)
    print("\n✅ Script finalizado!")
