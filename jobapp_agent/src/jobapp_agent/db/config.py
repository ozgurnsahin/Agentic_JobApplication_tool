from configparser import ConfigParser
from pathlib import Path


class GenerateConfig:
    def __init__(self) -> None:
        pass

    @staticmethod
    def config(filename=None, section="postgresql"):
        if filename is None:
            config_path = Path(__file__).resolve().parent / "sql" / "database.ini"
        else:
            config_path = Path(filename)
        parser = ConfigParser()
        parser.read(config_path)
        db_config = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db_config[param[0]] = param[1]
        else:
            raise Exception(f"Section {section} is not found in {config_path} file.")
        return db_config
