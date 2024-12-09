import ctypes
import random
import re
from datetime import datetime, timedelta
import tkinter.ttk as ttk
from tkinter import *
from tkinter.constants import *
from tkinter import messagebox as mb
from ttkwidgets.autocomplete import AutocompleteEntry, AutocompleteCombobox, AutocompleteEntryListbox

from models.color import get_colors
from models.category import check_category, get_all_categories, post_category
from models.config import get_config
from models.model import check_model, get_all_models, post_model
from models.parking import *
from models.users import *
from models.impressora import *

from schemas.category import CategoryModel
from schemas.color import ColorModel
from schemas.model import ModelModel
from schemas.parking import ParkingModel
from schemas.users import UsersModel


# CONFIG
root = Tk()
root.geometry("1366x768")
root.title("Estacionamento Costeira")
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview.Heading', font=(None, 12, "bold"), height=50)

# VARIABLES
login = StringVar(value="Usuário")
password = StringVar(value="Senha")

active_user_id = StringVar()
active_user_name = StringVar(value="-efetuar login-")
active_user_role = StringVar()

total_count = StringVar(value="XXXXXX")

new_user_name = StringVar()
new_user_password = StringVar()
new_user_role = StringVar()

new_model_name = StringVar()
new_model_category = StringVar()

new_category_name = StringVar()
new_category_price = StringVar()

new_color_name = StringVar()

new_status = StringVar()

config_tolerance = StringVar()
config_daily_price = StringVar()
config_daily_price_moto = StringVar()
config_printer_header = StringVar()
config_printer_footer = StringVar()

in_plate = StringVar()
in_model = StringVar()
in_category = StringVar()
in_color = StringVar()
in_time = StringVar()

barcode = StringVar(value="")
out_plate = StringVar(value="")
out_model = StringVar(value="")
out_category = StringVar(value="")
out_color = StringVar(value="")
out_time = StringVar()
delta_time = StringVar()
delta_time_value = StringVar()
total_value = StringVar()
value_received = StringVar()
change_value = StringVar(value="0.00")
addition = StringVar(value="0.00")
discount = StringVar(value="0.00")

order = True
header_in = [
    "Placa",
    "Modelo",
    "Categoria",
    "Cor",
    "Entrada",
    "Saída",
    "Permanência",
    "Status",
    "Total",
    "Usuário E",
    "Usuário S",
    "Desconto",
    "Acréscimo",
]
header_out = [
    "Placa",
    "Modelo",
    "Saída",
    "Permanência",
    "Total",
]
phrase = [
    "A alegria do coração transparece no rosto, mas o coração angustiado oprime o espírito. - Provérbios 15:13",
    "Regozija-te e alegra-te, porque o Senhor tem feito grandes coisas. - Joel 2:21",
    "Este é o dia em que o Senhor agiu; alegremo-nos e exultemos neste dia. - Salmos 118:24",
    "O amigo ama em todo o tempo; e na angústia nasce o irmão. - Provérbios 17:17",
    "O Senhor é a minha força e o meu escudo; nele o meu coração confia. - Salmos 28:7",
    "Porque vivemos por fé, e não pelo que vemos. - 2 Coríntios 5:7",
    "Os olhos são a candeia do corpo. Se os seus olhos forem bons, todo o seu corpo será cheio de luz. - Mateus 6:22",
    "Bem-aventurados os puros de coração, pois verão a Deus. - Mateus 5:8",
    "O próprio Senhor irá à sua frente e estará com você; Ele nunca o deixará, nunca o abandonará. Não tenha medo! Não se desanime! - Deuteronômio 31:8",
    "Algumas amizades não duram nada, mas um verdadeiro amigo é mais chegado que um irmão. - Provérbios 18:24",
    "A luz nasce sobre o justo e a alegria sobre os retos de coração. - Salmos 97:11",
    "Um olhar animador dá alegria ao coração, e as boas notícias revigoram os ossos. - Provérbios 15:30",
    "Enquanto estou no mundo, sou a luz do mundo. - João 9:5",
    "Jesus Cristo é o mesmo, ontem, hoje e para sempre. - Hebreus 13:8",
    "Meus amados irmãos, tenham isto em mente: Sejam todos prontos para ouvir, tardios para falar e tardios para irar-se. - Tiago 1:19",
    "E eis que eu estou convosco todos os dias, até a consumação dos séculos. - Mateus 28:20",
    "A esperança que se retarda deixa o coração doente, mas o anseio satisfeito é árvore de vida. - Provérbios 13:12",
    "No amor não há medo; antes, o perfeito amor lança fora o medo. - 1 João 4:18",
    "Escolhi o caminho da fidelidade; decidi seguir as tuas ordenanças. - Salmos 119:30",
    "O engano está no coração dos que maquinam o mal, mas a alegria está no meio dos que promovem a paz. - Provérbios 12:20",
    "Pois a palavra do Senhor é verdadeira; Ele é fiel em tudo o que faz. - Salmos 33:4",
    "Gloriem-se no seu santo nome; alegre-se o coração dos que buscam o Senhor. - 1 Crônicas 16:10",
    "Os preceitos do Senhor são justos e dão alegria ao coração. Os mandamentos do Senhor são límpidos e trazem luz aos olhos. - Salmos 19:8"
]
# AUXILIARY FUNCTIONS


def calc_total_count():
    prefix = random.randint(1000, 9999)
    sufix = random.randint(1000, 9999)
    total = get_total_open_parking()
    if total<10:
        result = f"{prefix}0{total}{sufix}"
    else:
        result = f"{prefix}{total}{sufix}"
    total_count.set(result)


def login_verification(event):
    user = get_user_by_id(login.get())
    if user:
        if user["password"] == password.get():
            active_user_id.set(user["id"])
            active_user_name.set(user["name"])
            active_user_role.set(user["role"])
            root_notebook.tab(parking_tab, state="normal")
            if user["role"] == "admin":
                root_notebook.tab(config_tab, state="normal")
            else:
                root_notebook.tab(config_tab, state="hidden")
            log_in(user["name"])
            calc_total_count()
            root_notebook.select(parking_tab)
            login.set("Usuário")
            password.set("Senha")
        else:
            mb.showwarning("OPS", "Senha inválida.")
            password.set("")
    else:
        mb.showwarning("OPS", "Usuário inválido.")


def ask_for_password(userID, tab):
    user = get_user_by_id(userID)
    passwd = mb.askquestion("CONFIRMAÇÃO DE SENHA", "Confirme sua senha, por favor.")
    if user["password"] == passwd:
        root_notebook.select(tab)


def logout():
    user_name = active_user_name.get()
    logout = mb.askyesno("LOGOUT", f"Olá {user_name}, deseja fazer logout?")
    if logout:
        log_out(user_name)


def notebook_tab_selection(event):
    selected_tab = event.widget.select()
    tab_name = event.widget.tab(selected_tab, "text")
    if ("acesso" in tab_name) and active_user_id.get():
        logout()
    if "Config" in tab_name:
        pass


def open_printer_connection():
    AbreConexaoImpressora(
        1,
        "I8",
        "USB",
        0
    )


def print_parking(code):
    config = get_config()
    ImpressaoTexto("================================", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("ESTACIONAMENTO C O S T E I R A", 1, 0, 0)
    AvancaPapel(1)
    ImpressaoTexto("Av. Pref. Osmar Cunha, 155 - Centro", 1, 1, 0)
    AvancaPapel(1)
    ImpressaoTexto(config["printer_header"], 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("================================", 1, 8, 0)
    AvancaPapel(3)
    ImpressaoTexto(f"{in_plate.get()} {in_category.get()}", 1, 8, 33)
    AvancaPapel(3)
    ImpressaoTexto(f"{in_model.get()}  {in_color.get()}", 1, 8, 17)
    AvancaPapel(3)
    ImpressaoTexto(f"{datetime.now():%Y-%m-%d %H:%M}", 1, 8, 17)
    AvancaPapel(3)
    
    ImpressaoCodigoBarras(2, str(code), 90, 4, 2)
    AvancaPapel(3)
    ImpressaoTexto("==================================================", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("SEM TOLERÂNCIA NA PRIMEIRA HORA", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("Horário de funcionamento:", 1, 0, 0)
    ImpressaoTexto(config["printer_footer"], 1, 1, 0)
    AvancaPapel(5)
    Corte(3)
    # ------------- Impressão chave
    ImpressaoTexto(in_plate.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(in_model.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(in_color.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(f"{datetime.now():%Y-%m-%d %H:%M}", 2, 8, 0)
    CorteTotal(4)


def hash_generator():
    code = str()
    for index in range(13):
        code = f"{code}{str(random.randint(0, 9))}"
    return code


def insert_parking(event):
    current_plate = in_plate.get()
    if not current_plate:
        mb.showwarning("ALERTA", "Digite uma placa válida")
        in_plate.set("")
        in_plate_entry.focus()
    else:
        parking_model = ParkingModel(
            plate=current_plate,
            barcode=hash_generator(),
            model=in_model.get(),
            category=in_category.get(),
            color=in_color.get(),
            status="EM ABERTO",
            entry_user=active_user_name.get()
        )
        post_parking(parking_model)
        calc_total_count()
        print_parking(parking_model.barcode)
        in_plate.set("")
        in_model.set("")
        in_category.set("")
        in_color.set("")
        update_in_grid()
        update_out_grid()
        in_plate_entry.focus()


def ending_parking(status):
    if status == "FINALIZAR":
        plateID = out_plate.get()
        finalize_parking(plateID, delta_time_value.get(), active_user_name.get())
        close_exit_tab()
    elif status == "DESISTIR":
        confirmation = mb.askyesno("CONFIRMAR", "Você deseja aplicar a desistência nesse veículo?")
        if confirmation:
            plateID = out_plate.get()
            cancel_parking(plateID)
    update_in_grid()
    update_out_grid()


def sort_in_table(col):
    header_map = dict(
        Placa = "plate",
        Modelo="model",
        Categoria="category",
        Cor="color",
        Entrada="entry_time",
        Saída="exit_time",
        Permanência="delta_time",
        Status="status",
        Total="total_value",
        Usuário_E="entry_user",
        Usuário_S="exit_user",
        Desconto="discount",
        Acréscimo="addition",
    )
    global df_in, order_in
    if order_in:
        order_in = False
    else:
        order_in = True
    df_in = df_in.sort_values(by=[header_map[col]], ascending=order)
    mount_in_table()


def sort_out_table(col):
    header_map = dict(
        Placa = "plate",
        Modelo="model",
        Saída="exit_time",
        Permanência="delta_time",
        Total="total_value",
    )
    global df_out, order_out
    if order_out:
        order_out = False
    else:
        order_out = True
    df_out = df_out.sort_values(by=[header_map[col]], ascending=order)
    mount_out_table()


def mount_in_table():
    in_table.delete(*in_table.get_children())
    global df_in, header_in
    rows = df_in.to_numpy().tolist()

    for col in header_in:
        in_table.column(col, anchor="center", width=100)
        in_table.heading(col, text=col, command=lambda col=col : sort_in_table(col))
    for row in rows:
        values = [value for value in row]
        if values[7] == "EM ABERTO":
            bg_tag = "green"
        elif values[7] == "FINALIZADO":
            bg_tag = "gray"
            out_table.insert("", 0, values=values, tags=bg_tag)
        elif values[7] == "CANCELADO":
            bg_tag = "red"
            out_table.insert("", 0, values=values, tags=bg_tag)
        in_table.insert("", 0, values=values, tags=bg_tag)


def mount_out_table():
    out_table.delete(*out_table.get_children())
    global df_out, header_out
    rows = df_out.to_numpy().tolist()

    for col in header_out:
        out_table.column(col, anchor="center", width=160)
        out_table.heading(col, text=col, command=lambda col=col : sort_out_table(col))
    for row in rows:
        values = [value for value in row]
        out_table.insert("", 0, values=values, tags="red")


def update_in_grid():
    global df_in
    df_in = get_today_parkings_as_df_in()
    mount_in_table()


def update_out_grid():
    global df_out
    df_out = get_today_parkings_as_df_out()
    mount_out_table()

def check_element(event, element):
    if element == "category":
        categoryID = in_category.get()
        if check_category(categoryID):
            in_color_entry.focus()
        else:
            mb.showwarning("ALERTA", "Categoria não encontrada")
    elif element == "model":
        modelID = in_model.get()
        modelDB = check_model(modelID)
        if modelDB:
            in_category.set(modelDB.category)
            in_color_entry.focus()
        else:
            mb.showwarning("ALERTA", "Modelo não encontrado")
    elif element == "in plate":
        plateID = in_plate.get().lower()
        in_plate.set(re.sub('[\W_]+', '', plateID))
        if not plateID:
            mb.showwarning("ALERTA", "Digite uma placa válida")
            in_plate_entry.focus()
            return
        if check_plate(plateID):
            in_model_entry.focus()
        else:
            mb.showwarning("ALERTA", "Esta placa já existe")
            in_plate.set("")
            in_plate_entry.focus()
    elif element == "out plate":
        plateID = out_plate.get()
        parking = get_parking_by_plate(plateID)
        if parking:
            out_model.set(parking["model"])
            out_category.set(parking["category"])
            out_color.set(parking["color"])
            out_finalize_button.focus()
            return parking
        else:
            mb.showwarning("ALERTA", "Placa não encontrada")
    elif element == "barcode":
        code = barcode.get()
        parking = get_parking_by_code(code)
        if parking:
            out_plate.set(parking["plate"])
            out_model.set(parking["model"])
            out_category.set(parking["category"])
            out_color.set(parking["color"])
            open_exit_tab("barcode")
        else:
            mb.showwarning("ALERTA", "Código não encontrado")


def enter_ent_button_focus(event):
    in_confirm_button.focus()


def clear_data(element):
    if "in" in element:
        in_plate.set("")
        in_model.set("")
        in_category.set("")
        in_color.set("")
        in_plate_entry.focus()
    if "out" in element:
        out_plate.set("")
        barcode.set("")
        out_model.set("")
        out_category.set("")
        out_color.set("")
        out_plate_entry.focus()


def on_click(event):
    event.widget.delete(0, END)


def calc_change(event):
    change_value.set(format(float(value_received.get())-float(total_value.get()), '.2f'))


def apply_add_and_discount(event, action: str):
    if action == "ADD":
        total = float(total_value.get()) + float(addition.get())
    if action == "DISC":
        total = float(total_value.get()) - float(discount.get())
    total_value.set(format(total, '.2f'))
    exit_finalize_button.focus()


def calc_total_value(delta_hours: int, delta_minutes: int):
    with get_dal_mysql() as db:
        config_info = db().select(db.config.ALL).first()
        category_info = db(db.category.id==out_category.get()).select().first()
    if delta_minutes > config_info["tolerance"]:
        delta_hours += 1
    if delta_hours<=1:
        value_color = "green"
    elif delta_hours==2:
        value_color = "red"
    elif delta_hours==3:
        value_color = "blue"
    elif delta_hours==4:
        value_color = "purple"
    elif delta_hours==5:
        value_color = "deep pink"
    factor = delta_hours if delta_hours!=0 else 1
    total = format(float(category_info["price"]*factor), '.2f')
    if "MOTO" in category_info["id"]:
        deily_price = "daily_price_moto"
    else:
        deily_price = "daily_price_vehicle"
    if float(category_info["price"]*delta_hours) >= config_info[deily_price]:
        value_color = "saddle brown"
        total = format(float(category_info["daily_price"]), '.2f')
    value_received.set(total)
    total_value_label_exit_tab.config(foreground=value_color)
    in_time_label_exit_tab.config(foreground=value_color)
    in_time_value_label_exit_tab.config(foreground=value_color)
    out_time_label_exit_tab.config(foreground=value_color)
    out_time_value_label_exit_tab.config(foreground=value_color)
    delta_time_label_exit_tab.config(foreground=value_color)
    delta_time_value_label_exit_tab.config(foreground=value_color)
    return total


def open_exit_tab(event):
    parking = check_element("out", element="out plate")
    if parking["status"] == "EM ABERTO":
        root_notebook.tab(exit_tab, state="normal")
        root_notebook.select(exit_tab)
        root_notebook.tab(login_tab, state="hidden")
        root_notebook.tab(config_tab, state="hidden")
        root_notebook.tab(parking_tab, state="disabled")
        in_time.set(parking["entry_time"].strftime("%H:%M"))
        out_time.set(datetime.now().time().strftime("%H:%M"))
        entry_delta_time = timedelta(hours=parking["entry_time"].hour, minutes=parking["entry_time"].minute)
        exit_delta_time = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
        delta_time_total = exit_delta_time-entry_delta_time
        delta_time_value.set(delta_time_total)
        delta_hours = int(delta_time_total.seconds/3600)
        delta_minutes = int(delta_time_total.seconds/60)-delta_hours*60
        delta_time.set(f"{delta_hours} hora(s), {delta_minutes} minuto(s)")
        total_value.set(calc_total_value(delta_hours, delta_minutes))
        total_received_entry_exit_tab.focus()
    else:
        mb.showwarning("ALERTA", "Não é possível finalizar um veículo que não está EM ABERTO")


def close_exit_tab():
    root_notebook.tab(parking_tab, state="normal")
    root_notebook.select(parking_tab)
    root_notebook.tab(login_tab, state="normal")
    root_notebook.tab(exit_tab, state="hidden")
    if active_user_role == "admin":
        root_notebook.tab(config_tab, state="normal")
    clear_data("out")
    out_barcode_entry.focus()


def add_element(element: str):
    if element == "model":
        model = ModelModel(id=new_model_name.get(), category=new_model_category.get())
        post_model(**model)
    elif element == "category":
        category = CategoryModel(name=new_category_name.get(), price=new_category_price.get())
        post_category(**category)
    elif element == "color":
        color = ColorModel(id=new_color_name.get())
        post_category(**category)
        
# -----------------------------------------------------------------------------------------------------------
# NOTEBOOK CONFIG
# -----------------------------------------------------------------------------------------------------------
root_notebook = ttk.Notebook(root)
root_notebook.pack(expand=1,fill=BOTH)
root_notebook.bind("<<NotebookTabChanged>>", notebook_tab_selection)

login_tab = ttk.Frame(root_notebook)
root_notebook.add(login_tab, text="Controle de acesso")
parking_tab = ttk.Frame(root_notebook)
root_notebook.add(parking_tab, text="Entrada e Saída", state="disabled")
exit_tab = ttk.Frame(root_notebook)
root_notebook.add(exit_tab, text="Finalizar veículo", state="hidden")
config_tab = ttk.Frame(root_notebook)
root_notebook.add(config_tab, text="Configurações", state="hidden")
report_tab = ttk.Frame(root_notebook)
root_notebook.add(report_tab, text="Relatórios", state="hidden")
user_frame = ttk.Frame(root, borderwidth=2, height=13, relief="sunken", width=50)
user_frame.place(relx=0.98, y=0, anchor=NE)
user_name_label = ttk.Label(user_frame, text="Usuário:", font=('Arial', 13, 'bold'))
user_name_label.pack(side=LEFT)
active_user_label = ttk.Label(user_frame, textvariable=active_user_name, font=('Arial', 13, 'bold'))
active_user_label.pack(side=LEFT)
count_frame = ttk.Frame(root, borderwidth=2, height=13, relief="sunken", width=50)
count_frame.place(relx=0.5, y=0, anchor=NE)
count_total_label = ttk.Label(count_frame, textvariable=total_count, font=('Arial', 13, 'bold'))
count_total_label.pack(side=LEFT)

# -----------------------------------------------------------------------------------------------------------
# LOGIN TAB WIDJETS
# -----------------------------------------------------------------------------------------------------------
login_entry = AutocompleteCombobox(login_tab, font=('Arial', 20, 'bold'),textvariable=login, completevalues=get_all_users())
# login_entry = AutocompleteEntry(
#     login_tab,
#     font=('Arial', 20, 'bold'),
#     textvariable=login,
#     completevalues=get_all_users()
# )
password_entry = ttk.Entry(
    login_tab,
    font=('Arial', 20, 'bold'),
    textvariable=password,
    show="*"
)
login_button = Button(
    login_tab,
    text="Entrar",
    font=('Arial', 18, 'bold'),
    command= lambda click="login click": login_verification(click),
    bg="royalblue",
    activebackground="coral1",
    activeforeground="white",
    height=2,
    width=15,
    cursor="hand2"
)
power_phrase = ttk.Label(login_tab, text=random.choice(phrase), font=('Arial', 15, 'bold'))

# -----------------------------------------------------------------------------------------------------------
# LOGIN TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
login_entry.place(relx=0.5, y=150, anchor=CENTER)
password_entry.place(relx=0.5, y=250, anchor=CENTER)
login_button.place(relx=0.5, y=350, anchor=CENTER)
power_phrase.place(relx=0.5, y=500, anchor=CENTER)

# -----------------------------------------------------------------------------------------------------------
# LOGIN TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
login_entry.bind("<Button-1>", on_click)
password_entry.bind("<Button-1>", on_click)
password_entry.bind("<Return>", login_verification)
password_entry.bind("<KP_Enter>", login_verification)

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB FRAMES
# -----------------------------------------------------------------------------------------------------------
in_frame = ttk.Frame(parking_tab, borderwidth=2, relief="sunken")
in_frame_top = ttk.Frame(in_frame, padding=10)
in_frame_center = ttk.Frame(in_frame, padding=10)
in_frame_bottom = ttk.Frame(in_frame, padding=10)
out_frame = ttk.Frame(parking_tab, borderwidth=2, relief="sunken")
out_frame_top = ttk.Frame(out_frame, padding=10)
out_frame_center_top = ttk.Frame(out_frame)
out_frame_center_bottom = ttk.Frame(out_frame)
out_frame_bottom = ttk.Frame(out_frame, padding=10)
report_in_frame = ttk.Frame(parking_tab, borderwidth=2, relief="sunken")
report_out_frame = ttk.Frame(parking_tab, borderwidth=2, relief="sunken")

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB WIDJETS - ENTRANCE
# -----------------------------------------------------------------------------------------------------------
in_plate_entry = ttk.Entry(
    in_frame_center,
    font=('Arial', 20, 'bold'),
    textvariable=in_plate,
    width=18,
)
in_model_entry = AutocompleteCombobox(
    in_frame_center,
    font=('Arial', 20, 'bold'),
    completevalues=get_all_models(),
    textvariable=in_model,
    width=18,
)
in_category_entry = AutocompleteCombobox(
    in_frame_center,
    font=('Arial', 20, 'bold'),
    completevalues=get_all_categories(),
    textvariable=in_category,
    width=18,
)
in_color_entry = AutocompleteCombobox(
    in_frame_center,
    font=('Arial', 20, 'bold'),
    completevalues=get_colors(),
    textvariable=in_color,
    width=18,
)
in_confirm_button = Button(
    in_frame_bottom,
    text="Entrar",
    font=('Arial', 18, 'bold'),
    command= lambda event="confirm": insert_parking(event),
    bg="royalblue",
    activebackground="coral1",
    activeforeground="white",
    width=15,
    cursor="hand2"
)
in_clear_button = Button(
    in_frame_bottom,
    text="Limpar",
    font=('Arial', 18, 'bold'),
    command=lambda element="in": clear_data(element),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=15,
    cursor="hand2"
)
in_title = ttk.Label(in_frame_top, text="ENTRADA", justify="right", font=('Arial', 20, 'bold'))
in_plate_label = ttk.Label(in_frame_center, text="Placa", font=('Arial', 18, 'bold'))
in_model_label = ttk.Label(in_frame_center, text="Modelo", font=('Arial', 18, 'bold'))
in_category_label = ttk.Label(in_frame_center, text="Categoria", font=('Arial', 18, 'bold'))
in_color_label = ttk.Label(in_frame_center, text="Cor", font=('Arial', 18, 'bold'))

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB WIDJETS - EXIT
# -----------------------------------------------------------------------------------------------------------
out_title = ttk.Label(out_frame_top, text="SAÍDA", justify="center", font=('Arial', 20, 'bold'))
out_plate_entry = ttk.Entry(out_frame_center_top, width=10, font=('Arial', 20, 'bold'), textvariable=out_plate)
out_plate_label = ttk.Label(out_frame_center_top, text="Placa", font=('Arial', 18, 'bold'))
out_barcode_entry = ttk.Entry(out_frame_center_top, width=15, font=('Arial', 20, 'bold'), textvariable=barcode)
out_barcode_label = ttk.Label(out_frame_center_top, text="Código de barras", font=('Arial', 18, 'bold'))
out_model_label = ttk.Label(out_frame_center_bottom, text="Modelo: ", font=('Arial', 18, 'bold'))
out_model_value = ttk.Label(out_frame_center_bottom, textvariable=out_model, font=('Arial', 18, 'bold'), width=12)
out_category_label = ttk.Label(out_frame_center_bottom, text="Categoria: ", font=('Arial', 18, 'bold'))
out_category_value = ttk.Label(out_frame_center_bottom, textvariable=out_category, font=('Arial', 18, 'bold'), width=12)
out_color_label = ttk.Label(out_frame_center_bottom, text="Cor: ", font=('Arial', 18, 'bold'))
out_color_value = ttk.Label(out_frame_center_bottom, textvariable=out_color, font=('Arial', 18, 'bold'), width=13)
out_finalize_button = Button(
    out_frame_bottom,
    text="Finalizar",
    command=lambda event="Return": open_exit_tab(event),
    font=('Arial', 18, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
out_clear_button = Button(
    out_frame_bottom,
    text="Limpar",
    font=('Arial', 18, 'bold'),
    command=lambda element="out": clear_data(element),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=16,
    cursor="hand2"
)
out_cancel_button = Button(
    out_frame_bottom,
    text="Desistência",
    font=('Arial', 18, 'bold'),
    command= lambda status="DESISTIR": ending_parking(status),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=16,
    cursor="hand2"
)

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB WIDJETS - REPORTS
# -----------------------------------------------------------------------------------------------------------
in_table = ttk.Treeview(report_in_frame, selectmode="browse", show="headings", height=10, columns=header_in)
in_table.pack(side=TOP, padx=10, pady=5)
in_table.tag_configure("green", background="lightgreen")
in_table.tag_configure("gray", background="lightgray")
in_table.tag_configure("red", background="red")

out_table = ttk.Treeview(report_out_frame, selectmode="browse", show="headings", height=7, columns=header_out)
out_table.pack(side=TOP)
out_table.tag_configure("green", background="lightgreen")
out_table.tag_configure("gray", background="lightgray")
out_table.tag_configure("red", background="red")

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
in_frame.place(x = 15, y = 15, anchor=NW)
in_frame_top.pack(fill="x")
in_frame_center.pack()
in_frame_bottom.pack(fill="x")
out_frame.place(x = 510, y = 15, anchor=NW)
out_frame_top.pack(side=TOP)
out_frame_center_top.pack(side=TOP)
out_frame_center_bottom.pack(side=TOP)
out_frame_bottom.pack(side=BOTTOM)
report_out_frame.place(x=510, y=260, anchor=NW)
report_in_frame.place(relx = 0, rely=0.98, relwidth=1, anchor="sw")

in_title.pack(side=TOP)
in_plate_entry.grid(column=1, row=2, sticky=W, padx=15, pady=10)
in_plate_label.grid(column=2, row=2, sticky=W, pady=10)
in_model_entry.grid(column=1, row=3, sticky=W, padx=15, pady=10)
in_model_label.grid(column=2, row=3, sticky=W, pady=10)
in_category_entry.grid(column=1, row=4, sticky=W, padx=15, pady=10)
in_category_label.grid(column=2, row=4, sticky=W, pady=10)
in_color_entry.grid(column=1, row=5, sticky=W, padx=15, pady=10)
in_color_label.grid(column=2, row=5, sticky=W, pady=10)
in_confirm_button.pack(side=RIGHT)
in_clear_button.pack(side=LEFT)

out_title.pack(side=TOP)
out_barcode_label.grid(column=1, row=1, sticky=W, padx=10, pady=10)
out_barcode_entry.grid(column=2, row=1, sticky=W, padx=10, pady=10)
out_plate_label.grid(column=3, row=1, sticky=W, padx=10, pady=10)
out_plate_entry.grid(column=4, row=1, sticky=W, padx=10, pady=10)
out_model_label.grid(column=1, row=2, sticky=W, pady=10, padx=10)
out_model_value.grid(column=2, row=2, sticky=W, pady=10)
out_category_label.grid(column=3, row=2, sticky=W, pady=10)
out_category_value.grid(column=4, row=2, sticky=W, pady=10)
out_color_label.grid(column=5, row=2, sticky=W, pady=10)
out_color_value.grid(column=6, row=2, sticky=W, pady=10)
out_clear_button.pack(side=LEFT, pady=5)
out_cancel_button.pack(side=LEFT, pady=5)
out_finalize_button.pack(side=LEFT, pady=5)

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
out_plate_entry.bind("<Return>", lambda event: check_element(event, "out plate"))
out_plate_entry.bind("<Tab>", lambda event: check_element(event, "out plate"))
out_plate_entry.bind("<KP_Enter>", lambda event: check_element(event, "out plate"))

out_barcode_entry.bind("<Return>", lambda event: check_element(event, "barcode"))
out_barcode_entry.bind("<Tab>", lambda event: check_element(event, "barcode"))
out_barcode_entry.bind("<KP_Enter>", lambda event: check_element(event, "barcode"))

in_plate_entry.bind("<Return>", lambda event: check_element(event, "in plate"))
in_plate_entry.bind("<Tab>", lambda event: check_element(event, "in plate"))
in_plate_entry.bind("<KP_Enter>", lambda event: check_element(event, "in plate"))

in_model_entry.bind("<Return>", lambda event: check_element(event, "model"))
in_model_entry.bind("<Tab>", lambda event: check_element(event, "model"))
in_model_entry.bind("<KP_Enter>", lambda event: check_element(event, "model"))

in_category_entry.bind("<Return>", lambda event: check_element(event, "catefory"))
in_category_entry.bind("<Tab>", lambda event: check_element(event, "catefory"))
in_category_entry.bind("<KP_Enter>", lambda event: check_element(event, "catefory"))

in_color_entry.bind("<Return>", enter_ent_button_focus)
in_color_entry.bind("<Tab>", enter_ent_button_focus)
in_color_entry.bind("<KP_Enter>", enter_ent_button_focus)

in_confirm_button.bind("<Return>", insert_parking)
out_finalize_button.bind("<Return>", open_exit_tab)

in_plate_entry.focus()

# -----------------------------------------------------------------------------------------------------------
# EXIT TAB WIDJETS
# -----------------------------------------------------------------------------------------------------------
out_plate_label_exit_tab = ttk.Label(exit_tab, text="Placa: ", font=('Arial', 45, 'bold'))
out_plate_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_plate, font=('Arial', 65, 'bold'))
out_model_label_exit_tab = ttk.Label(exit_tab, text="Modelo: ", font=('Arial', 45, 'bold'))
out_model_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_model, font=('Arial', 65, 'bold'))
out_color_label_exit_tab = ttk.Label(exit_tab, text="Cor: ", font=('Arial', 45, 'bold'))
out_color_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_color, font=('Arial', 50, 'bold'))
out_category_label_exit_tab = ttk.Label(exit_tab, text="Categoria: ", font=('Arial', 45, 'bold'))
out_category_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_category, font=('Arial', 55, 'bold'))
in_time_label_exit_tab = ttk.Label(exit_tab, text="Entrada: ", font=('Arial', 30))
in_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=in_time, font=('Arial', 35))
out_time_label_exit_tab = ttk.Label(exit_tab, text="Saída: ", font=('Arial', 30))
out_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_time, font=('Arial', 35))
delta_time_label_exit_tab = ttk.Label(exit_tab, text="Permanência: ", font=('Arial', 30))
delta_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=delta_time, font=('Arial', 30))
total_label_exit_tab = ttk.Label(exit_tab, text="Total R$ ", font=('Arial', 45, 'bold'))
total_value_label_exit_tab = ttk.Label(exit_tab, textvariable=total_value, font=('Arial', 100, 'bold'))
total_received_label_exit_tab = ttk.Label(exit_tab, text="Valor recebido:", font=('Arial', 20, 'bold'))
total_received_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=('Arial', 20, 'bold'),
    textvariable=value_received,
    width=10,
)
change_label_exit_tab = ttk.Label(exit_tab, text="Troco:", font=('Arial', 20, 'bold'))
change_value_label_exit_tab = ttk.Label(exit_tab, textvariable=change_value, font=('Arial', 20, 'bold'))
exit_cancel_button = Button(
    exit_tab,
    text="Cancelar",
    font=('Arial', 25, 'bold'),
    command=close_exit_tab,
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=12,
    cursor="hand2"
)
exit_finalize_button = Button(
    exit_tab,
    text="Finalizar",
    font=('Arial', 25, 'bold'),
    command=lambda status="FINALIZAR": ending_parking(status),
    bg="royalblue",
    activebackground="coral1",
    activeforeground="white",
    width=12,
    cursor="hand2"
)
discount_label_exit_tab = ttk.Label(exit_tab, text="Desconto:", font=('Arial', 20, 'bold'))
discount_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=('Arial', 20, 'bold'),
    textvariable=discount,
    width=10,
)
addition_label_exit_tab = ttk.Label(exit_tab, text="Acréscimo:", font=('Arial', 20, 'bold'))
addition_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=('Arial', 20, 'bold'),
    textvariable=addition,
    width=10,
)

# -----------------------------------------------------------------------------------------------------------
# EXIT TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
total_received_entry_exit_tab.bind("<Return>", calc_change)
total_received_entry_exit_tab.bind("<Tab>", calc_change)
total_received_entry_exit_tab.bind("<KP_Enter>", calc_change)
total_received_entry_exit_tab.bind("<Button-1>", on_click)
addition_entry_exit_tab.bind("<Return>", lambda event: apply_add_and_discount(event, "ADD"))
addition_entry_exit_tab.bind("<Tab>", lambda event: apply_add_and_discount(event, "ADD"))
addition_entry_exit_tab.bind("<KP_Enter>", lambda event: apply_add_and_discount(event, "ADD"))
addition_entry_exit_tab.bind("<Button-1>", on_click)
discount_entry_exit_tab.bind("<Return>", lambda event: apply_add_and_discount(event, "DISC"))
discount_entry_exit_tab.bind("<Tab>", lambda event: apply_add_and_discount(event, "DISC"))
discount_entry_exit_tab.bind("<KP_Enter>", lambda event: apply_add_and_discount(event, "DISC"))
discount_entry_exit_tab.bind("<Button-1>", on_click)

# -----------------------------------------------------------------------------------------------------------
# EXIT TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
out_plate_label_exit_tab.place(relx=0.21, y=100, anchor=SE)
out_plate_value_label_exit_tab.place(relx=0.215, y=104, anchor=SW)
out_model_label_exit_tab.place(relx=0.21, y=220, anchor=SE)
out_model_value_label_exit_tab.place(relx=0.215, y=220, anchor=SW)
out_color_label_exit_tab.place(relx=0.21, y=340, anchor=SE)
out_color_value_label_exit_tab.place(relx=0.215, y=340, anchor=SW)
out_category_label_exit_tab.place(relx=0.6, y=100, anchor=SE)
out_category_value_label_exit_tab.place(relx=0.61, y=104, anchor=SW)
in_time_label_exit_tab.place(relx=0.15, y=415, anchor=SE)
in_time_value_label_exit_tab.place(relx=0.155, y=415, anchor=SW)
out_time_label_exit_tab.place(relx=0.35, y=415, anchor=SE)
out_time_value_label_exit_tab.place(relx=0.355, y=415, anchor=SW)
delta_time_label_exit_tab.place(relx=0.65, y=415, anchor=SE)
delta_time_value_label_exit_tab.place(relx=0.665, y=415, anchor=SW)
total_label_exit_tab.place(relx=0.5, y=470, anchor=NW)
total_value_label_exit_tab.place(relx=0.85, y=490, anchor=CENTER)
total_received_label_exit_tab.place(relx=0.1, y=450, anchor=NW)
total_received_entry_exit_tab.place(relx=0.1, y=500, anchor=NW)
change_label_exit_tab.place(relx=0.1, y=550, anchor=NW)
change_value_label_exit_tab.place(relx=0.1, y=600, anchor=NW)
exit_cancel_button.place(relx=0.5, y=600, anchor=NW)
exit_finalize_button.place(relx=0.75, y=600, anchor=NW)
discount_label_exit_tab.place(relx=0.3, y=450, anchor=NW)
discount_entry_exit_tab.place(relx=0.3, y=500, anchor=NW)
addition_label_exit_tab.place(relx=0.3, y=550, anchor=NW)
addition_entry_exit_tab.place(relx=0.3, y=600, anchor=NW)

# -----------------------------------------------------------------------------------------------------------
# CONFIG TAB WIDGETS
# -----------------------------------------------------------------------------------------------------------
add_model_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_model_title = ttk.Label(add_model_frame, text="ADICIONAR NOVO MODELO", justify="center", font=('Arial', 14, 'bold'))
add_model_name = ttk.Label(add_model_frame, text="NOME:", justify="center", font=('Arial', 14, 'bold'))
add_model_entry = ttk.Entry(add_model_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_model_name)
add_model_category = ttk.Label(add_model_frame, text="CATEGORIA:", justify="center", font=('Arial', 14, 'bold'))
add_model_category_comb = AutocompleteCombobox(add_model_frame, completevalues=get_all_categories())
add_model_button = Button(
    add_model_frame,
    text="Adicionar",
    command=lambda element="model": add_element(element=element),
    font=('Arial', 14, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
add_category_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_category_title = ttk.Label(add_category_frame, text="ADICIONAR NOVA CATEGORIA", justify="center", font=('Arial', 14, 'bold'))
add_category_name = ttk.Label(add_category_frame, text="NOME:", justify="center", font=('Arial', 14, 'bold'))
add_category_name_entry = ttk.Entry(add_category_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_category_name)
add_category_price = ttk.Label(add_category_frame, text="VALOR DA HORA:", justify="center", font=('Arial', 14, 'bold'))
add_category_price_entry = ttk.Entry(add_category_frame, width=10, font=('Arial', 14, 'bold'), textvariable=new_category_price)
add_category_button = Button(
    add_category_frame,
    text="Adicionar",
    command=lambda element="category": add_element(element=element),
    font=('Arial', 14, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
add_color_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_color_title = ttk.Label(add_color_frame, text="ADICIONAR NOVA COR", justify="center", font=('Arial', 14, 'bold'))
add_color_name = ttk.Label(add_color_frame, text="NOME:", justify="center", font=('Arial', 14, 'bold'))
add_color_name_entry = ttk.Entry(add_color_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_color_name)
add_color_button = Button(
    add_color_frame,
    text="Adicionar",
    command=lambda element="color": add_element(element=element),
    font=('Arial', 14, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
add_status_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_status_title = ttk.Label(add_status_frame, text="ADICIONAR NOVO STATUS", justify="center", font=('Arial', 14, 'bold'))
add_status_name = ttk.Label(add_status_frame, text="NOME:", justify="center", font=('Arial', 14, 'bold'))
add_status_name_entry = ttk.Entry(add_status_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_status)
add_status_button = Button(
    add_status_frame,
    text="Adicionar",
    command=lambda element="status": add_element(element=element),
    font=('Arial', 14, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
add_user_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_user_title = ttk.Label(add_user_frame, text="ADICIONAR NOVO USUÁRIO", justify="center", font=('Arial', 14, 'bold'))
add_user_name = ttk.Label(add_user_frame, text="NOME:", justify="center", font=('Arial', 14, 'bold'))
add_user_name_entry = ttk.Entry(add_user_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_user_name)
add_user_pass = ttk.Label(add_user_frame, text="SENHA:", justify="center", font=('Arial', 14, 'bold'))
add_user_pass_entry = ttk.Entry(add_user_frame, width=23, font=('Arial', 14, 'bold'), textvariable=new_user_password)
add_user_role = ttk.Label(add_user_frame, text="PERMISSÃO:", justify="center", font=('Arial', 14, 'bold'))
add_user_role_comb = AutocompleteCombobox(add_user_frame, completevalues=["ADMIM", "CAIXA"])
add_user_button = Button(
    add_user_frame,
    text="Adicionar",
    command=lambda element="user": add_element(element=element),
    font=('Arial', 14, 'bold'),
    bg="royalblue",
    activebackground="coral1",
    width=16,
    cursor="hand2"
)
# -----------------------------------------------------------------------------------------------------------
# CONFIG TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
add_model_frame.place(x=10, y=20, height=150, width=350)
add_model_title.place(relx=0.5, y=5, anchor=CENTER)
add_model_name.place(x=5, y=25, anchor=NW)
add_model_entry.place(x=80, y=24, anchor=NW)
add_model_category.place(x=5, y=65, anchor=NW)
add_model_category_comb.place(x=140, y=65, anchor=NW)
add_model_button.place(relx=0.5, y=120, anchor=CENTER)

add_category_frame.place(x=10, y=200, height=150, width=350)
add_category_title.place(relx=0.5, y=5, anchor=CENTER)
add_category_name.place(x=5, y=25, anchor=NW)
add_category_name_entry.place(x=80, y=24, anchor=NW)
add_category_price.place(x=5, y=65, anchor=NW)
add_category_price_entry.place(x=190, y=64, anchor=NW)
add_category_button.place(relx=0.5, y=120, anchor=CENTER)

add_color_frame.place(x=10, y=380, height=100, width=350)
add_color_title.place(relx=0.5, y=5, anchor=CENTER)
add_color_name.place(x=5, y=25, anchor=NW)
add_color_name_entry.place(x=80, y=24, anchor=NW)
add_color_button.place(relx=0.5, y=70, anchor=CENTER)

add_status_frame.place(x=10, y=510, height=100, width=350)
add_status_title.place(relx=0.5, y=5, anchor=CENTER)
add_status_name.place(x=5, y=25, anchor=NW)
add_status_name_entry.place(x=80, y=24, anchor=NW)
add_status_button.place(relx=0.5, y=70, anchor=CENTER)

add_user_frame.place(x=380, y=20, height=200, width=350)
add_user_title.place(relx=0.5, y=5, anchor=CENTER)
add_user_name.place(x=5, y=25, anchor=NW)
add_user_name_entry.place(x=80, y=24, anchor=NW)
add_user_pass.place(x=5, y=65, anchor=NW)
add_user_pass_entry.place(x=80, y=64, anchor=NW)
add_user_role.place(x=5, y=105, anchor=NW)
add_user_role_comb.place(x=130, y=104, anchor=NW)
add_user_button.place(relx=0.5, y=160, anchor=CENTER)

if __name__ == "__main__":
    open_printer_connection()
    global df_in, df_out
    df_in = get_today_parkings_as_df_in()
    df_out = get_today_parkings_as_df_out()
    mount_in_table()
    mount_out_table()
    root.mainloop()
