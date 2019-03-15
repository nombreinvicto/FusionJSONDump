import adsk.core as adskc
import adsk.fusion as adskf
import adsk.cam as adskam
import traceback
import adsk
import ctypes, os, json

# default api unit is cm/ radian
# global variables
handlers = []


class JsonDumpButtPressEvtHandler(adskc.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adskc.CommandCreatedEventArgs):
        try:
            # this function sets up documents and initialises design global vars
            # setting up app and document
            app = adskc.Application.get()
            ui = app.userInterface
            doc = app.activeDocument
            current_product = app.activeProduct

            if not isinstance(current_product, adskf.Design):
                ui.messageBox('addin not supported in current workspace. \n ' +
                              'please choose design workspace and try again.')
                return

            # get the newly created command object
            cmd = args.command

            # get the command inputs collection associated with command
            inputs = cmd.commandInputs

            # add a button to initiate the dumping of json data
            booleanInput = inputs.addBoolValueInput('button1', 'JSONDump',
                                                    False,
                                                    '',
                                                    False)
            booleanInput.isFullWidth = True
            booleanInput.text = 'Initiate Dump'

            # executes as soon as inputs change
            onInputChanged = JsonDumpInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            # OK button event handler
            onOk = OKEventHandler()
            cmd.execute.add(onOk)
            handlers.append(onOk)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class JsonDumpInputChangedHandler(adskc.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args: adskc.InputChangedEventArgs):
        try:
            app = adskc.Application.get()
            ui = app.userInterface
            doc = app.activeDocument
            products = doc.products

            # get design product
            designProduct = products.itemByProductType('DesignProductType')
            design = adskf.Design.cast(designProduct)

            # find all components
            allComponents = design.allComponents

            # Returns the collection of command inputs that are
            # associated with the command this event is being fired for
            inputs = args.inputs

            # Returns the command input that has just changed.
            cmdInput = args.input

            if cmdInput.id == 'button1':
                # create fila dialog here
                folderDialog = ui.createFolderDialog()
                folderDialog.isMultiSelectEnabled = False
                folderDialog.initialDirectory = os.path.expanduser('~')
                dialogResult = folderDialog.showDialog()

                # folder selected
                if dialogResult == 0:
                    folderPath = folderDialog.folder
                    rootComp = design.rootComponent
                    rootCompName = rootComp.name
                    param_dict = min_max_routine(ui, allComponents)

                    with open(folderPath + '\\' +
                              rootCompName + '.json', 'w') as outfile:
                        json.dump(param_dict, outfile)
                    ui.messageBox('Json Dump Complete!')

                else:
                    pass

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Fires when the user presses OK
class OKEventHandler(adskc.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface

        try:
            command = args.firingEvent.sender

        except:
            if ui:
                ui.messageBox('command executed failed:\n{}'.format(
                    traceback.format_exc()))


def min_max_routine(ui, allComponents):
    param_dict = {}
    for comp in allComponents:
        tcomp = comp  # type: adskf.Component
        for param in tcomp.modelParameters:
            tparam = param  # type: adskf.Parameter

            # only dump values if allowed
            if tparam.comment != 'no':
                # set max min limits of param
                tdict = {}
                limit_strs = ['min', 'max']
                limit_input = ''
                i = 0
                while True:
                    # reVals will be a list 1st mem- input
                    limit_str = limit_strs[i]
                    retVals = ui.inputBox(
                        "enter {} value for dimension {}"
                            .format(limit_str, tparam.name),
                        'enter range for dimensions',
                        limit_input)

                    if retVals[0]:  # means value was entered
                        inp, isCancelled = retVals

                        if limit_str == 'max':
                            if float(inp) <= tdict['min']:
                                ui.messageBox(
                                    'max setting should '
                                    'be larger than min '
                                    'setting'
                                )
                                i = 0
                                tdict = {}
                                continue

                        tdict[limit_str] = round(float(inp), 2)
                        i += 1

                        if i > 1:
                            break

                    else:  # means cancel was hit
                        ui.messageBox(
                            'cancelling json dump '
                            'sequence')
                        # adsk.terminate()
                        return

                tdict["currentValue"] = tparam.value
                param_dict[tparam.name] = tdict
    return param_dict


def run(context):
    try:
        # this function sets up documents and initialises design global vars
        # setting up app and document - dont generate error on empty doc
        app = adskc.Application.get()
        ui = app.userInterface

        # get the command definition
        commDefs = ui.commandDefinitions

        # add a button command def
        jsonDumpButtDef = commDefs.addButtonDefinition(
            'jsonDumpButtDefID',
            'Dump CAD JSON Metadata',
            'Dumps json metadata in the required target location',
            'resources'
        )

        # grab the correct toolbar panel to add the button to
        global addInsPanel
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        jsonDumpButt = addInsPanel.controls.addCommand(
            jsonDumpButtDef,
            'jsonDumpButtID'
        )
        jsonDumpButt.isPromotedByDefault = True
        jsonDumpButt.isPromoted = True

        # connect the command created to the event handler
        jsonDumpButtHandler = JsonDumpButtPressEvtHandler()
        jsonDumpButtDef.commandCreated.add(jsonDumpButtHandler)
        handlers.append(jsonDumpButtHandler)
        # fial dialog


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adskc.Application.get()
        ui = app.userInterface
        # delete buttons
        addinButtDef = ui.commandDefinitions.itemById('jsonDumpButtDefID')
        if addinButtDef:
            addinButtDef.deleteMe()

        # get and delete the controls
        ctrl = addInsPanel.controls.itemById('jsonDumpButtDefID')
        if ctrl:
            ctrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
