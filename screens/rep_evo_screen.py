import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mb
from datetime import datetime, timedelta
import calendar
import threading
from models.coletor_repC import RepEvoCollector


class RepEvoScreen(ttk.Frame):
    """Tela para buscar registros de ponto do REP C EVO"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configurações do REP
        self.rep_host = tk.StringVar(value="192.168.1.11")
        self.rep_port = tk.IntVar(value=3000)
        self.rep_username = tk.StringVar(value="teste fabrica")
        self.rep_password = tk.StringVar(value="132435")
        
        # Variáveis de busca
        self.pis_funcionario = tk.StringVar()
        self.data_inicio = tk.StringVar()
        self.data_fim = tk.StringVar()
        
        # Status
        self.status_text = tk.StringVar(value="Aguardando conexão...")
        self.is_connected = False
        self.is_collecting = False
        
        # Collector instance
        self.collector = None
        
        # Definir datas padrão (dia 1 ao último dia do mês atual)
        self.set_default_dates()
        
        # Criar interface
        self.create_widgets()
    
    def set_default_dates(self):
        """Define datas padrão: dia 1 ao último dia do mês atual"""
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day_num = calendar.monthrange(today.year, today.month)[1]
        last_day = datetime(today.year, today.month, last_day_num)
        
        self.data_inicio.set(first_day.strftime("%d/%m/%Y"))
        self.data_fim.set(last_day.strftime("%d/%m/%Y"))
    
    def create_widgets(self):
        """Cria os widgets da tela"""
        
        # Frame principal com scroll
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== CONFIGURAÇÕES DE CONEXÃO =====
        config_frame = ttk.LabelFrame(main_frame, text="Configurações do REP", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Host
        ttk.Label(config_frame, text="Host:", font=('Arial', 12)).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(config_frame, textvariable=self.rep_host, font=('Arial', 12), width=20).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W
        )
        
        # Porta
        ttk.Label(config_frame, text="Porta:", font=('Arial', 12)).grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(config_frame, textvariable=self.rep_port, font=('Arial', 12), width=10).grid(
            row=0, column=3, padx=5, pady=5, sticky=tk.W
        )
        
        # Usuário
        ttk.Label(config_frame, text="Usuário:", font=('Arial', 12)).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(config_frame, textvariable=self.rep_username, font=('Arial', 12), width=20).grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.W
        )
        
        # Senha
        ttk.Label(config_frame, text="Senha:", font=('Arial', 12)).grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(config_frame, textvariable=self.rep_password, font=('Arial', 12), 
                 width=15, show="*").grid(
            row=1, column=3, padx=5, pady=5, sticky=tk.W
        )
        
        # Botão conectar
        self.connect_button = tk.Button(
            config_frame,
            text="Conectar",
            font=('Arial', 12, 'bold'),
            command=self.toggle_connection,
            bg="green",
            fg="white",
            activebackground="lightgreen",
            activeforeground="black",
            width=15,
            cursor="hand2"
        )
        self.connect_button.grid(row=0, column=4, rowspan=2, padx=10, pady=5)
        
        # ===== FILTROS DE BUSCA =====
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros de Busca", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # PIS do Funcionário
        ttk.Label(filter_frame, text="PIS Funcionário:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=10
        )
        pis_entry = ttk.Entry(
            filter_frame,
            textvariable=self.pis_funcionario,
            font=('Arial', 14),
            width=20
        )
        pis_entry.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        
        ttk.Label(filter_frame, text="(Deixe vazio para todos)", 
                 font=('Arial', 10, 'italic')).grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=10
        )
        
        # Data Início
        ttk.Label(filter_frame, text="Data Início:", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(
            filter_frame,
            textvariable=self.data_inicio,
            font=('Arial', 12),
            width=15
        ).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(filter_frame, text="(dd/mm/yyyy)", font=('Arial', 10, 'italic')).grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=5
        )
        
        # Data Fim
        ttk.Label(filter_frame, text="Data Fim:", font=('Arial', 12, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=5
        )
        ttk.Entry(
            filter_frame,
            textvariable=self.data_fim,
            font=('Arial', 12),
            width=15
        ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(filter_frame, text="(dd/mm/yyyy)", font=('Arial', 10, 'italic')).grid(
            row=2, column=2, sticky=tk.W, padx=5, pady=5
        )
        
        # Botão para redefinir datas
        tk.Button(
            filter_frame,
            text="Mês Atual",
            font=('Arial', 10),
            command=self.set_default_dates,
            bg="lightblue",
            cursor="hand2",
            width=12
        ).grid(row=2, column=3, padx=10, pady=5)
        
        # ===== BOTÃO DE BUSCA =====
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        self.search_button = tk.Button(
            search_frame,
            text="🔍 BUSCAR REGISTROS",
            font=('Arial', 16, 'bold'),
            command=self.buscar_registros,
            bg="royalblue",
            fg="white",
            activebackground="coral1",
            activeforeground="black",
            height=2,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.search_button.pack(pady=10)
        
        # ===== STATUS =====
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_text,
            font=('Arial', 12),
            foreground="orange"
        )
        self.status_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=600
        )
        self.progress.pack(pady=5)
        
        # ===== ÁREA DE RESULTADOS =====
        result_frame = ttk.LabelFrame(main_frame, text="Registros Encontrados", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Criar Treeview com scrollbars
        tree_scroll_y = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL)
        
        self.result_tree = ttk.Treeview(
            result_frame,
            columns=("NSR", "Data/Hora", "PIS", "Tipo"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=15
        )
        
        tree_scroll_y.config(command=self.result_tree.yview)
        tree_scroll_x.config(command=self.result_tree.xview)
        
        # Configurar colunas
        self.result_tree.heading("NSR", text="NSR")
        self.result_tree.heading("Data/Hora", text="Data/Hora")
        self.result_tree.heading("PIS", text="PIS")
        self.result_tree.heading("Tipo", text="Tipo")
        
        self.result_tree.column("NSR", width=80, anchor=tk.CENTER)
        self.result_tree.column("Data/Hora", width=150, anchor=tk.CENTER)
        self.result_tree.column("PIS", width=120, anchor=tk.CENTER)
        self.result_tree.column("Tipo", width=100, anchor=tk.CENTER)
        
        # Pack da árvore e scrollbars
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Label de total
        self.total_label = ttk.Label(
            result_frame,
            text="Total: 0 registros",
            font=('Arial', 11, 'bold')
        )
        self.total_label.pack(pady=5)
        
        # ===== BOTÕES DE AÇÃO =====
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)
        
        tk.Button(
            action_frame,
            text="Exportar CSV",
            font=('Arial', 12, 'bold'),
            command=self.exportar_csv,
            bg="green",
            fg="white",
            activebackground="lightgreen",
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Limpar Resultados",
            font=('Arial', 12, 'bold'),
            command=self.limpar_resultados,
            bg="lightblue",
            activebackground="coral1",
            width=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
    
    def toggle_connection(self):
        """Conecta ou desconecta do REP"""
        if not self.is_connected:
            self.conectar_rep()
        else:
            self.desconectar_rep()
    
    def conectar_rep(self):
        """Conecta ao REP EVO em thread separada"""
        if self.is_collecting:
            mb.showwarning("Atenção", "Aguarde a coleta atual finalizar!")
            return
        
        def connect_thread():
            try:
                self.update_status("Conectando ao REP...", "orange")
                self.progress.start(10)
                
                # Criar instância do collector
                self.collector = RepEvoCollector(
                    host=self.rep_host.get(),
                    port=self.rep_port.get()
                )
                
                # Conectar
                if not self.collector.connect():
                    raise Exception("Falha na conexão TCP")
                
                # Solicitar chave pública
                self.update_status("Obtendo chave pública...", "orange")
                if not self.collector.request_public_key():
                    raise Exception("Falha ao obter chave pública RSA")
                
                # Autenticar
                self.update_status("Autenticando...", "orange")
                if not self.collector.authenticate(
                    username=self.rep_username.get(),
                    password=self.rep_password.get()
                ):
                    raise Exception("Falha na autenticação")
                
                # Sucesso
                self.is_connected = True
                self.update_status("Conectado com sucesso!", "green")
                self.connect_button.config(text="Desconectar", bg="red")
                self.search_button.config(state=tk.NORMAL)
                
                mb.showinfo("Sucesso", "Conectado ao REP EVO com sucesso!")
                
            except Exception as e:
                self.update_status(f"Erro: {str(e)}", "red")
                mb.showerror("Erro de Conexão", f"Não foi possível conectar:\n{str(e)}")
                if self.collector:
                    self.collector.disconnect()
                    self.collector = None
            finally:
                self.progress.stop()
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
    
    def desconectar_rep(self):
        """Desconecta do REP EVO"""
        if self.collector:
            self.collector.disconnect()
            self.collector = None
        
        self.is_connected = False
        self.update_status("Desconectado", "orange")
        self.connect_button.config(text="Conectar", bg="green")
        self.search_button.config(state=tk.DISABLED)
    
    def buscar_registros(self):
        """Busca registros do REP em thread separada"""
        if not self.is_connected or not self.collector:
            mb.showwarning("Atenção", "Conecte ao REP primeiro!")
            return
        
        if self.is_collecting:
            mb.showwarning("Atenção", "Já existe uma coleta em andamento!")
            return
        
        # Validar datas
        try:
            data_ini = self.data_inicio.get()
            data_fim_val = self.data_fim.get()
            
            # Validar formato
            datetime.strptime(data_ini, "%d/%m/%Y")
            datetime.strptime(data_fim_val, "%d/%m/%Y")
            
        except ValueError:
            mb.showerror("Erro", "Formato de data inválido! Use dd/mm/yyyy")
            return
        
        def collect_thread():
            try:
                self.is_collecting = True
                self.search_button.config(state=tk.DISABLED)
                self.progress.start(10)
                
                self.update_status("Coletando registros...", "orange")
                
                # Buscar registros por data
                start_datetime = f"{data_ini} 00:00:01"
                
                # Usar quantidade grande para pegar todos os registros do período
                registers_data = self.collector.get_registers_by_date(
                    start_date=start_datetime,
                    quantity=100000
                )
                
                if not registers_data:
                    raise Exception("Nenhum registro retornado")
                
                # Processar e filtrar registros
                self.update_status("Processando registros...", "orange")
                registros = self.processar_registros(registers_data)
                
                # Filtrar por PIS se informado
                pis = self.pis_funcionario.get().strip()
                if pis:
                    registros = [r for r in registros if r['pis'] == pis]
                
                # Filtrar por período
                registros = self.filtrar_por_periodo(registros)
                
                # Exibir resultados
                self.exibir_registros(registros)
                
                self.update_status(f"Coleta concluída! {len(registros)} registros encontrados", "green")
                
                if len(registros) == 0:
                    mb.showinfo("Informação", "Nenhum registro encontrado para os filtros informados.")
                else:
                    mb.showinfo("Sucesso", f"{len(registros)} registros encontrados!")
                
            except Exception as e:
                self.update_status(f"Erro na coleta: {str(e)}", "red")
                mb.showerror("Erro", f"Erro ao buscar registros:\n{str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                self.is_collecting = False
                if self.is_connected:
                    self.search_button.config(state=tk.NORMAL)
                self.progress.stop()
        
        thread = threading.Thread(target=collect_thread, daemon=True)
        thread.start()
    
    def processar_registros(self, data):
        """Processa os registros retornados pelo REP"""
        registros = []
        
        # Dividir por linhas
        linhas = data.strip().split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha or not linha.startswith('3'):
                continue
            
            try:
                # Formato AFD tipo 3: 3|NSR|DATA|HORA|PIS
                partes = linha.split('|')
                
                if len(partes) >= 5:
                    tipo = partes[0]
                    nsr = partes[1]
                    data = partes[2]
                    hora = partes[3]
                    pis = partes[4]
                    
                    # Formatar data/hora
                    data_hora = f"{data} {hora}"
                    
                    registros.append({
                        'tipo': tipo,
                        'nsr': nsr,
                        'data_hora': data_hora,
                        'data': data,
                        'hora': hora,
                        'pis': pis
                    })
            except Exception as e:
                print(f"Erro ao processar linha: {linha} - {e}")
                continue
        
        return registros
    
    def filtrar_por_periodo(self, registros):
        """Filtra registros pelo período informado"""
        try:
            data_ini = datetime.strptime(self.data_inicio.get(), "%d/%m/%Y")
            data_fim = datetime.strptime(self.data_fim.get(), "%d/%m/%Y")
            
            registros_filtrados = []
            
            for reg in registros:
                try:
                    # Converter data do registro (formato ddmmyyyy)
                    data_reg_str = reg['data']
                    data_reg = datetime.strptime(data_reg_str, "%d%m%Y")
                    
                    if data_ini <= data_reg <= data_fim:
                        registros_filtrados.append(reg)
                except:
                    continue
            
            return registros_filtrados
            
        except Exception as e:
            print(f"Erro ao filtrar por período: {e}")
            return registros
    
    def exibir_registros(self, registros):
        """Exibe os registros na TreeView"""
        # Limpar árvore
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Inserir registros
        for reg in registros:
            # Formatar data/hora para exibição
            try:
                data_formatada = datetime.strptime(reg['data'], "%d%m%Y").strftime("%d/%m/%Y")
                hora_formatada = f"{reg['hora'][:2]}:{reg['hora'][2:4]}:{reg['hora'][4:]}"
                data_hora_display = f"{data_formatada} {hora_formatada}"
            except:
                data_hora_display = reg['data_hora']
            
            self.result_tree.insert('', 'end', values=(
                reg['nsr'],
                data_hora_display,
                reg['pis'],
                'Registro'
            ))
        
        # Atualizar total
        self.total_label.config(text=f"Total: {len(registros)} registros")
    
    def exportar_csv(self):
        """Exporta registros para CSV"""
        items = self.result_tree.get_children()
        
        if not items:
            mb.showwarning("Atenção", "Nenhum registro para exportar!")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"registros_rep_{timestamp}.csv"
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("NSR;Data/Hora;PIS;Tipo\n")
                
                # Dados
                for item in items:
                    values = self.result_tree.item(item)['values']
                    f.write(f"{values[0]};{values[1]};{values[2]};{values[3]}\n")
            
            mb.showinfo("Sucesso", f"Registros exportados para:\n{filename}")
            
        except Exception as e:
            mb.showerror("Erro", f"Erro ao exportar:\n{str(e)}")
    
    def limpar_resultados(self):
        """Limpa os resultados exibidos"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.total_label.config(text="Total: 0 registros")
    
    def update_status(self, text, color):
        """Atualiza o texto de status com cor"""
        self.status_text.set(text)
        self.status_label.config(foreground=color)