import os, sys, json, argparse, ast, shutil, zipfile
from templates import templates
from rich import print
from rich.console import Console


class ToKeyValue(argparse.Action):
    def __call__(self, _, namespace, values, option_string = None):
        setattr(namespace, self.dest, dict())
          
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

class Beloved:
    def __init__(self):
        self.call_location = os.getcwd()

        if getattr(sys, 'frozen', False):
            self.script_location = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.script_location = os.path.dirname(os.path.abspath(__file__))

        self.parser = argparse.ArgumentParser(prog="beloved")
        self.parser.add_argument('-i', '--init', type=str, help='Initialize a new project with base structure, with the name provided', metavar='Projectname')
        self.parser.add_argument('-c', '--add-class', type=str, nargs="+", help='Add new class(es) to the project', metavar='Classname')
        self.parser.add_argument('-l', '--add-library', type=str, nargs="+", help='Import the given library(es) to the project', metavar='Library')
        self.parser.add_argument('-ll', '--list-libraries', help='List all available libraries', action='store_true')
        self.parser.add_argument('-z', '--zip-project', help='Creates a runnable .love from your project', action='store_true')
        self.parser.add_argument('-o', '--output', type=str, help="Specifies the output file name when used with the -z flag, defaults to the parent directory's name", metavar='Filename')
        self.parser.add_argument('-p', '--parameters', nargs="*", type=str, help="Adds custom parameters for custom templates", metavar='KEY=VALUE', action=ToKeyValue)

        self.console = Console()

        self.parameters = {}

        self.conf = templates["beloved.conf"]
        self.templates = templates


    def load_config(self):
        with self.console.status(f"Reading beloved.conf") as status:
            if not os.path.exists(os.path.join(self.script_location, "beloved.conf")):
                with open(os.path.join(self.script_location, "beloved.conf"), "w+") as file:
                    json.dump(templates["beloved.conf"], file, indent=4)

                self.console.log(f"[bold red]Cannot load beloved.conf! Creating new one![/bold red]")
            
            else:
                with open(os.path.join(self.script_location, "beloved.conf"), "r") as file:
                    self.conf = json.load(file)

            if self.conf["templates"]:
                if not os.path.exists(self.conf["templates"]):
                    self.console.log(f"[bold red]Templates file {self.conf['templates']} does not exist![/bold red]")
                else:
                    with open(self.conf["templates"], "r") as template_file:
                        self.templates = ast.literal_eval(template_file.read())


    def parse_args(self):
        self.args = self.parser.parse_args()

        if self.args.parameters:
            self.parameters = self.args.parameters
            print(self.parameters)

        if self.args.init:
            self.parameters["projectname"] = self.args.init
            self.init_project()

        if self.args.add_class:
            self.add_class()

        if self.args.list_libraries:
            self.list_libraries()

        if self.args.add_library:
            self.import_libraries()

        if self.args.zip_project:
            self.create_love()


    def create_folders(self):
        yield f"Creating base folder [bold magenta]{self.args.init}[/bold magenta]"

        if os.path.exists(os.path.join(self.call_location, self.args.init)):
            yield f"[bold red]Skipping! Folder {self.args.init} already exists![/bold red]"
        else:
            try:
                os.mkdir(os.path.join(self.call_location, self.args.init))
                yield f"[bold green]Success! Folder {self.args.init} created successfully! [bold green]"
            except:
                yield f"[bold red]ERROR! {sys.exc_info()[0]}[/bold red]"
            

        yield f"Creating subfolder structure for [bold magenta]{self.args.init}[/bold magenta]"

        for dir_name in self.conf["directories"]:
            if os.path.exists(os.path.join(self.call_location, self.args.init, dir_name)):
                yield f"[bold red]Skipping! Folder {self.args.init}/{dir_name} already exists![/bold red]"
            else:
                try:
                    os.mkdir(os.path.join(self.call_location, self.args.init, dir_name))
                    yield f"Creating directory [bold green]{self.args.init}/{dir_name}[bold green]"
                except:
                    yield f"[bold red]ERROR! {sys.exc_info()[0]}[/bold red]"


    def create_files(self):
        for file_name in self.conf["files"]:
            if os.path.exists(os.path.join(self.call_location, self.args.init, file_name)):
                yield f"[bold red]Skipping! File {self.args.init}/{file_name} already exists![/bold red]"
            else:
                try:
                    yield f"Creating file [bold green]{self.args.init}/{file_name}[bold green]"

                    with open(os.path.join(self.call_location, self.args.init, file_name), "w+") as file:
                        if file_name in self.templates.keys():
                            file.write(self.templates[file_name].format(**self.parameters))
                except:
                    yield f"[bold red]ERROR! {sys.exc_info()[0]}[/bold red]"


    def init_project(self):
        with self.console.status(f"Creating [bold magenta]{self.args.init}[/bold magenta] in [bold green]{self.call_location}.") as status:
            folder_maker = self.create_folders()
            file_maker = self.create_files()
            
            for x in folder_maker:
                self.console.log(f"{x}")

            for x in file_maker:
                self.console.log(f"{x}")
        
        os.chdir(self.args.init)
        self.call_location = os.getcwd()


    def add_class(self):
        with self.console.status(f"Creating [bold magenta]{self.args.init}[/bold magenta] in [bold green]{self.call_location}.") as status:
            if not os.path.exists(os.path.join(self.call_location, 'main.lua')):
                self.console.log(f"[bold red]Invalid project directory! Run Beloved -i <ProjectName> to create a new project[/bold red]")
                return

            for class_name in self.args.add_class:
                if os.path.exists(os.path.join(self.call_location, class_name + ".lua")):
                    self.console.log(f"[bold red]Skipping! File {self.call_location}/{class_name} already exists![/bold red]")
                else:
                    try:
                        self.console.log(f"Creating class [bold green]{class_name}[bold green]")

                        with open(os.path.join(self.call_location, class_name + ".lua"), "w+") as file:
                            if "class.lua" in self.templates.keys():
                                file.write(self.templates["class.lua"].format(class_name=class_name))

                        self.append_to_includes(class_name)
                    except:
                        self.console.log(f"[bold red]ERROR! {sys.exc_info()[0]}[/bold red]")


    def append_to_includes(self, name, prefix = ""):
        if os.path.exists(os.path.join(self.call_location, 'includes.lua')):
            with open(os.path.join(self.call_location, "includes.lua"), "a") as file:
                file.write(f"{name} = require '{prefix}{name}'\n")

    
    def list_libraries(self):
        print("[bold magenta]Available libraries:[/bold magenta]")

        libraries = os.listdir(self.conf["libraries_folder"])
        libraries = sorted(libraries, key=str.casefold)

        for lib_name in libraries:
            print(f"[cyan]{lib_name}[/cyan]")


    def import_libraries(self):
        with self.console.status(f"Creating [bold magenta]{self.args.init}[/bold magenta] in [bold green]{self.call_location}.") as status:
            if not os.path.exists(os.path.join(self.call_location, 'main.lua')):
                self.console.log(f"[bold red]Invalid project directory! Run Beloved -i <ProjectName> to create a new project[/bold red]")
                return
            
            if not os.path.exists(os.path.join(self.call_location, 'lib')):
                os.mkdir(os.path.join(self.call_location, 'lib'))

            for lib_name in self.args.add_library:
                if os.path.exists(os.path.join(self.conf["libraries_folder"], lib_name)):
                    self.console.log(f"Importing [bold green]{lib_name}[/bold green]")
                    
                    if os.path.isfile(os.path.join(self.conf["libraries_folder"], lib_name)):
                        shutil.copy(os.path.join(self.conf["libraries_folder"], lib_name), os.path.join(self.call_location, 'lib'))
                    elif os.path.isdir(os.path.join(self.conf["libraries_folder"], lib_name)):
                        shutil.copytree(os.path.join(self.conf["libraries_folder"], lib_name), os.path.join(self.call_location, 'lib', lib_name))

                elif os.path.exists(os.path.join(self.conf["libraries_folder"], lib_name + ".lua")):
                    self.console.log(f"Importing [bold green]{lib_name}.lua[/bold green]")

                    if os.path.isfile(os.path.join(self.conf["libraries_folder"], lib_name + ".lua")):
                        shutil.copy(os.path.join(self.conf["libraries_folder"], lib_name + ".lua"), os.path.join(self.call_location, 'lib'))
                    elif os.path.isdir(os.path.join(self.conf["libraries_folder"], lib_name)):
                        shutil.copytree(os.path.join(self.conf["libraries_folder"], lib_name), os.path.join(self.call_location, 'lib'))
                    
                else:
                    self.console.log(f"[bold red]Cannot import {lib_name}! Library does not exist[/bold red]")
                    return

                self.append_to_includes(lib_name, "lib.")

    def create_love(self):
        output_name = self.args.output if self.args.output is not None else os.path.split(self.call_location)[-1]

        with self.console.status("") as status:
            self.console.log(f"Creating [bold magenta]{output_name}.love[/bold magenta] in [bold green]{os.path.join(self.call_location, self.conf['build_directory'], self.conf['love_output'])}.")
            if not os.path.exists(os.path.join(self.call_location, 'main.lua')):
                self.console.log(f"[bold red]Invalid project directory! Run Beloved -i <ProjectName> to create a new project[/bold red]")
                return

            if not os.path.exists(os.path.join(self.call_location, self.conf["build_directory"], self.conf["love_output"])):
                os.makedirs(os.path.join(self.call_location, self.conf["build_directory"], self.conf["love_output"]))


            with zipfile.ZipFile(os.path.join(self.call_location, self.conf["build_directory"], self.conf["love_output"], output_name + ".love"), 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for folder_name, subfolders, filenames in os.walk(self.call_location):
                    if self.conf["build_directory"] not in folder_name:
                        for filename in filenames:
                            file_path = os.path.join(folder_name, filename)
                            self.console.log(f"appending [bold magenta]{file_path}.love[/bold magenta]")
                            zip_ref.write(os.path.join(folder_name, file_path), arcname=os.path.relpath(os.path.join(folder_name, file_path)))

            zip_ref.close()
                

bl = Beloved()
bl.load_config()
bl.parse_args()
