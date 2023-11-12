"""
This module contains the business logic for a Speckle Automate function.
It demonstrates how to define input models, traverse and process data,
and generate reports based on user-specified criteria.
"""
from enum import Enum

from pydantic import Field
from speckle_automate import (
    AutomateBase,
    AutomationContext,
    execute_automate_function,
)

from Rules.checks import BaseObjectRules
from Rules.traversal import get_data_traversal_rules
from Utilities.report import generate_report


class ThresholdMode(Enum):
    """
    ThresholdMode: Defines different modes for reporting thresholds.
    """

    ERROR = "ERROR"
    WARN = "WARN"
    INFO = "INFO"


class Format(Enum):
    """
    Format: Enum for defining report formats.
    """

    PDF = "PDF"
    HTML = "HTML"
    JSON = "JSON"


def create_one_of_enum(enum_cls):
    """
    Helper function to create a JSON schema from an Enum class.
    This is used for generating user input forms in the UI.
    """
    return [{"const": item.value, "title": item.name} for item in enum_cls]


class FunctionInputs(AutomateBase):
    """
    FunctionInputs: Defines user inputs for the automation function.
    The structure is based on Pydantic models for data validation.

    Please use the pydantic model schema to define your inputs:
    https://docs.pydantic.dev/latest/usage/models/
    """

    ids_xml_file: str = Field(
        "https://example.com/project_standards/ids.xml",
        title="IDS XML File",
        description="URL or content of the IDS XML file defining project standards. e.g. https://example.com/project_standards/ids.xml",
        json_schema_extra={
            "readOnly": True,
            "label": "https://example.com/project_standards/ids.xml",
        },
    )
    bsdd_sheets: str = Field(
        "https://example.com/project_standards/bsdd.json",
        title="bsDD Sheet Identifier(s)",
        description="Identifier or URL for the bsDD sheet relevant to the project. e.g. https://example.com/project_standards/bsdd.json",
        json_schema_extra={
            "readOnly": True,
            "label": "https://example.com/project_standards/bsdd.json",
        },
    )

    single_category: str = Field(
        default="Windows",
        title="Single Category for Demo",
        description="For demonstration purposes only this is a single category. e.g. Windows.",
    )
    single_property: str = Field(
        default="OmniClass Number",
        title="Single Property for Demo",
        description="For demonstration purposes only this is a single property. e.g. OmniClass Number.",
    )
    single_rule: str = Field(
        default="23.30.20",
        title="Rule for Demo",
        description="For demonstration purposes only this is a single value for that property. e.g. Prefixed 23.30.20. ",
    )

    report_format: Format = Field(
        default=Format.PDF,
        title="Report Format",
        description="Preferred format for the compliance report. e.g. PDF, HTML, JSON.",
        json_schema_extra={
            "oneOf": create_one_of_enum(Format),
        },
    )
    threshold_mode: ThresholdMode = Field(
        default=ThresholdMode.ERROR,
        title="Reporting Threshold",
        description="Set the threshold mode for reporting results: ERROR, WARN, or INFO.",
        json_schema_extra={
            "oneOf": create_one_of_enum(ThresholdMode),
        },
    )


def automate_function(
    automate_context: AutomationContext,
    function_inputs: FunctionInputs,
) -> None:
    """
    The core logic of the Speckle Automate function.
    Processes Speckle data and generates a report based on user inputs.

    Args:
        automate_context: Context object with data and methods for the run.
        function_inputs: User-defined input values.
    """
    # the context provides a convenient way, to receive the triggering version
    version_root_object = automate_context.receive_version()

    # Traverse the received Speckle data.
    speckle_data = get_data_traversal_rules()
    traversal_contexts_collection = speckle_data.traverse(version_root_object)

    # Assuming each object has properties: name, type, and id
    assessed_objects = {"missing": [], "invalid": [], "passing": []}

    # Checking parameters
    for context in traversal_contexts_collection:
        current_object = getattr(context.current, "parameters", None)

        if current_object:
            for parameter_key in current_object.get_dynamic_member_names():
                parameter = current_object[parameter_key]
                assessment = BaseObjectRules.evaluate_parameter(
                    parameter, function_inputs
                )

                if getattr(
                    current_object, "speckle_type", None
                ) == "Objects.Other.Revit.RevitInstance" and hasattr(
                    current_object, "definition"
                ):
                    type_ = getattr(current_object.definition, "type", "Unknown")
                    family = getattr(current_object.definition, "family", "Unknown")
                else:
                    type_ = getattr(current_object, "type", "Unknown")
                    family = getattr(current_object, "family", "Unknown")

                object_info = {
                    "name": getattr(current_object, "name", "Unknown"),
                    "type": type_,
                    "family": family,
                    "id": getattr(current_object, "id", "Unknown"),
                }

                if assessment:
                    assessed_objects[assessment].append(object_info)

    # Attach errors or info to objects based on their parameter evaluation state
    for state, objects in assessed_objects.items():
        ids = [obj["id"] for obj in objects if "id" in obj and obj["id"]]
        if not ids:
            continue

        # Construct a detailed message for each object
        detailed_messages = [
            f"{obj['name']} (Type: {obj['type']}, ID: {obj['id']})"
            for obj in objects
            if "id" in obj and obj["id"]
        ]

        # Combine messages into a single string
        combined_message = (
            f"Found {len(objects)} objects with {state} parameters: "
            + "; ".join(detailed_messages)
        )

        if state in ["missing", "invalid"]:
            automate_context.attach_error_to_objects(
                category=state.capitalize(), object_ids=ids, message=combined_message
            )
        else:  # 'valid'
            automate_context.attach_info_to_objects(
                category=state.capitalize(), object_ids=ids, message=combined_message
            )

    # Determine overall automation success or failure
    if assessed_objects["missing"] or assessed_objects["invalid"]:
        automate_context.mark_run_failed("Automation failed due to parameter issues.")
    else:
        automate_context.mark_run_success("All parameters are valid.")

    # Generate and attach the report
    report_format = (
        function_inputs.report_format.value
    )  # Accessing the value of the Enum
    report_file = generate_report(
        assessed_objects,
        report_format,
        function_inputs.single_category,
        function_inputs.single_property,
        function_inputs.single_rule,
    )
    automate_context.store_file_result(report_file)


# make sure to call the function with the executor
if __name__ == "__main__":
    # NOTE: always pass in the automate function by its reference, do not invoke it!

    # pass in the function reference with the inputs schema to the executor
    execute_automate_function(automate_function, FunctionInputs)

    # if the function has no arguments, the executor can handle it like so
    # execute_automate_function(automate_function_without_inputs)
