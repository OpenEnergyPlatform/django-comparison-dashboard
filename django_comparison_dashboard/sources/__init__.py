from .core import SourceRegistry
from .csv import CSVDataSource
from .databus import DatabusDataSource
from .modex import ModexDataSource

SOURCES = SourceRegistry()
SOURCES.register(ModexDataSource)
SOURCES.register(CSVDataSource)
SOURCES.register(DatabusDataSource)
