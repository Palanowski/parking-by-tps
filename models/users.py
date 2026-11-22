from datetime import datetime, date
from db.dal_connect import get_dal_mysql
from schemas.users import UsersModel


def get_all_users():
    with get_dal_mysql() as db:
        usersDB = db(db.users.ISactive==True).select(db.users.name).as_list()
        if usersDB:
            return [user["name"] for user in usersDB]


def get_user_by_id(userID):
    with get_dal_mysql() as db:
        user = db(db.users.name == userID).select().first()
    return user.as_dict() if user else False


def update_or_insert_user(userModel: UsersModel):
    with get_dal_mysql() as db:
        user = db(db.users.name==userModel.name).select().first()
        if user:
            db(db.users.name==userModel.name).update(**userModel.model_dump(exclude_unset=True))
        else:
            db.users.insert(**userModel.model_dump(exclude_unset=True))
    return True


def delete_user(userID):
    with get_dal_mysql() as db:
        user = db(db.users.name==userID).select().first()
        if user:
            db(db.users.name==userID).update(ISactive=False)
    return True

def log_in(userID):
    with get_dal_mysql() as db:
        db.log_in.insert(userID=userID)


def log_out(userID):
    with get_dal_mysql() as db:
        db(db.log_in.userID==userID).update(log_out=datetime.now())


def get_user_repC():
    with get_dal_mysql() as db:
        today = datetime.today()
        date = today.replace(day=today.day - 2)


def insert_users_repC(registers):
    with get_dal_mysql() as db:
        for item in registers:
            register = db(db.repc.created==item['created']).select(db.repc.ALL).first()
            if register:
                continue
            else:
                db.repc.insert(**item)


FUNCIONARIOS = {
    "08705432960":"EZEQUIEL GONCALVES DA ROSA",
    "08531537959":"GLEDSON OSNILDO DE SOUZA",
    "07377791950":"JHONATTAN DA SILVA MORAIS",
    "11469513960":"PABLO ROBERTO RAULINO",
    "13967582400":"ITALO RODRIGO DOS SANTOS BRITO"
}


def processar_registros_lidos(data):
        """Processa os registros retornados pelo REP"""
        registros = []
        
        # Dividir por linhas
        linhas = data.strip().split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha or (len(linha.split(' '))<=1):
                continue
            
            try:
                # Formato AFD 00000025232026-01-05T06:57:00-030011469513960 FBEA\r
                partes = linha.split('T')
                linha_data = partes[0][-10:]
                partes_2 = partes[1].split('-')
                linha_hora = partes_2[0]
                linha_reg_number = partes_2[1].split(' ')[0].replace('0300','').replace('I', '')

                # Formatar data/hora
                data_hora = f"{linha_data} {linha_hora}"
                
                registros.append({
                    'created': datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S"),
                    'name': FUNCIONARIOS[linha_reg_number]
                })
            except Exception as e:
                print(f"Erro ao processar linha: {linha} - {e}")
                continue
        
        return registros