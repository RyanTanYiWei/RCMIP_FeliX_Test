"""
Python model 'ClimateModule.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import ramp, if_then_else
from pysd.py_backend.statefuls import Smooth, Integ, Initial
from pysd.py_backend.lookups import HardcodedLookups
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 1900,
    "final_time": lambda: 2100,
    "time_step": lambda: 0.125,
    "saveper": lambda: 1,
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Year",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Year",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name='"2xCO2 Forcing"',
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"co2_radiative_forcing_coefficient": 1},
)
def nvs_2xco2_forcing():
    """
    Radiative forcing at 2x CO2 equivalent.
    """
    return co2_radiative_forcing_coefficient() * float(np.log(2))


@component.add(
    name="a N2O",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c1": 1, "atmospheric_concentration_n2o": 1, "dmnl_adjustment_ppb": 1},
)
def a_n2o():
    return c1() * float(
        np.sqrt(atmospheric_concentration_n2o() * dmnl_adjustment_ppb())
    )


@component.add(
    name="a prime",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "atmospheric_concentration_co2": 4,
        "c_a_max": 1,
        "d1": 3,
        "b1": 2,
        "a1": 2,
        "atmospheric_co2_concentration_preindustrial": 3,
    },
)
def a_prime():
    return if_then_else(
        atmospheric_concentration_co2() > c_a_max(),
        lambda: d1() - b1() ** 2 / (4 * a1()),
        lambda: if_then_else(
            atmospheric_concentration_co2()
            < atmospheric_co2_concentration_preindustrial(),
            lambda: d1(),
            lambda: d1()
            + a1()
            * (
                atmospheric_concentration_co2()
                - atmospheric_co2_concentration_preindustrial()
            )
            ** 2
            + b1()
            * (
                atmospheric_concentration_co2()
                - atmospheric_co2_concentration_preindustrial()
            ),
        ),
    )


@component.add(
    name="a1", units="W/(m*m*ppm*ppm)", comp_type="Constant", comp_subtype="Normal"
)
def a1():
    return -2.4785e-07


@component.add(name="a2", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def a2():
    return -0.00034197


@component.add(name="a3", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def a3():
    return -8.9603e-05


@component.add(
    name="Area", units="Meter*Meter", comp_type="Constant", comp_subtype="Normal"
)
def area():
    """
    Global surface area.
    """
    return 510000000000000.0


@component.add(
    name="Atmospheric and Upper Ocean Heat Capacity",
    units="Year*W/(Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"upper_layer_volume_vu": 1, "volumetric_heat_capacity": 1, "area": 1},
)
def atmospheric_and_upper_ocean_heat_capacity():
    """
    Volumetric heat capacity for the land, atmosphere, and, upper ocean layer.
    """
    return upper_layer_volume_vu() * volumetric_heat_capacity() / area()


@component.add(
    name="Atmospheric CH4 Concentration 1850 AR6",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_ch4_concentration_1850_ar6():
    """
    https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_AnnexIII.p df pg 2141
    """
    return 808


@component.add(
    name="Atmospheric CH4 Concentration Preindustrial",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_ch4_concentration_preindustrial():
    return 731.41


@component.add(
    name="Atmospheric CO2 Concentration 1850 AR6",
    units="ppm",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_co2_concentration_1850_ar6():
    return 285.5


@component.add(
    name="Atmospheric CO2 Concentration Preindustrial",
    units="ppm",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_co2_concentration_preindustrial():
    """
    Meinhausen et al 2020
    """
    return 277.15


@component.add(
    name="Atmospheric CO2 Law Dome 1850",
    units="ppm",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_co2_law_dome_1850():
    """
    Historical CO2 record derived from a spline fit (20 year cutoff) of the Law Dome DE08 and DE08-2 ice cores for year 1850 https://www.ncei.noaa.gov/pub/data/paleo/icecore/antarctica/law/law_co2.txt
    """
    return 284.7


@component.add(
    name="Atmospheric Concentration CH4",
    units="ppb",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ch4_in_atmosphere": 1, "tonch4_to_ppb": 1},
)
def atmospheric_concentration_ch4():
    return ch4_in_atmosphere() * tonch4_to_ppb()


@component.add(
    name="Atmospheric Concentration CO2",
    units="ppm",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_atmosphere": 1, "gtc_to_tonc": 1, "ppm_to_gtc": 1},
)
def atmospheric_concentration_co2():
    """
    Converts weight of CO2 in atmosphere to concentration (ppm CO2). Source of Historical Data: Etheridge, D.M., Steele, L.P., Langenfelds, R.L., Francey, R.J., Barnola, J.-M., Morgan, V.I. 1998. Historical CO2 records from the Law Dome DE08, DE08-2, and DSS ice cores. In Trends: A Compendium of Data on Global Change. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, U.S. Department of Energy, Oak Ridge, Tenn., U.S.A
    """
    return c_in_atmosphere() / gtc_to_tonc() / ppm_to_gtc()


@component.add(
    name="Atmospheric Concentration N2O",
    units="ppb",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"n2o_in_atmosphere": 1, "tonn2o_to_ppb": 1},
)
def atmospheric_concentration_n2o():
    return n2o_in_atmosphere() * tonn2o_to_ppb()


@component.add(
    name="Atmospheric Lifetime of CH4",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_lifetime_of_ch4():
    """
    9-12 Years
    """
    return 9


@component.add(
    name="Atmospheric Lifetime of N2O",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_lifetime_of_n2o():
    return 116


@component.add(
    name="Atmospheric N2O Concentration 1850 AR6",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_n2o_concentration_1850_ar6():
    """
    https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_AnnexIII.p df pg 2141
    """
    return 273.2


@component.add(
    name="Atmospheric N2O Concentration Preindustrial",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_n2o_concentration_preindustrial():
    """
    Mein
    """
    return 273.87


@component.add(
    name="b1", units="W/(m*m*ppm)", comp_type="Constant", comp_subtype="Normal"
)
def b1():
    return 0.00075906


@component.add(name="b2", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def b2():
    return 0.00025455


@component.add(name="b3", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def b3():
    return -0.00012462


@component.add(
    name="Biomass Res Time", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def biomass_res_time():
    """
    Average residence time of carbon in biomass.
    """
    return 10.6


@component.add(
    name="Biostimulation Coefficient",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def biostimulation_coefficient():
    """
    Coefficient for response of primary production to carbon concentration.
    """
    return 0.35


@component.add(
    name="Buff C Coeff", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def buff_c_coeff():
    """
    Coefficient of carbon concentration influence on buffer factor.
    """
    return 3.92


@component.add(
    name="Buffer Factor",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ref_buffer_factor": 1,
        "preindustrial_c_in_mixed_layer": 1,
        "c_in_mixed_layer": 1,
        "buff_c_coeff": 1,
    },
)
def buffer_factor():
    """
    Buffer factor for atmosphere/mixed ocean carbon equilibration.
    """
    return (
        ref_buffer_factor()
        * (c_in_mixed_layer() / preindustrial_c_in_mixed_layer()) ** buff_c_coeff()
    )


@component.add(
    name="C a max",
    units="ppm",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"atmospheric_co2_concentration_preindustrial": 1, "b1": 1, "a1": 1},
)
def c_a_max():
    return atmospheric_co2_concentration_preindustrial() - b1() / (2 * a1())


@component.add(
    name="C Concentration Ratio",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_atmosphere": 1, "init_c_in_atmosphere": 1},
)
def c_concentration_ratio():
    """
    Current to initial carbon concentration in atmosphere.
    """
    return c_in_atmosphere() / init_c_in_atmosphere()


@component.add(
    name="C in Atmosphere",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_atmosphere": 1},
    other_deps={
        "_integ_c_in_atmosphere": {
            "initial": {"init_c_in_atmosphere": 1},
            "step": {
                "flux_biomass_to_atmosphere": 1,
                "flux_humus_to_atmosphere": 1,
                "total_c_emission": 1,
                "carbon_removal_rate": 2,
                "flux_atmosphere_to_biomass": 1,
                "flux_atmosphere_to_ocean": 1,
            },
        }
    },
)
def c_in_atmosphere():
    """
    Carbon in atmosphere.
    """
    return _integ_c_in_atmosphere()


_integ_c_in_atmosphere = Integ(
    lambda: flux_biomass_to_atmosphere()
    + flux_humus_to_atmosphere()
    + total_c_emission()
    - carbon_removal_rate()
    - flux_atmosphere_to_biomass()
    - flux_atmosphere_to_ocean()
    - carbon_removal_rate(),
    lambda: init_c_in_atmosphere(),
    "_integ_c_in_atmosphere",
)


@component.add(
    name="C in Biomass",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_biomass": 1},
    other_deps={
        "_integ_c_in_biomass": {
            "initial": {"init_c_in_biomass": 1},
            "step": {
                "flux_atmosphere_to_biomass": 1,
                "flux_biomass_to_atmosphere": 1,
                "flux_biomass_to_humus": 1,
            },
        }
    },
)
def c_in_biomass():
    """
    Carbon in biosphere (biomass, litter, and humus)
    """
    return _integ_c_in_biomass()


_integ_c_in_biomass = Integ(
    lambda: flux_atmosphere_to_biomass()
    - flux_biomass_to_atmosphere()
    - flux_biomass_to_humus(),
    lambda: init_c_in_biomass(),
    "_integ_c_in_biomass",
)


@component.add(
    name="C in Deep Ocean 1",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_deep_ocean_1": 1},
    other_deps={
        "_integ_c_in_deep_ocean_1": {
            "initial": {"init_c_in_deep_ocean_1": 1},
            "step": {"diffusion_flux_1": 1, "diffusion_flux_2": 1},
        }
    },
)
def c_in_deep_ocean_1():
    """
    Carbon in the first layer of deep ocean.
    """
    return _integ_c_in_deep_ocean_1()


_integ_c_in_deep_ocean_1 = Integ(
    lambda: diffusion_flux_1() - diffusion_flux_2(),
    lambda: init_c_in_deep_ocean_1(),
    "_integ_c_in_deep_ocean_1",
)


@component.add(
    name="C in Deep Ocean 1 per meter",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_deep_ocean_1": 1, "layer_depth_1": 1},
)
def c_in_deep_ocean_1_per_meter():
    """
    Carbon in the first ocean layer per its meter.
    """
    return c_in_deep_ocean_1() / layer_depth_1()


@component.add(
    name="C in Deep Ocean 2",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_deep_ocean_2": 1},
    other_deps={
        "_integ_c_in_deep_ocean_2": {
            "initial": {"init_c_in_deep_ocean_2": 1},
            "step": {"diffusion_flux_2": 1, "diffusion_flux_3": 1},
        }
    },
)
def c_in_deep_ocean_2():
    """
    Carbon in the second layer of deep ocean.
    """
    return _integ_c_in_deep_ocean_2()


_integ_c_in_deep_ocean_2 = Integ(
    lambda: diffusion_flux_2() - diffusion_flux_3(),
    lambda: init_c_in_deep_ocean_2(),
    "_integ_c_in_deep_ocean_2",
)


@component.add(
    name="C in Deep Ocean 2 per meter",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_deep_ocean_2": 1, "layer_depth_2": 1},
)
def c_in_deep_ocean_2_per_meter():
    """
    Carbon in the second ocean layer per its meter.
    """
    return c_in_deep_ocean_2() / layer_depth_2()


@component.add(
    name="C in Deep Ocean 3",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_deep_ocean_3": 1},
    other_deps={
        "_integ_c_in_deep_ocean_3": {
            "initial": {"init_c_in_deep_ocean_3": 1},
            "step": {"diffusion_flux_3": 1, "diffusion_flux_4": 1},
        }
    },
)
def c_in_deep_ocean_3():
    """
    Carbon in the third layer of deep ocean.
    """
    return _integ_c_in_deep_ocean_3()


_integ_c_in_deep_ocean_3 = Integ(
    lambda: diffusion_flux_3() - diffusion_flux_4(),
    lambda: init_c_in_deep_ocean_3(),
    "_integ_c_in_deep_ocean_3",
)


@component.add(
    name="C in Deep Ocean 3 per meter",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_deep_ocean_3": 1, "layer_depth_3": 1},
)
def c_in_deep_ocean_3_per_meter():
    """
    Carbon in the third ocean layer per its meter.
    """
    return c_in_deep_ocean_3() / layer_depth_3()


@component.add(
    name="C in Deep Ocean 4",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_deep_ocean_4": 1},
    other_deps={
        "_integ_c_in_deep_ocean_4": {
            "initial": {"init_c_in_deep_ocean_4": 1},
            "step": {"diffusion_flux_4": 1},
        }
    },
)
def c_in_deep_ocean_4():
    """
    Carbon in the fourth layer of deep ocean.
    """
    return _integ_c_in_deep_ocean_4()


_integ_c_in_deep_ocean_4 = Integ(
    lambda: diffusion_flux_4(),
    lambda: init_c_in_deep_ocean_4(),
    "_integ_c_in_deep_ocean_4",
)


@component.add(
    name="C in Deep Ocean 4 per meter",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_deep_ocean_4": 1, "layer_depth_4": 1},
)
def c_in_deep_ocean_4_per_meter():
    """
    Carbon in the fourth ocean layer per its meter.
    """
    return c_in_deep_ocean_4() / layer_depth_4()


@component.add(
    name="C in Humus",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_humus": 1},
    other_deps={
        "_integ_c_in_humus": {
            "initial": {"init_c_in_humus": 1},
            "step": {"flux_biomass_to_humus": 1, "flux_humus_to_atmosphere": 1},
        }
    },
)
def c_in_humus():
    """
    Carbon in humus.
    """
    return _integ_c_in_humus()


_integ_c_in_humus = Integ(
    lambda: flux_biomass_to_humus() - flux_humus_to_atmosphere(),
    lambda: init_c_in_humus(),
    "_integ_c_in_humus",
)


@component.add(
    name="C in Mixed Layer",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_mixed_layer": 1},
    other_deps={
        "_integ_c_in_mixed_layer": {
            "initial": {"init_c_in_mixed_ocean": 1},
            "step": {"flux_atmosphere_to_ocean": 1, "diffusion_flux_1": 1},
        }
    },
)
def c_in_mixed_layer():
    """
    Carbon in mixed layer.
    """
    return _integ_c_in_mixed_layer()


_integ_c_in_mixed_layer = Integ(
    lambda: flux_atmosphere_to_ocean() - diffusion_flux_1(),
    lambda: init_c_in_mixed_ocean(),
    "_integ_c_in_mixed_layer",
)


@component.add(
    name="C in Mixed Layer per meter",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_mixed_layer": 1, "mixed_layer_depth": 1},
)
def c_in_mixed_layer_per_meter():
    """
    Carbon in mixed layer per its meter.
    """
    return c_in_mixed_layer() / mixed_layer_depth()


@component.add(name="c1", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def c1():
    """
    *note: units is supposed to be W m-2 ppb-0.5 due to the sqrt in N, but here it's simplified to remove the ppb
    """
    return -0.0021492


@component.add(name="c2", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def c2():
    return -0.00024357


@component.add(
    name="Carbon Removal Impact Slope", comp_type="Constant", comp_subtype="Normal"
)
def carbon_removal_impact_slope():
    return 1.1


@component.add(
    name="Carbon Removal Rate",
    units="TonC/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"climate_policy_scenario": 1, "_smooth_carbon_removal_rate": 1},
    other_deps={
        "_smooth_carbon_removal_rate": {
            "initial": {
                "reference_co2_removal_rate": 1,
                "climate_action_year": 1,
                "time": 1,
            },
            "step": {
                "reference_co2_removal_rate": 1,
                "climate_action_year": 1,
                "time": 1,
                "cdr_policy_transition_period": 1,
            },
        }
    },
)
def carbon_removal_rate():
    """
    Climate Policy Scenario*SMOOTH(STEP(Carbon Removal Impact Slope*Reference Removal Rate, Climate Action Year), Climate Policy Transition Period)
    """
    return climate_policy_scenario() * _smooth_carbon_removal_rate()


_smooth_carbon_removal_rate = Smooth(
    lambda: ramp(
        __data["time"], reference_co2_removal_rate(), climate_action_year(), 2100
    ),
    lambda: cdr_policy_transition_period(),
    lambda: ramp(
        __data["time"], reference_co2_removal_rate(), climate_action_year(), 2100
    ),
    lambda: 1,
    "_smooth_carbon_removal_rate",
)


@component.add(
    name="CDR Policy Transition Period",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def cdr_policy_transition_period():
    return 1


@component.add(
    name="CH4 Concentration Ratio",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ch4_in_atmosphere": 1, "init_ch4_in_atmosphere": 1},
)
def ch4_concentration_ratio():
    return ch4_in_atmosphere() / init_ch4_in_atmosphere()


@component.add(
    name="CH4 in Atmosphere",
    units="TonCH4",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ch4_in_atmosphere": 1},
    other_deps={
        "_integ_ch4_in_atmosphere": {
            "initial": {"init_ch4_in_atmosphere": 1},
            "step": {"total_ch4_emission": 1, "total_ch4_breakdown": 1},
        }
    },
)
def ch4_in_atmosphere():
    return _integ_ch4_in_atmosphere()


_integ_ch4_in_atmosphere = Integ(
    lambda: total_ch4_emission() - total_ch4_breakdown(),
    lambda: init_ch4_in_atmosphere(),
    "_integ_ch4_in_atmosphere",
)


@component.add(
    name="CH4 Radiative Efficiency",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "a3": 1,
        "dmnl_adjustment_ppb": 2,
        "atmospheric_concentration_ch4": 1,
        "atmospheric_concentration_n2o": 1,
        "b3": 1,
        "d3": 1,
    },
)
def ch4_radiative_efficiency():
    """
    Meinshausen et al 2020
    """
    return (
        a3() * float(np.sqrt(atmospheric_concentration_ch4() * dmnl_adjustment_ppb()))
        + b3() * float(np.sqrt(atmospheric_concentration_n2o() * dmnl_adjustment_ppb()))
        + d3()
    )


@component.add(
    name="CH4 Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "ch4_radiative_forcing_history": 1,
        "ch4_radiative_forcing_rcp26": 1,
        "ch4_radiative_forcing_rcp85": 1,
        "ch4_radiative_forcing_rcp45": 1,
        "rcp_scenario": 5,
        "ch4_radiative_forcing_rcp34": 1,
        "ch4_radiative_forcing_rcp60": 1,
        "ch4_radiative_forcing_rcp19": 1,
    },
)
def ch4_radiative_forcing():
    """
    Radiative forcing from CH4 in the atmosphere.
    """
    return if_then_else(
        time() <= 2010,
        lambda: ch4_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 0,
            lambda: ch4_radiative_forcing_rcp19(),
            lambda: if_then_else(
                rcp_scenario() == 1,
                lambda: ch4_radiative_forcing_rcp26(),
                lambda: if_then_else(
                    rcp_scenario() == 2,
                    lambda: ch4_radiative_forcing_rcp34(),
                    lambda: if_then_else(
                        rcp_scenario() == 3,
                        lambda: ch4_radiative_forcing_rcp45(),
                        lambda: if_then_else(
                            rcp_scenario() == 4,
                            lambda: ch4_radiative_forcing_rcp60(),
                            lambda: ch4_radiative_forcing_rcp85(),
                        ),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="CH4 Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "dimensionless_time": 1, "table_ch4_radiative_forcing": 1},
)
def ch4_radiative_forcing_history():
    """
    Historical data for radiative forcing from CH4 in the atmosphere.
    """
    return table_ch4_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing New",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ch4_radiative_efficiency": 1,
        "dmnl_adjustment_ppb": 2,
        "atmospheric_concentration_ch4": 1,
        "atmospheric_ch4_concentration_preindustrial": 1,
    },
)
def ch4_radiative_forcing_new():
    return ch4_radiative_efficiency() * (
        float(np.sqrt(atmospheric_concentration_ch4() * dmnl_adjustment_ppb()))
        - float(
            np.sqrt(
                atmospheric_ch4_concentration_preindustrial() * dmnl_adjustment_ppb()
            )
        )
    )


@component.add(
    name="CH4 Radiative Forcing RCP19",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp19": 1,
    },
)
def ch4_radiative_forcing_rcp19():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 1.9).
    """
    return table_ch4_radiative_forcing_ssp2_rcp19(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp26": 1,
    },
)
def ch4_radiative_forcing_rcp26():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 2.6).
    """
    return table_ch4_radiative_forcing_ssp2_rcp26(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing RCP34",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp34": 1,
    },
)
def ch4_radiative_forcing_rcp34():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_ch4_radiative_forcing_ssp2_rcp34(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp45": 1,
    },
)
def ch4_radiative_forcing_rcp45():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 4.5).
    """
    return table_ch4_radiative_forcing_ssp2_rcp45(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp60": 1,
    },
)
def ch4_radiative_forcing_rcp60():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return table_ch4_radiative_forcing_ssp2_rcp60(time() * dimensionless_time())


@component.add(
    name="CH4 Radiative Forcing RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_ch4_radiative_forcing_ssp2_rcp85": 1,
    },
)
def ch4_radiative_forcing_rcp85():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_ch4_radiative_forcing_ssp2_rcp85(time() * dimensionless_time())


@component.add(
    name="CH4 to CO2 via Oxidation in TonCO2",
    units="TonCO2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "molar_mass_of_co2": 1,
        "molar_mass_of_ch4": 1,
        "dmnl_adjustment_tonco2": 1,
        "total_ch4_breakdown": 1,
    },
)
def ch4_to_co2_via_oxidation_in_tonco2():
    return (
        molar_mass_of_co2() / molar_mass_of_ch4() / dmnl_adjustment_tonco2()
    ) * total_ch4_breakdown()


@component.add(
    name="Climate Action Year",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def climate_action_year():
    return 2020


@component.add(
    name="Climate Feedback Parameter",
    units="Watt/(Meter*Meter)/DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"nvs_2xco2_forcing": 1, "climate_sensitivity_to_2xco2": 1},
)
def climate_feedback_parameter():
    """
    Determines feedback effect from temperature increase.
    """
    return nvs_2xco2_forcing() / climate_sensitivity_to_2xco2()


@component.add(
    name="Climate Policy Scenario",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def climate_policy_scenario():
    """
    0: No climate policy 1: Climate policy
    """
    return 0


@component.add(
    name="Climate Sensitivity to 2xCO2",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def climate_sensitivity_to_2xco2():
    """
    Equilibrium temperature change in response to a 2xCO2 equivalent change in radiative forcing. Deterministic = 3, Low=2, High =4.5.
    """
    return 3


@component.add(
    name="CO2 Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def co2_radiative_forcing_aim_rcp60():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by AIM (RCP 6.0).
    """
    return 0


@component.add(
    name="CO2 Radiative Forcing Coefficient",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"a_prime": 1, "a_n2o": 1},
)
def co2_radiative_forcing_coefficient():
    return a_prime() + a_n2o()


@component.add(
    name="CO2 Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def co2_radiative_forcing_image_rcp26():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by IMAGE (RCP 2.6).
    """
    return 0


@component.add(
    name="CO2 Radiative Forcing Indicator",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"co2_radiative_forcing_new": 1},
)
def co2_radiative_forcing_indicator():
    return co2_radiative_forcing_new()


@component.add(
    name="CO2 Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def co2_radiative_forcing_message_rcp85():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return 0


@component.add(
    name="CO2 Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def co2_radiative_forcing_minicam_rcp45():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MiniCAM (RCP 4.5).
    """
    return 0


@component.add(
    name="CO2 Radiative Forcing New",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "co2_radiative_forcing_coefficient": 1,
        "atmospheric_co2_concentration_preindustrial": 1,
        "atmospheric_concentration_co2": 1,
    },
)
def co2_radiative_forcing_new():
    """
    Radiative forcing from CO2 in the atmosphere. Source of Historical Data: IIASA RCP Database https://tntcat.iiasa.ac.at:8743/RcpDb/dsd?Action=htmlpage&page=welcome
    """
    return co2_radiative_forcing_coefficient() * float(
        np.log(
            atmospheric_concentration_co2()
            / atmospheric_co2_concentration_preindustrial()
        )
    )


@component.add(
    name="CO2 to C", units="TonCO2/TonC", comp_type="Constant", comp_subtype="Normal"
)
def co2_to_c():
    return 3.664


@component.add(
    name="Current year", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def current_year():
    return 2023


@component.add(name="d1", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def d1():
    return 5.2488


@component.add(name="d2", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def d2():
    return 0.012173


@component.add(name="d3", units="W/(m*m)", comp_type="Constant", comp_subtype="Normal")
def d3():
    return 0.045194


@component.add(
    name="Deep Ocean 1 Heat Capacity",
    units="Year*W/(Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"lower_layer_volume_vu_1": 1, "volumetric_heat_capacity": 1, "area": 1},
)
def deep_ocean_1_heat_capacity():
    """
    Volumetric heat capacity for the first layer of the deep ocean.
    """
    return lower_layer_volume_vu_1() * volumetric_heat_capacity() / area()


@component.add(
    name="Deep Ocean 2 Heat Capacity",
    units="Year*W/(Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"lower_layer_volume_vu_2": 1, "volumetric_heat_capacity": 1, "area": 1},
)
def deep_ocean_2_heat_capacity():
    """
    Volumetric heat capacity for the second layer of the deep ocean.
    """
    return lower_layer_volume_vu_2() * volumetric_heat_capacity() / area()


@component.add(
    name="Deep Ocean 3 Heat Capacity",
    units="Year*W/(Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"lower_layer_volume_vu_3": 1, "volumetric_heat_capacity": 1, "area": 1},
)
def deep_ocean_3_heat_capacity():
    """
    Volumetric heat capacity for the third layer of the deep ocean.
    """
    return lower_layer_volume_vu_3() * volumetric_heat_capacity() / area()


@component.add(
    name="Deep Ocean 4 Heat Capacity",
    units="Year*W/(Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"lower_layer_volume_vu_4": 1, "volumetric_heat_capacity": 1, "area": 1},
)
def deep_ocean_4_heat_capacity():
    """
    Volumetric heat capacity for the fourth layer of the deep ocean.
    """
    return lower_layer_volume_vu_4() * volumetric_heat_capacity() / area()


@component.add(
    name="Density", units="kg/(m*m*m)", comp_type="Constant", comp_subtype="Normal"
)
def density():
    """
    Density of water, i.e., mass per volume of water.
    """
    return 1000


@component.add(
    name="Diffusion Flux 1",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_mixed_layer_per_meter": 1,
        "c_in_deep_ocean_1_per_meter": 1,
        "eddy_diff_coeff_m_1": 1,
        "mean_depth_of_adjacent_m_1_layers": 1,
    },
)
def diffusion_flux_1():
    """
    Diffusion flux between mixed and the first ocean layers.
    """
    return (
        (c_in_mixed_layer_per_meter() - c_in_deep_ocean_1_per_meter())
        * eddy_diff_coeff_m_1()
        / mean_depth_of_adjacent_m_1_layers()
    )


@component.add(
    name="Diffusion Flux 2",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_deep_ocean_1_per_meter": 1,
        "c_in_deep_ocean_2_per_meter": 1,
        "eddy_diff_coeff_1_2": 1,
        "mean_depth_of_adjacent_1_2_layers": 1,
    },
)
def diffusion_flux_2():
    """
    Diffusion flux between the first and the second ocean layers.
    """
    return (
        (c_in_deep_ocean_1_per_meter() - c_in_deep_ocean_2_per_meter())
        * eddy_diff_coeff_1_2()
        / mean_depth_of_adjacent_1_2_layers()
    )


@component.add(
    name="Diffusion Flux 3",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_deep_ocean_2_per_meter": 1,
        "c_in_deep_ocean_3_per_meter": 1,
        "eddy_diff_coeff_2_3": 1,
        "mean_depth_of_adjacent_2_3_layers": 1,
    },
)
def diffusion_flux_3():
    """
    Diffusion flux between the second and the third ocean layers.
    """
    return (
        (c_in_deep_ocean_2_per_meter() - c_in_deep_ocean_3_per_meter())
        * eddy_diff_coeff_2_3()
        / mean_depth_of_adjacent_2_3_layers()
    )


@component.add(
    name="Diffusion Flux 4",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_deep_ocean_3_per_meter": 1,
        "c_in_deep_ocean_4_per_meter": 1,
        "eddy_diff_coeff_3_4": 1,
        "mean_depth_of_adjacent_3_4_layers": 1,
    },
)
def diffusion_flux_4():
    """
    Diffusion flux between the third and the fourth ocean layers.
    """
    return (
        (c_in_deep_ocean_3_per_meter() - c_in_deep_ocean_4_per_meter())
        * eddy_diff_coeff_3_4()
        / mean_depth_of_adjacent_3_4_layers()
    )


@component.add(
    name="Dimensionless Time",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def dimensionless_time():
    """
    Parameter to make table data dimensionless.
    """
    return 1


@component.add(
    name="Dmnl Adjustment ppb",
    units="1/ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def dmnl_adjustment_ppb():
    return 1


@component.add(
    name="Dmnl Adjustment ppm",
    units="1/ppm",
    comp_type="Constant",
    comp_subtype="Normal",
)
def dmnl_adjustment_ppm():
    return 1


@component.add(
    name="Dmnl Adjustment TonCO2",
    units="gCO2*TonCH4/(gCH4*TonCO2)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def dmnl_adjustment_tonco2():
    return 1


@component.add(
    name="Eddy diff coeff 1 2",
    units="Meter*Meter/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"eddy_diff_coeff_index_1_2": 1, "eddy_diff_coeff_mean_1_2": 1},
)
def eddy_diff_coeff_1_2():
    """
    Coefficient of carbon diffusion to the second layer of deep ocean.
    """
    return eddy_diff_coeff_index_1_2() * eddy_diff_coeff_mean_1_2()


@component.add(
    name="Eddy diff coeff 2 3",
    units="Meter*Meter/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"eddy_diff_coeff_index_2_3": 1, "eddy_diff_coeff_mean_2_3": 1},
)
def eddy_diff_coeff_2_3():
    """
    Coefficient of carbon diffusion to the third layer of deep ocean.
    """
    return eddy_diff_coeff_index_2_3() * eddy_diff_coeff_mean_2_3()


@component.add(
    name="Eddy diff coeff 3 4",
    units="Meter*Meter/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"eddy_diff_coeff_index_3_4": 1, "eddy_diff_coeff_mean_3_4": 1},
)
def eddy_diff_coeff_3_4():
    """
    Coefficient of carbon diffusion to the fourth layer of deep ocean.
    """
    return eddy_diff_coeff_index_3_4() * eddy_diff_coeff_mean_3_4()


@component.add(
    name="Eddy diff coeff index 1 2",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_index_1_2():
    """
    Index of coefficient for rate at which carbon is mixed in the ocean due to eddy motion, where 1 is equivalent to the expected value of 4400 meter/meter/year.
    """
    return 1


@component.add(
    name="Eddy diff coeff index 2 3",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_index_2_3():
    """
    Index of coefficient for rate at which carbon is mixed in the ocean due to eddy motion, where 1 is equivalent to the expected value of 4400 meter/meter/year.
    """
    return 1


@component.add(
    name="Eddy diff coeff index 3 4",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_index_3_4():
    """
    Index of coefficient for rate at which carbon is mixed in the ocean due to eddy motion, where 1 is equivalent to the expected value of 4400 meter/meter/year.
    """
    return 1


@component.add(
    name="Eddy diff coeff index M 1",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_index_m_1():
    """
    Index of coefficient for rate at which carbon is mixed in the ocean due to eddy motion, where 1 is equivalent to the expected value of 4400 meter/meter/year.
    """
    return 1


@component.add(
    name="Eddy diff coeff M 1",
    units="Meter*Meter/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"eddy_diff_coeff_index_m_1": 1, "eddy_diff_coeff_mean_m_1": 1},
)
def eddy_diff_coeff_m_1():
    """
    Coefficient of carbon diffusion to the first layer of deep ocean.
    """
    return eddy_diff_coeff_index_m_1() * eddy_diff_coeff_mean_m_1()


@component.add(
    name="Eddy diff coeff mean 1 2",
    units="Meter*Meter/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_mean_1_2():
    """
    Expected value at which carbon is mixed in the ocean due to eddy motion.
    """
    return 4400


@component.add(
    name="Eddy diff coeff mean 2 3",
    units="Meter*Meter/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_mean_2_3():
    """
    Expected value at which carbon is mixed in the ocean due to eddy motion.
    """
    return 4400


@component.add(
    name="Eddy diff coeff mean 3 4",
    units="Meter*Meter/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_mean_3_4():
    """
    Expected value at which carbon is mixed in the ocean due to eddy motion.
    """
    return 4400


@component.add(
    name="Eddy diff coeff mean M 1",
    units="Meter*Meter/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def eddy_diff_coeff_mean_m_1():
    """
    Expected value at which carbon is mixed in the ocean due to eddy motion.
    """
    return 4400


@component.add(
    name="Effect of Temp on C Flux Atm ML",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "sensitivity_of_c_flux_to_temp": 1,
        "temperature_change_from_preindustrial": 1,
    },
)
def effect_of_temp_on_c_flux_atm_ml():
    return 1 - sensitivity_of_c_flux_to_temp() * temperature_change_from_preindustrial()


@component.add(
    name="Effective Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_radiative_forcing": 1},
)
def effective_radiative_forcing():
    """
    Total radiative forcing from various factors in the atmosphere.
    """
    return total_radiative_forcing()


@component.add(
    name="Total CO2 Emissions",
    units="TonCO2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_co2_emissions():
    return 1


@component.add(
    name="Equil C in Mixed Layer",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "preindustrial_c_in_mixed_layer": 1,
        "effect_of_temp_on_c_flux_atm_ml": 1,
        "preindustrial_c_in_atmosphere": 1,
        "buffer_factor": 1,
        "c_in_atmosphere": 1,
    },
)
def equil_c_in_mixed_layer():
    """
    Equilibrium carbon content of mixed layer.
    """
    return (
        preindustrial_c_in_mixed_layer()
        * effect_of_temp_on_c_flux_atm_ml()
        * (c_in_atmosphere() / preindustrial_c_in_atmosphere()) ** (1 / buffer_factor())
    )


@component.add(
    name="Equilibrium C per meter in Mixed Layer",
    units="TonC/Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"equil_c_in_mixed_layer": 1, "mixed_layer_depth": 1},
)
def equilibrium_c_per_meter_in_mixed_layer():
    return equil_c_in_mixed_layer() / mixed_layer_depth()


@component.add(
    name="Equilibrium Temperature",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"co2_radiative_forcing_new": 1, "climate_feedback_parameter": 1},
)
def equilibrium_temperature():
    """
    Ratio of Radiative Forcing to the Climate Feedback Parameter
    """
    return co2_radiative_forcing_new() / (
        climate_feedback_parameter() * float(np.log(2))
    )


@component.add(
    name="F Gases Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "f_gases_radiative_forcing_history": 1,
        "f_gases_radiative_forcing_rcp60": 1,
        "f_gases_radiative_forcing_rcp19": 1,
        "f_gases_radiative_forcing_rcp45": 1,
        "f_gases_radiative_forcing_rcp34": 1,
        "f_gases_radiative_forcing_rcp85": 1,
        "f_gases_radiative_forcing_rcp26": 1,
        "rcp_scenario": 5,
    },
)
def f_gases_radiative_forcing():
    """
    Radiative forcing from F-gases (HFC and others) in the atmosphere.
    """
    return if_then_else(
        time() <= 2010,
        lambda: f_gases_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 0,
            lambda: f_gases_radiative_forcing_rcp19(),
            lambda: if_then_else(
                rcp_scenario() == 1,
                lambda: f_gases_radiative_forcing_rcp26(),
                lambda: if_then_else(
                    rcp_scenario() == 2,
                    lambda: f_gases_radiative_forcing_rcp34(),
                    lambda: if_then_else(
                        rcp_scenario() == 3,
                        lambda: f_gases_radiative_forcing_rcp45(),
                        lambda: if_then_else(
                            rcp_scenario() == 4,
                            lambda: f_gases_radiative_forcing_rcp60(),
                            lambda: f_gases_radiative_forcing_rcp85(),
                        ),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="F Gases Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing": 1,
    },
)
def f_gases_radiative_forcing_history():
    """
    Historical data for radiative forcing from CH4 in the atmosphere.
    """
    return table_f_gases_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP19",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp19": 1,
    },
)
def f_gases_radiative_forcing_rcp19():
    """
    Future projections of f-gases radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 1.9).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp19(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp26": 1,
    },
)
def f_gases_radiative_forcing_rcp26():
    """
    Future projections of f-gases radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 2.6).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp26(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP34",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp34": 1,
    },
)
def f_gases_radiative_forcing_rcp34():
    """
    Future projections of f gases radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp34(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp45": 1,
    },
)
def f_gases_radiative_forcing_rcp45():
    """
    Future projections of f gases radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 4.5).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp45(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp60": 1,
    },
)
def f_gases_radiative_forcing_rcp60():
    """
    Future projections of CH4 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp60(time() * dimensionless_time())


@component.add(
    name="F Gases Radiative Forcing RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_f_gases_radiative_forcing_ssp2_rcp85": 1,
    },
)
def f_gases_radiative_forcing_rcp85():
    """
    Future projections of f gases radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_f_gases_radiative_forcing_ssp2_rcp85(time() * dimensionless_time())


@component.add(
    name="Feedback Cooling",
    units="Watt/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "temperature_change_from_preindustrial": 1,
        "climate_feedback_parameter": 1,
    },
)
def feedback_cooling():
    """
    Feedback cooling of atmosphere/upper ocean system due to blackbody radiation.
    """
    return temperature_change_from_preindustrial() * climate_feedback_parameter()


@component.add(
    name="Flux Atmosphere to Biomass",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "initial_net_primary_production": 1,
        "preindustrial_c_in_atmosphere": 1,
        "biostimulation_coefficient": 1,
        "c_in_atmosphere": 1,
    },
)
def flux_atmosphere_to_biomass():
    """
    Carbon flux from atmosphere to biosphere (from primary production)
    """
    return initial_net_primary_production() * (
        1
        + biostimulation_coefficient()
        * float(np.log(c_in_atmosphere() / preindustrial_c_in_atmosphere()))
    )


@component.add(
    name="Flux Atmosphere to Ocean",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"equil_c_in_mixed_layer": 1, "c_in_mixed_layer": 1, "mixing_time": 1},
)
def flux_atmosphere_to_ocean():
    """
    Carbon flux from atmosphere to mixed ocean layer.
    """
    return (equil_c_in_mixed_layer() - c_in_mixed_layer()) / mixing_time()


@component.add(
    name="Flux Biomass to Atmosphere",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_biomass": 1, "biomass_res_time": 1, "humification_fraction": 1},
)
def flux_biomass_to_atmosphere():
    """
    Carbon flux from biomass to atmosphere.
    """
    return (c_in_biomass() / biomass_res_time()) * (1 - humification_fraction())


@component.add(
    name="Flux Biomass to Humus",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_biomass": 1, "biomass_res_time": 1, "humification_fraction": 1},
)
def flux_biomass_to_humus():
    """
    Carbon flux from biomass to humus.
    """
    return (c_in_biomass() / biomass_res_time()) * humification_fraction()


@component.add(
    name="Flux Humus to Atmosphere",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_humus": 1, "humus_res_time": 1},
)
def flux_humus_to_atmosphere():
    """
    Carbon flux from humus to atmosphere.
    """
    return c_in_humus() / humus_res_time()


@component.add(
    name="GtC to TonC", units="TonC/GtC", comp_type="Constant", comp_subtype="Normal"
)
def gtc_to_tonc():
    """
    1 GtC equals 1000000000 tons of carbon
    """
    return 1000000000.0


@component.add(
    name="Heat Diffusion Covar",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def heat_diffusion_covar():
    """
    Heat transfer coefficient parameter.
    """
    return 1


@component.add(
    name="Heat in Atmosphere and Upper Ocean",
    units="Year*Watt/(Meter*Meter)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_heat_in_atmosphere_and_upper_ocean": 1},
    other_deps={
        "_integ_heat_in_atmosphere_and_upper_ocean": {
            "initial": {
                "init_atmospheric_and_upper_ocean_temperature": 1,
                "atmospheric_and_upper_ocean_heat_capacity": 1,
            },
            "step": {
                "effective_radiative_forcing": 1,
                "feedback_cooling": 1,
                "heat_transfer_1": 1,
            },
        }
    },
)
def heat_in_atmosphere_and_upper_ocean():
    """
    Temperature of the atmosphere and the mixed ocean layer.
    """
    return _integ_heat_in_atmosphere_and_upper_ocean()


_integ_heat_in_atmosphere_and_upper_ocean = Integ(
    lambda: effective_radiative_forcing() - feedback_cooling() - heat_transfer_1(),
    lambda: init_atmospheric_and_upper_ocean_temperature()
    * atmospheric_and_upper_ocean_heat_capacity(),
    "_integ_heat_in_atmosphere_and_upper_ocean",
)


@component.add(
    name="Heat in Deep Ocean 1",
    units="Year*Watt/(Meter*Meter)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_heat_in_deep_ocean_1": 1},
    other_deps={
        "_integ_heat_in_deep_ocean_1": {
            "initial": {
                "init_deep_ocean_1_temperature": 1,
                "deep_ocean_1_heat_capacity": 1,
            },
            "step": {"heat_transfer_1": 1, "heat_transfer_2": 1},
        }
    },
)
def heat_in_deep_ocean_1():
    """
    Heat content of the first layer of the deep ocean.
    """
    return _integ_heat_in_deep_ocean_1()


_integ_heat_in_deep_ocean_1 = Integ(
    lambda: heat_transfer_1() - heat_transfer_2(),
    lambda: init_deep_ocean_1_temperature() * deep_ocean_1_heat_capacity(),
    "_integ_heat_in_deep_ocean_1",
)


@component.add(
    name="Heat in Deep Ocean 2",
    units="Year*Watt/(Meter*Meter)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_heat_in_deep_ocean_2": 1},
    other_deps={
        "_integ_heat_in_deep_ocean_2": {
            "initial": {
                "init_deep_ocean_2_temperature": 1,
                "deep_ocean_2_heat_capacity": 1,
            },
            "step": {"heat_transfer_2": 1, "heat_transfer_3": 1},
        }
    },
)
def heat_in_deep_ocean_2():
    """
    Heat content of the second layer of the deep ocean.
    """
    return _integ_heat_in_deep_ocean_2()


_integ_heat_in_deep_ocean_2 = Integ(
    lambda: heat_transfer_2() - heat_transfer_3(),
    lambda: init_deep_ocean_2_temperature() * deep_ocean_2_heat_capacity(),
    "_integ_heat_in_deep_ocean_2",
)


@component.add(
    name="Heat in Deep Ocean 3",
    units="Year*Watt/(Meter*Meter)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_heat_in_deep_ocean_3": 1},
    other_deps={
        "_integ_heat_in_deep_ocean_3": {
            "initial": {
                "init_deep_ocean_3_temperature": 1,
                "deep_ocean_3_heat_capacity": 1,
            },
            "step": {"heat_transfer_3": 1, "heat_transfer_4": 1},
        }
    },
)
def heat_in_deep_ocean_3():
    """
    Heat content of the third layer of the deep ocean.
    """
    return _integ_heat_in_deep_ocean_3()


_integ_heat_in_deep_ocean_3 = Integ(
    lambda: heat_transfer_3() - heat_transfer_4(),
    lambda: init_deep_ocean_3_temperature() * deep_ocean_3_heat_capacity(),
    "_integ_heat_in_deep_ocean_3",
)


@component.add(
    name="Heat in Deep Ocean 4",
    units="Year*Watt/(Meter*Meter)",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_heat_in_deep_ocean_4": 1},
    other_deps={
        "_integ_heat_in_deep_ocean_4": {
            "initial": {
                "init_deep_ocean_4_temperature": 1,
                "deep_ocean_4_heat_capacity": 1,
            },
            "step": {"heat_transfer_4": 1},
        }
    },
)
def heat_in_deep_ocean_4():
    """
    Heat content of the fourth layer of the deep ocean.
    """
    return _integ_heat_in_deep_ocean_4()


_integ_heat_in_deep_ocean_4 = Integ(
    lambda: heat_transfer_4(),
    lambda: init_deep_ocean_4_temperature() * deep_ocean_4_heat_capacity(),
    "_integ_heat_in_deep_ocean_4",
)


@component.add(
    name="Heat to 2000m",
    units="Year*W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_to_700m": 1, "heat_in_deep_ocean_3": 1},
)
def heat_to_2000m():
    """
    Heat to 2000m in deep ocean. Assumes default layer thicknesses, i.e., 100 m for the mixed ocean, 300 m each for layers 1 and 2, and 1300 m for layer 3.
    """
    return heat_to_700m() + heat_in_deep_ocean_3()


@component.add(
    name="Heat to 2000m J",
    units="Je22",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_to_2000m": 1,
        "j_per_w_year": 1,
        "area": 1,
        "land_area_fraction": 1,
    },
)
def heat_to_2000m_j():
    """
    Heat to 2000m in Joules*1e22 for the area covered by water.
    """
    return heat_to_2000m() * j_per_w_year() * (area() * (1 - land_area_fraction()))


@component.add(
    name="Heat to 700m",
    units="Year*W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_in_atmosphere_and_upper_ocean": 1,
        "land_area_fraction": 1,
        "heat_in_deep_ocean_1": 1,
        "heat_in_deep_ocean_2": 1,
    },
)
def heat_to_700m():
    """
    Sum of the heat in the atmosphere and upper ocean and that in the top two layers of the deep ocean. Assumes default layer thicknesses, i.e., 100 m for the mixed ocean and 300 m each for layers 1 and 2.
    """
    return (
        heat_in_atmosphere_and_upper_ocean() * (1 - land_area_fraction())
        + heat_in_deep_ocean_1()
        + heat_in_deep_ocean_2()
    )


@component.add(
    name="Heat to 700m J",
    units="Je22",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_to_700m": 1,
        "j_per_w_year": 1,
        "area": 1,
        "land_area_fraction": 1,
        "offset_700m_heat": 1,
    },
)
def heat_to_700m_j():
    """
    Heat to 700 m in Joules*1e22 for the area covered by water. Source of Historical Data: NOAA – Ocean heat content anomalies; http://www.nodc.noaa.gov/OC5/3M_HEAT_CONTENT/ Levitus S., J. I. Antonov, T. P. Boyer, R. A. Locarnini, H. E. Garcia, and A. V. Mishonov, 2009. Global ocean heat content 1955-2008 in light of recently revealed instrumentation problems GRL, 36, L07608, doi:10.1029/2008GL037155.
    """
    return (
        heat_to_700m() * j_per_w_year() * (area() * (1 - land_area_fraction()))
        + offset_700m_heat()
    )


@component.add(
    name="Heat Transfer 1",
    units="Watt/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "temperature_change_from_preindustrial": 1,
        "relative_deep_1_ocean_temperature": 1,
        "heat_transfer_coefficient_1": 1,
        "mean_depth_of_adjacent_m_1_layers": 1,
    },
)
def heat_transfer_1():
    """
    Heat transfer from the atmosphere & upper ocean to the first layer of the deep ocean.
    """
    return (
        (temperature_change_from_preindustrial() - relative_deep_1_ocean_temperature())
        * heat_transfer_coefficient_1()
        / mean_depth_of_adjacent_m_1_layers()
    )


@component.add(
    name="Heat Transfer 2",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "relative_deep_1_ocean_temperature": 1,
        "relative_deep_2_ocean_temperature": 1,
        "heat_transfer_coefficient_2": 1,
        "mean_depth_of_adjacent_1_2_layers": 1,
    },
)
def heat_transfer_2():
    """
    Heat transfer from the first to the second layer of the deep ocean.
    """
    return (
        (relative_deep_1_ocean_temperature() - relative_deep_2_ocean_temperature())
        * heat_transfer_coefficient_2()
        / mean_depth_of_adjacent_1_2_layers()
    )


@component.add(
    name="Heat Transfer 3",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "relative_deep_2_ocean_temperature": 1,
        "relative_deep_3_ocean_temperature": 1,
        "heat_transfer_coefficient_3": 1,
        "mean_depth_of_adjacent_2_3_layers": 1,
    },
)
def heat_transfer_3():
    """
    Heat transfer from the second to the third layer of the deep ocean.
    """
    return (
        (relative_deep_2_ocean_temperature() - relative_deep_3_ocean_temperature())
        * heat_transfer_coefficient_3()
        / mean_depth_of_adjacent_2_3_layers()
    )


@component.add(
    name="Heat Transfer 4",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "relative_deep_3_ocean_temperature": 1,
        "relative_deep_4_ocean_temperature": 1,
        "heat_transfer_coefficient_4": 1,
        "mean_depth_of_adjacent_3_4_layers": 1,
    },
)
def heat_transfer_4():
    """
    Heat transfer from the third to the fourth layer of the deep ocean.
    """
    return (
        (relative_deep_3_ocean_temperature() - relative_deep_4_ocean_temperature())
        * heat_transfer_coefficient_4()
        / mean_depth_of_adjacent_3_4_layers()
    )


@component.add(
    name="Heat Transfer Coefficient 1",
    units="W/(Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_transfer_rate": 1,
        "mean_depth_of_adjacent_m_1_layers": 1,
        "heat_diffusion_covar": 2,
        "eddy_diff_coeff_mean_m_1": 1,
        "eddy_diff_coeff_m_1": 1,
    },
)
def heat_transfer_coefficient_1():
    """
    The ratio of the actual to the mean of the heat transfer coefficient, which controls the movement of heat through the climate sector.
    """
    return (heat_transfer_rate() * mean_depth_of_adjacent_m_1_layers()) * (
        heat_diffusion_covar() * (eddy_diff_coeff_m_1() / eddy_diff_coeff_mean_m_1())
        + (1 - heat_diffusion_covar())
    )


@component.add(
    name="Heat Transfer Coefficient 2",
    units="W/(Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_transfer_rate": 1,
        "mean_depth_of_adjacent_1_2_layers": 1,
        "heat_diffusion_covar": 2,
        "eddy_diff_coeff_mean_1_2": 1,
        "eddy_diff_coeff_1_2": 1,
    },
)
def heat_transfer_coefficient_2():
    """
    The ratio of the actual to the mean of the heat transfer coefficient, which controls the movement of heat through the climate sector.
    """
    return (heat_transfer_rate() * mean_depth_of_adjacent_1_2_layers()) * (
        heat_diffusion_covar() * (eddy_diff_coeff_1_2() / eddy_diff_coeff_mean_1_2())
        + (1 - heat_diffusion_covar())
    )


@component.add(
    name="Heat Transfer Coefficient 3",
    units="W/(Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_transfer_rate": 1,
        "mean_depth_of_adjacent_2_3_layers": 1,
        "heat_diffusion_covar": 2,
        "eddy_diff_coeff_mean_2_3": 1,
        "eddy_diff_coeff_2_3": 1,
    },
)
def heat_transfer_coefficient_3():
    """
    The ratio of the actual to the mean of the heat transfer coefficient, which controls the movement of heat through the climate sector.
    """
    return (heat_transfer_rate() * mean_depth_of_adjacent_2_3_layers()) * (
        heat_diffusion_covar() * (eddy_diff_coeff_2_3() / eddy_diff_coeff_mean_2_3())
        + (1 - heat_diffusion_covar())
    )


@component.add(
    name="Heat Transfer Coefficient 4",
    units="W/(Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_transfer_rate": 1,
        "mean_depth_of_adjacent_3_4_layers": 1,
        "heat_diffusion_covar": 2,
        "eddy_diff_coeff_mean_3_4": 1,
        "eddy_diff_coeff_3_4": 1,
    },
)
def heat_transfer_coefficient_4():
    """
    The ratio of the actual to the mean of the heat transfer coefficient, which controls the movement of heat through the climate sector.
    """
    return (heat_transfer_rate() * mean_depth_of_adjacent_3_4_layers()) * (
        heat_diffusion_covar() * (eddy_diff_coeff_3_4() / eddy_diff_coeff_mean_3_4())
        + (1 - heat_diffusion_covar())
    )


@component.add(
    name="Heat Transfer Rate",
    units="Watt/(Meter*Meter)/DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def heat_transfer_rate():
    """
    Rate of heat transfer between the surface and deep ocean.
    """
    return 1.23


@component.add(
    name="HFC Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "hfc_radiative_forcing_history": 1,
        "hfc_radiative_forcing_minicam_rcp45": 1,
        "hfc_radiative_forcing_image_rcp26": 1,
        "hfc_radiative_forcing_message_rcp85": 1,
        "hfc_radiative_forcing_aim_rcp60": 1,
        "hfc_radiative_forcing_aim_rcp7": 1,
        "rcp_scenario": 4,
    },
)
def hfc_radiative_forcing():
    """
    Radiative forcing from HFC in the atmosphere.
    """
    return if_then_else(
        time() < 2005,
        lambda: hfc_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 1,
            lambda: hfc_radiative_forcing_image_rcp26(),
            lambda: if_then_else(
                rcp_scenario() == 2,
                lambda: hfc_radiative_forcing_minicam_rcp45(),
                lambda: if_then_else(
                    rcp_scenario() == 3,
                    lambda: hfc_radiative_forcing_aim_rcp60(),
                    lambda: if_then_else(
                        rcp_scenario() == 4,
                        lambda: hfc_radiative_forcing_message_rcp85(),
                        lambda: hfc_radiative_forcing_aim_rcp7(),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="HFC Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_hfc_radiative_forcing_aim_rcp60": 1,
    },
)
def hfc_radiative_forcing_aim_rcp60():
    """
    Future projections of HFC radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by AIM (RCP 6.0).
    """
    return table_hfc_radiative_forcing_aim_rcp60(time() * dimensionless_time())


@component.add(
    name="HFC Radiative Forcing AIM RCP7",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_hfc_radiative_forcing_aim_ssp3_rcp7": 1,
    },
)
def hfc_radiative_forcing_aim_rcp7():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_hfc_radiative_forcing_aim_ssp3_rcp7(time() * dimensionless_time())


@component.add(
    name="HFC Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "dimensionless_time": 1, "table_hfc_radiative_forcing": 1},
)
def hfc_radiative_forcing_history():
    """
    Historical data for radiative forcing from HFC in the atmosphere.
    """
    return table_hfc_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="HFC Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_hfc_radiative_forcing_image_rcp26": 1,
    },
)
def hfc_radiative_forcing_image_rcp26():
    """
    Future projections of HFC radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by IMAGE (RCP 2.6).
    """
    return table_hfc_radiative_forcing_image_rcp26(time() * dimensionless_time())


@component.add(
    name="HFC Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_hfc_radiative_forcing_message_rcp85": 1,
    },
)
def hfc_radiative_forcing_message_rcp85():
    """
    Future projections of CO2 radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_hfc_radiative_forcing_message_rcp85(time() * dimensionless_time())


@component.add(
    name="HFC Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_hfc_radiative_forcing_minicam_rcp45": 1,
    },
)
def hfc_radiative_forcing_minicam_rcp45():
    """
    Future projections of HFC radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MiniCAM (RCP 4.5).
    """
    return table_hfc_radiative_forcing_minicam_rcp45(time() * dimensionless_time())


@component.add(
    name="Humification Fraction",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def humification_fraction():
    """
    Fraction of carbon outflow from biomass that enters humus stock.
    """
    return 0.428


@component.add(
    name="Humus Res Time", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def humus_res_time():
    """
    Average carbon residence time in humus.
    """
    return 27.8


@component.add(
    name="INIT Atmospheric and Upper Ocean Temperature",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_atmospheric_and_upper_ocean_temperature():
    """
    Initial value of Atmospheric and Upper Ocean Temperature.
    """
    return 0


@component.add(
    name="INIT C in Atmosphere",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"atmospheric_co2_law_dome_1850": 1, "gtc_to_tonc": 1, "ppm_to_gtc": 1},
)
def init_c_in_atmosphere():
    """
    Initial carbon in atmosphere.
    """
    return atmospheric_co2_law_dome_1850() * gtc_to_tonc() * ppm_to_gtc()


@component.add(
    name="INIT C in Biomass",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_init_c_in_biomass": 1},
    other_deps={
        "_initial_init_c_in_biomass": {
            "initial": {"flux_atmosphere_to_biomass": 1, "biomass_res_time": 1},
            "step": {},
        }
    },
)
def init_c_in_biomass():
    """
    Initial carbon in biomass.
    """
    return _initial_init_c_in_biomass()


_initial_init_c_in_biomass = Initial(
    lambda: flux_atmosphere_to_biomass() * biomass_res_time(),
    "_initial_init_c_in_biomass",
)


@component.add(
    name="INIT C in Deep Ocean 1",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"init_c_in_deep_ocean_per_meter": 1, "layer_depth_1": 1},
)
def init_c_in_deep_ocean_1():
    """
    Initial carbon in the first layer of deep ocean. was constant at 3.115e+012 in the earlier versions of the model.
    """
    return init_c_in_deep_ocean_per_meter() * layer_depth_1()


@component.add(
    name="INIT C in Deep Ocean 2",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"init_c_in_deep_ocean_per_meter": 1, "layer_depth_2": 1},
)
def init_c_in_deep_ocean_2():
    """
    Initial carbon in the second layer of deep ocean. was constant at 3.099e+012 in earlier versions of the model
    """
    return init_c_in_deep_ocean_per_meter() * layer_depth_2()


@component.add(
    name="INIT C in Deep Ocean 3",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"init_c_in_deep_ocean_per_meter": 1, "layer_depth_3": 1},
)
def init_c_in_deep_ocean_3():
    """
    Initial carbon in the third layer of deep ocean. was constant at 1.3356e+013 in earlier versions of the model
    """
    return init_c_in_deep_ocean_per_meter() * layer_depth_3()


@component.add(
    name="INIT C in Deep Ocean 4",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"init_c_in_deep_ocean_per_meter": 1, "layer_depth_4": 1},
)
def init_c_in_deep_ocean_4():
    """
    Initial carbon in the fourth layer of deep ocean. was constant at 1.8477e+013 in earlier versions of the model.
    """
    return init_c_in_deep_ocean_per_meter() * layer_depth_4()


@component.add(
    name="Init C in Deep Ocean per meter",
    units="TonC/Meter",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_init_c_in_deep_ocean_per_meter": 1},
    other_deps={
        "_initial_init_c_in_deep_ocean_per_meter": {
            "initial": {"equilibrium_c_per_meter_in_mixed_layer": 1},
            "step": {},
        }
    },
)
def init_c_in_deep_ocean_per_meter():
    return _initial_init_c_in_deep_ocean_per_meter()


_initial_init_c_in_deep_ocean_per_meter = Initial(
    lambda: equilibrium_c_per_meter_in_mixed_layer(),
    "_initial_init_c_in_deep_ocean_per_meter",
)


@component.add(
    name="INIT C in Humus",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Initial",
    depends_on={"_initial_init_c_in_humus": 1},
    other_deps={
        "_initial_init_c_in_humus": {
            "initial": {"flux_biomass_to_humus": 1, "humus_res_time": 1},
            "step": {},
        }
    },
)
def init_c_in_humus():
    """
    Inital carbon in humus.
    """
    return _initial_init_c_in_humus()


_initial_init_c_in_humus = Initial(
    lambda: flux_biomass_to_humus() * humus_res_time(), "_initial_init_c_in_humus"
)


@component.add(
    name="INIT C in Mixed Ocean",
    units="TonC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_c_in_mixed_ocean():
    """
    Initial carbon in mixed ocean layer.
    """
    return 901800000000.0


@component.add(
    name="INIT CH4 in Atmosphere",
    units="TonCH4",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"atmospheric_ch4_concentration_1850_ar6": 1, "tonch4_to_ppb": 1},
)
def init_ch4_in_atmosphere():
    return atmospheric_ch4_concentration_1850_ar6() / tonch4_to_ppb()


@component.add(
    name="INIT Deep Ocean 1 Temperature",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_deep_ocean_1_temperature():
    """
    Initial value of temperature in the first layer of deep ocean.
    """
    return 0


@component.add(
    name="INIT Deep Ocean 2 Temperature",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_deep_ocean_2_temperature():
    """
    Initial value of temperature in the second layer of deep ocean.
    """
    return 0


@component.add(
    name="INIT Deep Ocean 3 Temperature",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_deep_ocean_3_temperature():
    """
    Initial value of temperature in the third layer of deep ocean.
    """
    return 0


@component.add(
    name="INIT Deep Ocean 4 Temperature",
    units="DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def init_deep_ocean_4_temperature():
    """
    Initial value of temperature in the fourth layer of deep ocean.
    """
    return 0


@component.add(
    name="INIT N2O in Atmosphere",
    units="TonN2O",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"atmospheric_n2o_concentration_1850_ar6": 1, "tonn2o_to_ppb": 1},
)
def init_n2o_in_atmosphere():
    return atmospheric_n2o_concentration_1850_ar6() / tonn2o_to_ppb()


@component.add(
    name="Initial Net Primary Production",
    units="TonC/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_net_primary_production():
    """
    Initial net primary production.
    """
    return 85177100000.0


@component.add(
    name="J per W Year",
    units="Je22/Watt/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def j_per_w_year():
    """
    Convertion from watts*year to Joules*1e22.
    """
    return 365 * 24 * 60 * 60 / 1e22


@component.add(
    name="Land Area Fraction", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def land_area_fraction():
    """
    Fraction of global surface area that is land.
    """
    return 0.292


@component.add(
    name="Land Thickness", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def land_thickness():
    """
    Effective land area heat capacity, expressed as equivalent water layer thickness.
    """
    return 8.4


@component.add(
    name="Layer Depth 1", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def layer_depth_1():
    """
    Depth of the first ocean layer.
    """
    return 300


@component.add(
    name="Layer Depth 2", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def layer_depth_2():
    """
    Depth of the second ocean layer.
    """
    return 300


@component.add(
    name="Layer Depth 3", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def layer_depth_3():
    """
    Depth of the third ocean layer.
    """
    return 1300


@component.add(
    name="Layer Depth 4", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def layer_depth_4():
    """
    Depth of the fourth ocean layer.
    """
    return 1800


@component.add(
    name="Layer Time Constant 1 2",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_2": 2, "eddy_diff_coeff_1_2": 1, "layer_depth_1": 1},
)
def layer_time_constant_1_2():
    """
    Time constant of exchange between the first and the second ocean layers.
    """
    return layer_depth_2() / (
        eddy_diff_coeff_1_2() / ((layer_depth_1() + layer_depth_2()) / 2)
    )


@component.add(
    name="Layer Time Constant 2 3",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_3": 2, "layer_depth_2": 1, "eddy_diff_coeff_2_3": 1},
)
def layer_time_constant_2_3():
    """
    Time constant of exchange between the second and the third ocean layers.
    """
    return layer_depth_3() / (
        eddy_diff_coeff_2_3() / ((layer_depth_2() + layer_depth_3()) / 2)
    )


@component.add(
    name="Layer Time Constant 3 4",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_4": 2, "eddy_diff_coeff_3_4": 1, "layer_depth_3": 1},
)
def layer_time_constant_3_4():
    """
    Time constant of exchange between the third and the fourth ocean layers.
    """
    return layer_depth_4() / (
        eddy_diff_coeff_3_4() / ((layer_depth_3() + layer_depth_4()) / 2)
    )


@component.add(
    name="Layer Time Constant M 1",
    units="Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_1": 2, "mixed_layer_depth": 1, "eddy_diff_coeff_m_1": 1},
)
def layer_time_constant_m_1():
    """
    Time constant of exchange between mixed and the first ocean layers.
    """
    return layer_depth_1() / (
        eddy_diff_coeff_m_1() / ((mixed_layer_depth() + layer_depth_1()) / 2)
    )


@component.add(
    name="Lower Layer Volume Vu 1",
    units="Meter*Meter*Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"area": 1, "land_area_fraction": 1, "layer_depth_1": 1},
)
def lower_layer_volume_vu_1():
    """
    Water equivalent volume of the first layer of deep ocean.
    """
    return area() * (1 - land_area_fraction()) * layer_depth_1()


@component.add(
    name="Lower Layer Volume Vu 2",
    units="Meter*Meter*Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"area": 1, "land_area_fraction": 1, "layer_depth_2": 1},
)
def lower_layer_volume_vu_2():
    """
    Water equivalent volume of the second layer of deep ocean.
    """
    return area() * (1 - land_area_fraction()) * layer_depth_2()


@component.add(
    name="Lower Layer Volume Vu 3",
    units="Meter*Meter*Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"area": 1, "land_area_fraction": 1, "layer_depth_3": 1},
)
def lower_layer_volume_vu_3():
    """
    Water equivalent volume of the third layer of deep ocean.
    """
    return area() * (1 - land_area_fraction()) * layer_depth_3()


@component.add(
    name="Lower Layer Volume Vu 4",
    units="Meter*Meter*Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"area": 1, "land_area_fraction": 1, "layer_depth_4": 1},
)
def lower_layer_volume_vu_4():
    """
    Water equivalent volume of the fourth layer of deep ocean.
    """
    return area() * (1 - land_area_fraction()) * layer_depth_4()


@component.add(
    name="Mass Heat Capacity",
    units="J/kg/DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def mass_heat_capacity():
    """
    Specific heat of water, i.e., amount of heat in Joules per kg water required to raise the temperature by one C degree.
    """
    return 4186


@component.add(
    name="Mean Depth of Adjacent 1 2 Layers",
    units="Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_1": 1, "layer_depth_2": 1},
)
def mean_depth_of_adjacent_1_2_layers():
    """
    Mean depth of the first and the second ocean layers.
    """
    return (layer_depth_1() + layer_depth_2()) / 2


@component.add(
    name="Mean Depth of Adjacent 2 3 Layers",
    units="Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_2": 1, "layer_depth_3": 1},
)
def mean_depth_of_adjacent_2_3_layers():
    """
    Mean depth of the second and the third ocean layers.
    """
    return (layer_depth_2() + layer_depth_3()) / 2


@component.add(
    name="Mean Depth of Adjacent 3 4 Layers",
    units="Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"layer_depth_3": 1, "layer_depth_4": 1},
)
def mean_depth_of_adjacent_3_4_layers():
    """
    Mean depth of the third and the fourth ocean layers.
    """
    return (layer_depth_3() + layer_depth_4()) / 2


@component.add(
    name="Mean Depth of Adjacent M 1 Layers",
    units="Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"mixed_layer_depth": 1, "layer_depth_1": 1},
)
def mean_depth_of_adjacent_m_1_layers():
    """
    Mean depth of mixed and the first ocean layers.
    """
    return (mixed_layer_depth() + layer_depth_1()) / 2


@component.add(
    name="Mixed Layer Depth", units="Meter", comp_type="Constant", comp_subtype="Normal"
)
def mixed_layer_depth():
    """
    Mixed ocean layer depth.
    """
    return 100


@component.add(
    name="Mixing Time", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def mixing_time():
    """
    Atmosphere - mixed ocean layer mixing time.
    """
    return 1


@component.add(
    name="Molar mass of CH4",
    units="gCH4/mol",
    comp_type="Constant",
    comp_subtype="Normal",
)
def molar_mass_of_ch4():
    return 16.04


@component.add(
    name="Molar mass of CO2",
    units="gCO2/mol",
    comp_type="Constant",
    comp_subtype="Normal",
)
def molar_mass_of_co2():
    return 44.01


@component.add(
    name="Molar mass of N2O",
    units="gN2O/mol",
    comp_type="Constant",
    comp_subtype="Normal",
)
def molar_mass_of_n2o():
    return 44.013


@component.add(
    name="N2O Concentration Ratio",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"n2o_in_atmosphere": 1, "init_n2o_in_atmosphere": 1},
)
def n2o_concentration_ratio():
    return n2o_in_atmosphere() / init_n2o_in_atmosphere()


@component.add(
    name="N2O in Atmosphere",
    units="TonN2O",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_n2o_in_atmosphere": 1},
    other_deps={
        "_integ_n2o_in_atmosphere": {
            "initial": {"init_n2o_in_atmosphere": 1},
            "step": {"total_n2o_emission": 1, "total_n2o_breakdown": 1},
        }
    },
)
def n2o_in_atmosphere():
    return _integ_n2o_in_atmosphere()


_integ_n2o_in_atmosphere = Integ(
    lambda: total_n2o_emission() - total_n2o_breakdown(),
    lambda: init_n2o_in_atmosphere(),
    "_integ_n2o_in_atmosphere",
)


@component.add(
    name="N2O Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "n2o_radiative_forcing_history": 1,
        "n2o_radiative_forcing_rcp19": 1,
        "n2o_radiative_forcing_rcp45": 1,
        "n2o_radiative_forcing_rcp85": 1,
        "n2o_radiative_forcing_rcp34": 1,
        "n2o_radiative_forcing_rcp26": 1,
        "rcp_scenario": 5,
        "n2o_radiative_forcing_rcp60": 1,
    },
)
def n2o_radiative_forcing():
    """
    Radiative forcing from N2O in the atmosphere.
    """
    return if_then_else(
        time() <= 2010,
        lambda: n2o_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 0,
            lambda: n2o_radiative_forcing_rcp19(),
            lambda: if_then_else(
                rcp_scenario() == 1,
                lambda: n2o_radiative_forcing_rcp26(),
                lambda: if_then_else(
                    rcp_scenario() == 2,
                    lambda: n2o_radiative_forcing_rcp34(),
                    lambda: if_then_else(
                        rcp_scenario() == 3,
                        lambda: n2o_radiative_forcing_rcp45(),
                        lambda: if_then_else(
                            rcp_scenario() == 4,
                            lambda: n2o_radiative_forcing_rcp60(),
                            lambda: n2o_radiative_forcing_rcp85(),
                        ),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="N2O Radiative Forcing Coefficient",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "a2": 1,
        "atmospheric_concentration_co2": 1,
        "dmnl_adjustment_ppm": 1,
        "atmospheric_concentration_n2o": 1,
        "dmnl_adjustment_ppb": 2,
        "b2": 1,
        "atmospheric_concentration_ch4": 1,
        "c2": 1,
        "d2": 1,
    },
)
def n2o_radiative_forcing_coefficient():
    return (
        a2() * float(np.sqrt(atmospheric_concentration_co2() * dmnl_adjustment_ppm()))
        + b2() * float(np.sqrt(atmospheric_concentration_n2o() * dmnl_adjustment_ppb()))
        + c2() * float(np.sqrt(atmospheric_concentration_ch4() * dmnl_adjustment_ppb()))
        + d2()
    )


@component.add(
    name="N2O Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "dimensionless_time": 1, "table_n2o_radiative_forcing": 1},
)
def n2o_radiative_forcing_history():
    """
    Historical data for radiative forcing from N2O in the atmosphere.
    """
    return table_n2o_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing New",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "n2o_radiative_forcing_coefficient": 1,
        "atmospheric_concentration_n2o": 1,
        "dmnl_adjustment_ppb": 2,
        "atmospheric_n2o_concentration_preindustrial": 1,
    },
)
def n2o_radiative_forcing_new():
    return n2o_radiative_forcing_coefficient() * (
        float(np.sqrt(atmospheric_concentration_n2o() * dmnl_adjustment_ppb()))
        - float(
            np.sqrt(
                atmospheric_n2o_concentration_preindustrial() * dmnl_adjustment_ppb()
            )
        )
    )


@component.add(
    name="N2O Radiative Forcing RCP19",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp19": 1,
    },
)
def n2o_radiative_forcing_rcp19():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 1.9).
    """
    return table_n2o_radiative_forcing_ssp2_rcp19(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp26": 1,
    },
)
def n2o_radiative_forcing_rcp26():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 2.6).
    """
    return table_n2o_radiative_forcing_ssp2_rcp26(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing RCP34",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp34": 1,
    },
)
def n2o_radiative_forcing_rcp34():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (SSP2 RCP 3.4).
    """
    return table_n2o_radiative_forcing_ssp2_rcp34(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp45": 1,
    },
)
def n2o_radiative_forcing_rcp45():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 4.5).
    """
    return table_n2o_radiative_forcing_ssp2_rcp45(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp60": 1,
    },
)
def n2o_radiative_forcing_rcp60():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return table_n2o_radiative_forcing_ssp2_rcp60(time() * dimensionless_time())


@component.add(
    name="N2O Radiative Forcing RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_n2o_radiative_forcing_ssp2_rcp85": 1,
    },
)
def n2o_radiative_forcing_rcp85():
    """
    Future projections of N2O radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_n2o_radiative_forcing_ssp2_rcp85(time() * dimensionless_time())


@component.add(
    name="Offset 700m Heat", units="Je22", comp_type="Constant", comp_subtype="Normal"
)
def offset_700m_heat():
    """
    Calibration offset.
    """
    return -16


@component.add(
    name="Other Anhtropogenic Radiative Forcing RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp60": 1,
    },
)
def other_anhtropogenic_radiative_forcing_rcp60():
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp60(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "other_anthropogenic_radiative_forcing_history": 1,
        "other_anthropogenic_radiative_forcing_rcp85": 1,
        "other_anthropogenic_radiative_forcing_rcp26": 1,
        "other_anthropogenic_radiative_forcing_rcp34": 1,
        "other_anthropogenic_radiative_forcing_rcp19": 1,
        "other_anthropogenic_radiative_forcing_rcp45": 1,
        "other_anhtropogenic_radiative_forcing_rcp60": 1,
        "rcp_scenario": 5,
    },
)
def other_anthropogenic_radiative_forcing():
    """
    Radiative forcing from other anthropogenic gases in the atmosphere. Calculated fro mthe SSP2 database as total forcing - (forcing from C02, CH4, N2O, F-Gases)
    """
    return if_then_else(
        time() <= 2010,
        lambda: other_anthropogenic_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 0,
            lambda: other_anthropogenic_radiative_forcing_rcp19(),
            lambda: if_then_else(
                rcp_scenario() == 1,
                lambda: other_anthropogenic_radiative_forcing_rcp26(),
                lambda: if_then_else(
                    rcp_scenario() == 2,
                    lambda: other_anthropogenic_radiative_forcing_rcp34(),
                    lambda: if_then_else(
                        rcp_scenario() == 3,
                        lambda: other_anthropogenic_radiative_forcing_rcp45(),
                        lambda: if_then_else(
                            rcp_scenario() == 4,
                            lambda: other_anhtropogenic_radiative_forcing_rcp60(),
                            lambda: other_anthropogenic_radiative_forcing_rcp85(),
                        ),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing": 1,
    },
)
def other_anthropogenic_radiative_forcing_history():
    """
    Historical data for radiative forcing from CH4 in the atmosphere.
    """
    return table_other_anthropogenic_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="Other Anthropogenic Radiative Forcing RCP19",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp19": 1,
    },
)
def other_anthropogenic_radiative_forcing_rcp19():
    """
    MESSAGE-GLOBIOM (RCP 1.9).
    """
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp19(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp26": 1,
    },
)
def other_anthropogenic_radiative_forcing_rcp26():
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp26(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing RCP34",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp34": 1,
    },
)
def other_anthropogenic_radiative_forcing_rcp34():
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp34(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp45": 1,
    },
)
def other_anthropogenic_radiative_forcing_rcp45():
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp45(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Anthropogenic Radiative Forcing RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_anthropogenic_radiative_forcing_ssp2_rcp85": 1,
    },
)
def other_anthropogenic_radiative_forcing_rcp85():
    return table_other_anthropogenic_radiative_forcing_ssp2_rcp85(
        time() * dimensionless_time()
    )


@component.add(
    name="Other Forcings",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "f_gases_radiative_forcing": 1,
        "other_anthropogenic_radiative_forcing": 1,
    },
)
def other_forcings():
    """
    Radiative forcing from factors other than CO2 in the atmosphere.
    """
    return f_gases_radiative_forcing() + other_anthropogenic_radiative_forcing()


@component.add(
    name="Other Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "other_radiative_forcing_history": 1,
        "other_radiative_forcing_minicam_rcp45": 1,
        "other_radiative_forcing_aim_rcp7": 1,
        "other_radiative_forcing_aim_rcp60": 1,
        "rcp_scenario": 4,
        "other_radiative_forcing_message_rcp85": 1,
        "other_radiative_forcing_image_rcp26": 1,
    },
)
def other_radiative_forcing():
    """
    Radiative forcing from other factors than CO2, CH4, N2O and HFC in the atmosphere.
    """
    return if_then_else(
        time() < 2000,
        lambda: other_radiative_forcing_history(),
        lambda: if_then_else(
            rcp_scenario() == 1,
            lambda: other_radiative_forcing_image_rcp26(),
            lambda: if_then_else(
                rcp_scenario() == 2,
                lambda: other_radiative_forcing_minicam_rcp45(),
                lambda: if_then_else(
                    rcp_scenario() == 3,
                    lambda: other_radiative_forcing_aim_rcp60(),
                    lambda: if_then_else(
                        rcp_scenario() == 4,
                        lambda: other_radiative_forcing_message_rcp85(),
                        lambda: other_radiative_forcing_aim_rcp7(),
                    ),
                ),
            ),
        ),
    )


@component.add(
    name="Other Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_radiative_forcing_aim_rcp60": 1,
    },
)
def other_radiative_forcing_aim_rcp60():
    """
    Future projections of other radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by AIM (RCP 6.0).
    """
    return table_other_radiative_forcing_aim_rcp60(time() * dimensionless_time())


@component.add(
    name="Other Radiative Forcing AIM RCP7",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_radiative_forcing_aim_ssp3_rcp7": 1,
    },
)
def other_radiative_forcing_aim_rcp7():
    """
    Future projections of other radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_other_radiative_forcing_aim_ssp3_rcp7(time() * dimensionless_time())


@component.add(
    name="Other Radiative Forcing History",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1, "dimensionless_time": 1, "table_other_radiative_forcing": 1},
)
def other_radiative_forcing_history():
    """
    Historical data for radiative forcing from other factors in the atmosphere.
    """
    return table_other_radiative_forcing(time() * dimensionless_time())


@component.add(
    name="Other Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_radiative_forcing_image_rcp26": 1,
    },
)
def other_radiative_forcing_image_rcp26():
    """
    Future projections of other radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by IMAGE (RCP 2.6).
    """
    return table_other_radiative_forcing_image_rcp26(time() * dimensionless_time())


@component.add(
    name="Other Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_radiative_forcing_message_rcp85": 1,
    },
)
def other_radiative_forcing_message_rcp85():
    """
    Future projections of other radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return table_other_radiative_forcing_message_rcp85(time() * dimensionless_time())


@component.add(
    name="Other Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "time": 1,
        "dimensionless_time": 1,
        "table_other_radiative_forcing_minicam_rcp45": 1,
    },
)
def other_radiative_forcing_minicam_rcp45():
    """
    Future projections of other radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MiniCAM (RCP 4.5).
    """
    return table_other_radiative_forcing_minicam_rcp45(time() * dimensionless_time())


@component.add(
    name="Overlap Coefficient",
    units="W/(m*m)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def overlap_coefficient():
    """
    Etminan et al. (2016)
    """
    return 0.00047


@component.add(
    name="Overlap Exponent", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def overlap_exponent():
    """
    Etminan et al. (2016)
    """
    return 0.75


@component.add(name="ppb", units="ppb", comp_type="Constant", comp_subtype="Normal")
def ppb():
    return 1000000000.0


@component.add(
    name="ppm to GtC", units="GtC/ppm", comp_type="Constant", comp_subtype="Normal"
)
def ppm_to_gtc():
    """
    1 ppm by volume of atmosphere CO2 equals 2.13 GtC
    """
    return 2.13


@component.add(
    name="Preindustrial C in Atmosphere",
    units="TonC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def preindustrial_c_in_atmosphere():
    """
    Preindustrial carbon content of atmosphere.
    """
    return 590000000000.0


@component.add(
    name="Preindustrial C in Mixed Layer",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"preindustrial_ocean_c_per_meter": 1, "mixed_layer_depth": 1},
)
def preindustrial_c_in_mixed_layer():
    """
    Initial carbon content of mixed ocean layer.
    """
    return preindustrial_ocean_c_per_meter() * mixed_layer_depth()


@component.add(
    name="Preindustrial Ocean C per meter",
    units="TonC/m",
    comp_type="Constant",
    comp_subtype="Normal",
)
def preindustrial_ocean_c_per_meter():
    """
    Preindustrial carbon content in ocean per meter.
    """
    return 9000000000.0


@component.add(
    name="RCP Scenario",
    units="Dmnl",
    limits=(1.0, 4.0, 1.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def rcp_scenario():
    """
    Trigger for Representative Concentration Pathways scenarios. RCP Scenario=0, RCP1.9 RCP Scenario=1,RCP2.6, RCP Scenario=2,RCP3.4, RCP Scenario=3, RCP 4.5, RCP Scenario=4, RCP 6, RCP Scenario=5, RCP 8.5
    """
    return 3


@component.add(
    name="Ref Buffer Factor", units="Dmnl", comp_type="Constant", comp_subtype="Normal"
)
def ref_buffer_factor():
    """
    Normal buffer factor.
    """
    return 9.7


@component.add(
    name="Reference CO2 Removal Rate",
    units="TonC/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def reference_co2_removal_rate():
    return 37000000.0


@component.add(
    name="Relative Deep 1 Ocean Temperature",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_1": 1, "deep_ocean_1_heat_capacity": 1},
)
def relative_deep_1_ocean_temperature():
    """
    Temperature of the first layer of the deep ocean.
    """
    return heat_in_deep_ocean_1() / deep_ocean_1_heat_capacity()


@component.add(
    name="Relative Deep 2 Ocean Temperature",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_2": 1, "deep_ocean_2_heat_capacity": 1},
)
def relative_deep_2_ocean_temperature():
    """
    Temperature of the second layer of the deep ocean.
    """
    return heat_in_deep_ocean_2() / deep_ocean_2_heat_capacity()


@component.add(
    name="Relative Deep 3 Ocean Temperature",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_3": 1, "deep_ocean_3_heat_capacity": 1},
)
def relative_deep_3_ocean_temperature():
    """
    Temperature of the third layer of the deep ocean.
    """
    return heat_in_deep_ocean_3() / deep_ocean_3_heat_capacity()


@component.add(
    name="Relative Deep 4 Ocean Temperature",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_4": 1, "deep_ocean_4_heat_capacity": 1},
)
def relative_deep_4_ocean_temperature():
    """
    Temperature of the fourth layer of the deep ocean.
    """
    return heat_in_deep_ocean_4() / deep_ocean_4_heat_capacity()


@component.add(
    name="sec per Year", units="sec/Year", comp_type="Constant", comp_subtype="Normal"
)
def sec_per_year():
    """
    Conversion from year to sec.
    """
    return 31536000.0


@component.add(
    name="Sensitivity of C flux to temp",
    units="Dmnl",
    comp_type="Constant",
    comp_subtype="Normal",
)
def sensitivity_of_c_flux_to_temp():
    return 0.003


@component.add(
    name="TABLE CH4 Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing"},
)
def table_ch4_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of CH4 radiative forcing. Pre-2000 From AR5, 2005 AND 2010 from the SSP database, SSP2 Message-GLOBIOM (marker).
    """
    return _hardcodedlookup_table_ch4_radiative_forcing(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing = HardcodedLookups(
    [
        1900.0,
        1910.0,
        1920.0,
        1930.0,
        1940.0,
        1950.0,
        1960.0,
        1970.0,
        1980.0,
        1990.0,
        2000.0,
        2005.0,
        2010.0,
    ],
    [
        0.097,
        0.121,
        0.15,
        0.179,
        0.205,
        0.233,
        0.28,
        0.342,
        0.409,
        0.465,
        0.485,
        0.562305,
        0.588276,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP19",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp19"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp19(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 1.9.
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp19(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp19 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.588276,
        0.61707,
        0.58715,
        0.509574,
        0.435621,
        0.380312,
        0.338259,
        0.301909,
        0.271782,
        0.249517,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp19",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp26"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp26(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 2.6.
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp26(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp26 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.588276,
        0.617437,
        0.60655,
        0.559263,
        0.496306,
        0.449361,
        0.420164,
        0.395895,
        0.366439,
        0.33553,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp26",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP34",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp34"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp34(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by MESSAGE-GLOBIOM (RCP 3.4).
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp34(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp34 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.588276,
        0.618688,
        0.621345,
        0.592793,
        0.537515,
        0.488544,
        0.459203,
        0.441564,
        0.425481,
        0.405663,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp34",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp45"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp45(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by MESSAGE-GLOBIOM in SSP2 RCP 4.5.
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp45(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp45 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.588276,
        0.619873,
        0.627489,
        0.614632,
        0.578009,
        0.532435,
        0.499299,
        0.477175,
        0.46059,
        0.449891,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp45",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp60"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp60(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp60(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp60 = HardcodedLookups(
    [2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.621315,
        0.636997,
        0.6457,
        0.637477,
        0.614447,
        0.590103,
        0.56345,
        0.535615,
        0.507884,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp60",
)


@component.add(
    name="TABLE CH4 Radiative Forcing SSP2 RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp85"
    },
)
def table_ch4_radiative_forcing_ssp2_rcp85(x, final_subs=None):
    """
    Data series for future projections of CH4 radiative forcing by MESSAGE-GLOBIOM (RCP 8.5).
    """
    return _hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp85(x, final_subs)


_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp85 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.588276,
        0.624748,
        0.647046,
        0.664906,
        0.676129,
        0.685959,
        0.695531,
        0.699882,
        0.698119,
        0.688933,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_ch4_radiative_forcing_ssp2_rcp85",
)


@component.add(
    name="TABLE F Gases Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing"},
)
def table_f_gases_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of F-gases radiative forcing. Pre-2000 From AR5, 2005 AND 2010 from the SSP database, SSP2 Message-GLOBIOM (marker).
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing = HardcodedLookups(
    [1900.0, 1950.0, 2005.0, 2010.0],
    [0.00000e00, 1.00000e-05, 2.11050e-02, 3.11024e-02],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP19",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp19"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp19(x, final_subs=None):
    """
    Data series for future projections of f-gases radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 1.9.
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp19(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp19 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.0613296,
        0.0770876,
        0.0756992,
        0.0766076,
        0.0793937,
        0.0825332,
        0.0849748,
        0.0865851,
        0.0877894,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp19",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp26"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp26(x, final_subs=None):
    """
    Data series for future projections of f-gases radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 2.6.
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp26(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp26 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.061264,
        0.0782927,
        0.080345,
        0.0847037,
        0.0891935,
        0.0927838,
        0.0960691,
        0.0987984,
        0.101286,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp26",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP34",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp34"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp34(x, final_subs=None):
    """
    Data series for future projections of f-gases radiative forcing by MESSAGE-GLOBIOM (RCP 3.4).
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp34(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp34 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.0612598,
        0.0836687,
        0.0909787,
        0.0942257,
        0.0980601,
        0.103224,
        0.106661,
        0.108445,
        0.110579,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp34",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp45"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp45(x, final_subs=None):
    """
    Data series for future projections of f-gases radiative forcing by MESSAGE-GLOBIOM in SSP2 RCP 4.5.
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp45(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp45 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.0612728,
        0.0871134,
        0.0987915,
        0.101803,
        0.103702,
        0.108015,
        0.112576,
        0.116856,
        0.119682,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp45",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp60"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp60(x, final_subs=None):
    """
    Data series for future projections of f gases radiative forcing by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp60(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp60 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.061275,
        0.091407,
        0.119426,
        0.148527,
        0.173135,
        0.183224,
        0.17176,
        0.157098,
        0.151042,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp60",
)


@component.add(
    name="TABLE F Gases Radiative Forcing SSP2 RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp85"
    },
)
def table_f_gases_radiative_forcing_ssp2_rcp85(x, final_subs=None):
    """
    Data series for future projections of f-gases radiative forcing by MESSAGE-GLOBIOM (RCP 8.5).
    """
    return _hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp85(x, final_subs)


_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp85 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.0311024,
        0.061417,
        0.0930176,
        0.122854,
        0.156046,
        0.192871,
        0.23523,
        0.283043,
        0.334059,
        0.386994,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_f_gases_radiative_forcing_ssp2_rcp85",
)


@component.add(
    name="TABLE HFC Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing"},
)
def table_hfc_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of HFC radiative forcing.
    """
    return _hardcodedlookup_table_hfc_radiative_forcing(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing = HardcodedLookups(
    [
        1900.0,
        1910.0,
        1920.0,
        1930.0,
        1940.0,
        1950.0,
        1960.0,
        1970.0,
        1980.0,
        1990.0,
        2000.0,
        2005.0,
    ],
    [0.001, 0.001, 0.001, 0.002, 0.003, 0.008, 0.022, 0.069, 0.174, 0.288, 0.332, 0.34],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing",
)


@component.add(
    name="TABLE HFC Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing_aim_rcp60"},
)
def table_hfc_radiative_forcing_aim_rcp60(x, final_subs=None):
    """
    Data series for future projections of HFC radiative forcing by AIM (RCP 6.0).
    """
    return _hardcodedlookup_table_hfc_radiative_forcing_aim_rcp60(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing_aim_rcp60 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [0.34, 0.344, 0.346, 0.339, 0.316, 0.272, 0.236, 0.211, 0.194, 0.18, 0.168],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing_aim_rcp60",
)


@component.add(
    name="TABLE HFC Radiative Forcing AIM SSP3 RCP7",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing_aim_ssp3_rcp7"
    },
)
def table_hfc_radiative_forcing_aim_ssp3_rcp7(x, final_subs=None):
    """
    Data series for future projections of HFC radiative forcing by AIM (RCP 7).
    """
    return _hardcodedlookup_table_hfc_radiative_forcing_aim_ssp3_rcp7(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing_aim_ssp3_rcp7 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [0.021, 0.031, 0.061, 0.096, 0.129, 0.16, 0.188, 0.211, 0.231, 0.251, 0.27],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing_aim_ssp3_rcp7",
)


@component.add(
    name="TABLE HFC Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing_image_rcp26"
    },
)
def table_hfc_radiative_forcing_image_rcp26(x, final_subs=None):
    """
    Data series for future projections of HFC radiative forcing by IMAGE (RCP 2.6).
    """
    return _hardcodedlookup_table_hfc_radiative_forcing_image_rcp26(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing_image_rcp26 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [0.34, 0.344, 0.346, 0.329, 0.301, 0.273, 0.253, 0.243, 0.236, 0.229, 0.22],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing_image_rcp26",
)


@component.add(
    name="TABLE HFC Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing_message_rcp85"
    },
)
def table_hfc_radiative_forcing_message_rcp85(x, final_subs=None):
    """
    Data series for future projections of HFC radiative forcing by MESSAGE (RCP 8.5).
    """
    return _hardcodedlookup_table_hfc_radiative_forcing_message_rcp85(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing_message_rcp85 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [0.34, 0.345, 0.36, 0.371, 0.366, 0.339, 0.316, 0.303, 0.297, 0.294, 0.294],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing_message_rcp85",
)


@component.add(
    name="TABLE HFC Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_hfc_radiative_forcing_minicam_rcp45"
    },
)
def table_hfc_radiative_forcing_minicam_rcp45(x, final_subs=None):
    """
    Data series for future projections of HFC radiative forcing by MiniCAM (RCP 4.5).
    """
    return _hardcodedlookup_table_hfc_radiative_forcing_minicam_rcp45(x, final_subs)


_hardcodedlookup_table_hfc_radiative_forcing_minicam_rcp45 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [0.34, 0.344, 0.348, 0.344, 0.323, 0.279, 0.242, 0.215, 0.197, 0.188, 0.183],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_hfc_radiative_forcing_minicam_rcp45",
)


@component.add(
    name="TABLE N2O Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing"},
)
def table_n2o_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of N2O radiative forcing.
    """
    return _hardcodedlookup_table_n2o_radiative_forcing(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing = HardcodedLookups(
    [
        1900.0,
        1910.0,
        1920.0,
        1930.0,
        1940.0,
        1950.0,
        1960.0,
        1970.0,
        1980.0,
        1990.0,
        2000.0,
        2005.0,
        2010.0,
    ],
    [
        0.025,
        0.029,
        0.036,
        0.043,
        0.048,
        0.056,
        0.064,
        0.077,
        0.098,
        0.124,
        0.145,
        0.155711,
        0.167804,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP19",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp19"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp19(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (RCP 1.9).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp19(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp19 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.190979,
        0.212475,
        0.22977,
        0.240821,
        0.246385,
        0.248219,
        0.247229,
        0.244504,
        0.240289,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp19",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp26"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp26(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (RCP 2.6).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp26(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp26 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.190994,
        0.213422,
        0.233756,
        0.249976,
        0.262045,
        0.270751,
        0.275577,
        0.277001,
        0.27603,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp26",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP34",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp34"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp34(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (SSP 2 RCP 34).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp34(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp34 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.191089,
        0.214084,
        0.235924,
        0.254871,
        0.270427,
        0.282841,
        0.291311,
        0.29594,
        0.298074,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp34",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp45"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp45(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (SSP2 RCP 4.5).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp45(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp45 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.191135,
        0.21432,
        0.236786,
        0.257099,
        0.274837,
        0.289969,
        0.301271,
        0.308584,
        0.312947,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp45",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp60"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp60(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (SSP2 RCP 6.0).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp60(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp60 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.191189,
        0.214542,
        0.237486,
        0.258855,
        0.278363,
        0.296147,
        0.311316,
        0.324115,
        0.335382,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp60",
)


@component.add(
    name="TABLE N2O Radiative Forcing SSP2 RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp85"
    },
)
def table_n2o_radiative_forcing_ssp2_rcp85(x, final_subs=None):
    """
    Data series for future projections of N2O radiative forcing by MESSAGE-GLOBIOM (SSP2 RCP 8.5).
    """
    return _hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp85(x, final_subs)


_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp85 = HardcodedLookups(
    [2010.0, 2020.0, 2030.0, 2040.0, 2050.0, 2060.0, 2070.0, 2080.0, 2090.0, 2100.0],
    [
        0.167804,
        0.191292,
        0.215286,
        0.239765,
        0.263741,
        0.286982,
        0.30948,
        0.331141,
        0.352599,
        0.374267,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_n2o_radiative_forcing_ssp2_rcp85",
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing"
    },
)
def table_other_anthropogenic_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of other radiative forcing. 2005 AND 2010 from the SSP database, SSP2 Message-GLOBIOM (marker). Calculated as (total forcing) - (CO2, CH4, N2O and F-Gases forcings)
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing(x, final_subs)


_hardcodedlookup_table_other_anthropogenic_radiative_forcing = HardcodedLookups(
    [1900.0, 2005.0],
    [0.0, -0.557989],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_anthropogenic_radiative_forcing",
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP19",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp19"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp19(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 1.9.
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp19(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp19 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.487374,
            -0.397824,
            -0.230515,
            -0.210926,
            -0.27021,
            -0.319045,
            -0.350269,
            -0.372422,
            -0.388618,
            -0.39696,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp19",
    )
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp26"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp26(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by Message-GLOBIOM (SSP2 marker model) in RCP 2.6.
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp26(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp26 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.487232,
            -0.399799,
            -0.306337,
            -0.244383,
            -0.274545,
            -0.331504,
            -0.375821,
            -0.401136,
            -0.411268,
            -0.411342,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp26",
    )
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP34",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp34"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp34(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by MESSAGE-GLOBIOM (RCP 3.4).
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp34(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp34 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.487367,
            -0.405055,
            -0.362333,
            -0.311911,
            -0.331126,
            -0.356647,
            -0.378118,
            -0.400985,
            -0.420509,
            -0.426015,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp34",
    )
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp45"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp45(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by MESSAGE-GLOBIOM in SSP2 RCP 4.5.
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp45(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp45 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.487489,
            -0.40917,
            -0.40208,
            -0.36824,
            -0.38091,
            -0.404117,
            -0.425465,
            -0.437686,
            -0.43453,
            -0.434378,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp45",
    )
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp60"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp60(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by MESSAGE-GLOBIOM (RCP 6.0).
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp60(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp60 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.487543,
            -0.411289,
            -0.431191,
            -0.416421,
            -0.435845,
            -0.461476,
            -0.470064,
            -0.486857,
            -0.499783,
            -0.500466,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp60",
    )
)


@component.add(
    name="TABLE Other Anthropogenic Radiative Forcing SSP2 RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp85"
    },
)
def table_other_anthropogenic_radiative_forcing_ssp2_rcp85(x, final_subs=None):
    """
    Data series for future projections of other radiative forcing by MESSAGE-GLOBIOM (RCP 8.5).
    """
    return _hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp85(
        x, final_subs
    )


_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp85 = (
    HardcodedLookups(
        [
            2005.0,
            2010.0,
            2020.0,
            2030.0,
            2040.0,
            2050.0,
            2060.0,
            2070.0,
            2080.0,
            2090.0,
            2100.0,
        ],
        [
            -0.557989,
            -0.48777,
            -0.415208,
            -0.439654,
            -0.432948,
            -0.454012,
            -0.477328,
            -0.486185,
            -0.499955,
            -0.503879,
            -0.497409,
        ],
        {},
        "interpolate",
        {},
        "_hardcodedlookup_table_other_anthropogenic_radiative_forcing_ssp2_rcp85",
    )
)


@component.add(
    name="TABLE Other Radiative Forcing",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={"__lookup__": "_hardcodedlookup_table_other_radiative_forcing"},
)
def table_other_radiative_forcing(x, final_subs=None):
    """
    Data series for historical data of other factors radiative forcing.
    """
    return _hardcodedlookup_table_other_radiative_forcing(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing = HardcodedLookups(
    [
        1900.0,
        1910.0,
        1920.0,
        1930.0,
        1940.0,
        1950.0,
        1960.0,
        1970.0,
        1980.0,
        1990.0,
        2000.0,
        2005.0,
    ],
    [
        -0.234,
        -0.282,
        -0.287,
        -0.301,
        -0.301,
        -0.369,
        -0.461,
        -0.523,
        -0.618,
        -0.681,
        -0.781,
        -0.766,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing",
)


@component.add(
    name="TABLE Other Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_radiative_forcing_aim_rcp60"
    },
)
def table_other_radiative_forcing_aim_rcp60(x, final_subs=None):
    """
    Data series for future projections of other factors radiative forcing by AIM (RCP 6.0).
    """
    return _hardcodedlookup_table_other_radiative_forcing_aim_rcp60(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing_aim_rcp60 = HardcodedLookups(
    [
        2000.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [
        -0.781,
        -0.751,
        -0.671,
        -0.573,
        -0.575,
        -0.521,
        -0.509,
        -0.386,
        -0.32,
        -0.322,
        -0.328,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing_aim_rcp60",
)


@component.add(
    name="TABLE Other Radiative Forcing AIM SSP3 RCP7",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_radiative_forcing_aim_ssp3_rcp7"
    },
)
def table_other_radiative_forcing_aim_ssp3_rcp7(x, final_subs=None):
    """
    Data series for future projections of other factors radiative forcing by AIM (RCP 7).
    """
    return _hardcodedlookup_table_other_radiative_forcing_aim_ssp3_rcp7(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing_aim_ssp3_rcp7 = HardcodedLookups(
    [
        2005.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [
        -1.115,
        -1.06,
        -1.088,
        -1.09,
        -1.079,
        -1.081,
        -1.069,
        -1.057,
        -1.043,
        -1.017,
        -0.983,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing_aim_ssp3_rcp7",
)


@component.add(
    name="TABLE Other Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_radiative_forcing_image_rcp26"
    },
)
def table_other_radiative_forcing_image_rcp26(x, final_subs=None):
    """
    Data series for future projections of other factors radiative forcing by IMAGE (RCP 2.6).
    """
    return _hardcodedlookup_table_other_radiative_forcing_image_rcp26(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing_image_rcp26 = HardcodedLookups(
    [
        2000.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [
        -0.781,
        -0.717,
        -0.577,
        -0.489,
        -0.427,
        -0.413,
        -0.432,
        -0.418,
        -0.382,
        -0.353,
        -0.323,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing_image_rcp26",
)


@component.add(
    name="TABLE Other Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_radiative_forcing_message_rcp85"
    },
)
def table_other_radiative_forcing_message_rcp85(x, final_subs=None):
    """
    Data series for future projections of other factors radiative forcing by MESSAGE (RCP 8.5).
    """
    return _hardcodedlookup_table_other_radiative_forcing_message_rcp85(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing_message_rcp85 = HardcodedLookups(
    [
        2000.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [
        -0.781,
        -0.696,
        -0.648,
        -0.573,
        -0.452,
        -0.341,
        -0.274,
        -0.226,
        -0.189,
        -0.121,
        -0.088,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing_message_rcp85",
)


@component.add(
    name="TABLE Other Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Lookup",
    comp_subtype="Normal",
    depends_on={
        "__lookup__": "_hardcodedlookup_table_other_radiative_forcing_minicam_rcp45"
    },
)
def table_other_radiative_forcing_minicam_rcp45(x, final_subs=None):
    """
    Data series for future projections of other factors radiative forcing by MiniCAM (RCP 4.5).
    """
    return _hardcodedlookup_table_other_radiative_forcing_minicam_rcp45(x, final_subs)


_hardcodedlookup_table_other_radiative_forcing_minicam_rcp45 = HardcodedLookups(
    [
        2000.0,
        2010.0,
        2020.0,
        2030.0,
        2040.0,
        2050.0,
        2060.0,
        2070.0,
        2080.0,
        2090.0,
        2100.0,
    ],
    [
        -0.781,
        -0.713,
        -0.605,
        -0.518,
        -0.431,
        -0.344,
        -0.296,
        -0.257,
        -0.226,
        -0.227,
        -0.224,
    ],
    {},
    "interpolate",
    {},
    "_hardcodedlookup_table_other_radiative_forcing_minicam_rcp45",
)


@component.add(
    name="Temperature Anomalies GISS v Preindustrial",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"temperature_change_from_preindustrial": 1},
)
def temperature_anomalies_giss_v_preindustrial():
    """
    Historical values of temperature anomalies of the Atmosphere and Upper Ocean as by GISS. Source: NASA Goddard Institute for Space Studies, http://data.giss.nasa.gov/gistemp/graphs_v3/
    """
    return temperature_change_from_preindustrial()


@component.add(
    name="Temperature Anomalies HadCRUT4 v Preindustrial",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"temperature_change_from_preindustrial": 1},
)
def temperature_anomalies_hadcrut4_v_preindustrial():
    """
    Historical values of temperature anomalies of the Atmosphere and Upper Ocean as by HadCRUT4. Source: Met Office Hadley Centre http://www.metoffice.gov.uk/hadobs/hadcrut4/data/versions/HadCRUT.4.1.1.0_r elease_notes.html
    """
    return temperature_change_from_preindustrial()


@component.add(
    name="Temperature Change from Preindustrial",
    units="DegreesC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_in_atmosphere_and_upper_ocean": 1,
        "atmospheric_and_upper_ocean_heat_capacity": 1,
    },
)
def temperature_change_from_preindustrial():
    """
    Temperature of the Atmosphere and Upper Ocean and how it has changed from preindustrial period.
    """
    return (
        heat_in_atmosphere_and_upper_ocean()
        / atmospheric_and_upper_ocean_heat_capacity()
    )


@component.add(
    name="Terrestrial carbon sink",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"flux_atmosphere_to_biomass": 1, "flux_biomass_to_atmosphere": 1},
)
def terrestrial_carbon_sink():
    return flux_atmosphere_to_biomass() - flux_biomass_to_atmosphere()


@component.add(
    name="Ton to G CH4",
    units="gCH4/TonCH4",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ton_to_g_ch4():
    return 1000000.0


@component.add(
    name="Ton to g N2O",
    units="gN2O/TonN2O",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ton_to_g_n2o():
    return 1000000.0


@component.add(
    name="TonCH4 to ppb",
    units="ppb/TonCH4",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ppb": 1,
        "ton_to_g_ch4": 1,
        "molar_mass_of_ch4": 1,
        "total_moles_of_air_in_atmosphere": 1,
    },
)
def tonch4_to_ppb():
    return (
        ppb()
        * ton_to_g_ch4()
        / molar_mass_of_ch4()
        / total_moles_of_air_in_atmosphere()
    )


@component.add(
    name="TonN2O to ppb",
    units="ppb/TonN2O",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ppb": 1,
        "ton_to_g_n2o": 1,
        "molar_mass_of_n2o": 1,
        "total_moles_of_air_in_atmosphere": 1,
    },
)
def tonn2o_to_ppb():
    return (
        ppb()
        * ton_to_g_n2o()
        / molar_mass_of_n2o()
        / total_moles_of_air_in_atmosphere()
    )


@component.add(
    name="Total C Emission",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_co2_emissions": 1, "co2_to_c": 1},
)
def total_c_emission():
    """
    Emissions of carbon from energy use and other sources.
    """
    return total_co2_emissions() / co2_to_c()


@component.add(
    name="Total CH4 Breakdown",
    units="TonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ch4_in_atmosphere": 1, "atmospheric_lifetime_of_ch4": 1},
)
def total_ch4_breakdown():
    """
    Oxidation Losses
    """
    return ch4_in_atmosphere() / atmospheric_lifetime_of_ch4()


@component.add(
    name="Total CH4 Emission",
    units="TonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_ch4_emissions": 1},
)
def total_ch4_emission():
    return total_ch4_emissions()


@component.add(
    name="Total CH4 Emissions",
    units="TonCH4/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_ch4_emissions():
    return 1


@component.add(
    name="Total N2O Emissions",
    units="TonCO2/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_n2o_emissions():
    return 1


@component.add(
    name="Total moles of air in atmosphere",
    units="mol",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_moles_of_air_in_atmosphere():
    return 1.77e20


@component.add(
    name="Total N2O Breakdown",
    units="TonN2O/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"n2o_in_atmosphere": 1, "atmospheric_lifetime_of_n2o": 1},
)
def total_n2o_breakdown():
    return n2o_in_atmosphere() / atmospheric_lifetime_of_n2o()


@component.add(
    name="Total N2O Emission",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_n2o_emissions": 1},
)
def total_n2o_emission():
    return total_n2o_emissions()


@component.add(
    name="Total Radiative Forcing",
    units="W/(m*m)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "ch4_radiative_forcing_new": 1,
        "co2_radiative_forcing_new": 1,
        "n2o_radiative_forcing_new": 1,
        "other_forcings": 1,
    },
)
def total_radiative_forcing():
    """
    Radiative forcing from various factors in the atmosphere. Source of Historical Data: IIASA RCP Database https://tntcat.iiasa.ac.at:8743/RcpDb/dsd?Action=htmlpage&page=welcome
    """
    return (
        ch4_radiative_forcing_new()
        + co2_radiative_forcing_new()
        + n2o_radiative_forcing_new()
        + other_forcings()
    )


@component.add(
    name="Total Radiative Forcing AIM RCP60",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_radiative_forcing_aim_rcp60():
    """
    Future projections of total radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by AIM (RCP 6.0).
    """
    return 0


@component.add(
    name="Total Radiative Forcing IMAGE RCP26",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_radiative_forcing_image_rcp26():
    """
    Future projections of total radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by IMAGE (RCP 2.6).
    """
    return 0


@component.add(
    name="Total Radiative Forcing MESSAGE RCP85",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_radiative_forcing_message_rcp85():
    """
    Future projections of total radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MESSAGE (RCP 8.5).
    """
    return 0


@component.add(
    name="Total Radiative Forcing MiniCAM RCP45",
    units="W/(Meter*Meter)",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_radiative_forcing_minicam_rcp45():
    """
    Future projections of total radiative forcing from Representative Concentration Pathways prepared for the Fifth Assessment Report of the United Nations Intergovernmental Panel on Climate Change by MiniCAM (RCP 4.5).
    """
    return 0


@component.add(
    name="Upper Layer Volume Vu",
    units="Meter*Meter*Meter",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "area": 1,
        "mixed_layer_depth": 1,
        "land_thickness": 1,
        "land_area_fraction": 2,
    },
)
def upper_layer_volume_vu():
    """
    Water equivalent volume of the upper box, which is a weighted combination of land, atmosphere,and upper ocean volumes.
    """
    return area() * (
        land_area_fraction() * land_thickness()
        + (1 - land_area_fraction()) * mixed_layer_depth()
    )


@component.add(
    name="Volumetric Heat Capacity",
    units="Year*W/(Meter*Meter*Meter*DegreesC)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "mass_heat_capacity": 1,
        "watt_per_j_s": 1,
        "sec_per_year": 1,
        "density": 1,
    },
)
def volumetric_heat_capacity():
    """
    Volumetric heat capacity of water, i.e., amount of heat in watt*year required to raise 1 cubic meter of water by one degree C.
    """
    return mass_heat_capacity() * watt_per_j_s() / sec_per_year() * density()


@component.add(
    name="Watt per J s", units="W/(J/sec)", comp_type="Constant", comp_subtype="Normal"
)
def watt_per_j_s():
    """
    Conversion from J/s to watts.
    """
    return 1
