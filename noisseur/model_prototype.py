import os.path
import logging
import pytest
from noisseur.model import Model, ModelFactory, Form, Item, Relation, Rect, ItemType, ControlPointType
from noisseur.cfg import AppConfig

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)


def generate_model_007():
    model = Model()
    model.id = "model007"
    model.screen_type = "patient-registration"
    model.description = "Model One"
    model.image_path = "data/s_007.png"

    form = Form()
    form.id = "form1"
    form.description = "Patient Registration Form"

    form.rect = Rect(0, 0, 1031, 710)

    item = Item()
    item.id = "title"
    item.type = ItemType.CAPTION
    item.rect = Rect(0, 0, 170, 30)
    item.text = ["Patient Registration", "tient Registration"]
    item.control_point = ControlPointType.TOP_LEFT
    form.items.append(item)

    item = Item()
    item.id = "iso"
    item.type = ItemType.CAPTION
    item.rect = Rect(878, 692, 931, 708)
    item.text = ["[ISO_IR", "ISO_IR", "ISO IR"]
    item.control_point = ControlPointType.BOTTOM_RIGHT
    form.items.append(item)


    item = Item()
    item.id = "lastNameLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(130, 60, 226, 86)
    item.text = ["Last name"]
    form.items.append(item)

    item = Item()
    item.id = "lastNameValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 60, 490, 86)
    item.text = None
    item.data_field = "last_name"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "firstNameLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(135, 94, 226, 118)
    item.text = ["First name"]
    form.items.append(item)

    item = Item()
    item.id = "firstNameValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 94, 490, 118)
    item.text = None
    item.data_field = "first_name"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "titleLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(187, 127, 226, 149)
    item.text = ["Title"]
    form.items.append(item)

    item = Item()
    item.id = "titleValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 127, 318, 149)
    item.text = None
    item.data_field = "title"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "patientIdLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(135, 160, 226, 182)
    item.text = ["Patient ID"]
    form.items.append(item)

    item = Item()
    item.id = "patientIdValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 160, 490, 182)
    item.text = None
    item.data_field = "patient_id"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "dobLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(115, 193, 226, 215)
    item.text = ["Date of birth"]
    form.items.append(item)

    item = Item()
    item.id = "dobValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 193, 344, 215)
    item.text = None
    item.data_field = "date_of_birth"
    item.data_type = "date"
    item.data_format = "M/d/yyyy"
    form.items.append(item)

    item = Item()
    item.id = "sexLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(183, 225, 226, 247)
    item.text = ["Sex"]
    form.items.append(item)

    item = Item()
    item.id = "sexValue"
    item.type = ItemType.RADIO_BOX
    item.rect = Rect(230, 225, 455, 247)
    item.text = None
    item.data_field = "sex"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "ageLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(183, 252, 226, 275)
    item.text = ["Age"]
    form.items.append(item)

    item = Item()
    item.id = "ageValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 252, 320, 275)
    item.text = None
    item.data_field = "age"
    item.data_type = "int"
    form.items.append(item)

    item = Item()
    item.id = "ageUnitValue"
    item.type = ItemType.TEXT
    item.rect = Rect(330, 252, 385, 275)
    item.text = None
    item.data_field = "age_unit"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "heightLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(162, 284, 226, 306)
    item.text = ["Height"]
    form.items.append(item)

    item = Item()
    item.id = "heightValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 284, 298, 306)
    item.text = None
    item.data_field = "height"
    item.data_type = "float"
    form.items.append(item)

    item = Item()
    item.id = "heightUnitValue"
    item.type = ItemType.TEXT
    item.rect = Rect(301, 284, 330, 306)
    item.text = None
    item.data_field = "height_unit"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "weightLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(162, 317, 226, 339)
    item.text = ["Weight"]
    form.items.append(item)

    item = Item()
    item.id = "weightValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 317, 298, 339)
    item.text = None
    item.data_field = "weight"
    item.data_type = "float"
    form.items.append(item)

    item = Item()
    item.id = "weightUnitValue"
    item.type = ItemType.TEXT
    item.rect = Rect(301, 317, 330, 339)
    item.text = None
    item.data_field = "weight_unit"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "metricLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(436, 319, 485, 341)
    item.text = ["Metric"]
    form.items.append(item)

    item = Item()
    item.id = "metricValue"
    item.type = ItemType.CHECK_BOX
    item.rect = Rect(417, 319, 434, 341)
    item.text = None
    item.data_field = "metric"
    item.data_type = "bool"
    form.items.append(item)

    item = Item()
    item.id = "addInfoLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(115, 353, 226, 375)
    item.text = ["Additional info"]
    form.items.append(item)

    item = Item()
    item.id = "addInfoValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 356, 463, 423)
    item.text = None
    item.data_field = "additional_info"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "accNoLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(620, 60, 732, 84)
    item.text = ["Accession info"]
    form.items.append(item)

    item = Item()
    item.id = "accNoValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 60, 998, 83)
    item.text = None
    item.data_field = "accession_no"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "reqIdLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(640, 91, 732, 114)
    item.text = ["Accession info"]
    form.items.append(item)

    item = Item()
    item.id = "reqIdValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 91, 998, 114)
    item.text = None
    item.data_field = "request_id"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "patientPosLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(595, 220, 732, 242)
    item.text = ["Patient position"]
    form.items.append(item)

    item = Item()
    item.id = "patientPosValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 220, 973, 242)
    item.text = None
    item.data_field = "patient_position"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "instNameLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(610, 298, 732, 320)
    item.text = ["Institution name"]
    form.items.append(item)

    item = Item()
    item.id = "instNameValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 298, 973, 320)
    item.text = None
    item.data_field = "institution_name"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "perfPhysLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(579, 363, 732, 385)
    item.text = ["Performing physician"]
    form.items.append(item)

    item = Item()
    item.id = "perfPhysValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 363, 973, 385)
    item.text = None
    item.data_field = "performing_physician"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "operLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(663, 429, 732, 451)
    item.text = ["Operator"]
    form.items.append(item)

    item = Item()
    item.id = "operValue"
    item.type = ItemType.TEXT
    item.rect = Rect(737, 429, 973, 451)
    item.text = None
    item.data_field = "operator"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "refPhysLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(80, 519, 226, 519+21)
    item.text = ["Referring physician"]
    form.items.append(item)

    item = Item()
    item.id = "refPhysValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 519, 462, 519+21)
    item.text = None
    item.data_field = "referring_physician"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "reqPhysLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(65, 553, 226, 553+21)
    item.text = ["Requesting physician"]
    form.items.append(item)

    item = Item()
    item.id = "reqPhysValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 553, 462, 553+21)
    item.text = None
    item.data_field = "requesting_physician"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "admissionIdLabel"
    item.type = ItemType.LABEL
    item.rect = Rect(120, 586, 226, 586+21)
    item.text = ["Admission ID"]
    form.items.append(item)

    item = Item()
    item.id = "admissionIdValue"
    item.type = ItemType.TEXT
    item.rect = Rect(230, 586, 487, 586+21)
    item.text = None
    item.data_field = "admission_id"
    item.data_type = "str"
    form.items.append(item)

    rel = Relation()
    rel.id = "lastNameRel"
    rel.from_id = "lastNameLabel"
    rel.to_id = "lastNameValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "firstNameRel"
    rel.from_id = "firstNameLabel"
    rel.to_id = "firstNameValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "titleRel"
    rel.from_id = "titleLabel"
    rel.to_id = "titleValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "patientIdRel"
    rel.from_id = "patientIdLabel"
    rel.to_id = "patientIdValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "dobRel"
    rel.from_id = "dobLabel"
    rel.to_id = "dobValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "sexRel"
    rel.from_id = "sexLabel"
    rel.to_id = "sexValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "ageRel"
    rel.from_id = "ageLabel"
    rel.to_id = "ageValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "ageUnitRel"
    rel.from_id = "ageValue"
    rel.to_id = "ageUnit"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "heightRel"
    rel.from_id = "heightLabel"
    rel.to_id = "heightValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "heightUnitRel"
    rel.from_id = "heightValue"
    rel.to_id = "heightUnit"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "weightRel"
    rel.from_id = "weightLabel"
    rel.to_id = "weightValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "weightUnitRel"
    rel.from_id = "weightValue"
    rel.to_id = "weightUnit"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "metricRel"
    rel.from_id = "metricLabel"
    rel.to_id = "metricValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "addInfoRel"
    rel.from_id = "addInfoLabel"
    rel.to_id = "addInfoValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "accNoRel"
    rel.from_id = "accNoLabel"
    rel.to_id = "accNoValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "reqIdRel"
    rel.from_id = "reqIdLabel"
    rel.to_id = "reqIdValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "patientPosRel"
    rel.from_id = "patientPosLabel"
    rel.to_id = "patientPosValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "instNameRel"
    rel.from_id = "instNameLabel"
    rel.to_id = "instNameValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "perfPhysRel"
    rel.from_id = "perfPhysLabel"
    rel.to_id = "perfPhysValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "operRel"
    rel.from_id = "operLabel"
    rel.to_id = "operValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "reqPhysRel"
    rel.from_id = "reqPhysLabel"
    rel.to_id = "reqPhysValue"
    form.relations.append(rel)

    rel = Relation()
    rel.id = "admissionIdRel"
    rel.from_id = "admissionIdLabel"
    rel.to_id = "admissionIdValue"
    form.relations.append(rel)

    # fname
    # Rect(120, 94, +96, +30)
    # Rect(230, 94, +260, +30)

    # Title
    # Rect(120, 125, +96, +30)
    # Rect(230, 125, +260, +30)

    # Patient ID
    # Rect(120, 169, +96, +30)
    # Rect(230, 169, +260, +30)

    model.form = form

    s = model.to_json(indent=4)
    logger.debug("json=\n")
    logger.debug(s)

    with open(os.path.join(AppConfig.instance.ROOT_PATH, "data/s_007.json"), 'w') as f:
        f.write(s)

    model2 = Model.from_json(s)
    logger.debug("model2={}".format(model2))

def generate_model_010():
    model = Model()
    model.id = "model010"
    model.screen_type = "dot-cockpit-editor"
    model.description = "Dot Cockpit Program Editor Screen"
    model.image_path = "data/s_010.png"

    form = Form()
    form.id = "form1"
    form.description = "Dot Cockpit Editor Form"

    form.rect = Rect(0, 0, 948, 799)

    item = Item()
    item.id = "title"
    item.type = ItemType.CAPTION
    item.rect = Rect(0, 0, 264, 27)
    item.text = ["Dot Cockpit - Program Editor"]
    item.control_point = ControlPointType.TOP_LEFT
    form.items.append(item)

    item = Item()
    item.id = "list_1"
    item.type = ItemType.LIST
    item.rect = Rect(10, 150, 640, 787)
    item.row_height = 44
    item.list_item_screen_type = "dot-cockpit-editor-list_1"
    item.text = None
    item.data_field = "list_1"
    item.data_type = "list"
    form.items.append(item)


    model.form = form

    s = model.to_json(indent=4)
    logger.debug("json=\n")
    logger.debug(s)

    with open(os.path.join(AppConfig.instance.ROOT_PATH, "data/s_010.json"), 'w') as f:
        f.write(s)

    model2 = Model.from_json(s)
    logger.debug("model2={}".format(model2))

def generate_model_011():
    model = Model()
    model.id = "model011"
    model.screen_type = "dot-cockpit-editor-list_1"
    model.description = "List item renderer"
    model.image_path = "data/s_011.png"

    form = Form()
    form.id = "form1"
    form.description = "Dot Cockpit Editor list_1 Form"

    form.rect = Rect(0, 0, 629, 44)

    item = Item()
    item.id = "name"
    item.type = ItemType.TEXT
    item.rect = Rect(10, 2, 265, 20)
    item.text = None
    item.data_field = "name"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "time"
    item.type = ItemType.TEXT
    item.rect = Rect(268, 2, 318, 20)
    item.text = None
    item.data_field = "time"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "mark_1"
    item.type = ItemType.TEXT
    item.rect = Rect(10, 22, 70, 42)
    item.text = None
    item.data_field = "mark_1"
    item.data_type = "str"
    form.items.append(item)

    item = Item()
    item.id = "mark_2"
    item.type = ItemType.TEXT
    item.rect = Rect(95, 22, 140, 42)
    item.text = None
    item.data_field = "mark_2"
    item.data_type = "str"
    form.items.append(item)

    model.form = form

    s = model.to_json(indent=4)
    logger.debug("json=\n")
    logger.debug(s)

    with open(os.path.join(AppConfig.instance.ROOT_PATH, "data/s_011.json"), 'w') as f:
        f.write(s)

    model2 = Model.from_json(s)
    logger.debug("model2={}".format(model2))

def generate_models():
    logger.debug("generate_models()")
    generate_model_007()
    generate_model_010()
    generate_model_011()
    # ModelFactory.reload()