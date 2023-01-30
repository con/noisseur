import pytest
from noisseur.model import Model, Form, Item, Relation, Rect, ItemType, ControlPointType
from typing import cast


def test_model_1():
    model = Model()
    model.id = "model007"
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

    rel = Relation()
    rel.id = "lastNameRel"
    rel.from_id = "lastNameLabel"
    rel.to_id = "lastNameValue"
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
    print("json=\n")
    print(s)

    model2 = Model.from_json(s)
    print("model2={}".format(model2))
    assert True
