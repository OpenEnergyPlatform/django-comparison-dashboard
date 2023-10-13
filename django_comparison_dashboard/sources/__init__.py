from .core import SourceRegistry
from .csv import CSVDataSource
from .modex import ModexDataSource

SOURCES = SourceRegistry()
SOURCES.register(ModexDataSource)
SOURCES.register(CSVDataSource)
