import importlib
import pkgutil

from text_processor.processors.base_processor import BaseFileProcessor

class FileProcessorFactory:
    _registry = {}

    @classmethod
    def autodiscover_processors(cls):
        """
        Automatically discover and register all processor classes in the 'processors' folder.
        Each processor must:
        - inherit from BaseFileProcessor
        - have 'file_extension' attribute (e.g. ".txt", ".csv")
        """
        import text_processor.processors as processors_pkg
        for _, module_name, _ in pkgutil.iter_modules(processors_pkg.__path__):
            # Skip the factory module itself
            if module_name == "file_processor_factory":
                continue

            module = importlib.import_module(f"text_processor.processors.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseFileProcessor)
                        and attr is not BaseFileProcessor
                        and getattr(attr, "file_extension", None)
                ):
                    cls.register_processor(attr)

    @classmethod
    def register_processor(cls, processor_cls):
        ext = processor_cls.file_extension.lower()
        cls._registry[ext] = processor_cls

    @classmethod
    def get_processor(cls, file_extension):
        ext = file_extension.lower()
        if ext not in cls._registry:
            raise ValueError(f"No processor registered for extension '{ext}'")
        return cls._registry[ext]

FileProcessorFactory.autodiscover_processors()
