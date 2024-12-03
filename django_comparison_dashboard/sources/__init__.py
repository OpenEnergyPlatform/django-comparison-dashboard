from .core import SourceRegistry
from .csv import CSVDataSource
from .databus import DatabusDataSource

SOURCES = SourceRegistry()
SOURCES.register(CSVDataSource)
SOURCES.register(DatabusDataSource)
