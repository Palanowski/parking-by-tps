import pandas as pd

from datetime import datetime
from db.dal_connect import get_dal_mysql
from schemas.parking import ParkingModel

def check_plate(plateID):
    with get_dal_mysql() as db:
        park = db(
            (db.parking.plate == plateID)
            & (db.parking.entry_date == datetime.now().date())
            ).select().first()
    return False if park else True


def post_parking(parkingModel: ParkingModel):
    with get_dal_mysql() as db:
        new = db.parking.insert(**parkingModel.model_dump())
    return new


def get_today_parkings_as_df_in():
    with get_dal_mysql() as db:
        parkings = db(db.parking.entry_date == datetime.now().date()).select(
            db.parking.plate,
            db.parking.model,
            db.parking.category,
            db.parking.color,
            db.parking.entry_time,
            db.parking.exit_time,
            db.parking.delta_time,
            db.parking.status,
            db.parking.total_value,
            db.parking.entry_user,
            db.parking.exit_user,
            db.parking.discount,
            db.parking.addition,
        ).as_list()
    return pd.DataFrame.from_records(parkings)

def get_today_parkings_as_df_out():
    with get_dal_mysql() as db:
        parkings = db(
            (db.parking.entry_date == datetime.now().date()) 
            & (db.parking.status == "FINALIZADO")
        ).select(
            db.parking.plate,
            db.parking.model,
            db.parking.exit_time,
            db.parking.delta_time,
            db.parking.total_value,
        ).as_list()
    return pd.DataFrame.from_records(parkings)


def get_parking_by_plate(plateID):
    with get_dal_mysql() as db:
        parking = db(
            (db.parking.plate==plateID)
            & (db.parking.entry_date==datetime.now().date())
        ).select().first()
        if parking:
            result = parking.as_dict()
        else:
            result = False
    return result


def get_parking_by_code(barcode):
    with get_dal_mysql() as db:
        parking = db(
            (db.parking.barcode==barcode)
            & (db.parking.entry_date==datetime.now().date())
        ).select().first()
        if parking:
            result = parking.as_dict()
        else:
            result = False
    return result


def get_total_open_parking():
    with get_dal_mysql() as db:
        return db(
            (db.parking.status=="EM ABERTO")
            & (db.parking.entry_date==datetime.now().date())
        ).count()

def finalize_parking(plateID, delta_time, userID, total, addition=None, discount=None, byPlate=None):
    with get_dal_mysql() as db:
        exit_time = datetime.now().time()
        db((db.parking.plate == plateID) & (db.parking.entry_date == datetime.now().date())).update(
            exit_user=userID,
            exit_time=exit_time,
            delta_time=delta_time,
            total_value=total,
            status="FINALIZADO",
            addition=addition,
            discount=discount,
            byPlate=byPlate,
        )


def cancel_parking(plateID):
    with get_dal_mysql() as db:
        db(
            (db.parking.plate == plateID)
            & (db.parking.entry_date==datetime.now().date())
        ).update(exit_time=datetime.now().time(), status="CANCELADO")


def return_parking(plateID):
    with get_dal_mysql() as db:
        db(
            (db.parking.plate == plateID)
            & (db.parking.entry_date==datetime.now().date())
        ).update(ISreturn=True, status="RETORNO")
