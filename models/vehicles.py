from db.dal_connect import get_dal_mysql
from schemas.vehicles import VehicleModel


def get_all_vehicles():
    with get_dal_mysql() as db:
        vehicles = db().select(db.vehicles.ALL).as_list()
    plate_list = list()
    if vehicles:
        for vehicle in vehicles:
            plate_list.append(vehicle["plate"])
    return plate_list


def get_vehicle_by_id(vehicleID):
    with get_dal_mysql() as db:
        vehicle = db(db.vehicles.id==vehicleID).select().first()
    return vehicle.as_dict() if vehicle else False


def get_vehicle_by_plate(vehicle_plate):
    with get_dal_mysql() as db:
        vehicle = db(db.vehicles.plate==vehicle_plate).select()
    return vehicle.as_list() if vehicle else False


def create_vehicle(vehicleModel: VehicleModel):
    with get_dal_mysql() as db:
        vehicle = db(
            (db.vehicles.plate==vehicleModel.plate)
            & (db.vehicles.model==vehicleModel.model)
        ).select().first()
        if not vehicle:
            db.vehicles.insert(**vehicleModel.model_dump())
    return True


def update_vehicle(vehicleModel: VehicleModel):
    with get_dal_mysql() as db:
        vehicle = db(
            (db.vehicles.plate==vehicleModel.plate)
            & (db.vehicles.model==vehicleModel.model)
        ).select().first()
        if vehicle:
            db(
                (db.vehicles.plate==vehicleModel.plate)
                & (db.vehicles.model==vehicleModel.model)
            ).update(**vehicleModel.model_dump())
    return True


def delete_vehicle(vehicle_plate, vehicle_model):
    with get_dal_mysql() as db:
        vehicle = db(
            (db.vehicles.plate==vehicle_plate)
            & (db.vehicles.model==vehicle_model)).select().first()
        if vehicle:
            db(db.vehicles.id == vehicle["id"]).delete()
    return True
