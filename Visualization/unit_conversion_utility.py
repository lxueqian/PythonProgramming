import math


def degree_to_radian(deg):
    return deg/180.0*math.pi


def radian_to_degree(rad):
    return rad/math.pi*180.0


def radian_per_meter_to_degree_per_hundred_feet(val):
    return radian_to_degree(val) * 0.3048 * 100


def degree_per_hundred_feet_to_radian_per_meter(val):
    return degree_to_radian(val) / 0.3048 / 100


def radian_per_meter_to_degree_per_thirty_meters(val):
    return radian_to_degree(val) * 30.0


def degree_per_thirty_meters_to_radian_per_meter(val):
    return degree_to_radian(val) / 30.0


def foot_to_meter(val):
    return val*0.3048

def meter_to_foot(val):
    return val/0.3048

def meter_to_inch(val):
    return val/0.3048*12

def inch_to_meter(val):
    return val*0.3048/12

def newton_to_klbf(val):
    return val*0.0002248089

def klbf_to_newton(val):
    return val/0.0002248089

def newton_meter_to_klbf_foot(val):
    return val*0.0007375610332

def klbf_foot_to_newton_meter(val):
    return val/0.0007375610332

def ppg_to_kg_per_liter(val):
    return val*0.1198264273

def ppg_to_kg_per_cubic_meter(val):
    return val*119.82642732

def gpm_to_cubic_meter_per_second(val):
    return val*0.0000630902

def cubic_meter_per_second_to_gpm(val):
    return val/0.0000630902

def cubic_meter_per_second_to_liter_per_minute(val):
    return val*60000.0

def gpm_to_liter_per_minute(val):
    return val*3.785411784

def rpm_to_rad_per_second(val):
    return val*math.pi/30

def rad_per_second_to_rpm(val):
    return val/math.pi*30

def foot_per_hour_to_meter_per_second(val):
    return val*0.0000846667

def foot_per_hour_to_meter_per_hour(val):
    return val*0.3048

def meter_per_second_to_meter_per_hour(val):
    return val*3600.0

def meter_per_second_to_foot_per_hour(val):
    return val*3600.0/0.3048

def psi_to_pa(val):
    return val*6894.7572932

def pa_to_psi(val):
    return val/6894.7572932

def pound_to_kilogram(val):
    return val*0.4535924

def kilogram_to_pound(val):
    return val/0.4535924