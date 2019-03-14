# Initial Author- Jordan Oldroyd, Autodesk
# Edited by Mahmud Hasan for 3D Print Calculator
# Description- Calculates Estimated Cost for 3D Printing

commandId = 'CommandInputGallery'
import adsk.core, adsk.fusion, adsk.cam, traceback, math, os.path

handlers = []


class CostButtonPressedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.command
            inputs = cmd.commandInputs

            # Adding all the different features to the dialog box
            # First adding selection input to select solid geometry
            selectionInput1 = inputs.addSelectionInput('selection_1',
                                                       'Select Model to be 3D Printed',
                                                       'Select a Water Tight Body')
            selectionInput1.setSelectionLimits(1, 1)
            selectionInput1.addSelectionFilter('SolidBodies')

            # Now adding Slider Bar for Scale Factor Manipulation
            valueList = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
            inputs.addFloatSliderListCommandInput('slider_1',
                                                  'Scale Factor',
                                                  '',
                                                  valueList)

            # Now adding Drop Down List for Material Choice
            dropdownInput1 = inputs.addDropDownCommandInput(
                'CommandInputGallery', 'Material Option',
                adsk.core.DropDownStyles.LabeledIconDropDownStyle);
            dropdown1Items = dropdownInput1.listItems
            dropdown1Items.add('ABS', True, '')
            dropdown1Items.add('PLA', False, '')

            inputs.addTextBoxCommandInput('textBox1', 'Cost of 3D Print', '', 2,
                                          True)

            # Executes As soon as Inputs Change
            onInputChanged = CostDialogInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            # Executes When Ok Pressed
            onExecute = CostDialogOKEventHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CostDialogInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            command = args.firingEvent.sender

            # Initialising Volume and Cost Variables
            vol1 = 0
            formatted_vol1 = 0
            material_cost_factor = 1

            # Detecting Selected Body, Extracting Volume and Converting Unit to in^3
            selectionInput = command.commandInputs.itemById('selection_1')
            if selectionInput.selectionCount > 0:
                selection1 = selectionInput.selection(0).entity
                geom1 = selection1.volume
                vol1 = geom1  # default value in cm^3
                formatted_vol1 = vol1 * 0.0610237  # formatted to in^3

            # Detecting Selected Material and Assigning Corresponding Cost Factors
            drpdwnInput = command.commandInputs.itemById('CommandInputGallery')
            objectItems = drpdwnInput.listItems
            for item in objectItems:
                if item.isSelected and item.name == 'ABS':
                    material_cost_factor = 25
                if item.isSelected and item.name == 'PLA':
                    material_cost_factor = 47.5

            # Finding Total Cost Based on Volume, Material and Scale Factor
            if vol1:
                slider = command.commandInputs.itemById('slider_1')
                sfactor = slider.valueOne

                cost_print = sfactor * formatted_vol1 * material_cost_factor
                formatted_cost_print = "$ %.2f" % (cost_print)

                textBox = command.commandInputs.itemById('textBox1')
                textBox.text = str(formatted_cost_print)

        except:
            if ui:
                ui.messageBox(
                    'Input change failed:\n{}'.format(traceback.format_exc()))


# Fires when the user presses OK
class CostDialogOKEventHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct

        try:
            command = args.firingEvent.sender

        except:
            if ui:
                ui.messageBox('command executed failed:\n{}'.format(
                    traceback.format_exc()))


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the command definitions collection
        commandDefinitions = ui.commandDefinitions
        # Add a button command definition to that collection
        CostButtonDefinition = commandDefinitions.addButtonDefinition(
            'CostButton',
            '3D Print Cost Calculator',
            'Calculates the Estimated cost for 3D Printing',
            'resources')

        # Grabbing the correct toolbar panel to add the button to
        addinsToolbarPanel = ui.allToolbarPanels.itemById(
            'SolidScriptsAddinsPanel')
        # Adding the Cost button to the add-in toolbar panel
        CostButtonControl = addinsToolbarPanel.controls.addCommand(
            CostButtonDefinition, 'CostButtonControl')
        # Making the button visible without having to use the dropdown
        CostButtonControl.isPromotedByDefault = True
        CostButtonControl.isPromoted = True

        # Setting up the handler if the Cost button is pressed
        # Calling the class?
        CostButtonPressed = CostButtonPressedEventHandler()
        CostButtonDefinition.commandCreated.add(CostButtonPressed)
        handlers.append(CostButtonPressed)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Deleting the Cost button
        ui.messageBox('Deleting the button')
        CostButtonDefinition = ui.commandDefinitions.itemById('CostButton')
        if CostButtonDefinition:
            CostButtonDefinition.deleteMe()
        addinsToolbarPanel = ui.allToolbarPanels.itemById(
            'SolidScriptsAddinsPanel')
        CostButtonControl = addinsToolbarPanel.controls.itemById(
            'CostButton')
        if CostButtonControl:
            CostButtonControl.deleteMe()


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
