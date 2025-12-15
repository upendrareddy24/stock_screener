"""
US Stock Universe - Comprehensive Lists

This file contains curated lists of liquid US stocks for the breakout scanner.
Organized by market cap and liquidity for optimal scanning.

Total: ~1000 stocks across all tiers
"""

# S&P 500 - Technology (Ultra liquid, 1-minute scanning)
SP500_TECH = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
    "AVGO", "ORCL", "ADBE", "CRM", "CSCO", "ACN", "AMD", "INTC",
    "QCOM", "TXN", "INTU", "NOW", "AMAT", "MU", "PANW", "SNPS",
    "CDNS", "LRCX", "KLAC", "MRVL", "NXPI", "ADSK", "FTNT", "MCHP",
    "ADI", "ABNB", "SNOW", "PLTR", "CRWD", "ZS", "DDOG", "NET",
    "OKTA", "MDB", "TEAM", "WDAY", "VEEV", "DOCU", "ZM", "TWLO",
    "SHOP", "SQ", "UBER", "LYFT", "DASH", "RBLX", "U", "PINS",
    "SNAP", "SPOT", "ROKU", "TTD", "MTCH", "BMBL", "YELP", "CVNA",
]

# Major ETFs & Indices (1-minute scanning)
MAJOR_ETFS = [
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO",
    "EEM", "EFA", "AGG", "BND", "LQD", "HYG", "TLT", "GLD",
    "SLV", "USO", "XLE", "XLF", "XLK", "XLV", "XLI", "XLP",
    "XLY", "XLU", "XLB", "XLRE", "XLC", "VNQ", "SMH", "SOXX",
    "ARKK", "ARKG", "ARKW", "ARKF", "ARKQ", "ARKX", "SQQQ", "TQQQ",
    "SPXL", "SPXS", "UPRO", "UDOW", "TNA", "TZA", "FAS", "FAZ",
]

# S&P 500 - Large Cap (All sectors)
SP500_LARGE_CAP = [
    # Consumer Discretionary
    "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX",
    "BKNG", "CMG", "MAR", "ABNB", "GM", "F", "DHI", "LEN",
    "YUM", "ORLY", "AZO", "ROST", "DG", "DLTR", "ULTA", "DPZ",
    
    # Consumer Staples
    "WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ",
    "CL", "KMB", "GIS", "K", "HSY", "MNST", "KDP", "TSN",
    "HRL", "SJM", "CPB", "CAG", "LW", "TAP", "BF.B", "STZ",
    
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO",
    "OXY", "HAL", "BKR", "DVN", "FANG", "MRO", "APA", "HES",
    "KMI", "WMB", "OKE", "LNG", "TRGP", "EPD", "ET", "MPLX",
    
    # Financials
    "BRK.B", "JPM", "BAC", "WFC", "C", "GS", "MS", "SCHW",
    "BLK", "SPGI", "CME", "ICE", "MCO", "AXP", "V", "MA",
    "PYPL", "USB", "PNC", "TFC", "COF", "BK", "STT", "NTRS",
    "AIG", "PRU", "MET", "AFL", "ALL", "TRV", "PGR", "CB",
    "AJG", "MMC", "AON", "WTW", "BRO", "HIG", "CNA", "RLI",
    
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "DHR",
    "PFE", "BMY", "AMGN", "GILD", "REGN", "VRTX", "CI", "CVS",
    "HUM", "ELV", "CNC", "MOH", "BIIB", "ISRG", "SYK", "BSX",
    "MDT", "ZTS", "EW", "IDXX", "DXCM", "ALGN", "RMD", "HOLX",
    "BAX", "BDX", "A", "TECH", "PODD", "XRAY", "ZBH", "RVTY",
    
    # Industrials
    "UPS", "CAT", "HON", "RTX", "BA", "GE", "LMT", "DE",
    "MMM", "ETN", "ITW", "EMR", "PH", "FDX", "NOC", "GD",
    "TDG", "LHX", "CARR", "OTIS", "PCAR", "CMI", "EMR", "ROK",
    "DOV", "AME", "FTV", "XYL", "IEX", "GNRC", "PWR", "AOS",
    
    # Materials
    "LIN", "APD", "SHW", "ECL", "DD", "DOW", "NEM", "FCX",
    "NUE", "VMC", "MLM", "ALB", "CE", "EMN", "LYB", "CF",
    "MOS", "FMC", "IFF", "PPG", "RPM", "SEE", "BALL", "AVY",
    
    # Real Estate
    "AMT", "PLD", "CCI", "EQIX", "PSA", "WELL", "DLR", "O",
    "SPG", "VICI", "AVB", "EQR", "VTR", "ARE", "INVH", "MAA",
    "ESS", "UDR", "CPT", "EXR", "CUBE", "LSI", "REXR", "FR",
    
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "PEG",
    "XEL", "ED", "WEC", "ES", "AWK", "DTE", "PPL", "CMS",
    "AEE", "LNT", "EVRG", "NI", "ATO", "CNP", "NWE", "PNW",
    
    # Communication Services
    "GOOGL", "META", "DIS", "NFLX", "CMCSA", "T", "VZ", "TMUS",
    "CHTR", "EA", "TTWO", "ATVI", "OMC", "IPG", "FOXA", "PARA",
]

# Mid Cap Growth & Momentum
MID_CAP_GROWTH = [
    "COIN", "HOOD", "SOFI", "AFRM", "UPST", "LC", "SQ", "PYPL",
    "RIVN", "LCID", "FSR", "GOEV", "PLUG", "FCEL", "BE", "BLNK",
    "CHPT", "EVGO", "ENPH", "SEDG", "RUN", "NOVA", "ARRY", "MAXN",
    "MARA", "RIOT", "CLSK", "HUT", "BITF", "ARBK", "WULF", "CIFR",
    "DKNG", "PENN", "GENI", "FUBO", "MSGS", "BETZ", "RSI", "CZR",
    "MGM", "WYNN", "LVS", "MLCO", "BYD", "RCL", "CCL", "NCLH",
    "ALK", "UAL", "DAL", "AAL", "LUV", "JBLU", "SAVE", "HA",
]

# Semiconductors Extended
SEMICONDUCTORS_ALL = [
    "NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "MU", "AMAT",
    "LRCX", "KLAC", "SNPS", "CDNS", "MRVL", "NXPI", "MCHP", "ADI",
    "ON", "MPWR", "SWKS", "QRVO", "WOLF", "CRUS", "SLAB", "ALGM",
    "NVMI", "COHU", "FORM", "UCTT", "MKSI", "ENTG", "ICHR", "ACLS",
    "ASML", "TSM", "UMC", "ASX", "HIMX", "SIMO", "DIOD", "POWI",
]

# Biotech & Pharma Extended
BIOTECH_PHARMA_ALL = [
    "MRNA", "BNTX", "NVAX", "VRTX", "REGN", "GILD", "BIIB", "AMGN",
    "SGEN", "EXAS", "ILMN", "INCY", "ALNY", "BMRN", "RARE", "FOLD",
    "ARWR", "IONS", "RGEN", "TECH", "VCEL", "BLUE", "CRSP", "EDIT",
    "NTLA", "BEAM", "VERV", "FATE", "SGMO", "PACB", "CDNA", "TWST",
    "SRPT", "UTHR", "JAZZ", "HALO", "NBIX", "ACAD", "SAGE", "ALKS",
    "PTCT", "ITCI", "ARVN", "KRTX", "SAVA", "AXSM", "CORT", "LBPH",
    "KRYS", "PRTA", "TGTX", "AGIO", "APLS", "YMAB", "IMVT", "KYMR",
]

# Software & Cloud Extended
SOFTWARE_CLOUD = [
    "MSFT", "ORCL", "ADBE", "CRM", "NOW", "INTU", "WDAY", "SNOW",
    "PLTR", "CRWD", "ZS", "DDOG", "NET", "OKTA", "MDB", "TEAM",
    "VEEV", "DOCU", "ZM", "TWLO", "SHOP", "SQ", "UBER", "LYFT",
    "DASH", "ABNB", "RBLX", "U", "PINS", "SNAP", "SPOT", "ROKU",
    "TTD", "MTCH", "BMBL", "YELP", "CVNA", "CARG", "CPNG", "SE",
    "MELI", "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI",
]

# Financial Technology
FINTECH = [
    "V", "MA", "PYPL", "SQ", "COIN", "HOOD", "SOFI", "AFRM",
    "UPST", "LC", "NU", "PAGS", "STNE", "MELI", "MARA", "RIOT",
    "CLSK", "HUT", "BITF", "ARBK", "WULF", "CIFR", "SI", "FOUR",
]

# E-commerce & Digital
ECOMMERCE_DIGITAL = [
    "AMZN", "SHOP", "MELI", "SE", "CPNG", "BABA", "JD", "PDD",
    "EBAY", "ETSY", "W", "CHWY", "FTCH", "REAL", "RVLV", "VSCO",
]

# Cybersecurity
CYBERSECURITY = [
    "CRWD", "ZS", "PANW", "FTNT", "NET", "OKTA", "S", "TENB",
    "CYBR", "QLYS", "VRNS", "RPD", "SAIL", "RBRK", "FSLY", "AKAM",
]

# Cloud Infrastructure
CLOUD_INFRA = [
    "AMZN", "MSFT", "GOOGL", "ORCL", "IBM", "CSCO", "ANET", "DELL",
    "HPE", "NTAP", "PSTG", "WDC", "STX", "MU", "SMCI", "NVDA",
]

# Advertising & Media
AD_MEDIA = [
    "GOOGL", "META", "TTD", "MGNI", "PUBM", "APPS", "DIS", "NFLX",
    "PARA", "WBD", "FOXA", "CMCSA", "OMC", "IPG", "ROKU", "SPOT",
]

# Consumer Internet
CONSUMER_INTERNET = [
    "GOOGL", "META", "NFLX", "UBER", "LYFT", "DASH", "ABNB", "BKNG",
    "EXPE", "TRIP", "YELP", "GRUB", "CVNA", "CARG", "VROOM", "KMX",
]

# Healthcare Technology
HEALTH_TECH = [
    "TDOC", "DOCS", "ONEM", "HIMS", "ACCD", "LFST", "SDGR", "GDRX",
    "OSCR", "PHR", "TNDM", "DXCM", "PODD", "ISRG", "VEEV", "CERN",
]

# Russell 1000 Additional Names
RUSSELL_1000_ADDS = [
    "ABBV", "ACN", "ADBE", "ADP", "AIG", "ALL", "AMAT", "AMD",
    "AMT", "AMZN", "ANTM", "AON", "APD", "APH", "ASML", "ATVI",
    "AVB", "AVGO", "AXP", "AZO", "BA", "BAC", "BAX", "BDX",
    "BIIB", "BK", "BKNG", "BLK", "BMY", "BR", "BRK.B", "BSX",
    "C", "CAH", "CAT", "CB", "CCI", "CDNS", "CE", "CHTR",
    "CI", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", "CMI",
    "CNC", "CNP", "COF", "COP", "COST", "CTAS", "CTLT", "CTSH",
    "CTVA", "CVS", "CVX", "D", "DAL", "DD", "DE", "DFS",
    "DG", "DHI", "DHR", "DIS", "DLTR", "DOV", "DOW", "DPZ",
    "DTE", "DUK", "DVA", "DVN", "DXC", "DXCM", "EA", "EBAY",
    "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH",
    "EOG", "EQIX", "EQR", "ES", "ESS", "ETN", "ETR", "EVRG",
    "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FAST", "FB",
    "FBHS", "FCX", "FDX", "FE", "FFIV", "FIS", "FISV", "FITB",
    "FLT", "FMC", "FOX", "FOXA", "FRC", "FRT", "FTNT", "FTV",
]

# Additional High Volume Stocks
HIGH_VOLUME_ADDS = [
    "GD", "GE", "GILD", "GIS", "GL", "GLW", "GM", "GNRC",
    "GOOG", "GPC", "GPN", "GPS", "GRMN", "GS", "GWW", "HAL",
    "HAS", "HBAN", "HBI", "HCA", "HD", "HES", "HIG", "HII",
    "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST",
    "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", "IFF",
    "ILMN", "INCY", "INFO", "INTC", "INTU", "IP", "IPG", "IPGP",
    "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J",
    "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KEY",
    "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO",
    "KR", "L", "LDOS", "LEN", "LH", "LHX", "LIN", "LKQ",
    "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LUMN", "LUV",
    "LVS", "LW", "LYB", "LYV", "MA", "MAA", "MAR", "MAS",
]

# Combine all lists with strategic distribution
ALL_STOCKS_1MIN = sorted(list(set(
    SP500_TECH + MAJOR_ETFS + SEMICONDUCTORS_ALL[:20] + 
    SOFTWARE_CLOUD[:30] + FINTECH[:15] + MID_CAP_GROWTH[:20]
)))

ALL_STOCKS_5MIN = sorted(list(set(
    SP500_LARGE_CAP + MID_CAP_GROWTH + SEMICONDUCTORS_ALL +
    BIOTECH_PHARMA_ALL[:40] + SOFTWARE_CLOUD + FINTECH +
    ECOMMERCE_DIGITAL + CYBERSECURITY + CLOUD_INFRA[:15] +
    AD_MEDIA[:15] + CONSUMER_INTERNET[:15] + HEALTH_TECH[:12]
)))

ALL_STOCKS_15MIN = sorted(list(set(
    SP500_LARGE_CAP + BIOTECH_PHARMA_ALL + SOFTWARE_CLOUD +
    SEMICONDUCTORS_ALL + FINTECH + ECOMMERCE_DIGITAL +
    CYBERSECURITY + CLOUD_INFRA + AD_MEDIA + CONSUMER_INTERNET +
    HEALTH_TECH + RUSSELL_1000_ADDS + HIGH_VOLUME_ADDS
)))

# Print statistics
if __name__ == "__main__":
    print(f"1-minute tier: {len(ALL_STOCKS_1MIN)} stocks")
    print(f"5-minute tier: {len(ALL_STOCKS_5MIN)} stocks")
    print(f"15-minute tier: {len(ALL_STOCKS_15MIN)} stocks")
    total_unique = len(set(ALL_STOCKS_1MIN + ALL_STOCKS_5MIN + ALL_STOCKS_15MIN))
    print(f"Total unique stocks: {total_unique}")
    print(f"\nSample 1m stocks: {ALL_STOCKS_1MIN[:10]}")
    print(f"Sample 5m stocks: {ALL_STOCKS_5MIN[:10]}")
    print(f"Sample 15m stocks: {ALL_STOCKS_15MIN[:10]}")
