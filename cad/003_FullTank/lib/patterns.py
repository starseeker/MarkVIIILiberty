"""Expand reusable source-linked assembly templates into stable native occurrences."""
from .parameters import scalar


def expand(data):
    records = data.get("patterns", [])
    assemblies = data.get("assemblies", {})
    values = data["values"]
    existing_ids = {x["id"] for x in data["occurrences"]}
    def add(identifier, parent, definition, parent_frame, tr, rot, evidence, template=None):
        if identifier in existing_ids or identifier in data["datums"]:
            raise ValueError("Generated occurrence/datum ID collision: " + identifier)
        existing_ids.add(identifier)
        data["datums"][identifier] = {"parent": parent_frame, "translation": tr, "rotation_deg": rot,
                                       "evidence": evidence, "notes": "Generated from a versioned assembly template and pattern."}
        entry = {"id": identifier, "parent": parent, "definition": definition, "frame": identifier, "evidence": evidence}
        if template:
            entry["assembly_template"] = template
            entry["survey_ids"] = assemblies[template].get("survey_ids", [])
        data["occurrences"].append(entry)
        return identifier
    def children(template_key, prefix, parent, frame, stack):
        if template_key in stack or template_key not in assemblies:
            raise ValueError("Missing/cyclic assembly template: " + template_key)
        spec = assemblies[template_key]
        for child in spec["children"]:
            identifier = prefix + "_" + child["id"]
            # Preserve expressions so an in-memory parameter perturbation updates
            # both native definitions and every nested installation datum.
            translation = child.get("translation", [0,0,0])
            rotation = child.get("rotation_deg", [0,0,0])
            nested = child.get("assembly")
            add(identifier, parent, child.get("definition"), frame, translation, rotation,
                child.get("evidence", spec["evidence"]), nested)
            for key in ['wheel_child','wheel_side','wheel_angle','wheel_rivet','idler_child','idler_side','idler_index','drive_mount_child','drive_mount_side','drive_mount_index']:
                if key in child:data['datums'][identifier][key]=child[key]
            if nested:
                children(nested, identifier, identifier, identifier, stack | {template_key})
    for pattern in records:
        count = scalar(pattern["count"], values, (0,0))
        if count < 1 or count != int(count):
            raise ValueError("Assembly pattern count must be a positive integer")
        root = pattern["id"]
        add(root, pattern["parent"], None, pattern["frame"], [0,0,0], [0,0,0], pattern["evidence"])
        data["occurrences"][-1]["survey_ids"] = pattern.get("survey_ids",[])
        step = pattern.get("step",[0,0,0])
        for index in range(int(count)):
            identifier = root + "_Unit" + str(index).zfill(3)
            translation = [str(index)+"*("+x+")" if isinstance(x,str) else index*x for x in step]
            template=pattern["assembly"]
            if pattern.get('mode')=='roller_bank':
                if int(count)!=len(data['roller_stations']):raise ValueError('Roller station count mismatch')
                template='roller_'+data['roller_stations'][index]['kind']+'_stack'
            add(identifier, root, None, root, translation, [0,0,0],
                pattern["evidence"], template)
            if pattern.get("mode") == "closed_track":
                data["datums"][identifier]["track_unit_index"] = index
            if pattern.get('mode')=='roller_bank':
                data['datums'][identifier]['roller_station']=data['roller_stations'][index]['id']
            children(template, identifier, identifier, identifier, set())
            if pattern.get('mode')=='roller_bank' and pattern['hand']==1:
                data['datums'][identifier+'_PinAssembly']['rotation_deg']=[180,0,0]
