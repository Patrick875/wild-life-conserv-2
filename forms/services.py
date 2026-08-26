import requests
import os
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from forms.helpers import *
from warning.models import Warning
from warning_feedbacks.models import WarningFeedback
from werkzeug.exceptions import BadRequest
from extensions import db
from sqlalchemy import and_

load_dotenv()

kobo_timeout = int(os.getenv("KOBO_TIMEOUT", 15))
kobo_token = os.getenv("KOBO_API_TOKEN")
KOBO_BASE_URL= os.getenv("KOBO_SERVER_URL")

headers = {
        "Authorization": f"Token {kobo_token}",
        "Content-Type": "application/json"
}

def get_kobo_kpi_base_url():
    """Kobo v2 endpoints live on KPI, which uses kf instead of the old kc host."""
    base_url = (KOBO_BASE_URL or "https://kf.kobotoolbox.org").rstrip("/")
    if "://kc." in base_url:
        return base_url.replace("://kc.", "://kf.", 1)
    return base_url

def append_submission_xml(parent, key, value):
    child = ET.SubElement(parent, key)

    if isinstance(value, dict):
        for child_key, child_value in value.items():
            append_submission_xml(child, child_key, child_value)
        return

    if isinstance(value, list):
        child.text = json.dumps(value)
        return

    child.text = "" if value is None else str(value)

def build_openrosa_xml(form_uuid: str, submission: dict, form_data=None):
    content = (form_data or {}).get("content", {})
    settings = content.get("settings", {})
    root_name = settings.get("id_string") or (form_data or {}).get("uid") or form_uuid
    formhub_uuid = (form_data or {}).get("deployment__uuid") or form_uuid

    submission["formhub"] = {"uuid": formhub_uuid}

    root = ET.Element(root_name)
    for key, value in submission.items():
        append_submission_xml(root, key, value)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def get_forms():
    try:
       
        KOBO_TOKEN=os.getenv("KOBO_API_TOKEN")
        url = f"{get_kobo_kpi_base_url()}/api/v2/assets/?asset_type=survey"

        headers = {
                "Authorization": f"Token {KOBO_TOKEN}",
                "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=15)
       
        if not response.ok:
            raise BadRequest(response.text)
        print(response.json())
        return response.json()
        
    except ValueError as error:
        raise ValueError(f"Error fetching forms {str(error)}")


def get_form_by_uuid(uuid:str):
    
    try:
        # response=make_kobo_request(method='GET',url=get_kobo_kpi_base_url()+"/api/v2/assets/"+uuid)
        response=requests.get(get_kobo_kpi_base_url()+"/api/v2/assets/"+uuid,headers=headers,timeout=kobo_timeout)
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
            
            response=requests.get(get_kobo_kpi_base_url()+"/api/v2/assets/"+form_uid+"/data",headers=headers,timeout=kobo_timeout)
            submissions = Warning.query.order_by(Warning.created_at.desc()).filter_by(kobo_form_id=form_uid).all()
            
            submissions_normalized=[submission.to_dict(include_feedbacks=True) for submission in submissions] or []
           
            return {
                "api_results":submissions_normalized,
                "count": len(submissions_normalized),
                "next": response.json().get("next"),
                "previous": response.json().get("previous")
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get submissions for form {form_uid}: {e}")

def get_submissions_by_user(form_id:int,user_id:int):
     submissions = Warning.query.order_by(Warning.created_at.desc()).filter(and_(Warning.user_id==user_id,Warning.kobo_form_id==form_id)).all()
     submissions_normalized=[submission.to_dict(include_feedbacks=True) for submission in submissions] or []
     return {
            "api_results":submissions_normalized,
            "count": len(submissions_normalized),
            }

def submit_warning(form_uuid: str, submission_data: dict,user_id:int):
    """
    form_uuid is the Kobo asset uid used by the KPI v2 API.
    """
    submission = build_submission_dict(submission_data)
    form_data = get_form_by_uuid(form_uuid)
    submission_xml = build_openrosa_xml(form_uuid, submission, form_data)
    submitted_instance_id = submission.get("meta", {}).get("instanceID", "")

    warning=Warning(
        kobo_form_id = form_uuid,
        submission_data = submission,
        user_id = user_id
      )
    
    db.session.add(warning)
    db.session.flush()

    submit_headers = {
        "Authorization": headers.get("Authorization"),
    }

    response = requests.post(
        f"{get_kobo_kpi_base_url()}/submission",
        headers=submit_headers,
        files={
            "xml_submission_file": (
                "submission.xml",
                submission_xml,
                "text/xml",
            )
        },
        timeout=30,
    )

    response_text = response.text or ""
    try:
        kobo_response = response.json() if response_text.strip() else {}
    except ValueError:
        kobo_response = {}

    print(f'\n\n\n\n this is submission-response {response.status_code} {response_text} \n\n\n\n\n\n ')

    if not response.ok:
        raise BadRequest(
            f"Kobo submit failed: {response.status_code} {response_text or response.reason}"
        )

    submission_id = str(
        kobo_response.get("instanceID")
        or kobo_response.get("uuid")
        or kobo_response.get("_uuid")
        or kobo_response.get("root_uuid")
        or kobo_response.get("uid")
        or kobo_response.get("_id")
        or submitted_instance_id
        or ""
    ).replace("uuid:", "")
    if not submission_id:
        raise BadRequest(f"Kobo submit response missing instanceID: {response_text}")
    warning.status='submitted'
    warning.kobo_submission_id=submission_id
    
    db.session.commit()

    if kobo_response:
        return kobo_response

    return {
        "success": True,
        "instanceID": submitted_instance_id,
        "kobo_response": response_text,
    }

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
            warning = Warning.query.filter_by(id=submission_id, kobo_form_id=form_uid).first()
            kobo_submission_id = warning.kobo_submission_id if warning else submission_id
            response=requests.put(get_kobo_kpi_base_url()+"/api/v2/assets/"+form_uid+"/data/"+kobo_submission_id,headers=headers,timeout=kobo_timeout,json=submission_data)
            if not response.ok:
                raise ValueError(response.text)

            if warning:
                warning.submission_data = submission_data
                db.session.commit()

            # logger.info(f"Successfully updated submission {submission_id}")
            return response.json() if response.text else {"success": response.ok}
            
        except Exception as e:
            raise ValueError(f"Failed to update submission {submission_id}: {e}")
    
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
            warning = Warning.query.filter_by(id=submission_id, kobo_form_id=form_uid).first()
            kobo_submission_id = warning.kobo_submission_id if warning else submission_id
            response = requests.delete(get_kobo_kpi_base_url()+"/api/v2/assets/"+form_uid+"/data/"+kobo_submission_id,headers=headers,timeout=kobo_timeout)
            if not response.ok:
                raise ValueError(response.text)

            if warning:
                WarningFeedback.query.filter_by(warning_id=warning.id).delete()
                db.session.delete(warning)
                db.session.commit()
            
            # logger.info(f"Successfully deleted submission {submission_id}")
            return {"success": response.ok}
            
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
    
