import re

def decompose_requirements(subject: str, body: str):
    """Naive requirement decomposition:
    - Groups by header-like lines (uppercase or lines ending with a colon)
    - Collects bulleted lines as individual requirements
    Returns list of dicts: {group, title, description}
    """

    lines_body = re.split(r'\n\s*\n', body)  # Split by blank lines for better grouping
    split_subject = re.split(r'[:\-–|]', subject)
    requirements = []
    current_group = None
    for lineperreq in lines_body:
        lines = lineperreq.splitlines()
        if lines[0].endswith(":") :
            current_group = lines[0].rstrip(":")
        if lines[0].startswith("#"):
            current_group = lines[0].split(".")[1].strip()
        title = split_subject[1] + " " + current_group
        description = ""
        for index, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if(index == 0):
                continue  # Skip the first line as it's the group name
            description += line + "\n"
        requirements.append({"group": current_group or "General", "title": title, "description": description})        
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
