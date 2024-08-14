# Dictionary of indicators
indicators = {
    'Economic Growth': [
        'NY.GDP.MKTP.CD',  # GDP (current US$)
        'NY.GDP.PCAP.CD',  # GDP per capita (current US$)
        'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
        'NE.TRD.GNFS.ZS',  # Trade (% of GDP)
        'BX.KLT.DINV.WD.GD.ZS'  # Foreign direct investment, net inflows (% of GDP)
    ],
    'Liquidity and Debt': [
        'FP.CPI.TOTL.ZG',  # Inflation, consumer prices (annual %)
        'DT.DOD.DECT.CD',  # External debt stocks, total (current US$)
        'GC.DOD.TOTL.GD.ZS',  # Central government debt, total (% of GDP)
        'FR.INR.RINR'  # Real interest rate (%)
    ],
    'Poverty and Inequality': [
        'SI.POV.NAHC',  # Poverty headcount ratio at national poverty lines (% of population)
        'SI.POV.DDAY',  # Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)
        'SI.POV.GINI',  # GINI index
        'SI.DST.05TH.20'  # Income share held by highest 20%
    ],
    'Health': [
        'SH.DYN.MORT',  # Mortality rate, under-5 (per 1,000 live births)
        'SH.STA.MMRT',  # Maternal mortality ratio (modeled estimate, per 100,000 live births)
        'SH.HIV.INCD.ZS',  # Incidence of HIV (% of uninfected population ages 15-49)
        'SH.IMM.MEAS',  # Immunization, measles (% of children ages 12-23 months)
        'SH.XPD.CHEX.PC.CD',  # Current health expenditure per capita (current US$)
        'SP.DYN.LE00.IN'  # Life expectancy at birth, total (years)
    ],
    'Education': [
        'SE.PRM.ENRR',  # School enrollment, primary (% gross)
        'SE.SEC.ENRR',  # School enrollment, secondary (% gross)
        'SE.ADT.LITR.ZS',  # Literacy rate, adult total (% of people ages 15 and above)
        'SE.XPD.TOTL.GD.ZS',  # Government expenditure on education, total (% of GDP)
        'SE.TER.ENRR'  # School enrollment, tertiary (% gross)
    ],
    'Gender Equality': [
        'SG.GEN.PARL.ZS',  # Proportion of seats held by women in national parliaments (%)
        'SL.TLF.CACT.FE.ZS',  # Labor force participation rate, female (% of female population ages 15+)
        'SE.ENR.PRIM.FM.ZS',  # School enrollment, primary (gross), gender parity index (GPI)
        'SG.VAW.REAS.ZS'  # Women who believe a husband is justified in beating his wife (any of five reasons) (%)
    ],
    'Water and Sanitation': [
        'SH.H2O.SMDW.ZS',  # People using safely managed drinking water services (% of population)
        'SH.STA.SMSS.ZS',  # People using safely managed sanitation services (% of population)
        'ER.H2O.FWTL.ZS',  # Annual freshwater withdrawals, total (% of internal resources)
        'EE.BOD.TOTL.KG'  # Organic water pollutant (BOD) emissions (kg per day)
    ],
    'Energy': [
        'EG.ELC.ACCS.ZS',  # Access to electricity (% of population)
        'EG.USE.ELEC.KH.PC',  # Electric power consumption (kWh per capita)
        'EG.USE.PCAP.KG.OE',  # Energy use (kg of oil equivalent per capita)
        'EG.FEC.RNEW.ZS'  # Renewable energy consumption (% of total final energy consumption)
    ],
    'Employment and Decent Work': [
        'SL.EMP.VULN.ZS',  # Vulnerable employment, total (% of total employment)
        'SL.UEM.TOTL.ZS',  # Unemployment, total (% of total labor force)
        'SL.TLF.CACT.ZS',  # Labor force participation rate, total (% of total population ages 15+)
        'SL.EMP.TOTL.SP.ZS'  # Employment to population ratio, 15+, total (%)
    ],
    'Infrastructure and Innovation': [
        'IT.NET.USER.ZS',  # Individuals using the Internet (% of population)
        'IT.CEL.SETS.P2',  # Mobile cellular subscriptions (per 100 people)
        'GB.XPD.RSDV.GD.ZS',  # Research and development expenditure (% of GDP)
        'IP.PAT.RESD'  # Patent applications, residents
    ],
    'Climate Action': [
        'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
        'AG.LND.FRST.ZS',  # Forest area (% of land area)
        'EG.ELC.RNEW.ZS',  # Renewable electricity output (% of total electricity output)
        'ER.PTD.TOTL.ZS'  # Terrestrial and marine protected areas (% of total territorial area)
    ],
    'Agriculture and Food Security': [
        'AG.YLD.CREL.KG',  # Cereal yield (kg per hectare)
        'SN.ITK.DEFC.ZS',  # Prevalence of undernourishment (% of population)
        'AG.LND.AGRI.ZS',  # Agricultural land (% of land area)
        'AG.PRD.FOOD.XD'  # Food production index (2014-2016 = 100)
    ],
    'Financial Inclusion': [
        'FX.OWN.TOTL.ZS',  # Account ownership at a financial institution or with a mobile-money-service provider (% of population ages 15+)
        'FB.ATM.TOTL.P5',  # Automated teller machines (ATMs) (per 100,000 adults)
        'FS.AST.PRVT.GD.ZS',  # Domestic credit to private sector (% of GDP)
        'CM.MKT.LCAP.GD.ZS'  # Market capitalization of listed domestic companies (% of GDP)
    ],
    'Demographics': [
        'SP.POP.TOTL',  # Population, total
        'SP.POP.GROW',  # Population growth (annual %)
        'SP.URB.TOTL.IN.ZS',  # Urban population (% of total population)
        'SP.DYN.TFRT.IN'  # Fertility rate, total (births per woman)
    ],
    'Governance': [
        'IC.BUS.EASE.XQ',  # Ease of doing business score (0 = lowest performance to 100 = best performance)
        'IQ.CPA.PROT.XQ',  # CPIA property rights and rule-based governance rating (1=low to 6=high)
        'GE.EST',  # Government Effectiveness: Estimate
        'RQ.EST'  # Regulatory Quality: Estimate
    ]
}

# Function to get all indicator codes
def get_all_indicator_codes():
    return [code for theme_codes in indicators.values() for code in theme_codes]

# Function to get theme for a given indicator code
def get_theme_for_indicator(indicator_code):
    for theme, codes in indicators.items():
        if indicator_code in codes:
            return theme
    return None
