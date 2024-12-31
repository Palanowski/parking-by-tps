import pandas as pd
import random
import re
from datetime import datetime, timedelta
import tkinter.ttk as ttk
from tkinter import *
from tkinter.constants import *
from tkinter import messagebox as mb
from ttkwidgets.autocomplete import AutocompleteCombobox

from models.color import *
from models.category import *
from models.config import *
from models.model import *
from models.parking import *
from models.reports import calc_metrics
from models.status import *
from models.users import *
from models.impressora import *

from schemas.category import CategoryModel
from schemas.model import ModelModel
from schemas.parking import ParkingModel
from schemas.users import UsersModel


# CONFIG
root = Tk()
root.geometry("1300x760")
root.title("Estacionamento Costeira")
style = ttk.Style()
style.theme_use('clam')
style.configure('Treeview.Heading', font=(None, 12, "bold"), height=50)
style.configure('TCheckbutton', font = 18)

# VARIABLES
login = StringVar(value="Usuário")
password = StringVar(value="Senha")

confirm_login = StringVar(value="Usuário")
confirm_password = StringVar(value="Senha")

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
new_category_daily_price = StringVar()

new_color_name = StringVar()

new_status = StringVar()

new_tolerance = IntVar()
new_header = StringVar()
new_footer = StringVar()

config_tolerance = StringVar()
config_daily_price = StringVar()
config_daily_price_moto = StringVar()
config_printer_header = StringVar()
config_printer_footer = StringVar()

search_in_plate = StringVar()
in_plate = StringVar()
in_model = StringVar()
in_category = StringVar()
in_color = StringVar()
in_time = StringVar()

barcodeVar = StringVar(value="")
byPlateVar = BooleanVar()
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
byCashVar = BooleanVar()
out_quit_return_button = StringVar(value="Desistência")

report_resp_var = StringVar(value="GERAL")
report_total_vehicles = IntVar()
report_total_cashier = DoubleVar()
report_total_cash = DoubleVar()
report_total_card = DoubleVar()
report_total_add = DoubleVar()
report_total_discount = DoubleVar()
report_total_open_vehicles = IntVar()
report_total_open_vehicles_1 = IntVar()
report_total_open_vehicles_2 = IntVar()
report_total_open_vehicles_3 = IntVar()
report_total_open_vehicles_4 = IntVar()
report_total_finalized_vehicles = IntVar()
report_total_finalized_vehicles_1 = IntVar()
report_total_finalized_vehicles_2 = IntVar()
report_total_finalized_vehicles_3 = IntVar()
report_total_finalized_vehicles_4 = IntVar()
report_total_canceled_vehicles = IntVar()
report_total_canceled_vehicles_1 = IntVar()
report_total_canceled_vehicles_2 = IntVar()
report_total_canceled_vehicles_3 = IntVar()
report_total_canceled_vehicles_4 = IntVar()

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

font13 = ('Arial', 13, 'bold')
font14 = ('Arial', 14, 'bold')
font18 = ('Arial', 18, 'bold')
font20 = ('Arial', 20, 'bold')
font45 = ('Arial', 45, 'bold')

# AUXILIARY FUNCTIONS
def update_completion_list(element):
    if "model" in element:
        models = get_all_models()
        in_model_entry.configure(values=models)
        add_model_entry.configure(values=models)
    elif "category" in element:
        categories = get_all_categories()
        in_category_entry.configure(values=categories)
        add_category_name_entry.configure(values=categories)
    elif "color" in element:
        colors = get_all_colors()
        in_color_entry.configure(values=colors)
        add_color_name_entry.configure(values=colors)
    elif "status" in element:
        status = get_all_status()
        add_status_name_entry.configure(values=status)
    elif "user" in element:
        users = get_all_users()
        login_entry.configure(values=users)
        add_user_name_entry.configure(values=users)
    elif "plate":
        plates = get_parkings_plates()
        out_plate_entry.configure(values=plates)


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
            active_user_name.set(user["name"])
            active_user_role.set(user["role"])
            root_notebook.tab(parking_tab, state="normal")
            if user["role"] == "admin":
                root_notebook.tab(config_tab, state="normal")
                root_notebook.tab(report_tab, state="normal")
            else:
                root_notebook.tab(config_tab, state="hidden")
                root_notebook.tab(report_tab, state="hidden")
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


# def login_confirmation(event):
#     user = get_user_by_id(confirm_login.get())
#     if user:
#         if user["password"] == confirm_password.get():
#             if user["role"] == "admin":
#                 login_modal.destroy()
#                 if "Config" in event:
#                     root_notebook.select(config_tab)
#                 elif "Relat" in event:
#                     root_notebook.select(report_tab)
#             else:
#                 root_notebook.select(parking_tab)
#                 mb.showwarning("OPS", "Usuário não tem permissão para acesso.")
#     else:
#         root_notebook.select(parking_tab)
#         mb.showwarning("OPS", "Usuário inválido.")

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


# def notebook_tab_selection(event):
#     selected_tab = event.widget.select()
#     tab_name = event.widget.tab(selected_tab, "text")
#     if ("acesso" in tab_name) and active_user_name.get():
#         logout()
#     if "Config" in tab_name:
#         pass


def open_printer_connection():
    AbreConexaoImpressora(
        1,
        "I8",
        "USB",
        0
    )


def print_parking(code):
    config = get_config()
    ImpressaoTexto("================================================", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("ESTACIONAMENTO C O S T E I R A", 1, 0, 0)
    AvancaPapel(1)
    ImpressaoTexto("Av. Pref. Osmar Cunha, 155 - Centro", 1, 1, 0)
    AvancaPapel(1)
    ImpressaoTexto(config["printer_header"], 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("================================================", 1, 8, 0)
    AvancaPapel(3)
    ImpressaoTexto(f"{in_plate.get()} {in_category.get()}", 1, 8, 33)
    AvancaPapel(3)
    ImpressaoTexto(f"{in_model.get()}  {in_color.get()}", 1, 8, 17)
    AvancaPapel(3)
    ImpressaoTexto(f"{datetime.now():%Y-%m-%d %H:%M}", 1, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto("================================================", 1, 0, 0)
    AvancaPapel(3)
    
    ImpressaoCodigoBarras(4, f"*{code}*", 80, 3, 4)
    AvancaPapel(3)
    ImpressaoTexto("================================================", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("SEM TOLERÂNCIA NA PRIMEIRA HORA", 1, 8, 0)
    AvancaPapel(1)
    ImpressaoTexto("Horário de funcionamento:", 1, 0, 0)
    ImpressaoTexto(config["printer_footer"], 1, 1, 0)
    AvancaPapel(3)
    Corte(3)
    # ------------- Impressão chave
    AvancaPapel(3)
    ImpressaoTexto(in_plate.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(in_model.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(in_color.get(), 2, 8, 17)
    AvancaPapel(1)
    ImpressaoTexto(f"{datetime.now():%Y-%m-%d %H:%M}", 2, 8, 0)
    CorteTotal(4)


def print_report():
    selected_resp = report_resp_var.get()
    if selected_resp:
        date = datetime.now().date()
        ImpressaoTexto("================================================", 1, 8, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Relatório {selected_resp}", 1, 0, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Data: {date}", 1, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto("================================================", 1, 8, 0)
        AvancaPapel(3)
        ImpressaoTexto(f"Total em caixa: {report_total_cashier.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total caixa em dinheiro: {report_total_cash.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total caixa no cartão: {report_total_card.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total de acréscimos: {report_total_add.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total de descontos: {report_total_discount.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total de veículos: {report_total_vehicles.get()}", 0, 1, 0)
        AvancaPapel(2)
        ImpressaoTexto("VEÍCULOS EM ABERTO:", 1, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total: {report_total_open_vehicles.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CARROS: {report_total_open_vehicles_1.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"SUVS: {report_total_open_vehicles_2.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CAMINHONETES: {report_total_open_vehicles_4.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"MOTOS: {report_total_open_vehicles_3.get()}", 0, 1, 0)
        AvancaPapel(2)
        ImpressaoTexto("VEÍCULOS FINALIZADOS:", 1, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total: {report_total_finalized_vehicles.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CARROS: {report_total_finalized_vehicles_1.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"SUVS: {report_total_finalized_vehicles_2.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CAMINHONETES: {report_total_finalized_vehicles_4.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"MOTOS: {report_total_finalized_vehicles_3.get()}", 0, 1, 0)
        AvancaPapel(2)
        ImpressaoTexto("VEÍCULOS CANCELADOS:", 1, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"Total: {report_total_canceled_vehicles.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CARROS: {report_total_canceled_vehicles_1.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"SUVS: {report_total_canceled_vehicles_2.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"CAMINHONETES: {report_total_canceled_vehicles_4.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto(f"MOTOS: {report_total_canceled_vehicles_3.get()}", 0, 1, 0)
        AvancaPapel(1)
        ImpressaoTexto("================================================", 1, 8, 0)
        AvancaPapel(3)
        Corte(3)
    else:
        mb.showwarning("ATENÇÃO", "Primeiro selecione o responsável antes de imprimir")


def hash_generator():
    code = ""
    for index in range(10):
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
        update_completion_list("plate")
        in_plate_entry.focus()


def ending_parking(event, status):
    if status == "FINALIZAR":
        plateID = out_plate.get()
        finalize_parking(
            plateID,
            delta_time_value.get(),
            active_user_name.get(),
            total_value.get(),
            addition.get(),
            discount.get(),
            byPlateVar.get(),
            byCashVar.get(),
        )
        close_exit_tab()
    elif status == "DESISTIR|RETORNAR":
        confirmation = mb.askyesno("CONFIRMAR", f"Você deseja aplicar a {out_quit_return_button.get()} nesse veículo?")
        if confirmation:
            if "Desist" in out_quit_return_button.get():
                plateID = out_plate.get()
                cancel_parking(plateID=plateID, userID=active_user_name.get())
                clear_data("out")
                out_barcode_entry.focus()
            elif out_quit_return_button.get() == "Retorno":
                plateID = out_plate.get()
                return_parking(plateID)
                clear_data("out")
                out_barcode_entry.focus()
    out_quit_return_button.set("Desistência")
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
    df_in = df_in.sort_values(by=[header_map[col]], ascending=order_in)
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
    df_out = df_out.sort_values(by=[header_map[col]], ascending=order_out)
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
        if (values[7] == "EM ABERTO") or (values[7] == "RETORNO"):
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

    for col_out in header_out:
        out_table.column(col_out, anchor="center", width=158)
        out_table.heading(col_out, text=col_out, command=lambda col=col_out : sort_out_table(col))
    for row in rows:
        values = [value for value in row]
        out_table.insert("", 0, values=values, tags="gray")


def update_in_grid(plateID: str = None):
    global df_in
    df_in = get_today_parkings_as_df_in(plateID)
    mount_in_table()
    update_out_grid()


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
            byPlateVar.set(True)
            out_finalize_button.focus()
            if parking["status"] in ["CANCELADO", "FINALIZADO"]:
                out_quit_return_button.set("Retorno")
                out_cancel_button.focus()
            else:
                out_finalize_button.focus()
        else:
            mb.showwarning("ALERTA", "Placa não encontrada")
    elif element == "barcode":
        code = barcodeVar.get()
        parking = get_parking_by_code(code)
        if parking:
            out_plate.set(parking["plate"])
            out_model.set(parking["model"])
            out_category.set(parking["category"])
            out_color.set(parking["color"])
            byPlateVar.set(False)
            if parking["status"] in ["CANCELADO", "FINALIZADO"]:
                out_quit_return_button.set("Retorno")
            else:
                open_exit_tab("barcode")
        else:
            mb.showwarning("ALERTA", "Código não encontrado")


def check_config_element(event, element):
    if element == "category":
        category = get_category_by_id(new_category_name.get())
        if category:
            new_category_price.set(category["price"])
            new_category_daily_price.set(category["daily_price"])
    elif element == "model":
        model = get_model_by_id(new_model_name.get())
        if model:
            new_model_category.set(model["category"])
    elif element == "user":
        user = get_user_by_id(new_user_name.get())
        if user:
            new_user_role.set(user["role"])


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
        barcodeVar.set("")
        out_model.set("")
        out_category.set("")
        out_color.set("")
        out_plate_entry.focus()
        addition.set("0.00")
        discount.set("0.00")
        change_value.set("0.00")


def clear_data_records_func():
    clear_data_records()
    update_in_grid()

def on_click(event):
    event.widget.delete(0, END)


def calc_change(event):
    change_value.set(format(float(value_received.get())-float(total_value.get()), '.2f'))


def apply_add_and_discount(event, action: str):
    if action == "ADD":
        addition.set(format(float(addition.get()), '.2f'))
        total = float(total_value.get()) + float(addition.get())
    if action == "DISC":
        discount.set(format(float(discount.get()), '.2f'))
        total = float(total_value.get()) - float(discount.get())
    total_value.set(format(total, '.2f'))
    exit_finalize_button.focus()


def calc_total_value(delta_hours: int, delta_minutes: int):
    config_info = get_config()
    category_info = get_category_by_id(out_category.get())
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
    if float(category_info["price"]*delta_hours) >= category_info["daily_price"]:
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
    parking = get_parking_by_plate(out_plate.get())
    out_model.set(parking["model"])
    out_category.set(parking["category"])
    out_color.set(parking["color"])
    if (parking["status"] == "EM ABERTO") or (parking["status"] == "RETORNO"):
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
        byCashVar.set(value=False)
        exit_finalize_button.focus()
    else:
        mb.showwarning("ALERTA", "Não é possível finalizar um veículo que não está EM ABERTO")


def close_exit_tab():
    root_notebook.tab(parking_tab, state="normal")
    root_notebook.select(parking_tab)
    root_notebook.tab(login_tab, state="normal")
    root_notebook.tab(exit_tab, state="hidden")
    if active_user_role.get() == "admin":
        root_notebook.tab(config_tab, state="normal")
        root_notebook.tab(report_tab, state="normal")
    clear_data("out")
    out_barcode_entry.focus()


def add_element(element: str):
    if "ADD" in element:
        if "model" in element:
            model = ModelModel(id=new_model_name.get(), category=add_model_category_entry.get())
            update_or_insert_model(model)
            update_completion_list("model")
            mb.showwarning("SUCESSO", f"Modelo {model.id} adicionado/atualizado com sucesso.")
        elif "category" in element:
            category = CategoryModel(id=new_category_name.get(), price=new_category_price.get(), daily_price=new_category_daily_price.get())
            update_or_insert_category(category)
            update_completion_list("category")
            mb.showwarning("SUCESSO", f"Categoria {category.id} adicionada/atualizada com sucesso.")
        elif "color" in element:
            update_or_insert_color(new_color_name.get())
            update_completion_list("color")
            mb.showwarning("SUCESSO", f"Cor {new_color_name.get()} adicionada com sucesso.")
        elif "user" in element:
            user = UsersModel(name=new_user_name.get(), password=new_user_password.get(), role=new_user_role.get(), ISactive=True)
            update_or_insert_user(user)
            update_completion_list("users")
            mb.showwarning("SUCESSO", f"Usuário {new_user_name.get()} adicionado/atualizado com sucesso.")
        elif "status" in element:
            update_or_insert_status(new_status.get())
            update_completion_list("status")
            mb.showwarning("SUCESSO", f"Status {new_status.get()} adicionado com sucesso.")
        elif "config" in element:
            update_config(tolerance=new_tolerance.get(), header=new_header.get(), footer=new_footer.get())
            update_completion_list("config")
            mb.showwarning("SUCESSO", "Configurações gerais atualizadas com sucesso.")
    elif "RMV" in element:
        if "model" in element:
            delete_model(new_model_name.get())
            update_completion_list("model")
            mb.showwarning("SUCESSO", f"Modelo {new_model_name.get()} removido com sucesso.")
        elif "category" in element:
            delete_category(new_category_name.get())
            update_completion_list("category")
            mb.showwarning("SUCESSO", f"Categoria {new_category_name.get()} removida com sucesso.")
        elif "color" in element:
            delete_color(new_color_name.get())
            update_completion_list("color")
            mb.showwarning("SUCESSO", f"Cor {new_color_name.get()} removida com sucesso.")
        elif "user" in element:
            delete_user(new_user_name.get())
            update_completion_list("users")
            mb.showwarning("SUCESSO", f"Usuário {new_user_name.get()} desativado com sucesso.")
        elif "status" in element:
            delete_status(new_status.get())
            update_completion_list("status")
            mb.showwarning("SUCESSO", f"Status {new_status.get()} removido com sucesso.")


def calc_report_metrics(event, userID: str):
    if userID == "GERAL":
        parkings = get_parkings_by_user_order_by_status()
    else:
        parkings_closed = get_parkings_by_user_order_by_status(userID=userID)
        parkings = get_parkings_by_user_order_by_status(userID=userID, statusID="EM ABERTO") + parkings_closed
    metrics = calc_metrics(parkings=parkings)
    report_total_vehicles.set(metrics["total_count"])
    report_total_cashier.set(format(float(metrics["total_cashier"]), '.2f'))
    report_total_cash.set(format(float(metrics["total_cash"]), '.2f'))
    report_total_card.set(format(float(metrics["total_card"]), '.2f'))
    report_total_add.set(format(float(metrics["total_add"]), '.2f'))
    report_total_discount.set(format(float(metrics["total_discount"]), '.2f'))
    report_total_open_vehicles.set(metrics["total_open_vehicles"])
    report_total_open_vehicles_1.set(metrics["total_open_cat_1"])
    report_total_open_vehicles_2.set(metrics["total_open_cat_2"])
    report_total_open_vehicles_3.set(metrics["total_open_cat_3"])
    report_total_open_vehicles_4.set(metrics["total_open_cat_4"])
    report_total_finalized_vehicles.set(metrics["total_finalized_vehicles"])
    report_total_finalized_vehicles_1.set(metrics["total_finalized_cat_1"])
    report_total_finalized_vehicles_2.set(metrics["total_finalized_cat_2"])
    report_total_finalized_vehicles_3.set(metrics["total_finalized_cat_3"])
    report_total_finalized_vehicles_4.set(metrics["total_finalized_cat_4"])
    report_total_canceled_vehicles.set(metrics["total_canceled_vehicles"])
    report_total_canceled_vehicles_1.set(metrics["total_canceled_cat_1"])
    report_total_canceled_vehicles_2.set(metrics["total_canceled_cat_2"])
    report_total_canceled_vehicles_3.set(metrics["total_canceled_cat_3"])
    report_total_canceled_vehicles_4.set(metrics["total_canceled_cat_4"])


def export_parking_to_csv():
    date = datetime.now().strftime("%Y_%m_%d")
    with get_dal_mysql() as db:
        parkings = db().select(db.parking.ALL).as_list()
        report = list()
        for parking in parkings:
            line = dict(
                id=parking["id"],
                placa=parking["plate"],
                modelo=parking["model"],
                categoria=parking["category"],
                cor=parking["color"],
                data=parking["entry_date"],
                entrada=parking["entry_time"],
                saida=parking["exit_time"],
                permanencia=parking["delta_time"],
                status=parking["status"],
                usuario_entrada=parking["entry_user"],
                usuario_saida=parking["exit_user"],
                total=parking["total_value"],
                retorno="RETORNO" if parking["ISreturn"] else "NORMAL",
                parcial=parking["partialPayment"],
                acrescimo=parking["addition"],
                desconto=parking["discount"],
                tipo_fechamento="PLACA" if parking["byPlate"] else "CODIGO-DE-BARRAS",
                pagamento="DINHEIRO" if parking["byCash"] else "CARTÃO",
            )
            report.append(line)
        report_df = pd.DataFrame(report)
        report_df.to_csv(f"/home/estacionamento/Documentos/relatorio_{date}.csv", header=True)
        open(f'/home/estacionamento/Documentos/login_{date}.csv', 'w').write(str(db().select(db.log_in.ALL)))
        mb.showinfo("SUCESSO", "Planilhas exportadas com sucesso na pasta Documentos.")


def set_checkbox_cash(event):
    state = byCashVar.get()
    if state:
        byCashVar.set(False)
    else:
        byCashVar.set(True)


# def open_login_modal(tab):
#     login_modal = Toplevel()
#     login_modal.protocol("WM_DELETE_WINDOW", go_to_parking_tab)
#     login_modal.geometry("350x250+650+360")
#     login_modal.title("Confirmação de usuário admin")
#     login_modal_user_entry = AutocompleteCombobox(login_modal, font=font14,textvariable=confirm_login, completevalues=get_all_users())
#     login_modal_user_entry.pack(side=TOP, padx=20, pady=20)
#     login_modal_password_entry = ttk.Entry(login_modal, font=font14, textvariable=confirm_password)
#     login_modal_password_entry.pack(side=TOP)
#     login_modal_password_entry.bind("<Button-1>", on_click)
#     login_modal_confirm_button = Button(
#         login_modal,
#         text="Confirmar",
#         font=font14,
#         command= lambda event=tab: login_confirmation(event),
#         bg="royalblue",
#         fg="white",
#         activebackground="coral1",
#         activeforeground="black",
#         width=15,
#     )
#     login_modal_confirm_button.pack(side=TOP, padx=20, pady=20)


def on_tab_change(event):
    tab = event.widget.tab('current')['text']
    if "Relat" in tab:
        calc_report_metrics("teste", "GERAL")
    #     open_login_modal(tab)
    # elif "Config" in tab:
    #     open_login_modal(tab)


# def go_to_parking_tab():
#     root_notebook.select(parking_tab)
#     login_modal.destroy()
# -----------------------------------------------------------------------------------------------------------
# NOTEBOOK CONFIG
# -----------------------------------------------------------------------------------------------------------
root_notebook = ttk.Notebook(root)
root_notebook.pack(expand=1,fill=BOTH)
# root_notebook.bind("<<NotebookTabChanged>>", notebook_tab_selection)

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
user_name_label = ttk.Label(user_frame, text="Usuário:", font=font13)
user_name_label.pack(side=LEFT)
active_user_label = ttk.Label(user_frame, textvariable=active_user_name, font=font13)
active_user_label.pack(side=LEFT)
count_frame = ttk.Frame(root, borderwidth=2, height=13, relief="sunken", width=50)
count_frame.place(relx=0.5, y=0, anchor=NE)
count_total_label = ttk.Label(count_frame, textvariable=total_count, font=font13)
count_total_label.pack(side=LEFT)

root_notebook.bind('<<NotebookTabChanged>>', on_tab_change)

# login_modal = Toplevel()
# login_modal.protocol("WM_DELETE_WINDOW", go_to_parking_tab)
# -----------------------------------------------------------------------------------------------------------
# LOGIN TAB WIDJETS
# -----------------------------------------------------------------------------------------------------------
login_entry = AutocompleteCombobox(login_tab, font=font20,textvariable=login, completevalues=get_all_users())
password_entry = ttk.Entry(
    login_tab,
    font=font20,
    textvariable=password,
    show="*"
)
login_button = Button(
    login_tab,
    text="Entrar",
    font=font18,
    command= lambda click="login click": login_verification(click),
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    height=2,
    width=15,
    cursor="hand2"
)

# -----------------------------------------------------------------------------------------------------------
# LOGIN TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
login_entry.place(relx=0.5, y=150, anchor=CENTER)
password_entry.place(relx=0.5, y=250, anchor=CENTER)
login_button.place(relx=0.5, y=350, anchor=CENTER)

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
    font=font20,
    textvariable=in_plate,
    width=18,
)
in_model_entry = AutocompleteCombobox(
    in_frame_center,
    font=font20,
    completevalues=get_all_models(),
    textvariable=in_model,
    width=18,
)
in_category_entry = AutocompleteCombobox(
    in_frame_center,
    font=font20,
    completevalues=get_all_categories(),
    textvariable=in_category,
    width=18,
)
in_color_entry = AutocompleteCombobox(
    in_frame_center,
    font=font20,
    completevalues=get_all_colors(),
    textvariable=in_color,
    width=18,
)
in_confirm_button = Button(
    in_frame_bottom,
    text="Entrar",
    font=font18,
    command= lambda event="confirm": insert_parking(event),
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=15,
    cursor="hand2"
)
in_clear_button = Button(
    in_frame_bottom,
    text="Limpar",
    font=font18,
    command=lambda element="in": clear_data(element),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=15,
    cursor="hand2"
)
in_title = ttk.Label(in_frame_top, text="ENTRADA", justify="right", font=font20)
in_plate_label = ttk.Label(in_frame_center, text="Placa", font=font18)
in_model_label = ttk.Label(in_frame_center, text="Modelo", font=font18)
in_category_label = ttk.Label(in_frame_center, text="Categoria", font=font18)
in_color_label = ttk.Label(in_frame_center, text="Cor", font=font18)

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB WIDJETS - EXIT
# -----------------------------------------------------------------------------------------------------------
out_title = ttk.Label(out_frame_top, text="SAÍDA", justify="center", font=font20)
out_plate_label = ttk.Label(out_frame_center_top, text="Placa", font=font18)
out_barcode_entry = ttk.Entry(out_frame_center_top, width=15, font=font20, textvariable=barcodeVar)
out_barcode_label = ttk.Label(out_frame_center_top, text="Código de barras", font=font18)
out_model_label = ttk.Label(out_frame_center_bottom, text="Modelo: ", font=font18)
out_model_value = ttk.Label(out_frame_center_bottom, textvariable=out_model, font=font18, width=12)
out_category_label = ttk.Label(out_frame_center_bottom, text="Categoria: ", font=font18)
out_category_value = ttk.Label(out_frame_center_bottom, textvariable=out_category, font=font18, width=12)
out_color_label = ttk.Label(out_frame_center_bottom, text="Cor: ", font=font18)
out_color_value = ttk.Label(out_frame_center_bottom, textvariable=out_color, font=font18, width=13)
out_plate_entry = AutocompleteCombobox(out_frame_center_top, width=10, font=font20, textvariable=out_plate, completevalues=get_parkings_plates())
out_finalize_button = Button(
    out_frame_bottom,
    text="Finalizar",
    command=lambda event="Return": open_exit_tab(event),
    font=font18,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=16,
    cursor="hand2"
)
out_clear_button = Button(
    out_frame_bottom,
    text="Limpar",
    font=font18,
    command=lambda element="out": clear_data(element),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=16,
    cursor="hand2"
)
out_cancel_button = Button(
    out_frame_bottom,
    textvariable=out_quit_return_button,
    font=font18,
    command= lambda status="DESISTIR|RETORNAR": ending_parking("click", status),
    bg="lightblue",
    activebackground="coral1",
    activeforeground="white",
    width=16,
    cursor="hand2"
)

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB WIDJETS - REPORTS
# -----------------------------------------------------------------------------------------------------------
in_search_plate_name = ttk.Label(parking_tab, text="FILTRAR POR PLACA:", font=font14)
in_search_plate_entry = ttk.Entry(parking_tab, textvariable=search_in_plate, font= font14, width=12)
in_table = ttk.Treeview(report_in_frame, selectmode="browse", show="headings", height=10, columns=header_in)
in_table.pack(side=TOP, padx=10, pady=5)
in_table.tag_configure("green", background="lightgreen")
in_table.tag_configure("gray", background="lightgray")
in_table.tag_configure("red", background="coral1")

out_table = ttk.Treeview(report_out_frame, selectmode="browse", show="headings", height=6, columns=header_out)
out_table.pack(side=TOP)
out_table.tag_configure("green", background="lightgreen")
out_table.tag_configure("gray", background="lightgray")
out_table.tag_configure("red", background="coral1")

# -----------------------------------------------------------------------------------------------------------
# PARKING TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
in_frame.place(x = 15, y = 15, anchor=NW)
in_frame_top.pack(fill="x")
in_frame_center.pack()
in_frame_bottom.pack(fill="x")
out_frame.place(x = 500, y = 15, anchor=NW, width=800)
out_frame_top.pack(side=TOP)
out_frame_center_top.pack(side=TOP)
out_frame_center_bottom.pack(side=TOP)
out_frame_bottom.pack(side=BOTTOM)
in_search_plate_name.place(x=30, y=380, anchor=NW)
in_search_plate_entry.place(x=250, y=380, anchor=NW)
report_out_frame.place(x=500, y=260, anchor=NW)
report_in_frame.place(relx = 0, rely=0.99, relwidth=1, anchor="sw")

in_title.pack(side=TOP)
in_plate_entry.grid(column=1, row=2, sticky=W, padx=15, pady=6)
in_plate_label.grid(column=2, row=2, sticky=W, pady=6)
in_model_entry.grid(column=1, row=3, sticky=W, padx=15, pady=6)
in_model_label.grid(column=2, row=3, sticky=W, pady=6)
in_category_entry.grid(column=1, row=4, sticky=W, padx=15, pady=6)
in_category_label.grid(column=2, row=4, sticky=W, pady=6)
in_color_entry.grid(column=1, row=5, sticky=W, padx=15, pady=6)
in_color_label.grid(column=2, row=5, sticky=W, pady=6)
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
out_barcode_entry.bind("<Button-1>", on_click)

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
in_confirm_button.bind("<KP_Enter>", insert_parking)
out_finalize_button.bind("<Return>", open_exit_tab)
out_finalize_button.bind("<KP_Enter>", open_exit_tab)

in_search_plate_entry.bind("<KeyPress>", lambda event: update_in_grid(search_in_plate.get()))
in_search_plate_entry.bind("<Return>", lambda event: update_in_grid(search_in_plate.get()))
in_search_plate_entry.bind("<Tab>", lambda event: update_in_grid(search_in_plate.get()))
in_search_plate_entry.bind("<KP_Enter>", lambda event: update_in_grid(search_in_plate.get()))

in_plate_entry.focus()

# -----------------------------------------------------------------------------------------------------------
# EXIT TAB WIDJETS
# -----------------------------------------------------------------------------------------------------------
out_plate_label_exit_tab = ttk.Label(exit_tab, text="Placa: ", font=font45)
out_plate_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_plate, font=('Arial', 65, 'bold'))
out_model_label_exit_tab = ttk.Label(exit_tab, text="Modelo: ", font=font45)
out_model_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_model, font=('Arial', 65, 'bold'))
out_color_label_exit_tab = ttk.Label(exit_tab, text="Cor: ", font=font45)
out_color_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_color, font=('Arial', 50, 'bold'))
out_category_label_exit_tab = ttk.Label(exit_tab, text="Categoria: ", font=font45)
out_category_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_category, font=('Arial', 55, 'bold'))
in_time_label_exit_tab = ttk.Label(exit_tab, text="Entrada: ", font=('Arial', 30))
in_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=in_time, font=('Arial', 35))
out_time_label_exit_tab = ttk.Label(exit_tab, text="Saída: ", font=('Arial', 30))
out_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=out_time, font=('Arial', 35))
delta_time_label_exit_tab = ttk.Label(exit_tab, text="Permanência: ", font=('Arial', 30))
delta_time_value_label_exit_tab = ttk.Label(exit_tab, textvariable=delta_time, font=('Arial', 30))
total_label_exit_tab = ttk.Label(exit_tab, text="Total R$ ", font=font45)
total_value_label_exit_tab = ttk.Label(exit_tab, textvariable=total_value, font=('Arial', 100, 'bold'))
total_received_label_exit_tab = ttk.Label(exit_tab, text="Valor recebido:", font=font20)
total_received_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=font20,
    textvariable=value_received,
    width=10,
)
change_label_exit_tab = ttk.Label(exit_tab, text="Troco:", font=font20)
change_value_label_exit_tab = ttk.Label(exit_tab, textvariable=change_value, font=font20)
checkbox_by_cash = ttk.Checkbutton(exit_tab, text="Dinheiro", variable=byCashVar, onvalue=True, offvalue=False)
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
    command=lambda status="FINALIZAR": ending_parking("click", status),
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
discount_label_exit_tab = ttk.Label(exit_tab, text="Desconto:", font=font20)
discount_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=font20,
    textvariable=discount,
    width=10,
)
addition_label_exit_tab = ttk.Label(exit_tab, text="Acréscimo:", font=font20)
addition_entry_exit_tab = ttk.Entry(
    exit_tab,
    font=font20,
    textvariable=addition,
    width=10,
)

# -----------------------------------------------------------------------------------------------------------
# EXIT TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
exit_finalize_button.bind("<Return>", lambda event: ending_parking(event, "FINALIZAR"))
exit_finalize_button.bind("<KP_Enter>", lambda event: ending_parking(event, "FINALIZAR"))
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
out_plate_label_exit_tab.place(relx=0.25, y=100, anchor=SE)
out_plate_value_label_exit_tab.place(relx=0.255, y=104, anchor=SW)
out_model_label_exit_tab.place(relx=0.25, y=220, anchor=SE)
out_model_value_label_exit_tab.place(relx=0.255, y=224, anchor=SW)
out_color_label_exit_tab.place(relx=0.6, y=100, anchor=SE)
out_color_value_label_exit_tab.place(relx=0.61, y=104, anchor=SW)
out_category_label_exit_tab.place(relx=0.25, y=340, anchor=SE)
out_category_value_label_exit_tab.place(relx=0.255, y=344, anchor=SW)
in_time_label_exit_tab.place(relx=0.15, y=415, anchor=SE)
in_time_value_label_exit_tab.place(relx=0.155, y=415, anchor=SW)
out_time_label_exit_tab.place(relx=0.35, y=415, anchor=SE)
out_time_value_label_exit_tab.place(relx=0.355, y=415, anchor=SW)
delta_time_label_exit_tab.place(relx=0.65, y=415, anchor=SE)
delta_time_value_label_exit_tab.place(relx=0.665, y=415, anchor=SW)
total_label_exit_tab.place(relx=0.5, y=470, anchor=NW)
total_value_label_exit_tab.place(relx=0.85, y=490, anchor=CENTER)
checkbox_by_cash.place(relx=0.75, y=560, anchor=NW)
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
add_model_title = ttk.Label(add_model_frame, text="MODELOS", justify="center", font=font14)
add_model_name = ttk.Label(add_model_frame, text="NOME:", justify="center", font=font14)
add_model_entry = AutocompleteCombobox(add_model_frame, width=23, font=font14, textvariable=new_model_name, completevalues=get_all_models())
add_model_category = ttk.Label(add_model_frame, text="CATEGORIA:", justify="center", font=font14)
add_model_category_entry = AutocompleteCombobox(add_model_frame, width=20, font=font14, completevalues=get_all_categories())
add_model_button = Button(
    add_model_frame,
    text="Adicionar",
    command=lambda element="ADD model": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
rmv_model_button = Button(
    add_model_frame,
    text="Remover",
    command=lambda element="RMV model": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_category_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_category_title = ttk.Label(add_category_frame, text="CATEGORIAS", justify="center", font=font14)
add_category_name = ttk.Label(add_category_frame, text="NOME:", justify="center", font=font14)
add_category_name_entry = AutocompleteCombobox(add_category_frame, width=23, font=font14, textvariable=new_category_name, completevalues=get_all_categories())
add_category_price = ttk.Label(add_category_frame, text="VALOR DA HORA:", justify="center", font=font14)
add_category_price_entry = ttk.Entry(add_category_frame, width=15, font=font14, textvariable=new_category_price)
add_category_daily_price = ttk.Label(add_category_frame, text="VALOR DA DIÁRIA:", justify="center", font=font14)
add_category_daily_price_entry = ttk.Entry(add_category_frame, width=15, font=font14, textvariable=new_category_daily_price)
add_category_button = Button(
    add_category_frame,
    text="Adicionar",
    command=lambda element="ADD category": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
rmv_category_button = Button(
    add_category_frame,
    text="Remover",
    command=lambda element="RMV category": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_color_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_color_title = ttk.Label(add_color_frame, text="CORES", justify="center", font=font14)
add_color_name = ttk.Label(add_color_frame, text="NOME:", justify="center", font=font14)
add_color_name_entry = AutocompleteCombobox(add_color_frame, width=23, font=font14, textvariable=new_color_name, completevalues=get_all_colors())
add_color_button = Button(
    add_color_frame,
    text="Adicionar",
    command=lambda element="ADD color": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
rmv_color_button = Button(
    add_color_frame,
    text="Remover",
    command=lambda element="RMV color": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_user_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_user_title = ttk.Label(add_user_frame, text="USUÁRIOS", justify="center", font=font14)
add_user_name = ttk.Label(add_user_frame, text="NOME:", justify="center", font=font14)
add_user_name_entry = AutocompleteCombobox(add_user_frame, width=23, font=font14, textvariable=new_user_name, completevalues=get_all_users())
add_user_pass = ttk.Label(add_user_frame, text="SENHA:", justify="center", font=font14)
add_user_pass_entry = ttk.Entry(add_user_frame, width=23, font=font14, textvariable=new_user_password, show="*")
add_user_role = ttk.Label(add_user_frame, text="PERMISSÃO:", justify="center", font=font14)
add_user_role_entry = AutocompleteCombobox(add_user_frame, width=20, font=font14, textvariable=new_user_role, completevalues=["ADMIM", "CAIXA"])
add_user_button = Button(
    add_user_frame,
    text="Adicionar",
    command=lambda element="ADD user": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
rmv_user_button = Button(
    add_user_frame,
    text="Remover",
    command=lambda element="RMV user": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_status_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_status_title = ttk.Label(add_status_frame, text="STATUS DO VEÍCULO", justify="center", font=font14)
add_status_name = ttk.Label(add_status_frame, text="NOME:", justify="center", font=font14)
add_status_name_entry = AutocompleteCombobox(add_status_frame, width=23, font=font14, textvariable=new_status, completevalues=get_all_status())
add_status_button = Button(
    add_status_frame,
    text="Adicionar",
    command=lambda element="ADD status": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
rmv_status_button = Button(
    add_status_frame,
    text="Remover",
    command=lambda element="RMV status": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_clear_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_clear_title = ttk.Label(add_clear_frame, text="LIMPEZA DE DADOS", justify="center", font=font14)
add_clear_button = Button(
    add_clear_frame,
    text="Remover",
    command=clear_data_records_func,
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
add_config_frame = ttk.Frame(config_tab, borderwidth=2, relief="sunken")
add_config_title = ttk.Label(add_config_frame, text="CONFIGURAÇÕES GERAIS", justify="center", font=font14)
add_config_tolerance = ttk.Label(add_config_frame, text="TOLERÂNCIA EM MINUTOS:", justify="center", font=font14)
add_config_tolerance_entry = ttk.Entry(add_config_frame, width=7, font=font14, textvariable=new_tolerance)
add_config_header = ttk.Label(add_config_frame, text="CABEÇALHO DE IMPRESSÃO:", justify="center", font=font13)
add_config_header_value = Text(add_config_frame, height=12, width=44, borderwidth=2)
add_config_footer = ttk.Label(add_config_frame, text="RODAPÉ DE IMPRESSÃO:", justify="center", font=font13)
add_config_footer_value = Text(add_config_frame, height=12, width=44, borderwidth=2)
add_config_button = Button(
    add_config_frame,
    text="Atualizar",
    command=lambda element="ADD config": add_element(element=element),
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
# -----------------------------------------------------------------------------------------------------------
# CONFIG TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
add_model_frame.place(x=20, y=20, height=200, width=400)
add_model_title.place(relx=0.5, y=15, anchor=CENTER)
add_model_name.place(x=30, y=35, anchor=NW)
add_model_entry.place(x=370, y=34, anchor=NE)
add_model_category.place(x=30, y=90, anchor=NW)
add_model_category_entry.place(x=370, y=89, anchor=NE)
add_model_button.place(x=370, y=150, anchor=NE)
rmv_model_button.place(x=30, y=150, anchor=NW)

add_category_frame.place(x=20, y=250, height=250, width=400)
add_category_title.place(relx=0.5, y=15, anchor=CENTER)
add_category_name.place(x=30, y=45, anchor=NW)
add_category_name_entry.place(x=370, y=44, anchor=NE)
add_category_price.place(x=30, y=90, anchor=NW)
add_category_price_entry.place(x=370, y=89, anchor=NE)
add_category_daily_price.place(x=30, y=130, anchor=NW)
add_category_daily_price_entry.place(x=370, y=129, anchor=NE)
add_category_button.place(x=370, y=180, anchor=NE)
rmv_category_button.place(x=30, y=180, anchor=NW)

add_color_frame.place(x=20, y=530, height=180, width=400)
add_color_title.place(relx=0.5, y=15, anchor=CENTER)
add_color_name.place(x=30, y=45, anchor=NW)
add_color_name_entry.place(x=370, y=44, anchor=NE)
add_color_button.place(x=370, y=100, anchor=NE)
rmv_color_button.place(x=30, y=100, anchor=NW)

add_user_frame.place(x=450, y=20, height=250, width=400)
add_user_title.place(relx=0.5, y=15, anchor=CENTER)
add_user_name.place(x=30, y=45, anchor=NW)
add_user_name_entry.place(x=370, y=44, anchor=NE)
add_user_pass.place(x=30, y=90, anchor=NW)
add_user_pass_entry.place(x=370, y=89, anchor=NE)
add_user_role.place(x=30, y=135, anchor=NW)
add_user_role_entry.place(x=370, y=134, anchor=NE)
rmv_user_button.place(x=30, y=180, anchor=NW)
add_user_button.place(x=370, y=180, anchor=NE)

add_status_frame.place(x=450, y=320, height=180, width=400)
add_status_title.place(relx=0.5, y=15, anchor=CENTER)
add_status_name.place(x=30, y=45, anchor=NW)
add_status_name_entry.place(x=370, y=44, anchor=NE)
add_status_button.place(x=370, y=100, anchor=NE)
rmv_status_button.place(x=30, y=100, anchor=NW)

add_clear_frame.place(x=450, y=530, height=100, width=400)
add_clear_title.place(relx=0.5, y=15, anchor=CENTER)
add_clear_button.place(relx=0.5, y=60, anchor=CENTER)

add_config_frame.place(x=880, y=20, height=690, width=420)
add_config_title.place(relx=0.5, y=15, anchor=CENTER)
add_config_tolerance.place(x=30, y=45, anchor=NW)
config_from_db = get_config()
new_tolerance.set(config_from_db["tolerance"])
add_config_tolerance_entry.place(x=390, y=44, anchor=NE)
add_config_header.place(relx=0.5, y=120, anchor=CENTER)
add_config_header_value.insert(1.0, chars=config_from_db["printer_header"])
add_config_header_value.place(x=30, y=140, anchor=NW)
add_config_footer.place(relx=0.5, y=370, anchor=CENTER)
add_config_footer_value.insert(1.0, chars=config_from_db["printer_footer"])
add_config_footer_value.place(x=30, y=390, anchor=NW)
add_config_button.place(relx=0.5, y=635, anchor=CENTER)

# -----------------------------------------------------------------------------------------------------------
# CONFIG TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
add_model_entry.bind("<<ComboboxSelected>>", lambda event: check_config_element(event, "model"))
add_model_entry.bind("<Return>", lambda event: check_config_element(event, "model"))
add_model_entry.bind("<Tab>", lambda event: check_config_element(event, "model"))
add_model_entry.bind("<KP_Enter>", lambda event: check_config_element(event, "model"))

add_category_name_entry.bind("<<ComboboxSelected>>", lambda event: check_config_element(event, "category"))
add_category_name_entry.bind("<Return>", lambda event: check_config_element(event, "category"))
add_category_name_entry.bind("<Tab>", lambda event: check_config_element(event, "category"))
add_category_name_entry.bind("<KP_Enter>", lambda event: check_config_element(event, "category"))

add_user_name_entry.bind("<<ComboboxSelected>>", lambda event: check_config_element(event, "user"))
add_user_name_entry.bind("<Return>", lambda event: check_config_element(event, "user"))
add_user_name_entry.bind("<Tab>", lambda event: check_config_element(event, "user"))
add_user_name_entry.bind("<KP_Enter>", lambda event: check_config_element(event, "user"))

# -----------------------------------------------------------------------------------------------------------
# REPORT TAB WIDGETS
# -----------------------------------------------------------------------------------------------------------
report_tab_frame = ttk.Frame(report_tab, borderwidth=2, relief="sunken")
report_total_name = ttk.Label(report_tab_frame, text="Total de veículos:", font=font14)
report_total_value = ttk.Label(report_tab_frame, textvariable=report_total_vehicles, font=font14, borderwidth=3, relief="ridge", width=15, anchor=CENTER)
report_resp_name = ttk.Label(report_tab_frame, text="Responsável:", font=font14)
report_resp_entry = AutocompleteCombobox(report_tab_frame, width=15, font=font14, textvariable=report_resp_var, completevalues=get_users_from_parking())
report_open_veh_title = ttk.Label(report_tab_frame, text="Veículos em aberto:", font=font14)
report_finalized_veh_title = ttk.Label(report_tab_frame, text="Veículos finalizados:", font=font14)
report_canceled_veh_title = ttk.Label(report_tab_frame, text="Veículos desistêntes:", font=font14)
report_veh_name_1 = ttk.Label(report_tab_frame, text="CARRO", font=font14)
report_veh_name_2 = ttk.Label(report_tab_frame, text="SUV:", font=font14)
report_veh_name_3 = ttk.Label(report_tab_frame, text="MOTOCICLETA:", font=font14)
report_veh_name_4 = ttk.Label(report_tab_frame, text="CAMINHONETE:", font=font14)
report_veh_total = ttk.Label(report_tab_frame, text="TOTAL:", font=font14)
report_total_cash_title = ttk.Label(report_tab_frame, text="Total caixa:", font=font14)
report_total_cash_name = ttk.Label(report_tab_frame, text="Dinheiro:", font=font14)
report_total_cash_value = ttk.Label(report_tab_frame, textvariable=report_total_cash, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_total_card_name = ttk.Label(report_tab_frame, text="Cartão:", font=font14)
report_total_card_value = ttk.Label(report_tab_frame, textvariable=report_total_card, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_total_cashier_name = ttk.Label(report_tab_frame, text="Total:", font=font14)
report_total_cashier_value = ttk.Label(report_tab_frame, textvariable=report_total_cashier, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_total_add_name = ttk.Label(report_tab_frame, text="Acréscimos:", font=font14)
report_total_add_value = ttk.Label(report_tab_frame, textvariable=report_total_add, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_total_disc_name = ttk.Label(report_tab_frame, text="Descontos:", font=font14)
report_total_disc_value = ttk.Label(report_tab_frame, textvariable=report_total_discount, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_open_value_1 = ttk.Label(report_tab_frame, textvariable=report_total_open_vehicles_1, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_open_value_2 = ttk.Label(report_tab_frame, textvariable=report_total_open_vehicles_2, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_open_value_3 = ttk.Label(report_tab_frame, textvariable=report_total_open_vehicles_3, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_open_value_4 = ttk.Label(report_tab_frame, textvariable=report_total_open_vehicles_4, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_separator = ttk.Separator(report_tab_frame)
report_open_total_value = ttk.Label(report_tab_frame, textvariable=report_total_open_vehicles, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_finalized_value_1 = ttk.Label(report_tab_frame, textvariable=report_total_finalized_vehicles_1, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_finalized_value_2 = ttk.Label(report_tab_frame, textvariable=report_total_finalized_vehicles_2, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_finalized_value_3 = ttk.Label(report_tab_frame, textvariable=report_total_finalized_vehicles_3, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_finalized_value_4 = ttk.Label(report_tab_frame, textvariable=report_total_finalized_vehicles_4, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_finalized_total_value = ttk.Label(report_tab_frame, textvariable=report_total_finalized_vehicles, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_canceled_value_1 = ttk.Label(report_tab_frame, textvariable=report_total_canceled_vehicles_1, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_canceled_value_2 = ttk.Label(report_tab_frame, textvariable=report_total_canceled_vehicles_2, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_canceled_value_3 = ttk.Label(report_tab_frame, textvariable=report_total_canceled_vehicles_3, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_canceled_value_4 = ttk.Label(report_tab_frame, textvariable=report_total_canceled_vehicles_4, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_canceled_total_value = ttk.Label(report_tab_frame, textvariable=report_total_canceled_vehicles, font=font14, borderwidth=3, relief="groove", width=15, anchor=CENTER)
report_print_button = Button(
    report_tab_frame,
    text="Imprimir",
    command=print_report,
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
report_export_button = Button(
    report_tab_frame,
    text="Exportar",
    command=export_parking_to_csv,
    font=font14,
    bg="royalblue",
    fg="white",
    activebackground="coral1",
    activeforeground="black",
    width=12,
    cursor="hand2"
)
# -----------------------------------------------------------------------------------------------------------
# REPORT TAB LAYOUT
# -----------------------------------------------------------------------------------------------------------
report_tab_frame.place(x=20, y=20, anchor=NW, height=690, width=1260)
report_total_name.place(x=580, y=50, anchor=CENTER)
report_total_value.place(x=580, y=80, anchor=CENTER)
report_resp_name.place(x=880, y=50, anchor=CENTER)
report_resp_entry.place(x=880, y=80, anchor=CENTER)
report_open_veh_title.place(x=300, y=150, anchor=CENTER)
report_finalized_veh_title.place(x=580, y=150, anchor=CENTER)
report_canceled_veh_title.place(x=880, y=150, anchor=CENTER)
report_veh_name_1.place(x=190, y=200, anchor=NE)
report_veh_name_2.place(x=190, y=240, anchor=NE)
report_veh_name_3.place(x=190, y=280, anchor=NE)
report_veh_name_4.place(x=190, y=320, anchor=NE)
report_separator.place(x=100, y=355, width=900)
report_veh_total.place(x=190, y=370, anchor=NE)
report_total_cash_title.place(x=300, y=420, anchor=CENTER)
report_total_cash_name.place(x=190, y=450, anchor=NE)
report_total_cash_value.place(x=300, y=460, anchor=CENTER)
report_total_card_name.place(x=190, y=490, anchor=NE)
report_total_card_value.place(x=300, y=500, anchor=CENTER)
report_total_cashier_name.place(x=190, y=530, anchor=NE)
report_total_cashier_value.place(x=300, y=540, anchor=CENTER)
report_total_add_name.place(x=580, y=420, anchor=CENTER)
report_total_add_value.place(x=580, y=460, anchor=CENTER)
report_total_disc_name.place(x=880, y=420, anchor=CENTER)
report_total_disc_value.place(x=880, y=460, anchor=CENTER)
report_open_value_1.place(x=300, y=210, anchor=CENTER)
report_open_value_2.place(x=300, y=250, anchor=CENTER)
report_open_value_3.place(x=300, y=290, anchor=CENTER)
report_open_value_4.place(x=300, y=330, anchor=CENTER)
report_open_total_value.place(x=300, y=380, anchor=CENTER)
report_finalized_value_1.place(x=580, y=210, anchor=CENTER)
report_finalized_value_2.place(x=580, y=250, anchor=CENTER)
report_finalized_value_3.place(x=580, y=290, anchor=CENTER)
report_finalized_value_4.place(x=580, y=330, anchor=CENTER)
report_finalized_total_value.place(x=580, y=380, anchor=CENTER)
report_canceled_value_1.place(x=880, y=210, anchor=CENTER)
report_canceled_value_2.place(x=880, y=250, anchor=CENTER)
report_canceled_value_3.place(x=880, y=290, anchor=CENTER)
report_canceled_value_4.place(x=880, y=330, anchor=CENTER)
report_canceled_total_value.place(x=880, y=380, anchor=CENTER)
report_print_button.place(x=880, y=520, anchor=CENTER)
report_export_button.place(x=580, y=520, anchor=CENTER)
# -----------------------------------------------------------------------------------------------------------
# REPORT TAB COMMANDS
# -----------------------------------------------------------------------------------------------------------
report_resp_entry.bind("<<ComboboxSelected>>", lambda event: calc_report_metrics(event, report_resp_var.get()))
report_resp_entry.bind("<Return>", lambda event: calc_report_metrics(event, report_resp_var.get()))
report_resp_entry.bind("<Tab>", lambda event: calc_report_metrics(event, report_resp_var.get()))
report_resp_entry.bind("<KP_Enter>", lambda event: calc_report_metrics(event, report_resp_var.get()))
report_tab_frame.bind_all("<KeyPress-d>", set_checkbox_cash)

if __name__ == "__main__":
    open_printer_connection()
    global df_in, df_out
    df_in = get_today_parkings_as_df_in()
    df_out = get_today_parkings_as_df_out()
    mount_in_table()
    mount_out_table()
    # login_modal.destroy()
    root.mainloop()
    
