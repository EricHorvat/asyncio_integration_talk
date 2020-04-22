def control_int(nullable=False):
    def control(field_name, value):
        if value is None and nullable:
            return
        if value is None:
            raise ValueError(f"Trying to parse {field_name} with None value and should be an int")
        try:
            int(value)
        except ValueError:
            raise ValueError(f"Trying to parse {field_name} with value {value} and should be an int")

    return control


def control_str(field_name, value):
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")


def control_host(field_name, value):
    control_str(field_name, value)


def control_list(can_repeat=True):
    def control(field_name, value):
        if not isinstance(value, str):
            raise ValueError(f"Trying to parse {field_name} with value {value} and should be a list")
        listt = value.split(",")
        if len(listt) != len(set(listt)) and not can_repeat:
            raise ValueError(f"Trying to parse {field_name} with value {value} and contains repeated values")

    return control


def control_bool(field_name, value):
    if str(value).lower() not in ["true", "false", "t", "f"]:
        raise ValueError(f"Trying to parse {field_name} with value {value} and should be a bool")

