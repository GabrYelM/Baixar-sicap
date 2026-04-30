import tkinter as tk
from tkinter import messagebox
import sys
import threading
import BotSICAP as BS

# Redireciona as mensagens do terminal para a UI
class redirectTerminal:

    # Passamos a caixa de txt do tkInter para o redirecionador
    def __init__(self, widget_text):
        self.widget_text = widget_text

    # Funcao que faz a escrita na caixa de txt
    def write(self, txt):
        self.widget_text.insert(tk.END, txt)
        self.widget_text.see(tk.END) 
    
    # Serve para limpar a memoria, porem o tkInter ja faz esse gerenciamento, mas se a funcao nao estiver no codigo o python trava
    def flush(self):
        pass

# Configura a funçao de parada do bot
stop = threading.Event()

# Gerencia o funcionamento de duas coisas ao mesmo tempo, para q a UI mostre o texto enquanto o bot trabalha
def run_thread(dI, dF, user, password):
    try:
        # Inicia o bot e avisa caso de erro
        BS.automateDownloadSicap(dI, dF, user, password, stop)
    except Exception as e:
        print(f"\nERRO CRÍTICO NO ROBÔ: {e}")

    # Garante que o codigo avisa ao ser cancelado ou finalizado
    finally:
        print("\n" + "="*30)
        print("PROCESSO FINALIZADO OU CANCELADO!")
        print("="*30)
        
        # Troca o botao de cancelar pelo de voltar
        btn_cancel.pack_forget()
        btn_back.pack(pady=10)

        # Reativa o botão de cancelar para o próximo uso
        btn_cancel.config(state=tk.NORMAL)

# Configura o botao de cancelar para o bot
def stop_bot():
    print("\n[!] CANCELAMENTO SOLICITADO! O robô vai parar na próxima ação segura...")
    stop.set()
    btn_cancel.config(state=tk.DISABLED)

# Configura o botao de voltar para a tela inicial
def go_back():
    frame_log.pack_forget()
    frame_login.pack(pady=20)
    caixa_de_texto.delete(1.0, tk.END)
    btn_back.pack_forget()
    btn_cancel.pack(pady=10)

# Coleta as informacoes dadas pelo usuario e verifica se esta tudo preenchido 
def start_bot():
    # Coleta os dados
    user = entry_user.get()
    password = entry_pass.get()
    dI = entry_start.get()
    dF = entry_end.get()

    # Verifica se todos os dados foram informados
    if not user or not password or not dI or not dF:
        messagebox.showwarning("Aviso", "Por favor, preencha todos os campos antes de iniciar!")
        return

    # Limpa o sinalizador caso seja a segunda vez que a pessoa roda o robô
    stop.clear() 

    # Troca para a tela com terminal
    frame_login.pack_forget()
    frame_log.pack(fill="both", expand=True, padx=10, pady=10)
    sys.stdout = redirectTerminal(caixa_de_texto)

    # Configura a thread
    thread_bot = threading.Thread(
        target=run_thread, 
        args=(dI, dF, user, password),
        daemon=True 
    )
    thread_bot.start()

# Cria a janela principal
window = tk.Tk()
window.title("Bot - SICAP")
window.geometry("600x500")

# Primeiro frame a ser apresentado
frame_login = tk.Frame(window)
frame_login.pack(pady=20)

# Campos de digitacao
# user
tk.Label(frame_login, text="Usuário do e-Saude:").pack()
entry_user = tk.Entry(frame_login, width=35)
entry_user.pack(pady=5)
# senha
tk.Label(frame_login, text="Senha:").pack()
entry_pass = tk.Entry(frame_login, width=35, show="*")
entry_pass.pack(pady=5)
# data inicial
tk.Label(frame_login, text="Data Inicial (MM/AAAA):").pack()
entry_start = tk.Entry(frame_login, width=35)
entry_start.pack(pady=5)
# data final
tk.Label(frame_login, text="Data Final (MM/AAAA):").pack()
entry_end = tk.Entry(frame_login, width=35)
entry_end.pack(pady=5)

# Botao de start
btn_iniciar = tk.Button(frame_login, text="Iniciar Download", command=start_bot, bg="#0078D7", fg="white", font=("Arial", 10, "bold"))
btn_iniciar.pack(pady=20)

# segundo frame (log)
frame_log = tk.Frame(window)

tk.Label(frame_log, text="Progresso do Robô:", font=("Arial", 10, "bold")).pack(anchor="w")

# Caixa do log
caixa_de_texto = tk.Text(frame_log, bg="black", fg="white", font=("Consolas", 9), wrap="word")
caixa_de_texto.pack(fill="both", expand=True)

# Botao de cancelar e voltar
btn_cancel = tk.Button(frame_log, text="X Cancelar Execução", command=stop_bot, bg="#D32F2F", fg="white", font=("Arial", 10, "bold"))
btn_cancel.pack(pady=10)
btn_back = tk.Button(frame_log, text="← Voltar ao Formulário", command=go_back, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))

# Mantem a janela aberta
window.mainloop()