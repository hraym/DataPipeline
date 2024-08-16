# World Bank Data Pipeline
python3 main.py --indicators EG.ELC.ACCS.ZS SN.ITK.DEFC.ZS --countries BRA IND KEN --start_year 2000 --end_year 2020
## Project Overview

This data engineering solution automates the visualization of world bank development data. It demonstrates a robust, scalable approach to constructing data pipelines for economic analysis and business intelligence applications.

## Key Features

- Asynchronous data retrieval from the World Bank API
- Customizable selection of economic indicators and countries
- Comprehensive error handling and logging mechanisms
- Modular architecture facilitating maintenance and testing
- Efficient data processing and cleaning utilizing pandas
- Automated data quality checks and validation
- Dynamic visualization of development trends

## Technical Architecture

```
world_bank_data/
│
├── src/
│   ├── __init__.py
│   ├── api.py                # API interaction module
│   ├── indicators_config.py  # Indicator theme dictionary
│   ├── data_processor.py     # Data transformation module
│   ├── pipeline.py           # Core pipeline logic
│   ├── dashboard.py          # For data visualization
│   └── exceptions.py         # Exception handling
│
├── tests/
│   ├── __init__.py 
│   ├── test_api.py
│   ├── test_data_processor.py
│   ├── test_pipeline.py
│   └── test_dashboard.py
│
├── config.py                # Configuration parameters
├── main.py                  # Pipeline execution entry point
└── requirements.txt         # Dependency specifications
```

## Prerequisites

- Python 3.7+
- Dependencies: aiohttp, pandas (full list in requirements.txt)

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/world-bank-data-pipeline.git
   ```
2. Navigate to the project directory:
   ```
   cd world-bank-data-pipeline
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Execute the main script with desired parameters:

```bash
python main.py --indicators <indicator_codes> --countries <country_codes> --start_year <start> --end_year <end>
```

Example:
```bash
python3 main.py --indicators EG.ELC.ACCS.ZS SN.ITK.DEFC.ZS --countries BRA IND KEN --start_year 2000 --end_year 2020
```

## Testing and Quality Assurance

Execute the test suite:

```bash
pytest tests/
```

## Data Visualization Capabilities

Creates an interactive dahsboard showcasing the progress  

## Extensibility and Customization

The modular design allows for easy integration of additional data sources, processing steps, or analytical models. Customization can be achieved by modifying the relevant modules or extending the pipeline class.

## Performance Considerations

The asynchronous data fetching mechanism ensures efficient retrieval of large datasets. For very large data volumes or real-time processing needs, consider implementing a distributed processing framework.

## Security and Compliance

Data is processed locally, ensuring compliance with data protection regulations. Implement appropriate access controls and encryption if deploying in a multi-user or cloud environment.

## License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). This means you are free to:

Share — copy and redistribute the material in any medium or format
Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:

Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

## Acknowledgements

- World Bank for providing the data API
- Open-source community for the tools and libraries utilized in this project

## Contact Information

For inquiries or support, please contact:

Harry Raymond - harryraym@gmail.com