"""Compose the oil-pump component families; development, not release geometry."""
from engine_oil_pump_parts import parts as core_parts
from engine_oil_pump_services import extend as add_services
from engine_oil_pump_strainers import extend as add_strainers


def parts(controls, progress=None):
    definitions, occurrences, groups, datums = core_parts(controls)
    add_services(controls, definitions, occurrences, groups, datums)
    add_strainers(controls, definitions, occurrences, groups, datums, progress)
    for key, shape in definitions.items():
        if progress:
            progress(key, shape)
        assert shape.isValid() and len(shape.Solids) == 1 and shape.Volume > 0, key
    return definitions, occurrences, groups, datums
