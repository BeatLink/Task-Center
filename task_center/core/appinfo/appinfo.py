#!/bin/env python3
"""
Loads the pyproject.toml file for use by the application.
It first checks inside the task_center package, and if not found, it then checks the repository root
This module is the final authority on information about this software.
Whenever there is doubt about information regarding this app, use the information in this file.
"""

# Imports ##############################################################################################################
import pathlib
import appdirs
import tomlkit
import arrow


# AppInfo ##############################################################################################################
class AppInfo:
    def __init__(self):
        file_path = pathlib.Path(__file__).parents[3] / "pyproject.toml"
        with file_path.open('r') as app_data_file:
            self.__toml_file_contents = tomlkit.loads(app_data_file.read())
        app_data = self.__toml_file_contents['tool']['poetry']
        self.name = app_data['name']
        self.appid = self.__toml_file_contents['appinfo']['appid']
        self.version = app_data['version']
        self.description = app_data['description']
        self.readme_file_path = app_data['readme']
        self.homepage = app_data['homepage']
        self.repository = app_data['repository']
        self.authors = app_data['authors']
        self.license = app_data['license']
        self.application_folders = appdirs.AppDirs(appname=self.name, appauthor=self.authors[0].split()[0])
        self.icon_file_path = str((pathlib.Path(__file__).parents[3] / "resources" / "logo.png").resolve())
        self.license_file_path = ''
        self.__toml_file_contents = None

    @property
    def author_name(self):
        """Returns the name of the first author"""
        return self.authors[0].split()[0]

    @property
    def copyright(self):
        return f'Copyright © {arrow.now().date().year} {self.author_name}'
