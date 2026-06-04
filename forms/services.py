import requests
import os
from dotenv import load_dotenv
from utils.api_response import api_response
from datetime import datetime,timezone
from xml.etree.ElementTree import Element, SubElement, tostring
import uuid

load_dotenv()

kobo_timeout = int(os.getenv("KOBO_TIMEOUT", 15))
kobo_token = os.getenv("KOBO_API_TOKEN")
KOBO_BASE_URL= os.getenv("KOBO_SERVER_URL")

headers = {
        "Authorization": f"Token {kobo_token}",
        "Content-Type": "application/json"
}



def parse_form_content(form_data: dict):
       
        try:
            content = form_data.get('content', {})
            survey = content.get('survey', [])
            choices = content.get('choices', [])
            
            choices_map = {}
            for choice in choices:
                list_name = choice.get('list_name', '')
                if list_name not in choices_map:
                    choices_map[list_name] = []
                choices_map[list_name].append({
                    'name': choice.get('name', ''),
                    'label': get_label(choice)
                })
            
            questions = []
            for item in survey:
                question = parse_question(item, choices_map)
                if question:
                    questions.append(question)
            
            return {
                'form_id': form_data.get('uid', ''),
                'form_name': form_data.get('name', ''),
                'form_title': get_label(content.get('settings', {})),
                'questions': questions,
                'submission_url': f"/api/v1/submissions/",
                'created_at': form_data.get('date_created'),
                'modified_at': form_data.get('date_modified'),
                'deployment_status': form_data.get('deployment__active', False),
                'owner': form_data.get('owner__username', ''),
                'permissions': form_data.get('permissions', [])
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing form: {e}")
            
def parse_question(item:dict, choices_map: dict) :
        """Parse individual question from Kobo survey"""
        question_type = item.get('type', '')
        
        # Skip groups and notes for now (can be enhanced later)
        if question_type in ['begin_group', 'end_group', 'note', 'start', 'end']:
            return None
        
        question = {
            'name': item.get('name', ''),
            'label': get_label(item),
            'type': map_question_type(question_type),
            'required': item.get('required', False),
            'hint': get_hint(item),
            'constraint': item.get('constraint'),
            'constraint_message': get_label(item.get('constraint_message', {})),
            'relevant': item.get('relevant'),
            'default': item.get('default'),
            'readonly': item.get('readonly', False),
            'appearance': item.get('appearance', '')
        }
        
        if question_type.startswith('select_'):
            choice_list = item.get('select_from_list_name', '')
            if choice_list in choices_map:
                question['choices'] = choices_map[choice_list]
                question['allow_other'] = 'other' in item.get('appearance', '')
        
       
        if question_type == 'integer':
            question['min_value'] = item.get('constraint', {}).get('min')
            question['max_value'] = item.get('constraint', {}).get('max')
        elif question_type == 'decimal':
            question['decimal_places'] = item.get('bind', {}).get('jr:constraintMsg', {}).get('decimal_places')
        elif question_type == 'text':
            question['max_length'] = item.get('bind', {}).get('jr:constraintMsg', {}).get('max_length')
        elif question_type == 'geopoint':
            question['accuracy_threshold'] = item.get('bind', {}).get('jr:preload', {}).get('accuracy')
        
        return question

def map_question_type(kobo_type: str) -> str:
       
        type_mapping = {
            'text': 'text',
            'integer': 'number',
            'decimal': 'decimal',
            'date': 'date',
            'datetime': 'datetime',
            'time': 'time',
            'select_one': 'single_choice',
            'select_multiple': 'multiple_choice',
            'geopoint': 'location',
            'geotrace': 'line',
            'geoshape': 'area',
            'image': 'photo',
            'audio': 'audio',
            'video': 'video',
            'file': 'file',
            'barcode': 'barcode',
            'calculate': 'calculated',
            'acknowledge': 'acknowledge',
            'range': 'range'
        }
        return type_mapping.get(kobo_type, 'text')

def get_label(item: dict) -> str:

        if not item:
            return ''
            
        label = item.get('label', '') if isinstance(item, dict) else item
        
        if isinstance(label, dict):
            return (label.get('English') or 
                   label.get('english') or 
                   label.get('default') or 
                   list(label.values())[0] if label else '')
        return str(label) if label else ''
    
def get_hint(item: dict) -> str:
        
        hint = item.get('hint', '')
        if isinstance(hint, dict):
            return (hint.get('English') or 
                   hint.get('english') or 
                   hint.get('default') or 
                   list(hint.values())[0] if hint else '')
        return str(hint) if hint else ''
    


def get_forms():
    try:
       
        KOBO_TOKEN=os.getenv("KOBO_API_TOKEN")
        url = f"{KOBO_BASE_URL}/api/v2/assets/?asset_type=survey"

        headers = {
                "Authorization": f"Token {KOBO_TOKEN}",
                "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=15)
       
        if not response.ok:
            raise ValueError(response.text)
        print(response.json())
        return response.json()
        
    except ValueError as error:
        raise ValueError("Error fetching forms")


def get_form_by_uuid(uuid:str):
    
    try:
        KOBO_BASE_URL= os.getenv("KOBO_SERVER_URL")
        # response=make_kobo_request(method='GET',url=KOBO_BASE_URL+"/api/v2/assets/"+uuid)
        response=requests.get(KOBO_BASE_URL+"/api/v2/assets/"+uuid,headers=headers,timeout=kobo_timeout)
        print("form response",response)
        return response.json()
        
    except ValueError as error:
        raise(f"Error fetching form {str(error)}")
       

def get_parsed_form( form_uid: str) :
        """Get form and parse it for mobile app consumption"""
        try:
            form_data = get_form_by_uuid(form_uid)
            if not form_data:
                return None
            
            parsed_form = parse_form_content(form_data)
            return parsed_form
        except Exception as e:
            raise ValueError(f"Failed to parse form {form_uid}: {e}")
            


def get_form_submissions(
        form_uid: str, 
        limit: int = 100, 
        start: int = 0,
        sort: str = "-_submission_time"
    ) :
        """Get submissions for a specific form"""
        try:
            params = {
                # "limit": limit,
                # "start": start,
                # "sort": sort,
                "format": "json"
            }
            
            
            response=requests.get(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/data",headers=headers,timeout=kobo_timeout)
            print('submissions',response.json())
            # submissions = response.json().get("results", [])
            submissions = response.json()
            # logger.info(f"Retrieved {len(submissions)} submissions for form {form_uid}")
            
            return {
                "results": submissions,
                "count": response.json().get("count", len(submissions)),
                "next": response.json().get("next"),
                "previous": response.json().get("previous")
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get submissions for form {form_uid}: {e}")
            
    
# def submit_warning( 
#         form_uuid: str, 
#         submission_data: dict
#     ) :
#         """Submit data to a Kobo form"""
#         try:
#             # Prepare submission data in Kobo format
#             kobo_submission = {
#                 "submission": submission_data,
#                 "meta/instanceID": f"uuid:{submission_data.get('_uuid', '')}",
#                 "meta/submissionTime": datetime.now(timezone.utc).isoformat(),
#             }
            
#             # response = make_kobo_request(
#             #     "POST",
#             #     f"/api/v2/assets/{form_uid}/submissions/",
#             #     data=kobo_submission
#             # )
#             print('kobo_submission',kobo_submission)
#             response=requests.post(KOBO_BASE_URL+"/api/v2/assets/"+form_uuid,headers=headers,timeout=kobo_timeout,data=kobo_submission)
#             # logger.info(f"Successfully submitted data to form {form_uid}")
#             return response.json()
            
#         except Exception as e:
#             raise ValueError(f"Failed to submit data to form {form_uuid}: {e}")
            
    
# def normalize_value(value):
#     if isinstance(value, dict) and "latitude" in value and "longitude" in value:
#         # Kobo geopoint format: lat lon altitude accuracy
#         return f"{value['latitude']} {value['longitude']} 0 0"

#     if isinstance(value, list):
#         # select_multiple values are space-separated in Kobo XML
#         return " ".join(map(str, value))

#     return "" if value is None else str(value)

# def normalize_value(value) -> str:
#     """Converts values to strings, handling Kobo geopoint objects explicitly."""
#     if isinstance(value, dict):
#         # Check if the dictionary represents a GPS coordinate object
#         if 'latitude' in value and 'longitude' in value:
#             lat = value.get('latitude')
#             lng = value.get('longitude')
#             alt = value.get('altitude', 0)
#             acc = value.get('accuracy', 0)
#             return f"{lat} {lng} {alt} {acc}"
#         return str(value)
#     if value is None:
#         return ""
#     if isinstance(value, bool):
#         return str(value).lower() # Kobo expects 'true' or 'false'
#     return str(value)

# def add_field(parent, key, value):
#     # Supports grouped keys like "group_name/field_name"
#     parts = key.split("/")
#     current = parent

#     for part in parts[:-1]:
#         child = current.find(part)
#         if child is None:
#             child = SubElement(current, part)
#         current = child

#     tag_name = parts[-1]

#     # RECURSIVE FIX: If value is a dictionary and NOT a geopoint, process it as sub-fields
#     if isinstance(value, dict) and not ('latitude' in value and 'longitude' in value):
#         group_node = current.find(tag_name)
#         if group_node is None:
#             group_node = SubElement(current, tag_name)
#         for sub_key, sub_value in value.items():
#             add_field(group_node, sub_key, sub_value)
#     else:
#         # Standard field or a flattened geopoint string
#         field = SubElement(current, tag_name)
#         field.text = normalize_value(value)

# def build_kobo_xml(xml_form_id: str, submission_data: dict) -> bytes:
#     # Kobo forms require the version attribute if your XLSForm has one. 
#     # Added fallback to prevent schema validation drops.
#     version = submission_data.get("__version__") or submission_data.get("_version", "")
    
#     root_attrs = {"id": xml_form_id}
#     if version:
#         root_attrs["version"] = str(version)
        
#     root = Element("data", root_attrs)

#     # Filter out Kobo's read-only system metadata keys
#     system_keys_to_skip = [
#         "_id", "_uuid", "_submission_time", "_status", "_tags", 
#         "_notes", "_validation_status", "_submitted_by", "__version__", "_version"
#     ]

#     for key, value in submission_data.items():
#         if key in system_keys_to_skip:
#             continue
#         add_field(root, key, value)

#     # Build meta block correctly
#     meta = SubElement(root, "meta")
#     instance_id = SubElement(meta, "instanceID")
    
#     # Extract existing UUID or fall back to creating a new one
#     raw_uuid = submission_data.get("_uuid") or submission_data.get("meta/instanceID") or str(uuid.uuid4())
#     if not raw_uuid.startswith("uuid:"):
#         raw_uuid = f"uuid:{raw_uuid}"
        
#     instance_id.text = raw_uuid

#     return tostring(root, encoding="utf-8", xml_declaration=True)

# def submit_warning(xml_form_id: str, submission_data: dict):
#     xml_bytes = build_kobo_xml(xml_form_id, submission_data)

#     files = {
#         "xml_submission_file": (
#             "submission.xml",
#             xml_bytes,
#             "text/xml",''
#         )
#     }
#     submit_headers={
#           "Authorization":headers.get("Authorization")
#     }
#     print('files',files)
#     response = requests.post(
#         f"{KOBO_BASE_URL}/api/v1/submissions",
#         headers=submit_headers,
#         files=files,
#         timeout=30,
#     )

#     if not response.ok:
#         raise ValueError(f"Kobo submit failed: {response.status_code} {response.text}")

#     return response.json() if response.text else {"success": True}



import uuid
import requests

def normalize_value(value):
    """Converts values to their natural Python types for JSON."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        if 'latitude' in value and 'longitude' in value:
            lat = value.get('latitude')
            lng = value.get('longitude')
            alt = value.get('altitude', 0)
            acc = value.get('accuracy', 0)
            return f"{lat} {lng} {alt} {acc}"
        return value  # nested dicts stay as-is; build_submission handles them
    return value  # ints, floats, strings pass through naturally


def build_submission_dict(submission_data: dict) -> dict:
    """
    Converts a flat/nested submission_data dict into the JSON shape
    Kobo expects:
    {
        "id": "<xml_form_id>",
        "submission": {
            "formhub": {"uuid": "<form_uuid>"},
            "<field>": "<value>",
            ...groups as nested dicts...,
            "meta": {"instanceID": "uuid:<uuid>"}
        }
    }
    NOTE: xml_form_id and form_uuid are injected by the caller.
    """
    system_keys_to_skip = [
        "_id", "_uuid", "_submission_time", "_status", "_tags",
        "_notes", "_validation_status", "_submitted_by",
        "__version__", "_version"
    ]

    submission = {}

    for key, value in submission_data.items():
        if key in system_keys_to_skip:
            continue

        # Handle slash-separated group paths: "group/field" → nested dict
        parts = key.split("/")
        current = submission
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        leaf = parts[-1]

        normalized = normalize_value(value)

        # If the leaf is itself a non-geopoint dict, merge recursively
        if isinstance(normalized, dict) and not isinstance(value, dict):
            current[leaf] = normalized
        else:
            current[leaf] = normalized

    # Inject meta/instanceID
    raw_uuid = (
        submission_data.get("_uuid")
        or submission_data.get("meta/instanceID")
        or str(uuid.uuid4())
    )
    if not raw_uuid.startswith("uuid:"):
        raw_uuid = f"uuid:{raw_uuid}"

    submission.setdefault("meta", {})["instanceID"] = raw_uuid

    return submission


def submit_warning(form_uuid: str, submission_data: dict):
    """
    xml_form_id : the form's id_string  (e.g. "aXxYyZz123")
                  GET https://kc.kobotoolbox.org/api/v1/forms?format=json
                  and find  "id_string"  for your form.

    form_uuid   : the form-level UUID   (e.g. "f739945244514a6bb304dc35d6049880")
                  same endpoint, field  "uuid".
                  This is NOT the submission UUID — it identifies the form schema.
    """
    submission = build_submission_dict(submission_data)

    # Inject formhub/uuid — required by KoboCAT to route the submission
    submission["formhub"] = {"uuid": form_uuid}

    payload = {
        "id": form_uuid,
        "submission": submission,
    }

    submit_headers = {
        "Authorization": headers.get("Authorization"),
        "Content-Type": "application/json",
    }

    print("payload", payload)

    response = requests.post(
        f"{KOBO_BASE_URL}/api/v1/submissions",  # must be kc. subdomain, not kf.
        headers=submit_headers,
        json=payload,
        timeout=30,
    )

    if not response.ok:
        raise ValueError(
            f"Kobo submit failed: {response.status_code} {response.text}"
        )

    return response.json() if response.text else {"success": True}





def update_submission(
      
        form_uid: str, 
        submission_id: str, 
        submission_data: dict
    ) :
        """Update an existing submission"""
        try:
            # response = make_kobo_request(
            #     "PUT",
            #     f"/api/v2/assets/{form_uid}/submissions/{submission_id}/",
            #     data=submission_data
            # )
            response=requests.put(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/submissions/"+submission_id,headers=headers,timeout=kobo_timeout,data=submission_data)
            # logger.info(f"Successfully updated submission {submission_id}")
            return response.json()
            
        except Exception as e:
            raise ValueError(f"Failed to update submission {submission_id}: {e}")
            raise
    
def delete_submission(
   
        form_uid: str, 
        submission_id: str
    ) -> bool:
        """Delete a submission"""
        try:
            # make_kobo_request(
            #     "DELETE",
            #     f"/api/v2/assets/{form_uid}/submissions/{submission_id}/"
            # )
            requests.delete(KOBO_BASE_URL+"/api/v2/assets/"+form_uid+"/submissions/"+submission_id,headers=headers,timeout=kobo_timeout)
            
            # logger.info(f"Successfully deleted submission {submission_id}")
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to delete submission {submission_id}: {e}")
            
    
def get_form_schema( form_uid: str):
        """Get the JSON schema for a form"""
        try:
            form_data = get_form_by_uuid(form_uid)
            if not form_data:
                return None
            
            content = form_data.get("content", {})
            return {
                "survey": content.get("survey", []),
                "choices": content.get("choices", []),
                "settings": content.get("settings", {})
            }
            
        except Exception as e:
            # logger.error(f"Failed to get form schema {form_uid}: {e}")
            raise ValueError(f"Failed to get form schema {form_uid}: {e}")
    



def parse_submission_data(submission_data: dict, form_structure: dict):
        """
        Parse submission data according to form structure
        
        Args:
            submission_data: Raw submission data
            form_structure: Parsed form structure
            
        Returns:
            Cleaned and validated submission data
        """
        parsed_data = {}
        questions_map = {q['name']: q for q in form_structure.get('questions', [])}
        
        for field_name, field_value in submission_data.items():
            # Skip system fields
            if field_name.startswith('_') or field_name.startswith('meta/'):
                continue
            
            question = questions_map.get(field_name)
            if not question:
                # Include unknown fields as-is
                parsed_data[field_name] = field_value
                continue
            
            # Parse based on question type
            question_type = question.get('type', 'text')
            parsed_data[field_name] = parse_field_value(
                field_value, question_type, question
            )
        
        return parsed_data
    
def parse_field_value(value, question_type: str, question: dict) :
        """Parse individual field value based on question type"""
        if value is None or value == '':
            return None
        
        try:
            if question_type == 'number':
                return int(value) if isinstance(value, (str, float)) else value
            elif question_type == 'decimal':
                return float(value) if isinstance(value, (str, int)) else value
            elif question_type == 'multiple_choice':
               
                if isinstance(value, str):
                    return [v.strip() for v in value.split() if v.strip()]
                return value if isinstance(value, list) else [value]
            elif question_type == 'location':
                
                if isinstance(value, str):
                    coords = value.split()
                    if len(coords) >= 2:
                        return {
                            'latitude': float(coords[0]),
                            'longitude': float(coords[1]),
                            'altitude': float(coords[2]) if len(coords) > 2 else None,
                            'accuracy': float(coords[3]) if len(coords) > 3 else None
                        }
                return value
            elif question_type in ['date', 'datetime']:
               
                return str(value)
            else:
                return str(value)
        except (ValueError, TypeError, IndexError):
            
            return value
  
def validate_submission_data(submission_data: dict, form_structure: dict) :
        """
        Validate submission data against form structure
        
        Args:
            submission_data: Submission data to validate
            form_structure: Form structure for validation
            
        Returns:
            Dictionary of field names with validation errors
        """
        errors = {}
        questions_map = {q['name']: q for q in form_structure.get('questions', [])}
        
        for question in form_structure.get('questions', []):
            field_name = question['name']
            field_value = submission_data.get(field_name)
            field_errors = []
            
            # Check required fields
            if question.get('required', False) and (field_value is None or field_value == ''):
                field_errors.append(f"{question.get('label', field_name)} is required")
            
            # Type-specific validation
            if field_value is not None and field_value != '':
                question_type = question.get('type', 'text')
                
                if question_type == 'number':
                    try:
                        int(field_value)
                    except (ValueError, TypeError):
                        field_errors.append(f"{question.get('label', field_name)} must be a number")
                
                elif question_type == 'decimal':
                    try:
                        float(field_value)
                    except (ValueError, TypeError):
                        field_errors.append(f"{question.get('label', field_name)} must be a decimal number")
                
                elif question_type in ['single_choice', 'multiple_choice']:
                    choices = question.get('choices', [])
                    valid_choices = [choice['name'] for choice in choices]
                    
                    if question_type == 'single_choice':
                        if field_value not in valid_choices:
                            field_errors.append(f"Invalid choice for {question.get('label', field_name)}")
                    else:  # multiple_choice
                        selected_values = field_value if isinstance(field_value, list) else [field_value]
                        for selected in selected_values:
                            if selected not in valid_choices:
                                field_errors.append(f"Invalid choice '{selected}' for {question.get('label', field_name)}")
            
            if field_errors:
                errors[field_name] = field_errors
        
        return errors
    
def get_form_summary(form_structure: dict):
        """
        Get summary information about a form
        
        Args:
            form_structure: Parsed form structure
            
        Returns:
            Form summary with statistics
        """
        questions = form_structure.get('questions', [])
        
        question_types = {}
        required_count = 0
        choice_questions = 0
        
        for question in questions:
            q_type = question.get('type', 'text')
            question_types[q_type] = question_types.get(q_type, 0) + 1
            
            if question.get('required', False):
                required_count += 1
            
            if q_type in ['single_choice', 'multiple_choice']:
                choice_questions += 1
        
        return {
            'form_id': form_structure.get('form_id', ''),
            'form_name': form_structure.get('form_name', ''),
            'total_questions': len(questions),
            'required_questions': required_count,
            'optional_questions': len(questions) - required_count,
            'choice_questions': choice_questions,
            'question_types': question_types,
            'has_location': 'location' in question_types,
            'has_media': any(t in question_types for t in ['photo', 'audio', 'video']),
            'deployment_status': form_structure.get('deployment_status', False),
            'created_at': form_structure.get('created_at'),
            'modified_at': form_structure.get('modified_at')
        }

