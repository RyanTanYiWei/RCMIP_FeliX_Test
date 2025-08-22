"""
Python model 'ClimateModule_NaturalEmissions.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else, ramp
from pysd.py_backend.statefuls import Initial, Integ, Smooth
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
    name="Airborne Fraction",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_c_emission": 2,
        "ch4_oxidation": 1,
        "flux_humus_to_atmosphere": 1,
        "flux_biomass_to_atmosphere": 1,
        "flux_atmosphere_to_biomass": 1,
        "flux_atmosphere_to_ocean": 1,
    },
)
def airborne_fraction():
    return (
        total_c_emission()
        + ch4_oxidation()
        + flux_humus_to_atmosphere()
        + flux_biomass_to_atmosphere()
        - flux_atmosphere_to_biomass()
        - flux_atmosphere_to_ocean()
    ) / float(np.maximum(total_c_emission(), 1))


@component.add(
    name="Total CH4 Emission in MTonCH4",
    units="MTonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_ch4_emission": 1, "total_ch4_breakdown": 1, "mt_ch4_to_tch4": 1},
)
def total_ch4_emission_in_mtonch4():
    return (total_ch4_emission() - total_ch4_breakdown()) / mt_ch4_to_tch4()


@component.add(
    name="Net Primary Productivity",
    units="MTonCO2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "co2_to_c": 1,
        "flux_atmosphere_to_biomass": 1,
        "flux_biomass_to_humus": 1,
        "tonco2_to_mtonco2": 1,
    },
)
def net_primary_productivity():
    return (
        co2_to_c()
        * (flux_atmosphere_to_biomass() - flux_biomass_to_humus())
        * tonco2_to_mtonco2()
    )


@component.add(
    name="Heat Content 0 700m",
    units="ZJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_1": 1, "conversion_to_zj": 1},
)
def heat_content_0_700m():
    return heat_in_deep_ocean_1() * conversion_to_zj()


@component.add(
    name="Heat Content 700 2000m",
    units="ZJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"heat_in_deep_ocean_2": 1, "conversion_to_zj": 1},
)
def heat_content_700_2000m():
    return heat_in_deep_ocean_2() * conversion_to_zj()


@component.add(
    name="Heat Content Ocean",
    units="ZJ",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "heat_in_deep_ocean_1": 1,
        "heat_in_deep_ocean_2": 1,
        "heat_in_deep_ocean_3": 1,
        "conversion_to_zj": 1,
    },
)
def heat_content_ocean():
    return (
        heat_in_deep_ocean_1() + heat_in_deep_ocean_2() + heat_in_deep_ocean_3()
    ) * conversion_to_zj()


@component.add(
    name="Effective Sensitivity of Temperature on N2O Flux",
    units="1/DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def effective_sensitivity_of_temperature_on_n2o_flux():
    return 0


@component.add(
    name="Baseline Natural Flux",
    units="TonN2O/Year",
    limits=(10000000.0, 20000000.0, 1000000.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def baseline_natural_flux():
    return 20000000.0


@component.add(
    name="Effect of Warming on N2O Release from Biological Activity",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "effective_sensitivity_of_temperature_on_n2o_flux": 1,
        "temperature_change_from_preindustrial": 1,
    },
)
def effect_of_warming_on_n2o_release_from_biological_activity():
    return (
        1
        + effective_sensitivity_of_temperature_on_n2o_flux()
        * temperature_change_from_preindustrial()
    )


@component.add(
    name="Hist Conc N2O",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def hist_conc_n2o():
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
        ],
        [
            279.454,
            279.613,
            279.861,
            280.156,
            280.432,
            280.705,
            280.98,
            281.276,
            281.611,
            281.95,
            282.314,
            282.721,
            283.019,
            283.362,
            283.716,
            284.047,
            284.312,
            284.615,
            284.805,
            284.851,
            284.929,
            285.039,
            285.17,
            285.467,
            285.605,
            285.652,
            285.692,
            285.74,
            285.833,
            285.891,
            285.938,
            286.124,
            286.222,
            286.371,
            286.467,
            286.587,
            286.747,
            286.951,
            287.191,
            287.387,
            287.619,
            287.864,
            288.138,
            288.781,
            289.0,
            289.227,
            289.427,
            289.511,
            289.556,
            289.598,
            289.739,
            289.86,
            290.025,
            290.334,
            290.548,
            290.844,
            291.187,
            291.512,
            291.772,
            291.987,
            292.283,
            292.602,
            292.945,
            293.327,
            293.685,
            294.045,
            294.453,
            294.86,
            295.269,
            295.681,
            296.098,
            296.522,
            296.955,
            297.399,
            297.855,
            298.326,
            298.814,
            299.319,
            299.845,
            300.393,
            300.965,
            301.562,
            302.187,
            302.842,
            303.528,
            304.247,
            305.002,
            305.793,
            306.624,
            307.831,
            308.683,
            309.233,
            309.725,
            310.099,
            310.808,
            311.279,
            312.298,
            313.183,
            313.907,
            314.709,
            315.759,
            316.493,
            317.101,
            317.73,
            318.357,
            319.13,
            319.933,
            320.646,
            321.575,
            322.275,
            323.141,
            324.159,
            325.005,
            325.919,
            326.988,
        ],
    )


@component.add(
    name="Net Ocean to Atmosphere Flux CO2",
    units="MTonCO2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"flux_atmosphere_to_ocean": 1, "tonco2_to_mtonco2": 1, "co2_to_c": 1},
)
def net_ocean_to_atmosphere_flux_co2():
    return -flux_atmosphere_to_ocean() * tonco2_to_mtonco2() * co2_to_c()


@component.add(
    name="Heat Uptake",
    units="ZJ/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "effective_radiative_forcing": 1,
        "feedback_cooling": 1,
        "conversion_to_zj": 1,
    },
)
def heat_uptake():
    return (effective_radiative_forcing() + feedback_cooling()) * conversion_to_zj()


@component.add(
    name="J to ZJ", units="J/ZJ", comp_type="Constant", comp_subtype="Normal"
)
def j_to_zj():
    return 1e21


@component.add(
    name="second to years",
    units="sec/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def second_to_years():
    return 60 * 60 * 24 * 365.24


@component.add(
    name="Conversion to ZJ",
    units="m*m*ZJ/(W*Year)",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "earth_surface_area": 1,
        "second_to_years": 1,
        "unit_w_to_js": 1,
        "j_to_zj": 1,
    },
)
def conversion_to_zj():
    return earth_surface_area() * second_to_years() * unit_w_to_js() / j_to_zj()


@component.add(
    name='"unit W to J/s"', units="J/sec/W", comp_type="Constant", comp_subtype="Normal"
)
def unit_w_to_js():
    return 1


@component.add(
    name="Carbon Pool Atmosphere",
    units="MTonCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_atmosphere": 1, "co2_to_c": 1, "tonco2_to_mtonco2": 1},
)
def carbon_pool_atmosphere():
    return c_in_atmosphere() * co2_to_c() * tonco2_to_mtonco2()


@component.add(
    name="Carbon Pool Plant",
    units="MTonCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_biomass": 1, "co2_to_c": 1, "tonco2_to_mtonco2": 1},
)
def carbon_pool_plant():
    return c_in_biomass() * co2_to_c() * tonco2_to_mtonco2()


@component.add(
    name="Carbon Pool Soil",
    units="MTonCO2",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"c_in_humus": 1, "co2_to_c": 1, "tonco2_to_mtonco2": 1},
)
def carbon_pool_soil():
    return c_in_humus() * co2_to_c() * tonco2_to_mtonco2()


@component.add(
    name="KtN2O to tN2O",
    units="TonN2O/KTonN2O",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ktn2o_to_tn2o():
    return 1000


@component.add(
    name="Mt CH4 to tCH4",
    units="TonCH4/MTonCH4",
    comp_type="Constant",
    comp_subtype="Normal",
)
def mt_ch4_to_tch4():
    return 1000000.0


@component.add(
    name="Net Land to Atmosphere Flux CO2",
    units="MTonCO2/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "flux_biomass_to_atmosphere": 1,
        "flux_humus_to_atmosphere": 1,
        "flux_atmosphere_to_biomass": 1,
        "tonco2_to_mtonco2": 1,
        "co2_to_c": 1,
    },
)
def net_land_to_atmosphere_flux_co2():
    return (
        (
            flux_biomass_to_atmosphere()
            + flux_humus_to_atmosphere()
            - flux_atmosphere_to_biomass()
        )
        * tonco2_to_mtonco2()
        * co2_to_c()
    )


@component.add(
    name="TonCO2 to MTonCO2",
    units="MTonCO2/TonCO2",
    comp_type="Constant",
    comp_subtype="Normal",
)
def tonco2_to_mtonco2():
    return 1e-06


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
    name="Natural N2O Emission",
    units="TonN2O/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "baseline_natural_flux": 1,
        "effect_of_warming_on_n2o_release_from_biological_activity": 1,
    },
)
def natural_n2o_emission():
    return (
        baseline_natural_flux()
        * effect_of_warming_on_n2o_release_from_biological_activity()
    )


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
    name="Atmospheric Lifetime of N2O",
    units="Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_lifetime_of_n2o():
    return 103.322


@component.add(
    name="Earth Surface Area", units="m*m", comp_type="Constant", comp_subtype="Normal"
)
def earth_surface_area():
    return 510064000000000.0


@component.add(
    name="Total N2O Emission",
    units="TonN2O/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_n2o_emissions": 1,
        "ktn2o_to_tn2o": 1,
        "natural_n2o_emission": 1,
    },
)
def total_n2o_emission():
    return total_n2o_emissions() * ktn2o_to_tn2o() + natural_n2o_emission()


@component.add(
    name="Total CH4 Emission",
    units="TonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "total_ch4_emissions": 1,
        "mt_ch4_to_tch4": 1,
        "natural_ch4_emissions_flux_biosphere_to_ch4_natural": 1,
    },
)
def total_ch4_emission():
    return (
        total_ch4_emissions() * mt_ch4_to_tch4()
        + natural_ch4_emissions_flux_biosphere_to_ch4_natural()
    )


@component.add(
    name="C in Humus",
    units="TonC",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_c_in_humus": 1},
    other_deps={
        "_integ_c_in_humus": {
            "initial": {"init_c_in_humus": 1},
            "step": {
                "flux_biomass_to_humus": 1,
                "flux_humus_to_atmosphere": 1,
                "flux_humus_to_ch4": 1,
            },
        }
    },
)
def c_in_humus():
    """
    Carbon in humus.
    """
    return _integ_c_in_humus()


_integ_c_in_humus = Integ(
    lambda: flux_biomass_to_humus() - flux_humus_to_atmosphere() - flux_humus_to_ch4(),
    lambda: init_c_in_humus(),
    "_integ_c_in_humus",
)


@component.add(
    name="Fractional Rate of CH4 Released from Humus to Atm",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fractional_rate_of_ch4_released_from_humus_to_atm():
    return 0.00015


@component.add(
    name="CH4 Oxidation",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ch4_to_co2_via_oxidation_in_tonc": 1},
)
def ch4_oxidation():
    return ch4_to_co2_via_oxidation_in_tonc()


@component.add(
    name="C to CH4", units="TonCH4/TonC", comp_type="Constant", comp_subtype="Normal"
)
def c_to_ch4():
    return 16 / 12


@component.add(
    name="Flux Humus to CH4",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_humus": 1,
        "fractional_rate_of_ch4_released_from_humus_to_atm": 1,
        "effect_of_warming_on_ch4_release_from_biological_activity": 1,
    },
)
def flux_humus_to_ch4():
    """
    Does not factor C release from Permafrost and Clathrate
    """
    return c_in_humus() * (
        fractional_rate_of_ch4_released_from_humus_to_atm()
        * effect_of_warming_on_ch4_release_from_biological_activity()
    )


@component.add(
    name="Flux Biomass to CH4",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "c_in_biomass": 1,
        "effect_of_warming_on_ch4_release_from_biological_activity": 1,
        "fractional_rate_of_ch4_released_from_biomass_to_atm": 1,
    },
)
def flux_biomass_to_ch4():
    return (
        c_in_biomass()
        * effect_of_warming_on_ch4_release_from_biological_activity()
        * fractional_rate_of_ch4_released_from_biomass_to_atm()
    )


@component.add(
    name="Effect of Temperature on Land CH4 Flux",
    units="1/DegreesC",
    comp_type="Constant",
    comp_subtype="Normal",
)
def effect_of_temperature_on_land_ch4_flux():
    return 0.01


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
                "flux_biomass_to_ch4": 1,
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
    - flux_biomass_to_ch4()
    - flux_biomass_to_humus(),
    lambda: init_c_in_biomass(),
    "_integ_c_in_biomass",
)


@component.add(
    name="Fractional Rate of CH4 Released from Biomass to Atm",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def fractional_rate_of_ch4_released_from_biomass_to_atm():
    return 1e-05


@component.add(
    name="Effect of Warming on CH4 Release from Biological Activity",
    units="Dmnl",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "effect_of_temperature_on_land_ch4_flux": 1,
        "temperature_change_from_preindustrial": 1,
    },
)
def effect_of_warming_on_ch4_release_from_biological_activity():
    return 1 / (
        1
        - effect_of_temperature_on_land_ch4_flux()
        * temperature_change_from_preindustrial()
    )


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
                "ch4_oxidation": 1,
                "flux_biomass_to_atmosphere": 1,
                "flux_humus_to_atmosphere": 1,
                "total_c_emission": 1,
                "carbon_removal_rate": 1,
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
    lambda: ch4_oxidation()
    + flux_biomass_to_atmosphere()
    + flux_humus_to_atmosphere()
    + total_c_emission()
    - carbon_removal_rate()
    - flux_atmosphere_to_biomass()
    - flux_atmosphere_to_ocean(),
    lambda: init_c_in_atmosphere(),
    "_integ_c_in_atmosphere",
)


@component.add(
    name="Natural CH4 Emissions Flux Biosphere to CH4 Natural",
    units="TonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"flux_biomass_to_ch4": 1, "flux_humus_to_ch4": 1, "c_to_ch4": 1},
)
def natural_ch4_emissions_flux_biosphere_to_ch4_natural():
    return (flux_biomass_to_ch4() + flux_humus_to_ch4()) * c_to_ch4()


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
    name="Natural CH4 Emissions",
    units="TonCH4/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def natural_ch4_emissions():
    """
    There is a substantial discrepancy between estimates of natural global annual methane emissions from bottom-up and top-down methods, which yield values of 370 Mt and 215 Mt, respectively (Saunois et al. 2020). UNEP Global Methane Assessment 2030 Baseline Report
    """
    return 230000000.0


@component.add(
    name="ss370 Conc N2O",
    units="ppb",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def ss370_conc_n2o():
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2015.0,
            2016.0,
            2017.0,
            2018.0,
            2019.0,
            2020.0,
            2021.0,
            2022.0,
            2023.0,
            2024.0,
            2025.0,
            2026.0,
            2027.0,
            2028.0,
            2029.0,
            2030.0,
            2031.0,
            2032.0,
            2033.0,
            2034.0,
            2035.0,
            2036.0,
            2037.0,
            2038.0,
            2039.0,
            2040.0,
            2041.0,
            2042.0,
            2043.0,
            2044.0,
            2045.0,
            2046.0,
            2047.0,
            2048.0,
            2049.0,
            2050.0,
            2051.0,
            2052.0,
            2053.0,
            2054.0,
            2055.0,
            2056.0,
            2057.0,
            2058.0,
            2059.0,
            2060.0,
            2061.0,
            2062.0,
            2063.0,
            2064.0,
            2065.0,
            2066.0,
            2067.0,
            2068.0,
            2069.0,
            2070.0,
            2071.0,
            2072.0,
            2073.0,
            2074.0,
            2075.0,
            2076.0,
            2077.0,
            2078.0,
            2079.0,
            2080.0,
            2081.0,
            2082.0,
            2083.0,
            2084.0,
            2085.0,
            2086.0,
            2087.0,
            2088.0,
            2089.0,
            2090.0,
            2091.0,
            2092.0,
            2093.0,
            2094.0,
            2095.0,
            2096.0,
            2097.0,
            2098.0,
            2099.0,
            2100.0,
        ],
        [
            279.454,
            279.613,
            279.861,
            280.156,
            280.432,
            280.705,
            280.98,
            281.276,
            281.611,
            281.95,
            282.314,
            282.721,
            283.019,
            283.362,
            283.716,
            284.047,
            284.312,
            284.615,
            284.805,
            284.851,
            284.929,
            285.039,
            285.17,
            285.467,
            285.605,
            285.652,
            285.692,
            285.74,
            285.833,
            285.891,
            285.938,
            286.124,
            286.222,
            286.371,
            286.467,
            286.587,
            286.747,
            286.951,
            287.191,
            287.387,
            287.619,
            287.864,
            288.138,
            288.781,
            289.0,
            289.227,
            289.427,
            289.511,
            289.556,
            289.598,
            289.739,
            289.86,
            290.025,
            290.334,
            290.548,
            290.844,
            291.187,
            291.512,
            291.772,
            291.987,
            292.283,
            292.602,
            292.945,
            293.327,
            293.685,
            294.045,
            294.453,
            294.86,
            295.269,
            295.681,
            296.098,
            296.522,
            296.955,
            297.399,
            297.855,
            298.326,
            298.814,
            299.319,
            299.845,
            300.393,
            300.965,
            301.562,
            302.187,
            302.842,
            303.528,
            304.247,
            305.002,
            305.793,
            306.624,
            307.831,
            308.683,
            309.233,
            309.725,
            310.099,
            310.808,
            311.279,
            312.298,
            313.183,
            313.907,
            314.709,
            315.759,
            316.493,
            317.101,
            317.73,
            318.357,
            319.13,
            319.933,
            320.646,
            321.575,
            322.275,
            323.141,
            324.159,
            325.005,
            325.919,
            326.988,
            328.18,
            329.076,
            329.791,
            330.565,
            331.356,
            332.164,
            332.989,
            333.83,
            334.684,
            335.552,
            336.432,
            337.327,
            338.234,
            339.154,
            340.088,
            341.034,
            341.993,
            342.963,
            343.941,
            344.928,
            345.924,
            346.928,
            347.941,
            348.962,
            349.991,
            351.029,
            352.075,
            353.128,
            354.187,
            355.253,
            356.325,
            357.403,
            358.487,
            359.577,
            360.674,
            361.776,
            362.884,
            363.998,
            365.116,
            366.238,
            367.364,
            368.495,
            369.63,
            370.77,
            371.913,
            373.061,
            374.212,
            375.368,
            376.528,
            377.691,
            378.858,
            380.028,
            381.203,
            382.38,
            383.562,
            384.747,
            385.935,
            387.127,
            388.322,
            389.52,
            390.721,
            391.924,
            393.131,
            394.341,
            395.553,
            396.769,
            397.987,
            399.208,
            400.434,
            401.663,
            402.897,
            404.134,
            405.375,
            406.62,
            407.868,
            409.12,
            410.376,
            411.636,
            412.898,
            414.165,
            415.434,
            416.707,
            417.982,
            419.261,
            420.544,
            421.829,
        ],
    )


@component.add(
    name="ss370 Conc CH4",
    units="ppb",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def ss370_conc_ch4():
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2015.0,
            2016.0,
            2017.0,
            2018.0,
            2019.0,
            2020.0,
            2021.0,
            2022.0,
            2023.0,
            2024.0,
            2025.0,
            2026.0,
            2027.0,
            2028.0,
            2029.0,
            2030.0,
            2031.0,
            2032.0,
            2033.0,
            2034.0,
            2035.0,
            2036.0,
            2037.0,
            2038.0,
            2039.0,
            2040.0,
            2041.0,
            2042.0,
            2043.0,
            2044.0,
            2045.0,
            2046.0,
            2047.0,
            2048.0,
            2049.0,
            2050.0,
            2051.0,
            2052.0,
            2053.0,
            2054.0,
            2055.0,
            2056.0,
            2057.0,
            2058.0,
            2059.0,
            2060.0,
            2061.0,
            2062.0,
            2063.0,
            2064.0,
            2065.0,
            2066.0,
            2067.0,
            2068.0,
            2069.0,
            2070.0,
            2071.0,
            2072.0,
            2073.0,
            2074.0,
            2075.0,
            2076.0,
            2077.0,
            2078.0,
            2079.0,
            2080.0,
            2081.0,
            2082.0,
            2083.0,
            2084.0,
            2085.0,
            2086.0,
            2087.0,
            2088.0,
            2089.0,
            2090.0,
            2091.0,
            2092.0,
            2093.0,
            2094.0,
            2095.0,
            2096.0,
            2097.0,
            2098.0,
            2099.0,
            2100.0,
        ],
        [
            925.552,
            928.8,
            932.731,
            936.783,
            942.114,
            947.443,
            953.092,
            959.156,
            964.085,
            969.398,
            974.787,
            979.465,
            983.606,
            986.242,
            988.611,
            991.461,
            998.454,
            1003.57,
            1010.13,
            1017.63,
            1025.07,
            1032.2,
            1039.1,
            1045.13,
            1049.45,
            1052.16,
            1053.6,
            1055.77,
            1060.64,
            1066.66,
            1072.64,
            1077.49,
            1081.96,
            1086.54,
            1091.77,
            1097.08,
            1101.83,
            1106.32,
            1110.63,
            1116.91,
            1120.12,
            1123.24,
            1128.19,
            1132.66,
            1136.27,
            1139.32,
            1143.66,
            1149.64,
            1155.63,
            1160.35,
            1163.82,
            1168.81,
            1174.31,
            1183.36,
            1194.43,
            1206.65,
            1221.1,
            1235.8,
            1247.42,
            1257.32,
            1264.12,
            1269.46,
            1282.57,
            1300.79,
            1317.37,
            1331.06,
            1342.24,
            1354.27,
            1371.65,
            1389.34,
            1411.1,
            1431.12,
            1449.29,
            1462.86,
            1476.14,
            1491.74,
            1509.11,
            1527.68,
            1546.89,
            1566.16,
            1584.94,
            1602.65,
            1618.73,
            1632.62,
            1643.5,
            1655.91,
            1668.79,
            1683.75,
            1693.94,
            1705.63,
            1717.4,
            1729.33,
            1740.14,
            1743.1,
            1748.62,
            1755.23,
            1757.19,
            1761.5,
            1770.29,
            1778.2,
            1778.01,
            1776.53,
            1778.96,
            1783.59,
            1784.23,
            1783.36,
            1783.42,
            1788.95,
            1798.42,
            1802.1,
            1807.85,
            1813.07,
            1815.26,
            1822.58,
            1831.47,
            1841.93,
            1851.59,
            1874.51,
            1889.79,
            1905.45,
            1921.44,
            1937.74,
            1954.37,
            1971.4,
            1988.79,
            2006.51,
            2024.53,
            2042.82,
            2061.37,
            2080.15,
            2099.14,
            2118.32,
            2137.55,
            2156.7,
            2175.76,
            2194.75,
            2213.66,
            2232.5,
            2251.27,
            2269.97,
            2288.59,
            2307.15,
            2325.65,
            2344.1,
            2362.51,
            2380.87,
            2399.19,
            2417.46,
            2435.69,
            2453.87,
            2472.0,
            2490.08,
            2508.18,
            2526.34,
            2544.55,
            2562.82,
            2581.13,
            2599.48,
            2617.86,
            2636.26,
            2654.69,
            2673.13,
            2691.61,
            2710.12,
            2728.68,
            2747.26,
            2765.87,
            2784.5,
            2803.14,
            2821.8,
            2840.45,
            2859.11,
            2877.79,
            2896.52,
            2915.29,
            2934.08,
            2952.91,
            2971.75,
            2990.61,
            3009.48,
            3028.35,
            3047.22,
            3065.96,
            3084.46,
            3102.73,
            3120.78,
            3138.62,
            3156.25,
            3173.7,
            3190.97,
            3208.07,
            3225.01,
            3241.8,
            3258.48,
            3275.04,
            3291.48,
            3307.83,
            3324.06,
            3340.2,
            3356.24,
            3372.18,
        ],
    )


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
    return 9.3


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
    depends_on={"c1": 1, "dmnl_adjustment_ppb": 1, "atmospheric_concentration_n2o": 1},
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
        "a1": 2,
        "b1": 2,
        "d1": 3,
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
    name="Atmospheric CH4 Concentration 1900 AR6",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_ch4_concentration_1900_ar6():
    """
    https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_AnnexIII.p df pg 2141
    """
    return 925


@component.add(
    name="Atmospheric CH4 Concentration Preindustrial",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_ch4_concentration_preindustrial():
    return 731.41


@component.add(
    name="Atmospheric CO2 Concentration 1900 AR6",
    units="ppm",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_co2_concentration_1900_ar6():
    return 296.4


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
    name="Atmospheric N2O Concentration 1900 AR6",
    units="ppb",
    comp_type="Constant",
    comp_subtype="Normal",
)
def atmospheric_n2o_concentration_1900_ar6():
    """
    https://www.ipcc.ch/report/ar6/wg1/downloads/report/IPCC_AR6_WGI_AnnexIII.pdf pg 2141 278.9
    """
    return 278.9


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
        "buff_c_coeff": 1,
        "preindustrial_c_in_mixed_layer": 1,
        "c_in_mixed_layer": 1,
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
    depends_on={"atmospheric_co2_concentration_preindustrial": 1, "a1": 1, "b1": 1},
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
        "atmospheric_concentration_ch4": 1,
        "dmnl_adjustment_ppb": 2,
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
        "ch4_radiative_forcing_rcp45": 1,
        "rcp_scenario": 5,
        "ch4_radiative_forcing_rcp34": 1,
        "ch4_radiative_forcing_rcp85": 1,
        "ch4_radiative_forcing_rcp26": 1,
        "ch4_radiative_forcing_rcp19": 1,
        "ch4_radiative_forcing_rcp60": 1,
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
        "atmospheric_concentration_ch4": 1,
        "dmnl_adjustment_ppb": 2,
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
    name="CH4 to CO2 via Oxidation in TonC",
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "molar_mass_of_c": 1,
        "molar_mass_of_ch4": 1,
        "dmnl_adjustment_tonco2": 1,
        "total_ch4_breakdown": 1,
    },
)
def ch4_to_co2_via_oxidation_in_tonc():
    return (
        molar_mass_of_c() / molar_mass_of_ch4() / dmnl_adjustment_tonco2()
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
    units="gC*TonCH4/(gCH4*TonC)",
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
    units="W/(m*m)",
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
    units="TonCO2/Year",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def total_co2_emissions():
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2100.0,
        ],
        [
            4465.96,
            4768.88,
            4835.69,
            5115.66,
            5244.75,
            5479.76,
            5710.02,
            6046.02,
            5993.61,
            6115.29,
            6271.03,
            6113.83,
            6122.58,
            6265.77,
            5938.95,
            5864.56,
            6101.45,
            6227.24,
            6205.49,
            5833.87,
            6290.31,
            6065.15,
            6219.54,
            6673.12,
            6735.34,
            6795.89,
            6766.33,
            7280.51,
            7308.5,
            7704.45,
            7679.53,
            7335.5,
            6651.92,
            6798.48,
            7038.37,
            7216.33,
            7612.65,
            7825.86,
            7580.8,
            7836.4,
            8156.9,
            8184.23,
            8268.32,
            8410.16,
            8377.77,
            7621.09,
            8344.52,
            9027.47,
            9393.94,
            9334.31,
            10044.7,
            11290.7,
            11518.8,
            11706.3,
            12085.4,
            12923.1,
            13695.2,
            14153.1,
            14642.0,
            14941.2,
            15353.9,
            15695.8,
            16083.7,
            16722.3,
            17266.3,
            17924.5,
            18518.2,
            19135.1,
            19720.5,
            20540.2,
            21457.0,
            21678.1,
            22109.2,
            23064.2,
            22861.4,
            22836.2,
            23873.4,
            24612.4,
            25215.4,
            25589.0,
            25266.7,
            24889.5,
            24681.5,
            25343.6,
            25945.1,
            26305.7,
            26803.4,
            27328.5,
            28027.4,
            28374.7,
            27966.7,
            28681.6,
            28688.8,
            28363.3,
            28376.7,
            28815.3,
            29248.0,
            32092.8,
            29798.2,
            29186.4,
            29661.9,
            29018.3,
            29933.4,
            30509.2,
            32433.5,
            33416.6,
            34631.9,
            35352.2,
            34451.2,
            34225.4,
            36133.8,
            37266.0,
            37953.9,
            38762.7,
            39630.9,
            39630.9,
        ],
    )


@component.add(
    name="Equil C in Mixed Layer",
    units="TonC",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "preindustrial_c_in_mixed_layer": 1,
        "effect_of_temp_on_c_flux_atm_ml": 1,
        "buffer_factor": 1,
        "c_in_atmosphere": 1,
        "preindustrial_c_in_atmosphere": 1,
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
        "f_gases_radiative_forcing_rcp19": 1,
        "rcp_scenario": 5,
        "f_gases_radiative_forcing_rcp45": 1,
        "f_gases_radiative_forcing_rcp26": 1,
        "f_gases_radiative_forcing_rcp85": 1,
        "f_gases_radiative_forcing_rcp34": 1,
        "f_gases_radiative_forcing_rcp60": 1,
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
    units="W/(m*m)",
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
        "biostimulation_coefficient": 1,
        "c_in_atmosphere": 1,
        "preindustrial_c_in_atmosphere": 1,
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
        "land_area_fraction": 1,
        "area": 1,
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
        "land_area_fraction": 1,
        "area": 1,
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
        "eddy_diff_coeff_m_1": 1,
        "eddy_diff_coeff_mean_m_1": 1,
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
        "eddy_diff_coeff_2_3": 1,
        "eddy_diff_coeff_mean_2_3": 1,
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
        "eddy_diff_coeff_3_4": 1,
        "eddy_diff_coeff_mean_3_4": 1,
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
        "rcp_scenario": 4,
        "hfc_radiative_forcing_message_rcp85": 1,
        "hfc_radiative_forcing_image_rcp26": 1,
        "hfc_radiative_forcing_minicam_rcp45": 1,
        "hfc_radiative_forcing_aim_rcp60": 1,
        "hfc_radiative_forcing_aim_rcp7": 1,
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
    depends_on={"atmospheric_ch4_concentration_1900_ar6": 1, "tonch4_to_ppb": 1},
)
def init_ch4_in_atmosphere():
    return atmospheric_ch4_concentration_1900_ar6() / tonch4_to_ppb()


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
    depends_on={"atmospheric_n2o_concentration_1900_ar6": 1, "tonn2o_to_ppb": 1},
)
def init_n2o_in_atmosphere():
    return atmospheric_n2o_concentration_1900_ar6() / tonn2o_to_ppb()


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
    depends_on={"layer_depth_2": 2, "layer_depth_1": 1, "eddy_diff_coeff_1_2": 1},
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
    depends_on={"layer_depth_3": 2, "eddy_diff_coeff_2_3": 1, "layer_depth_2": 1},
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
    depends_on={"layer_depth_4": 2, "layer_depth_3": 1, "eddy_diff_coeff_3_4": 1},
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
    name="Molar mass of C", units="gC/mol", comp_type="Constant", comp_subtype="Normal"
)
def molar_mass_of_c():
    return 12.01


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
        "n2o_radiative_forcing_rcp60": 1,
        "n2o_radiative_forcing_rcp85": 1,
        "rcp_scenario": 5,
        "n2o_radiative_forcing_rcp45": 1,
        "n2o_radiative_forcing_rcp26": 1,
        "n2o_radiative_forcing_rcp34": 1,
        "n2o_radiative_forcing_rcp19": 1,
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
        "dmnl_adjustment_ppm": 1,
        "atmospheric_concentration_co2": 1,
        "dmnl_adjustment_ppb": 2,
        "b2": 1,
        "atmospheric_concentration_n2o": 1,
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
        "dmnl_adjustment_ppb": 2,
        "atmospheric_n2o_concentration_preindustrial": 1,
        "atmospheric_concentration_n2o": 1,
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
        "other_anthropogenic_radiative_forcing_rcp34": 1,
        "rcp_scenario": 5,
        "other_anthropogenic_radiative_forcing_rcp19": 1,
        "other_anhtropogenic_radiative_forcing_rcp60": 1,
        "other_anthropogenic_radiative_forcing_rcp85": 1,
        "other_anthropogenic_radiative_forcing_rcp45": 1,
        "other_anthropogenic_radiative_forcing_rcp26": 1,
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
        "rcp_scenario": 4,
        "other_radiative_forcing_message_rcp85": 1,
        "other_radiative_forcing_image_rcp26": 1,
        "other_radiative_forcing_minicam_rcp45": 1,
        "other_radiative_forcing_aim_rcp7": 1,
        "other_radiative_forcing_aim_rcp60": 1,
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
    units="TonC/Year/Year",
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
    units="1/DegreesC",
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
    units="TonC/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_co2_emissions": 1, "co2_to_c": 1},
)
def total_c_emission():
    """
    Emissions of carbon from energy use and other sources.
    """
    return total_co2_emissions() * 1000000.0 / co2_to_c()


@component.add(
    name="Total CH4 Emissions",
    units="MTonCH4/Year",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def total_ch4_emissions():
    """
    in MT CH4
    """
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2100.0,
        ],
        [
            87.6133,
            88.3912,
            89.2628,
            89.8907,
            91.3568,
            92.4013,
            93.25,
            94.5608,
            95.7124,
            96.4667,
            97.7719,
            98.4294,
            99.2661,
            100.613,
            102.284,
            103.058,
            104.089,
            105.44,
            106.746,
            108.095,
            109.134,
            109.809,
            110.486,
            112.254,
            112.634,
            113.67,
            114.546,
            115.747,
            116.796,
            118.02,
            119.67,
            119.908,
            121.422,
            122.344,
            123.953,
            124.895,
            126.465,
            127.182,
            127.905,
            129.501,
            130.135,
            132.218,
            134.706,
            136.63,
            138.931,
            141.023,
            142.706,
            144.794,
            147.272,
            150.216,
            152.201,
            155.272,
            160.573,
            165.682,
            170.371,
            174.74,
            180.671,
            186.056,
            188.386,
            192.687,
            197.261,
            205.138,
            207.212,
            216.192,
            216.556,
            222.666,
            226.311,
            232.333,
            235.335,
            239.185,
            244.418,
            249.29,
            257.21,
            260.295,
            261.808,
            263.059,
            269.948,
            274.03,
            276.333,
            281.6,
            283.346,
            279.789,
            287.669,
            281.618,
            285.003,
            285.675,
            290.808,
            295.049,
            298.685,
            302.164,
            305.273,
            318.731,
            299.402,
            299.443,
            310.252,
            305.41,
            307.291,
            331.289,
            315.333,
            309.408,
            310.187,
            312.896,
            322.279,
            328.124,
            338.942,
            346.396,
            356.47,
            355.023,
            360.492,
            364.2,
            370.896,
            372.658,
            380.81,
            381.594,
            387.874,
            387.874,
        ],
    )


@component.add(
    name="Total N2O Emissions",
    units="KTonN2O/Year",
    comp_type="Auxiliary",
    comp_subtype="with Lookup",
    depends_on={"time": 1},
)
def total_n2o_emissions():
    """
    ([(0,0)-(10,10)],(1900,1356.16),(1901,1369.1),(1902,1384.52),(1903,1399.36) ,(1904,1415.6),(1905,1432.56),(1906,1449.95),(1907,1466.75),(1908,1483.12), (1909,1499.1),(1910,1515.94),(1911,1533.71),(1912,1559.23),(1913,1589.12),( 1914,1621.62),(1915,1656.96),(1916,1693.36),(1917,1728.66),(1918,1761.61),( 1919,1791.47),(1920,1818.81),(1921,1843.61),(1922,1867.74),(1923,1893.42),( 1924,1920.28),(1925,1944.75),(1926,1968.03),(1927,1990.27),(1928,2010.73),( 1929,2028.07),(1930,2043.07),(1931,2053.98),(1932,2064.65),(1933,2073.56),( 1934,2083.43),(1935,2093.47),(1936,2103.27),(1937,2115.58),(1938,2129.1),(1 939,2147.48),(1940,2167.53),(1941,2242.12),(1942,2403.56),(1943,2636.05),(1 944,2912.5),(1945,3215.87),(1946,3522.87),(1947,3815.76),(1948,4068.7),(194 9,4264.1),(1950,4378.5),(1951,4447.58),(1952,4514.63),(1953,4585.34),(1954, 4658.92),(1955,4738.57),(1956,4819.78),(1957,4906.31),(1958,5002.82),(1959, 5106.72),(1960,5222.37),(1961,5570.29),(1962,5779.89),(1963,5976.28),(1964, 6199.34),(1965,6465.56),(1966,6773.51),(1967,7041.51),(1968,7256.01),(1969, 7435.62),(1970,7406.67),(1971,7327.06),(1972,7746.9),(1973,7935.57),(1974,7 909.79),(1975,8180.65),(1976,8409.33),(1977,8640.44),(1978,8837.87),(1979,9 123.76),(1980,9227.26),(1981,9121.12),(1982,9494.52),(1983,9530.29),(1984,9 421.16),(1985,9421.44),(1986,9620.41),(1987,9977.12),(1988,9722.72),(1989,9 842.47),(1990,9862.3),(1991,9968.82),(1992,9990.08),(1993,9915.09),(1994,10 121),(1995,10218.8),(1996,10278.8),(1997,10590.2),(1998,10128.4),(1999,9868 .59),(2000,9603.19),(2001,9722.25),(2002,9991.77),(2003,10099.8),(2004,1035 4.6),(2005,10516.6),(2006,10802.6),(2007,10363.5),(2008,10429.7),(2009,1054 6.7),(2010,10539.8),(2011,10446.4),(2012,10593.9),(2013,10759),(2014,10866. 3),(2100,10866.3) )
    """
    return np.interp(
        time(),
        [
            1900.0,
            1901.0,
            1902.0,
            1903.0,
            1904.0,
            1905.0,
            1906.0,
            1907.0,
            1908.0,
            1909.0,
            1910.0,
            1911.0,
            1912.0,
            1913.0,
            1914.0,
            1915.0,
            1916.0,
            1917.0,
            1918.0,
            1919.0,
            1920.0,
            1921.0,
            1922.0,
            1923.0,
            1924.0,
            1925.0,
            1926.0,
            1927.0,
            1928.0,
            1929.0,
            1930.0,
            1931.0,
            1932.0,
            1933.0,
            1934.0,
            1935.0,
            1936.0,
            1937.0,
            1938.0,
            1939.0,
            1940.0,
            1941.0,
            1942.0,
            1943.0,
            1944.0,
            1945.0,
            1946.0,
            1947.0,
            1948.0,
            1949.0,
            1950.0,
            1951.0,
            1952.0,
            1953.0,
            1954.0,
            1955.0,
            1956.0,
            1957.0,
            1958.0,
            1959.0,
            1960.0,
            1961.0,
            1962.0,
            1963.0,
            1964.0,
            1965.0,
            1966.0,
            1967.0,
            1968.0,
            1969.0,
            1970.0,
            1971.0,
            1972.0,
            1973.0,
            1974.0,
            1975.0,
            1976.0,
            1977.0,
            1978.0,
            1979.0,
            1980.0,
            1981.0,
            1982.0,
            1983.0,
            1984.0,
            1985.0,
            1986.0,
            1987.0,
            1988.0,
            1989.0,
            1990.0,
            1991.0,
            1992.0,
            1993.0,
            1994.0,
            1995.0,
            1996.0,
            1997.0,
            1998.0,
            1999.0,
            2000.0,
            2001.0,
            2002.0,
            2003.0,
            2004.0,
            2005.0,
            2006.0,
            2007.0,
            2008.0,
            2009.0,
            2010.0,
            2011.0,
            2012.0,
            2013.0,
            2014.0,
            2015.0,
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
            1356.16,
            1369.1,
            1384.52,
            1399.36,
            1415.6,
            1432.56,
            1449.95,
            1466.75,
            1483.12,
            1499.1,
            1515.94,
            1533.71,
            1559.23,
            1589.12,
            1621.62,
            1656.96,
            1693.36,
            1728.66,
            1761.61,
            1791.47,
            1818.81,
            1843.61,
            1867.74,
            1893.42,
            1920.28,
            1944.75,
            1968.03,
            1990.27,
            2010.73,
            2028.07,
            2043.07,
            2053.98,
            2064.65,
            2073.56,
            2083.43,
            2093.47,
            2103.27,
            2115.58,
            2129.1,
            2147.48,
            2167.53,
            2242.12,
            2403.56,
            2636.05,
            2912.5,
            3215.87,
            3522.87,
            3815.76,
            4068.7,
            4264.1,
            4378.5,
            4447.58,
            4514.63,
            4585.34,
            4658.92,
            4738.57,
            4819.78,
            4906.31,
            5002.82,
            5106.72,
            5222.37,
            5570.29,
            5779.89,
            5976.28,
            6199.34,
            6465.56,
            6773.51,
            7041.51,
            7256.01,
            7435.62,
            7406.67,
            7327.06,
            7746.9,
            7935.57,
            7909.79,
            8180.65,
            8409.33,
            8640.44,
            8837.87,
            9123.76,
            9227.26,
            9121.12,
            9494.52,
            9530.29,
            9421.16,
            9421.44,
            9620.41,
            9977.12,
            9722.72,
            9842.47,
            9862.3,
            9968.82,
            9990.08,
            9915.09,
            10121.0,
            10218.8,
            10278.8,
            10590.2,
            10128.4,
            9868.59,
            9603.19,
            9722.25,
            9991.77,
            10099.8,
            10354.6,
            10516.6,
            10802.6,
            10363.5,
            10429.7,
            10546.7,
            10539.8,
            10446.4,
            10593.9,
            10759.0,
            10866.3,
            10900.0,
            11774.9,
            13291.8,
            14526.6,
            15634.9,
            16638.0,
            17624.3,
            18581.1,
            19626.8,
            20654.1,
        ],
    )


@component.add(
    name="Total moles of air in atmosphere",
    units="mol",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_moles_of_air_in_atmosphere():
    return 1.77e20


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
        "land_thickness": 1,
        "mixed_layer_depth": 1,
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
