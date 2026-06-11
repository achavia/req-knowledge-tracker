def decompose_requirements(subject: str, body: str):
    """Naive requirement decomposition:
    - Groups by header-like lines (uppercase or lines ending with a colon)
    - Collects bulleted lines as individual requirements
    Returns list of dicts: {group, title, description}
    """

    lines = body.splitlines()
    requirements = []
    current_group = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") or line.isupper():
            current_group = line.rstrip(":")
            continue
        if line.startswith("-") or line.startswith("*"):
            title = line.lstrip("-* ").strip()
            requirements.append({"group": current_group or "General", "title": f"{current_group} - {title}" if current_group else title, "description": title})
        else:
            # treat short lines as possible group headers
            if len(line.split()) <= 3 and line[0].isupper():
                current_group = line
            else:
                requirements.append({"group": current_group or "General", "title": line, "description": line})
    return requirements


def find_related_requirements(db_session, group_name: str, project_name: str, exclude_requirement_id: int = None):
    """Find all requirements in the same feature group.
    Used to show developers previous changes to the same feature.
    """
    from app.models import RequirementGroup, Requirement
    
    group = db_session.query(RequirementGroup).filter(RequirementGroup.name == group_name, RequirementGroup.project_name == project_name).first()
    if not group:
        return []
    
    query = db_session.query(Requirement).filter(Requirement.group_id == group.id)
    if exclude_requirement_id:
        query = query.filter(Requirement.id != exclude_requirement_id)
    
    return query.all()
