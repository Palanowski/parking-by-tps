from models.parking import get_parkings_by_user_order_by_status


def total_open_vehicles_cat_1(userID: str = None):
    if userID:
        parkings = get_parkings_by_user_order_by_status(userID=userID, statusID="EM ABERTO")
    else:
        parkings = get_parkings_by_user_order_by_status(statusID="EM ABERTO")
    result = [parking for parking in parkings if parking["category"]=="1-CARRO"]
    return len(result)


def total_open_vehicles_cat_2(userID: str = None):
    if userID:
        parkings = get_parkings_by_user_order_by_status(userID=userID, statusID="EM ABERTO")
    else:
        parkings = get_parkings_by_user_order_by_status(statusID="EM ABERTO")
    result = [parking for parking in parkings if parking["category"]=="2-SUV"]
    return len(result)


def total_open_vehicles_cat_3(userID: str = None):
    if userID:
        parkings = get_parkings_by_user_order_by_status(userID=userID, statusID="EM ABERTO")
    else:
        parkings = get_parkings_by_user_order_by_status(statusID="EM ABERTO")
    result = [parking for parking in parkings if parking["category"]=="3-MOTO"]
    return len(result)


def total_open_vehicles_cat_4(userID: str = None):
    if userID:
        parkings = get_parkings_by_user_order_by_status(userID=userID, statusID="EM ABERTO")
    else:
        parkings = get_parkings_by_user_order_by_status(statusID="EM ABERTO")
    result = [parking for parking in parkings if parking["category"]=="4-CAMINHONETE"]
    return len(result)


def calc_metrics(parkings: list):
    total_cash_list = [parking["total_value"] for parking in parkings if parking["byCash"]==True]
    total_cash = sum(total_cash_list) if len(total_cash_list)>0 else 0
    total_card_list = [parking["total_value"] for parking in parkings if parking["total_value"] and (parking["byCash"]==False)]
    total_card = sum(total_card_list) if len(total_card_list)>0 else 0
    total_cashier = sum([total_cash, total_card])
    total_add_list = [parking["addition"] for parking in parkings if parking["addition"]]
    total_add = sum(total_add_list) if len(total_add_list)>0 else 0
    total_discount_list = [parking["discount"] for parking in parkings if parking["discount"]]
    total_discount = sum(total_discount_list) if len(total_discount_list)>0 else 0
    open_vehicles = [parking for parking in parkings if parking["status"]in["EM ABERTO", "RETORNO"]]
    open_vehicles_cat_1 = [parking for parking in open_vehicles if parking["category"]=="1-CARRO"]
    open_vehicles_cat_2 = [parking for parking in open_vehicles if parking["category"]=="2-SUV"]
    open_vehicles_cat_3 = [parking for parking in open_vehicles if parking["category"]=="3-MOTO"]
    open_vehicles_cat_4 = [parking for parking in open_vehicles if parking["category"]=="4-CAMINHONETE"]
    finalized_vehicles = [parking for parking in parkings if parking["status"]=="FINALIZADO"]
    finalized_vehicles_cat_1 = [parking for parking in finalized_vehicles if parking["category"]=="1-CARRO"]
    finalized_vehicles_cat_2 = [parking for parking in finalized_vehicles if parking["category"]=="2-SUV"]
    finalized_vehicles_cat_3 = [parking for parking in finalized_vehicles if parking["category"]=="3-MOTO"]
    finalized_vehicles_cat_4 = [parking for parking in finalized_vehicles if parking["category"]=="4-CAMINHONETE"]
    canceled_vehicles = [parking for parking in parkings if parking["status"]=="CANCELADO"]
    canceled_vehicles_cat_1 = [parking for parking in canceled_vehicles if parking["category"]=="1-CARRO"]
    canceled_vehicles_cat_2 = [parking for parking in canceled_vehicles if parking["category"]=="2-SUV"]
    canceled_vehicles_cat_3 = [parking for parking in canceled_vehicles if parking["category"]=="3-MOTO"]
    canceled_vehicles_cat_4 = [parking for parking in canceled_vehicles if parking["category"]=="4-CAMINHONETE"]
    return dict(
        total_count=len(parkings),
        total_cashier=total_cashier,
        total_cash=total_cash,
        total_card=total_card,
        total_add=total_add,
        total_discount=total_discount,
        total_open_vehicles=len(open_vehicles),
        total_open_cat_1=len(open_vehicles_cat_1),
        total_open_cat_2=len(open_vehicles_cat_2),
        total_open_cat_3=len(open_vehicles_cat_3),
        total_open_cat_4=len(open_vehicles_cat_4),
        total_finalized_vehicles=len(finalized_vehicles),
        total_finalized_cat_1=len(finalized_vehicles_cat_1),
        total_finalized_cat_2=len(finalized_vehicles_cat_2),
        total_finalized_cat_3=len(finalized_vehicles_cat_3),
        total_finalized_cat_4=len(finalized_vehicles_cat_4),
        total_canceled_vehicles=len(canceled_vehicles),
        total_canceled_cat_1=len(canceled_vehicles_cat_1),
        total_canceled_cat_2=len(canceled_vehicles_cat_2),
        total_canceled_cat_3=len(canceled_vehicles_cat_3),
        total_canceled_cat_4=len(canceled_vehicles_cat_4),
    )
