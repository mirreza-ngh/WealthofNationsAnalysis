# World Bank indicator codes and constants
GDP_PC = "NY.GDP.PCAP.CD"        # GDP per capita (current US$)
LIFE_EXP = "SP.DYN.LE00.IN"      # Life expectancy at birth (years)
HEALTH_SP = "SH.XPD.CHEX.PC.CD"  # Health expenditure per capita (US$)
CHILD_MORT = "SH.DYN.MORT"       # Under-5 mortality (per 1,000 births)

DEFAULT_INDICATORS = {
    "gdp_pc": GDP_PC,
    "life_exp": LIFE_EXP,
    "health_pc": HEALTH_SP,
    "u5_mort": CHILD_MORT,
}
