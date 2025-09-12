#!/usr/bin/env python3
import pexpect
import sys
import re
import requests
import base64
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
CMD_LIST_ONU = "show authorization slot 2 p 1"
CMD_LIST_CONFIG_WAN = "show startup-config module onu_wan"
# CMD_WAN_CFG = (
#     "set wancfg sl {slot} {pon} {onu} ind 1 mode tr069_internet ty r 3800 0 nat en qos dis dsp pppoe pro dis "
#     "emr_aroeiras_fib@tubaron.net key:khl1k+3& null auto entries 6 fe1 fe2 fe3 fe4 ssid1 ssid5"
# )

CMD_TR069 = (
    "set remote_manage_cfg slot {slot} pon {pon} onu {onu} tr069 enable "
    "acs_url http://acs.ixc.tubaron.net/tr069 acl_user admin acl_pswd 7W9wqMdIeIPnxIsWZeeA "
    "inform enable interval 200 port 7545 user IXCSoft pswd 7W9wqMdIeIPnxIsWZeeA"
)
COMPATIBLE_ONUS = ["HG6145E", "5506-04-FA"]

# IXCSoft API
IXC_URL = os.getenv("IXC_API_URL")
IXC_TOKEN = os.getenv("IXC_TOKEN")

# --------------------------------------------------------------------
def conectar(host, user, password, enable_password):
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

def listar_wan_cfg(session, onus_compat, timeout=60):
    session.expect(r"#")
    send_command(session, "cd ..")
    session.expect(r"#")
    send_command(session, CMD_LIST_CONFIG_WAN)
    session.expect(r"--Press any key to continue|Ctrl\+c to stop")
    
    stop_patterns = [r"Command execute success\.", r"[>#]"]
    more_pattern=r"--Press any key to continue|Ctrl\+c to stop"
    output = ""
    
    while True:
        try:
            chunk = session.before
        except Exception:
            chunk = b""
        
        if not chunk:
            continue
       
        index = session.expect([more_pattern] + stop_patterns, timeout=timeout)    
        
        output += chunk.replace("\x00", "")
        if index == 0:
            session.send(" ")
            continue
        else:
            break
    # # Limpa linhas vazias e espaços extras
    lines = [line.strip() for line in output.splitlines() if line.strip()]

    # # Monta chaves de filtro para cada ONU compatível
    wanted_keys = {
        f"set wancfg sl {slot} {pon} {onu}" for (slot, pon, onu, _onutype) in onus_compat
    }

    # # Mantém apenas linhas referentes às ONUs compatíveis
    filtered_lines = [line for line in lines if any(key in line for key in wanted_keys)]
    
    

    # Aplica limpeza em todas as linhas filtradas
    linhas_limpas = []
    for linha in filtered_lines:
        limpa = limpar_saida(linha)
        if limpa:  # Só adiciona se não estiver vazia após limpeza
            linhas_limpas.append(limpa)
    # Atualiza as linhas de PPPoE substituindo a chave por senha da API
    updated_lines = _atualizar_wan_com_senha(session, linhas_limpas)
    return updated_lines


def limpar_saida(texto: str) -> str:
    # Remove backspaces e o caractere anterior
    texto = re.sub(r".\x08", "", texto)
    texto = re.sub(r"\x08+", "", texto)

    # Para cada linha, se tiver \r, mantém apenas o que vem depois
    linhas = []
    for linha in texto.splitlines():
        if "\r" in linha:
            linha = linha.split("\r")[-1]
        
        # Remove espaços extras no início e fim
        linha = linha.strip()
        
        # Remove linhas que começam com comentários (--)
        if linha.startswith('--'):
            continue
            
        # Remove linhas vazias
        if not linha:
            continue
            
        linhas.append(linha)

    # Remove espaços extras entre palavras (múltiplos espaços viram um só)
    texto_limpo = "\n".join(re.sub(r'\s+', ' ', linha) for linha in linhas)

    return texto_limpo


def _extrair_login_e_chave(linha):
    """
    Extrai o modo (após 'mode'), o login PPPoE (email) e a chave atual (após 'key:')
    de uma linha wancfg em UMA única regex.

    Retorna (mode, login, chave) ou (None, None, None) se não encontrar.
    """
    pattern_unico = (
        r"\bmode\s+(\S+).*?"          # captura o modo após 'mode'
        r"pppoe\s+pro\s+(?:en|dis)\b"  # estado do PPPoE (en/dis)
        r".*?(\S+)\s+"                 # tolera texto de paginação e captura o login
        r"key:(\S+)"                    # captura a chave após 'key:'
    )
    match = re.search(pattern_unico, linha)
    if not match:
        return None, None, None
    return match.group(1), match.group(2), match.group(3)


def _buscar_senha_ixc(login):
    """
    Consulta a API IXCSoft para obter a senha do login informado.
    Retorna a senha (string) ou None em caso de falha.

    """
    if not IXC_URL or not IXC_TOKEN:
        return None

    payload = {
        "qtype": "radusuarios.login",
        "query": login,
        "oper": "=",
        "page": "1",
        "rp": "20",
        "sortname": "radusuarios.id",
        "sortorder": "asc",
    }

    try:
        basic_token = base64.b64encode(IXC_TOKEN.encode("utf-8")).decode("utf-8")
        headers = {
            "ixcsoft": "listar",
            "Authorization": f"Basic {basic_token}",
            "Content-Type": "application/json",
        }
        # Mantém a assinatura próxima ao exemplo fornecido
        resp = requests.post(IXC_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        registros = data.get("registros") or []
        if not registros:
            return None
        senha = registros[0].get("senha")
        return senha
    except Exception:
        return None


def _atualizar_wan_com_senha(session, linhas):
    """
    Para cada linha wancfg PPPoE com 'key:<valor>', consulta a API e substitui por '<senha>'.
    Linhas sem PPPoE/key permanecem inalteradas.
    """
    resultado = []
    for linha in linhas:
        if "pppoe" in linha and "key:" in linha:
            mode, login, chave = _extrair_login_e_chave(linha)
            if mode == "inter":
                linha = re.sub(r"\bmode\s+[^\s]+", "mode tr069_internet", linha)
            if login:
                senha = _buscar_senha_ixc(login)
                if senha:
                    linha = re.sub(r"\bkey:[^\s]+", senha, linha)
        resultado.append(linha)
    return resultado


# --------------------------------------------------------------------
def mostrar_tr069_e_wan(session, onus):
    # for slot, pon, onu, onutype in onus:
        # print(CMD_TR069.format(slot=slot, pon=pon, onu=onu))
    print(listar_wan_cfg(session, onus))

# --------------------------------------------------------------------
def aplicar_tr069_e_wan(session, onus):

    for slot, pon, onu, onutype in onus:
       tr069 = CMD_TR069.format(slot=slot, pon=pon, onu=onu)
       send_command(session, tr069, force=True)
    # Em modo aplicar, gerar saída no formato solicitado:
    # 1) Cabeçalho "cd /onu/lan"
    # 2) Para cada ONU: linhas "set wancfg sl <slot> <pon> <onu> ..." (apenas ind 1),
    #    com a linha PPPoE primeiro e depois a linha de ip-stack-mode
    # 3) "apply wancfg slot <slot> <pon> <onu>"
    wans = listar_wan_cfg(session, onus)
    linhas = [ln for ln in (wans.splitlines() if isinstance(wans, str) else wans) if ln and ln.strip()]
    # Entrar no contexto correto para aplicar as configurações
    send_command(session, "cd /onu/lan", force=True)

    # Ordena ONUs por slot, pon, onu numericamente para saída estável
    def _as_ints(t):
        s, p, o, tname = t
        try:
            return (int(s), int(p), int(o))
        except Exception:
            return (s, p, o)

    apply_cmds = []

    for slot, pon, onu, _onutype in sorted(onus, key=_as_ints):
        chave = f"set wancfg sl {slot} {pon} {onu}"
        grupo = [l for l in linhas if re.match(rf"^{re.escape(chave)}\b", l)]
        # manter apenas ind 1
        grupo = [l for l in grupo if re.search(r"\bind\s+1\b", l)]
        # ordenar: PPPoE primeiro (contém ' mode '), depois ip-stack-mode
        grupo.sort(key=lambda l: 1 if "ip-stack-mode" in l else 0)

        for linha in grupo:
            send_command(session, linha)

        apply_cmds.append(f"apply wancfg slot {slot} {pon} {onu}")

    # separador e depois todos os apply
    if apply_cmds:
        for cmd in apply_cmds:
            send_command(session, cmd)



# --------------------------------------------------------------------
if __name__ == "__main__":
    session = conectar(HOST, USER, PASSWORD, ENABLE_PASSWORD)
    onus_compat = listar_onus(session)
    if MODO_APLICAR:
        aplicar_tr069_e_wan(session, onus_compat)
    else:
        mostrar_tr069_e_wan(session, onus_compat)
    print("\n✅ Script finalizado!")



